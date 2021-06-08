import datetime
import math
import time
from PyQt5 import QtCore, QtWidgets
from ui_c_and_b import Ui_CAndBForm


class CAndBForm(QtWidgets.QWidget, Ui_CAndBForm):
    def __init__(self, mainwindow, *args, **kwargs):
        super(CAndBForm, self).__init__(*args, **kwargs)
        self.setupUi(self)
        self.mainwindow = mainwindow
        self.connect_signals()

    def connect_signals(self):
        self.calibrateButton.clicked.connect(self.onCalibrate)
        self.backgroundButton.clicked.connect(self.onBackground)

        # disable calendar edit if the checkbox is disabled
        self.calCheckBox.toggled.connect(self.calDateTimeEdit.setEnabled)
        self.bgCheckBox.toggled.connect(self.bgDateTimeEdit.setEnabled)

        self.stopBgPushButton.clicked.connect(self.onStopBg)
        self.stopCalPushButton.clicked.connect(self.onStopCal)

        # TODO: consider using a single timer in mainwindow
        self.redraw_timer = QtCore.QTimer()
        self.redraw_timer.setInterval(1000)
        self.redraw_timer.timeout.connect(self.update_displays)
        self.redraw_timer.start()


    def update_displays(self):
        # update the calibration time widgets
        # next 30 min interval
        next30min = datetime.datetime.fromtimestamp(
            math.ceil(time.time() / 60 / 30) * 60 * 30
        )
        self.bgDateTimeEdit.setMinimumDateTime(next30min)
        self.calDateTimeEdit.setMinimumDateTime(next30min)


    def onCalibrate(self, s):
        if self.calDateTimeEdit.isEnabled():
            start_time = self.calDateTimeEdit.dateTime().toUTC().toPyDateTime()
        else:
            start_time = None
        print(f"calibrate at {start_time} UTC")
        self.mainwindow.instrument_controller.run_calibration(start_time=start_time)

    def onStopCal(self, s):
        self.mainwindow.instrument_controller.stop_calibration()

    def onBackground(self, s):
        if self.bgDateTimeEdit.isEnabled():
            start_time = self.bgDateTimeEdit.dateTime().toUTC().toPyDateTime()
        else:
            start_time = None
        print(f"background at {start_time} UTC")
        # TODO: also need to determine duration from UI + config
        self.mainwindow.instrument_controller.run_background(start_time=start_time)

    def onStopBg(self, s):
        self.mainwindow.instrument_controller.stop_background()
