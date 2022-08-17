import datetime
import logging
import sys
import time
import typing

import numpy as np
import pyqtgraph as pg
from PyQt5 import QtCore, QtWidgets

from plotutils import data_to_columns, get_pen, groupby_series

_logger = logging.getLogger(__name__)


# PgPlot examples:
# python ...\env\lib\site-packages\pyqtgraph\examples\ExampleApp.py


class DataPlotter(object):
    def __init__(self, win: pg.GraphicsLayoutWidget, data: typing.List):
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
        self._units_dict = {
            "LLD_Tot": "/30-min",
            "ULD_Tot": "/30-min",
            "ExFlow_Tot": "l/min",
            "InFlow_Avg": "m/s",
            "HV_Avg": "V",
            "AirT_Avg": "degC",
        }
        self._name_dict = {
            "LLD_Tot": "Total counts",
            "ULD_Tot": "Noise counts",
            "ExFlow_Tot": "Ext. flow",
            "InFlow_Avg": "Int. flow",
            "HV_Avg": "PMT power",
            "AirT_Avg": "Air temp.",
        }

        N = len(plot_yvars)
        win.resize(400, 100 * N)

        datac = data_to_columns(data)
        datac["Datetime"] = np.array(
            [itm.timestamp() + time.timezone for itm in datac["Datetime"]]
        )

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
        p = win.addPlot(
            row=idx,
            col=0,
            axisItems={
                "bottom": pg.DateAxisItem(),
            },
        )
        labelStyle = {"font-size": "10pt"}
        p.setLabel(
            "left",
            self._name_dict.get(yvar, yvar),
            units=self._units_dict.get(yvar, "Unknown units"),
            **labelStyle,
        )
        # do not convert units from e.g. V to kV
        p.getAxis("left").enableAutoSIPrefix(False)
        po["plot"] = p
        po["series"] = {}
        if idx == Nplts - 1 and len(set(legend_data)) > 1:
            # add legend to the bottom plot, if there are more than one
            # detectors
            legend = p.addLegend(frame=False, rowCount=1, colCount=2)
            self._plot_objects["legend"] = legend

        for series_idx, (x, y, label) in enumerate(groupby_series(x, y, legend_data)):
            s = p.plot(x, y, pen=get_pen(series_idx), name=label)
            po["series"][series_idx] = s

        self._plot_objects[idx] = po

    def update(self, data):
        flag_need_regenerate = False
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
                try:
                    s = po["series"][series_idx]
                    # subtract time.timezone to get display in UTC
                    xfloat = [itm.timestamp() + time.timezone for itm in x]
                    s.setData(x=xfloat, y=y)
                except KeyError:
                    # update failed, plot needs to be regenerated
                    flag_need_regenerate = True

        if flag_need_regenerate:
            # regenerate the entire plot
            self.win.clear()
            self.setup(self.win, data)
