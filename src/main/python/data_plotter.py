import datetime
import logging
import sys
import typing

import numpy as np
import pyqtgraph as pg
from PyQt5 import QtCore, QtWidgets

_logger = logging.getLogger(__name__)


# PgPlot examples:
# python ...\env\lib\site-packages\pyqtgraph\examples\ExampleApp.py


def data_to_columns(data):
    """convert data (list of dicts) into dict of arrays"""
    data_arrays = {}
    for k in data[0]:
        data_arrays[k] = np.array([itm[k] for itm in data])
    return data_arrays


def groupby_series(x, y, legend_data):
    if legend_data is None:
        ret = [(x, y, None)]
    else:
        ret = []
        for label in sorted(set(legend_data)):
            mask = legend_data == label
            xii = x[mask]
            yii = y[mask]
            ret.append((xii, yii, str(label)))
    return ret


class DataPlotter(object):
    def __init__(self, win: pg.GraphicsLayoutWidget, data: typing.List):
        self._linewidth = 2
        self.setup(win, data)

    def setup(self, win, data):
        self.win: pg.GraphicsLayoutWidget = win
        # persistant storage of plot info needed for updates
        self._plot_objects = {}
        # TODO: this will need to change if we decide to support more than just the Results table
        plot_yvars = [
            "LLD_Tot",
            "ULD_Tot",
            "ExFlow_Tot",
            "InFlow_Avg",
            "HV_Avg",
            "AirT_Avg",
        ]

        N = len(plot_yvars)
        win.resize(400, 100 * N)
        self._colormap = (
            (158, 202, 225),
            (253, 174, 107),
            (161, 217, 155),
            (188, 189, 220),
            (189, 189, 189),
        )

        datac = data_to_columns(data)
        datac["Datetime"] = np.array([itm.timestamp() for itm in datac["Datetime"]])

        for idx, k in enumerate(plot_yvars):
            self.plot(
                win,
                data=datac,
                xvar="Datetime",
                yvar=k,
                huevar="DetectorName",
                idx=idx,
                Nplts=N,
            )

    def get_pen(self, idx):
        N = len(self._colormap)
        pen = pg.mkPen(self._colormap[idx % N])
        pen.setWidth(self._linewidth)
        return pen

    def plot(self, win, data, xvar, yvar, huevar, idx, Nplts):
        po = {}
        po["xvar"] = xvar
        po["yvar"] = yvar
        po["huevar"] = huevar
        po["idx"] = idx
        try:
            x = data[xvar]
            y = data[yvar]
            legend_data = data[huevar]
        except Exception as e:
            _logger.error(f"Encounted error while generating plot: {e}")
            print(str(data.keys()))
            return
        # TODO: look up units/nicer variable name
        p = win.addPlot(row=idx, col=0, axisItems={"bottom": pg.DateAxisItem()})
        p.setLabel("left", yvar, units="TODO")
        po["plot"] = p
        po["series"] = {}
        if idx == Nplts - 1 and len(set(legend_data)) > 1:
            # add legend to the bottom plot, if there are more than one
            # detectors
            legend = p.addLegend(frame=False, rowCount=1, colCount=2)
            self._plot_objects["legend"] = legend

        for series_idx, (x, y, label) in enumerate(groupby_series(x, y, legend_data)):
            s = p.plot(x, y, pen=self.get_pen(series_idx), name=label)
            po["series"][series_idx] = s

        self._plot_objects[idx] = po

    def update(self, data):
        datac = data_to_columns(data)
        for idx, po in self._plot_objects.items():
            if idx == "legend":
                continue
            x = po["xvar"]
            y = po["yvar"]
            hue = po["huevar"]
            idx = po["idx"]
            x = datac[x]
            y = datac[y]
            legend_data = datac[hue]

            for series_idx, (x, y, label) in enumerate(
                groupby_series(x, y, legend_data)
            ):
                s = po["series"][series_idx]
                xfloat = [itm.timestamp() for itm in x]
                s.setData(x=xfloat, y=y)
