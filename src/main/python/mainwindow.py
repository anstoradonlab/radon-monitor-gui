import copy
import datetime
import logging
import math
import os
import pprint
import sys
import threading
import time
from typing import Dict, List

import numpy as np
import pyqtgraph
from ansto_radon_monitor.configuration import (Configuration,
                                               config_from_yamlfile)
from ansto_radon_monitor.main import setup_logging
from ansto_radon_monitor.main_controller import MainController, initialize
from fbs_runtime.application_context.PyQt5 import ApplicationContext
from PyQt5 import QtCore, QtGui, QtWidgets, uic
# from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtCore import QSettings, Qt, QTimer

from c_and_b import CAndBForm
from system_information import SystemInformationForm
from data_view import DataViewForm
from ui_mainwindow import Ui_MainWindow

# import pandas as pd
# import tabulate


# data model for linking table view with instrument data
# here's an intro to this approach:
# https://www.learnpyqt.com/tutorials/qtableview-modelviews-numpy-pandas/
# more docs:
# https://doc.qt.io/archives/qtforpython-5.12/overviews/model-view-programming.html#model-view-programming
# https://doc.qt.io/qtforpython/PySide6/QtCore/QAbstractTableModel.html

# useful sample code:
# https://stackoverflow.com/questions/22791760/pyqt-adding-rows-to-qtableview-using-qabstracttablemodel


_logger = logging.getLogger(__name__)

# small class for our 'log message' signal to live in
class QTextEditLogger(logging.Handler, QtCore.QObject):
    appendPlainText = QtCore.pyqtSignal(str)

    def __init__(self, widget):
        super().__init__()
        QtCore.QObject.__init__(self)
        self.widget = widget
        self.widget.setReadOnly(True)
        self.appendPlainText.connect(self.widget.appendPlainText)

    def emit(self, record):
        msg = self.format(record)
        self.appendPlainText.emit(msg)


class QTextEditLogger_non_threadsafe(logging.Handler):
    def __init__(self, widget):
        """widget - a QPlainTextEdit to send log messages to"""
        super().__init__()
        self.widget = widget
        self.widget.setReadOnly(True)

    def emit(self, record):
        assert threading.current_thread() is threading.main_thread()
        msg = self.format(record)
        self.widget.appendPlainText(msg)


# Utility class for preventing windows' sleep

class WindowsInhibitor:
    '''Prevent OS sleep/hibernate in windows; code from:
    https://github.com/h3llrais3r/Deluge-PreventSuspendPlus/blob/master/preventsuspendplus/core.py
    API documentation:
    https://msdn.microsoft.com/en-us/library/windows/desktop/aa373208(v=vs.85).aspx'''
    ES_CONTINUOUS = 0x80000000
    ES_SYSTEM_REQUIRED = 0x00000001

    def __init__(self):
        pass

    def inhibit():
        import ctypes
        ctypes.windll.kernel32.SetThreadExecutionState(
            WindowsInhibitor.ES_CONTINUOUS | \
            WindowsInhibitor.ES_SYSTEM_REQUIRED)

    def uninhibit():
        import ctypes
        ctypes.windll.kernel32.SetThreadExecutionState(
            WindowsInhibitor.ES_CONTINUOUS)


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, appctxt: ApplicationContext, *args, **kwargs):
        # fbs application context
        self.appctxt = appctxt
        super(MainWindow, self).__init__(*args, **kwargs)

        if os.name == 'nt':
            WindowsInhibitor.inhibit()

        self.qsettings = QSettings("au.gov.ansto", appctxt.app.applicationName())
        _logger.debug(f"QSettings initialised at {self.qsettings.fileName()}")

        self.instrument_controller = None
        self.config: Configuration = None
        self.configured_tables: List[str] = []

        # Load the UI Page
        # uic.loadUi(appctxt.get_resource("main_window.ui"), baseinstance=self)
        
        self.setupUi(self)

        logTextBox = self.logArea
        guilogger = QTextEditLogger(logTextBox)
        logformat = "[%(levelname)1.1s %(asctime)s %(module)s:%(lineno)d %(threadName)s] %(message)s"
        guilogger.setFormatter(logging.Formatter(logformat))
        # filter out low-level messages from serial port comms
        class Blacklist(logging.Filter):
            def __init__(self):
                self.blacklist = ["pycampbellcr1000", "pylink"]

            def filter(self, record):
                """return True to keep message"""
                return not record.name in self.blacklist

        guilogger.addFilter(Blacklist())

        logging.getLogger().addHandler(guilogger)
        # You can control the logging level (TODO: get from config file)
        logging.getLogger().setLevel(logging.INFO)

        self.connect_signals()

        self.redraw_timer = QTimer()
        self.redraw_timer.setInterval(5000)
        self.redraw_timer.timeout.connect(self.update_displays)
        self.redraw_timer.start()

        self.cal_dialog = None
        self.sysinfo_dialog = None

        geom = self.qsettings.value("geometry")
        winstate = self.qsettings.value("windowState")
        # if the qsettings value does not exist it is set to None
        if geom is None or winstate is None:
            pass
        else:
            try:
                self.restoreGeometry(geom)
                self.restoreState(winstate)
            except Exception as ex:
                _logger.error(f'Error restoring window state: {ex}')

        # Begin logging if we can find a configuration file
        if self.qsettings.contains("config_fname"):
            config_fname = self.qsettings.value("config_fname")
            self.begin_controlling(config_fname)

    def show_data(self):
        if self.config is not None:
            data_dir = os.path.realpath(self.config.data_dir)
            QtGui.QDesktopServices.openUrl(QtCore.QUrl.fromLocalFile(data_dir))

    def connect_signals(self):
        self.actionLoad_Configuration.triggered.connect(self.onLoadConfiguration)
        self.actionQuit.triggered.connect(self.close)
        self.actionShow_Data.triggered.connect(self.show_data)
        self.actionViewCalibration.triggered.connect(self.view_calibration_dialog)
        self.actionViewSystemInformation.triggered.connect(self.view_system_information_dialog)

    def onLoadConfiguration(self, s):
        print(f"Load the configuration... {s}")
        config_fname, config_filter = QtWidgets.QFileDialog.getOpenFileName(
            self, "Open configuration", ".", "YAML files (*.yaml *.yml)"
        )
        print(f"Loading from {config_fname}")
        self.qsettings.setValue("config_fname", config_fname)
        self.begin_controlling(config_fname)

    def view_calibration_dialog(self):
        if self.cal_dialog is not None:
            self.cal_dialog.show()
        else:
            # side note: this is quite a nice example of how to generate UI with code
            # using current idioms
            # https://doc.qt.io/qtforpython/tutorials/basictutorial/dialog.html
            w = CAndBForm(mainwindow=self)
            cal_dialog = QtWidgets.QDialog(parent=self)
            cal_dialog.setWindowTitle("Calibration and Background Control")
            layout = QtWidgets.QVBoxLayout(cal_dialog)
            layout.addWidget(w)
            cal_dialog.show()
            self.cal_dialog = cal_dialog


    def view_system_information_dialog(self):
        if self.sysinfo_dialog is not None:
            self.sysinfo_dialog.show()
        else:
            w = SystemInformationForm(mainwindow=self)
            sysinfo_dialog = QtWidgets.QDialog(parent=self)
            sysinfo_dialog.setWindowTitle("System Information")
            layout = QtWidgets.QVBoxLayout(sysinfo_dialog)
            layout.addWidget(w)
            sysinfo_dialog.show()
            self.sysinfo_dialog = sysinfo_dialog

    def begin_controlling(self, config_fname):
        if self.instrument_controller is not None:
            self.instrument_controller.shutdown()
        _logger.debug(f"Reading configuration from {config_fname}")
        try:
            config = config_from_yamlfile(config_fname)
        except Exception as ex:
            _logger.warning(f"Exception occured while trying to load configuration: {ex}")
            return

        self.config = config
        # update times need to be reset
        self.update_times = {}
        self.instrument_controller = initialize(config, mode="thread")

    def closeEvent(self, event):
        # catch the close event
        if os.name == 'nt':
            WindowsInhibitor.uninhibit()
            
        # TODO: don't shut down IC on Linux 
        print("shutting down instrument controller")
        if self.instrument_controller is not None:
            self.instrument_controller.shutdown()

        self.qsettings.setValue("geometry", self.saveGeometry())
        self.qsettings.setValue("windowState", self.saveState())

        event.accept()
        # abort exiting with "event.ignore()"

    def update_displays(self):
        ic = self.instrument_controller
        if not self.is_logging:
            return

        tables = ic.list_data_tables()
        if not set(self.configured_tables) == set(tables):
            # build data view UI
            tabwidget = self.tabWidget
            # remove all tabs
            while len(tabwidget) > 0:
                data_view = tabwidget.removeTab(0)
                del data_view
            self.configured_tables = []
            for table_name in tables:
                data_view = DataViewForm(self, table_name)
                tabwidget.addTab(data_view, table_name)
                self.configured_tables.append(table_name)

    @property
    def is_logging(self):
        return self.instrument_controller is not None
    
    def stop_logging(self):
        if self.is_logging:
            self.instrument_controller.shutdown()
            self.instrument_controller = None
    
    def start_logging(self):
        if not self.is_logging:
            if self.qsettings.contains("config_fname"):
                config_fname = self.qsettings.value("config_fname")
                self.begin_controlling(config_fname)
            else:
                # TODO: this method might not exist!
                self.actionLoad_Configuration.emit()