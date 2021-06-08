import copy
import datetime
import math
import os
import pprint
import sys
import threading
import time
from typing import Dict

import numpy as np
import pyqtgraph
from ansto_radon_monitor.configuration import Configuration, config_from_yamlfile
from ansto_radon_monitor.main import setup_logging
from ansto_radon_monitor.main_controller import MainController, initialize
from fbs_runtime.application_context.PyQt5 import ApplicationContext
from PyQt5 import QtCore, QtGui, QtWidgets, uic

# from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtCore import Qt, QTimer, QSettings
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


class TableModel(QtCore.QAbstractTableModel):
    def __init__(self, data):
        super(TableModel, self).__init__()
        self._data = data
        if len(data) > 0:
            self._column_names = list(data[0])
        else:
            self._column_names = []

    def data(self, index, role):
        if role == Qt.DisplayRole:
            # Get the raw value
            value = list(self._data[index.row()].values())[index.column()]

            # Perform per-type checks and render accordingly.
            if isinstance(value, datetime.datetime):
                # Render date and time
                return value.strftime("%Y-%m-%d %H:%M:%S")

            if isinstance(value, float):
                # Render float to 2 dp
                return "%.2f" % value

            if isinstance(value, str):
                # Render strings with quotes
                return '"%s"' % value

            # Default (anything not captured above: e.g. int)
            return str(value)

    def rowCount(self, index):
        # The length of the outer list.
        return len(self._data)

    def columnCount(self, index):
        # The following takes the first dict, and returns
        # the length (only works if all rows are an equal length)
        return len(self._data[0])

    def headerData(self, section, orientation, role):
        # section is the index of the column/row.
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return str(self._column_names[section])

            if orientation == Qt.Vertical:
                # use row number here
                return str(section)

    def update_data(self, new_data):
        if len(new_data) == 0 and len(self._data) == 0:
            # no-op
            return
        self.beginResetModel()
        self._data = new_data
        self._column_names = list(new_data[0])
        self.endResetModel()

    # def append_data(self, new_data):
    #    self.beginResetModel()
    #    self._data.extend(new_data)
    #    self.endResetModel()

    def append_data(self, new_data):

        N = len(self._data)
        Nnew = len(new_data)
        if len(new_data) == 0:
            return

        print(f"new data:{new_data}, length {N}, {N+len(new_data)-1}")
        self.beginInsertRows(QtCore.QModelIndex(), N, N + len(new_data) - 1)
        self._data.extend(new_data)
        self.endInsertRows()

        assert len(self._data) == N + Nnew


import logging
import sys


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


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, appctxt:ApplicationContext, *args, **kwargs):
        # fbs application context
        self.appctxt = appctxt
        super(MainWindow, self).__init__(*args, **kwargs)

        self.qsettings = QSettings('au.gov.ansto', appctxt.app.applicationName())
        _logger.debug(f'QSettings initialised at {self.qsettings.fileName()}')

        self.instrument_controller = None
        self.config: Configuration = None

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
        # You can control the logging level (TODO: get from log file)
        logging.getLogger().setLevel(logging.INFO)

        # set up the current data display - the table widget is called
        # pastDataTableView

        data = [{"a": 1, "b": 2, "c": 3} for ii in range(10)]

        self.model = TableModel(data)
        self.pastDataTableView.setModel(self.model)

        # add some dummy data to the plot window
        # self.step_plot([1,2,3,4,5,6,7,8,9,10], [30,32,34,32,33,31,29,32,35,45])

        self.connect_signals()
        # when were the data tables updated?
        self.update_times: Dict[str, datetime.datetime] = {}

        self.redraw_timer = QTimer()
        self.redraw_timer.setInterval(1000)
        self.redraw_timer.timeout.connect(self.update_displays)
        self.redraw_timer.start()

        try:
            self.restoreGeometry(self.qsettings.value("geometry"))
            self.restoreState(self.qsettings.value("windowState"))
        except TypeError:
            pass

        if self.qsettings.contains('config_fname'):
            config_fname = self.qsettings.value('config_fname')
            self.begin_controlling(config_fname)


    def plot(self, x, y, title=None):
        self.graph_widget.plot(x, y)
        self.graph_widget.setTitle(title)

    def step_plot(self, x, y, title=None):
        dx = np.r_[np.diff(x), np.median(np.diff(x))]
        xplt = np.empty(len(x) * 2)
        xplt[::2] = x
        xplt[1::2] = x + dx
        yplt = np.empty(len(y) * 2)
        yplt[::2] = y
        yplt[1::2] = y
        self.graph_widget.plot(xplt, yplt)
        self.graph_widget.setTitle(title)
    
    def show_data(self):
        if self.config is not None:
            data_dir = os.path.realpath(self.config.data_dir)
            QtGui.QDesktopServices.openUrl(QtCore.QUrl.fromLocalFile(data_dir))

    def connect_signals(self):
        self.actionLoad_Configuration.triggered.connect(self.onLoadConfiguration)
        self.actionQuit.triggered.connect(self.close)
        self.actionShow_Data.triggered.connect(self.show_data)
        self.calibrateButton.clicked.connect(self.onCalibrate)
        self.backgroundButton.clicked.connect(self.onBackground)

        # disable calendar edit if the checkbox is disabled
        self.calCheckBox.toggled.connect(self.calDateTimeEdit.setEnabled)
        self.bgCheckBox.toggled.connect(self.bgDateTimeEdit.setEnabled)

        # scroll data view to end when new data comes in
        # TODO: make this only scroll if the scroll bar was already at the end
        self.model.rowsInserted.connect(
            lambda: QtCore.QTimer.singleShot(0, self.pastDataTableView.scrollToBottom)
        )

        self.stopBgPushButton.clicked.connect(self.onStopBg)
        self.stopCalPushButton.clicked.connect(self.onStopCal)

    def onLoadConfiguration(self, s):
        print(f"Load the configuration... {s}")
        config_fname, config_filter = QtWidgets.QFileDialog.getOpenFileName(
            self, "Open configuration", ".", "YAML files (*.yaml *.yml)"
        )
        print(f"Loading from {config_fname}")
        self.qsettings.setValue('config_fname', config_fname)
        self.begin_controlling(config_fname)
        

    def begin_controlling(self, config_fname):
        if self.instrument_controller is not None:
            self.instrument_controller.shutdown()
        config = config_from_yamlfile(config_fname)
        self.config = config
        # update times need to be reset
        self.update_times = {}
        self.instrument_controller = initialize(config, mode="thread")


    def closeEvent(self, event):
        # catch the close event
        print("shutting down instrument controller")
        if self.instrument_controller is not None:
            self.instrument_controller.shutdown()

        self.qsettings.setValue("geometry", self.saveGeometry());
        self.qsettings.setValue("windowState", self.saveState());       

        event.accept()
        # abort exiting with "event.ignore()"

    def onCalibrate(self, s):
        if self.calDateTimeEdit.isEnabled():
            start_time = self.calDateTimeEdit.dateTime().toUTC().toPyDateTime()
        else:
            start_time = None
        print(f"calibrate at {start_time} UTC")
        self.instrument_controller.run_calibration(start_time=start_time)

    def onStopCal(self, s):
        self.instrument_controller.stop_calibration()

    def onBackground(self, s):
        if self.bgDateTimeEdit.isEnabled():
            start_time = self.bgDateTimeEdit.dateTime().toUTC().toPyDateTime()
        else:
            start_time = None
        print(f"background at {start_time} UTC")
        # TODO: also need to determine duration from UI + config
        self.instrument_controller.run_background(start_time=start_time)

    def onStopBg(self, s):
        self.instrument_controller.stop_background()

    def update_displays(self):

        # update the calibration time widgets
        # next 30 min interval
        next30min = datetime.datetime.fromtimestamp(
            math.ceil(time.time() / 60 / 30) * 60 * 30
        )
        self.bgDateTimeEdit.setMinimumDateTime(next30min)
        self.calDateTimeEdit.setMinimumDateTime(next30min)

        # print('display update')
        if self.instrument_controller is None:
            return

        # TODO: first check if there is any updated data
        # TODO: only get the most recent data
        ic = self.instrument_controller

        # TODO: give InstrumentController a reasonable API, and only
        # access things via that API
        tables = ic.list_tables()
        for tname in tables:
            prev_time = self.update_times.get(tname, None)
            t, newdata = ic.get_rows(tname, start_time=prev_time)
            self.update_times[tname] = t

            if len(newdata) > 0:
                t, entire_data_table = ic.get_rows(tname)
                # print('recent times in datastore...')
                # print(', '.join([ f"{entire_data_table[ii]['Datetime']}" for ii in [-2, -1]]))
                # print('recent times in model...')
                try:
                    print(
                        ", ".join(
                            [f"{self.model._data[ii]['Datetime']}" for ii in [-2, -1]]
                        )
                    )
                except:
                    pass

            #            if 'RTV' in self.update_times:
            #                print(self.update_times['RTV'])
            if "RTV" in tname:
                if prev_time is None:
                    self.model.update_data(newdata)
                else:
                    self.model.append_data(newdata)

        # html = ""
        # for t in ['RTV']: #ds.tables:
        #     tdata = data[t]
        #     if len(tdata) > 0:
        #         headers = [tdata[0].keys()]
        #         row_contents = [itm.values() for itm in tdata]
        #         html += tabulate.tabulate(headers+row_contents, headers='firstrow', tablefmt='html')

        # there is also an "append" option
        status_dict = ic.get_status()
        #jq = ic.get_job_queue()
        status_text = pprint.pformat(status_dict)
        status_text += f'\nTables:{ic.list_tables()}'
        #status_text += "\n"
        #status_text += str(jq)
        self.livedataArea.setText(status_text)

        # tref = datetime.datetime.now()
        # x = [(itm['Datetime'] - tref).total_seconds() for itm in data['RTV']]
        tables = ic.list_tables()
        for tname in tables:
            if 'Results' in tname:
                t, data = ic.get_rows(tname)
                x = [itm['RecNbr'] for itm in data]
                y = [itm['PanTemp_Avg'] for itm in data]
                self.step_plot(x, y, title=tname)
