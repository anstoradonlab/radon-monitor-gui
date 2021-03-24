from fbs_runtime.application_context.PyQt5 import ApplicationContext
#from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtCore import QTimer
from PyQt5 import QtWidgets, QtCore
from PyQt5 import uic
from PyQt5.QtCore import Qt
import numpy as np
import sys
import datetime
import pyqtgraph
import math
import time
import copy

from ansto_radon_monitor.main_controller import MainController
from ansto_radon_monitor.main_controller import initialize
from ansto_radon_monitor.configuration import config_from_yamlfile


from ui_mainwindow import Ui_MainWindow

import pandas as pd

import tabulate


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
        if len(data)>0:
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
    

    #def append_data(self, new_data):
    #    self.beginResetModel()
    #    self._data.extend(new_data)
    #    self.endResetModel()

    def append_data(self, new_data):
        
        N = len(self._data)
        Nnew = len(new_data)
        if len(new_data) == 0:
            return
        
        print(f'new data:{new_data}, length {N}, {N+len(new_data)-1}')
        self.beginInsertRows(QtCore.QModelIndex(), N, N+len(new_data)-1)
        self._data.extend(new_data)
        self.endInsertRows()

        assert(len(self._data) == N + Nnew)



class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):

    def __init__(self, appctxt, *args, **kwargs):
        # fbs application context
        self.appctxt = appctxt
        super(MainWindow, self).__init__(*args, **kwargs)

        self.instrument_controller = None

        #Load the UI Page
        #uic.loadUi(appctxt.get_resource("main_window.ui"), baseinstance=self)

        self.setupUi(self)
        

        # set up the current data display - the table widget is called
        # pastDataTableView

        data = [ {'a':1, 'b':2, 'c':3} for ii in range(10)]
        

        self.model = TableModel(data)
        self.pastDataTableView.setModel(self.model)


        # add some dummy data to the plot window
        #self.step_plot([1,2,3,4,5,6,7,8,9,10], [30,32,34,32,33,31,29,32,35,45])

        self.connect_signals()
        # when were the data tables updated?
        self.update_times = {}

        self.redraw_timer = QTimer()
        self.redraw_timer.setInterval(1000)
        self.redraw_timer.timeout.connect(self.update_displays)
        self.redraw_timer.start()



    def plot(self, x, y):
        self.graph_widget.plot(x, y)
    
    def step_plot(self, x, y):
        dx = np.r_[np.diff(x), np.median(np.diff(x))]
        xplt = np.empty(len(x)*2)
        xplt[::2] = x
        xplt[1::2] = x+dx
        yplt = np.empty(len(y)*2)
        yplt[::2] = y
        yplt[1::2] = y
        self.graph_widget.plot(xplt,yplt)


    def connect_signals(self):
        self.actionLoad_Configuration.triggered.connect(self.onLoadConfiguration)
        self.actionQuit.triggered.connect(self.close)
        self.calibrateButton.clicked.connect(self.onCalibrate)
        self.backgroundButton.clicked.connect(self.onBackground)

        # disable calendar edit if the checkbox is disabled
        self.calCheckBox.toggled.connect(self.calDateTimeEdit.setEnabled)
        self.bgCheckBox.toggled.connect(self.bgDateTimeEdit.setEnabled)

        # scroll data view to end when new data comes in
        # TODO: make this only scroll if the scroll bar was already at the end
        self.model.rowsInserted.connect(lambda: QtCore.QTimer.singleShot(0, self.pastDataTableView.scrollToBottom))

    

    def onLoadConfiguration(self, s):
        print(f"Load the configuration... {s}")
        config_fname, config_filter = QtWidgets.QFileDialog.getOpenFileName(self, 'Open configuration', 
   '.',"YAML files (*.yaml *.yml)")
        print(f"Loading from {config_fname}")

        config = config_from_yamlfile(config_fname)

        # update times need to be reset
        self.update_times = {}

        self.instrument_controller = initialize(config, mode='thread')
        
    def closeEvent(self, event):
        # catch the close event
        print('shutting down instrument controller')
        if self.instrument_controller is not None:
            self.instrument_controller.shutdown()

        event.accept()
        # abort exiting with "event.ignore()"
       
    
    def onCalibrate(self, s):
        if self.calDateTimeEdit.isEnabled():
            start_time = self.calDateTimeEdit.dateTime().toUTC().toPyDateTime()
        else:
            start_time = None
        print(f"calibrate at {start_time} UTC")
        self.instrument_controller.run_calibration(start_time=start_time)

    def onBackground(self, s):
        if self.bgDateTimeEdit.isEnabled():
            start_time = self.bgDateTimeEdit.dateTime().toUTC().toPyDateTime()
        else:
            start_time = None
        print(f"background at {start_time} UTC")
        # TODO: also need to determine duration from UI + config
        self.instrument_controller.run_background(start_time=start_time)




    def update_displays(self):
        
        # update the calibration time widgets
        # next 30 min interval
        next30min = datetime.datetime.fromtimestamp(math.ceil( time.time() / 60 / 30) * 60*30)
        self.bgDateTimeEdit.setMinimumDateTime(next30min)
        self.calDateTimeEdit.setMinimumDateTime(next30min)


        #print('display update')
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
                #print('recent times in datastore...')
                #print(', '.join([ f"{entire_data_table[ii]['Datetime']}" for ii in [-2, -1]]))
                #print('recent times in model...')
                try:
                    print(', '.join([ f"{self.model._data[ii]['Datetime']}" for ii in [-2, -1]]))
                except:
                    pass


#            if 'RTV' in self.update_times:
#                print(self.update_times['RTV'])
            if tname == 'RTV':
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
        jq = ic.get_job_queue()
        status_text = str(status_dict)
        status_text += '\n'
        status_text += str(jq)
        self.livedataArea.setText(status_text)
        
        #tref = datetime.datetime.now()
        #x = [(itm['Datetime'] - tref).total_seconds() for itm in data['RTV']]
        #y = [itm['LLD'] for itm in data['RTV']]
        #self.step_plot(x, y)

