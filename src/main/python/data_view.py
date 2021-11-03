import datetime
import math
import time
from typing import Dict

import numpy as np
import pyqtgraph as pg
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import QSettings, Qt, QTimer
from pyqtgraph import PlotWidget

from ui_data_view import Ui_DataViewForm


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
        if len(self._data) > 0:
            ncols = len(self._data[0])
        else:
            ncols = 0
        return ncols

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
        if Nnew == 0:
            return

        if N == 0:
            # can't trust existing column names
            self.update_data(new_data)
            return

        # print(f"new data:{new_data}, length {N}, {N+len(new_data)-1}")
        self.beginInsertRows(QtCore.QModelIndex(), N, N + len(new_data) - 1)
        self._data.extend(new_data)
        self.endInsertRows()

        assert len(self._data) == N + Nnew

    def get_plot_data(self, column_idx):
        if len(self._data) == 0:
            return "", []
        values = [list(row.values())[column_idx] for row in self._data]
        colname = list(self._data[0].keys())[column_idx]
        return colname, values


class DataViewForm(QtWidgets.QWidget, Ui_DataViewForm):
    def __init__(self, main_window, table_name: str, *args, **kwargs):
        super(DataViewForm, self).__init__(*args, **kwargs)
        self.setupUi(self)
        self.graph_widget = pg.PlotWidget(axisItems={"bottom": pg.DateAxisItem()})
        self.graph_widget.showGrid(x=True, y=True)
        self.plot_series = None

        self.splitter.addWidget(self.graph_widget)

        self.main_window = main_window
        self.table_name = table_name
        self.selected_column = None

        self.model = TableModel([])
        self.pastDataTableView.setModel(self.model)
        # the last time this table was updated
        self.last_update_time = None
        self.last_redraw_time = 0

        self.connect_signals()

        self.update_times: Dict[str, datetime.datetime] = {}

    def connect_signals(self):
        self.redraw_timer = QTimer()
        self.redraw_timer.setInterval(1000)
        self.redraw_timer.timeout.connect(self.update_displays)
        self.redraw_timer.start()

        self.pastDataTableView.selectionModel().currentChanged.connect(
            self.table_selected
        )

    def table_selected(self, idx):
        # print('column selected')
        c0, r0 = idx.column(), idx.row()
        # print(f'{c0,r0}')
        self.selected_column = idx.column()

    def plot(self, x, y, title=None):
        if self.plot_series is not None:
            self.graph_widget.removeItem(self.plot_series)
        self.plot_series = self.graph_widget.plot(x, y)
        self.graph_widget.setTitle(title)

    def step_plot(self, x, y, title=None):
        if self.plot_series is not None:
            self.graph_widget.removeItem(self.plot_series)

        dx = np.r_[np.diff(x), np.median(np.diff(x))]
        xplt = np.empty(len(x) * 2)
        xplt[::2] = x
        xplt[1::2] = x + dx
        yplt = np.empty(len(y) * 2)
        yplt[::2] = y
        yplt[1::2] = y
        self.plot_series = self.graph_widget.plot(xplt, yplt)
        self.graph_widget.setTitle(title)

    def update_displays(self):
        dt_threshold = 1.0
        ic = self.main_window.instrument_controller
        # return if not connected or if the last redraw *completed* less than
        # dt_threshold seconds ago
        if ic is None or (time.time() - self.last_redraw_time) < dt_threshold:
            return

        if self.last_update_time is None:
            if self.table_name == "Results":
                # only retrieve data from the last week
                start_time = datetime.datetime.utcnow() - datetime.timedelta(days=7)
            else:
                start_time = datetime.datetime.utcnow() - datetime.timedelta(days=1)
        else:
            start_time = self.last_update_time
        t, newdata = ic.get_rows(self.table_name, start_time=start_time)
        self.last_update_time = t
        self.model.append_data(newdata)

        # TODO: link to plot data, or somehow avoid copying the entire
        # x/y series each time
        if self.selected_column is not None and self.selected_column != 0:
            yname, y = self.model.get_plot_data(column_idx=self.selected_column)
            xname, x = self.model.get_plot_data(column_idx=0)
            x = [itm.timestamp() for itm in x]
            self.step_plot(x, y, title=yname)

        self.last_redraw_time = time.time()
