import datetime
import math
import time

from PyQt5 import QtCore, QtWidgets
from ui_c_and_b import Ui_CAndBForm


def t_into_utc(t):
    """converts a datetime (t) without any timezone info into
    the same t but identified as utc"""
    t = datetime.datetime(*t.timetuple()[:6], tzinfo=datetime.timezone.utc)
    return t


# note: special handling for the case where this dialog appears
# before the controller is set up (or when it is turned off)
## - using the 'schedule_pending' flag
class CAndBForm(QtWidgets.QWidget, Ui_CAndBForm):
    def __init__(self, mainwindow, *args, **kwargs):
        super(CAndBForm, self).__init__(*args, **kwargs)
        self.setupUi(self)
        self.mainwindow = mainwindow
        self.schedule_pending = False
        self._controls_to_disable_in_scheduled_mode = [
            self.calRadioButton,
            self.bgRadioButton,
            self.startLaterCheckBox,
            self.startStopPushButton,
            self.firstScheduledCalibrationDateTimeEdit,
            self.calibrationIntervalSpinBox,
            self.firstScheduledBackgroundDateTimeEdit,
            self.backgroundIntervalSpinBox,
            self.flushSpinBox,
            self.injectSpinBox,
            self.backgroundSpinBox,
        ]
        self._controls_to_disable_during_onceoff = [
            self.calRadioButton,
            self.bgRadioButton,
            self.startLaterCheckBox,
            self.calbgDateTimeEdit,
        ]
        self.connect_signals()
        self.restore_state_from_qsettings()
        self.update_local_times()

    def connect_signals(self):
        self.enableScheduleButton.clicked.connect(self.on_enable_schedule_clicked)

        self.firstScheduledCalibrationDateTimeEdit.dateTimeChanged.connect(
            self.update_local_times
        )
        self.firstScheduledBackgroundDateTimeEdit.dateTimeChanged.connect(
            self.update_local_times
        )
        self.calbgDateTimeEdit.dateTimeChanged.connect(self.update_local_times)

        # disable calendar edit if the checkbox is disabled
        self.startLaterCheckBox.toggled.connect(self.calbgDateTimeEdit.setEnabled)

        self.startStopPushButton.clicked.connect(self.onStartStop)

        # TODO: consider using a single timer in mainwindow
        self.redraw_timer = QtCore.QTimer()
        self.redraw_timer.setInterval(1000)
        self.redraw_timer.timeout.connect(self.update_displays)
        self.redraw_timer.start()

    def onStartStop(self):
        flag_start = self.startStopPushButton.isChecked()
        flag_cal = self.calRadioButton.isChecked()
        flag_bg = self.bgRadioButton.isChecked()
        assert flag_cal == (not flag_bg)
        if flag_start:
            for itm in self._controls_to_disable_during_onceoff:
                itm.setEnabled(False)
            self.startStopPushButton.setText("Stop")
            if flag_cal:
                self.onCalibrate()
            elif flag_bg:
                self.onBackground()
        else:
            if flag_bg:
                self.mainwindow.instrument_controller.stop_background()
            elif flag_cal:
                self.mainwindow.instrument_controller.stop_calibration()
            else:
                _logger.error("Programming error - one of BG or cal should be flagged")
                self.mainwindow.instrument_controller.stop_background()
                self.mainwindow.instrument_controller.stop_calibration()
            self.update_main_display()
            for itm in self._controls_to_disable_during_onceoff:
                itm.setEnabled(True)
            # special case - enabled only if option box is checked
            self.calbgDateTimeEdit.setEnabled(self.startLaterCheckBox.isChecked())
            self.startStopPushButton.setText("Start")

    def update_local_times(self):
        t0_single = self.calbgDateTimeEdit.dateTime().toPyDateTime()
        tstr = str(t_into_utc(t0_single).astimezone())
        self.calbgLocalTimeLabel.setText(tstr)

        t0_background = (
            self.firstScheduledBackgroundDateTimeEdit.dateTime().toPyDateTime()
        )
        tstr = str(t_into_utc(t0_background).astimezone())
        self.bgLocalTimeLabel.setText(tstr)
        t0_cal = self.firstScheduledCalibrationDateTimeEdit.dateTime().toPyDateTime()
        tstr = str(t_into_utc(t0_cal).astimezone())
        self.calLocalTimeLabel.setText(tstr)

    def on_enable_schedule_clicked(self, s):

        ic = self.mainwindow.instrument_controller

        if s:
            msg = "Scheduled calibration and backgrounds are active"
            # durations are in seconds
            background_duration = self.backgroundSpinBox.value() * 3600.0
            inject_duration = self.injectSpinBox.value() * 3600.0
            flush_duration = self.flushSpinBox.value() * 3600.0
            # intervals are required in datetime.timedelta, but in the box are days
            background_interval = datetime.timedelta(
                days=self.backgroundIntervalSpinBox.value()
            )
            cal_interval = datetime.timedelta(
                days=self.calibrationIntervalSpinBox.value()
            )
            # t0 for each
            t0_background = (
                self.firstScheduledBackgroundDateTimeEdit.dateTime()
                .toUTC()
                .toPyDateTime()
                .replace(tzinfo=datetime.timezone.utc)
            )
            t0_cal = (
                self.firstScheduledCalibrationDateTimeEdit.dateTime()
                .toUTC()
                .toPyDateTime()
                .replace(tzinfo=datetime.timezone.utc)
            )
            if ic is not None:
                ic.schedule_recurring_calibration(
                    flush_duration, inject_duration, t0_cal, cal_interval
                )
                ic.schedule_recurring_background(
                    background_duration, t0_background, background_interval
                )
                self.schedule_pending = False
            else:
                self.schedule_pending = True
            button_msg = "Disable Schedule"
        else:
            msg = ""
            button_msg = "Enable Schedule"
            self.schedule_pending = False
            if ic is not None:
                ic.stop_calibration()
                ic.stop_background()
        for itm in self._controls_to_disable_in_scheduled_mode:
            itm.setEnabled(not s)
        self.scheduleEngagedLabel.setText(msg)
        self.enableScheduleButton.setText(button_msg)
        self.save_state_to_qsettings()

    def schedule_engaged(self):
        return self.enableScheduleButton.isChecked()

    def update_main_display(self):
        """tells the main Gui to update"""
        # TODO: there might be a simpler way to do this,
        #  'schedule next event loop' or similar
        t = QtCore.QTimer(self)
        t.setInterval(100)
        t.setSingleShot(True)
        t.timeout.connect(self.mainwindow.update_displays)
        t.start()

    def update_displays(self):
        # update the calibration time widgets
        # next 30 min interval
        next30min = datetime.datetime.fromtimestamp(
            math.ceil(time.time() / 60 / 30) * 60 * 30, tz=datetime.timezone.utc
        )
        self.calbgDateTimeEdit.setMinimumDateTime(next30min)

        # A period check that a cal or bg is running, if the start button is checked
        if self.startStopPushButton.isChecked():
            ic = self.mainwindow.instrument_controller
            reset_onceoff_controls = (ic is None) or (not ic.cal_running and not ic.bg_running)
            if reset_onceoff_controls:
                self.startStopPushButton.setChecked(False)
                for itm in self._controls_to_disable_during_onceoff:
                    itm.setEnabled(True)
                # special case - enabled only if option box is checked
                self.calbgDateTimeEdit.setEnabled(self.startLaterCheckBox.isChecked())
                self.startStopPushButton.setText("Start")

        # A periodic check that the
        # schedule is correctly engaged, if the button has been
        # engaged.
        # --- this is the situation where the schedule is engaged,
        # --- but the instrument controller was not ready
        if self.schedule_pending:
            self.on_enable_schedule_clicked(True)
        # --- this is the situation where the instrument controller
        # --- was stopped and restarted, and the schedule needs to be
        # --- retransmitted after the restart
        ic = self.mainwindow.instrument_controller
        if (
            self.schedule_engaged()
            and ic is not None
            and not ic.cal_and_bg_is_scheduled()
        ):
            self.on_enable_schedule_clicked(True)

    def onCalibrate(self, s=None):
        if self.startLaterCheckBox.isChecked():
            start_time = (
                self.calbgDateTimeEdit.dateTime()
                .toPyDateTime()
                .replace(tzinfo=datetime.timezone.utc)
            )
        else:
            start_time = None
        flush_duration_sec = self.flushSpinBox.value() * 3600
        inject_duration_sec = self.injectSpinBox.value() * 3600
        self.mainwindow.instrument_controller.run_calibration(
            start_time=start_time,
            flush_duration=flush_duration_sec,
            inject_duration=inject_duration_sec,
        )
        self.update_main_display()

    def onStopCal(self, s=None):
        self.mainwindow.instrument_controller.stop_calibration()
        # TODO: re-schedule calibrations if enabled
        self.update_main_display()

    def onBackground(self, s=None):
        if self.startLaterCheckBox.isChecked():
            start_time = (
                self.calbgDateTimeEdit.dateTime()
                .toPyDateTime()
                .replace(tzinfo=datetime.timezone.utc)
            )
        else:
            start_time = None
        duration_sec = self.backgroundSpinBox.value() * 3600
        self.mainwindow.instrument_controller.run_background(
            start_time=start_time, duration=duration_sec
        )
        self.update_main_display()

    def onStopBg(self, s):
        self.mainwindow.instrument_controller.stop_background()
        self.update_main_display()

    def save_state_to_qsettings(self):
        qs = self.mainwindow.qsettings
        background_duration = self.backgroundSpinBox.value()
        qs.setValue("background_duration", background_duration)
        inject_duration = self.injectSpinBox.value()
        qs.setValue("inject_duration", inject_duration)
        flush_duration = self.flushSpinBox.value()
        qs.setValue("flush_duration", flush_duration)
        # intervals are required in datetime.timedelta, but in the box are days
        background_interval = datetime.timedelta(
            days=self.backgroundIntervalSpinBox.value()
        )
        qs.setValue("background_interval", background_interval)
        cal_interval = datetime.timedelta(days=self.calibrationIntervalSpinBox.value())
        qs.setValue("cal_interval", cal_interval)
        # t0 for each
        t0_background = (
            self.firstScheduledBackgroundDateTimeEdit.dateTime().toUTC().toPyDateTime()
        )
        qs.setValue("t0_background", t0_background)
        t0_cal = (
            self.firstScheduledCalibrationDateTimeEdit.dateTime().toUTC().toPyDateTime()
        )
        qs.setValue("t0_cal", t0_cal)

        # schedule enabled/disabled
        qs.setValue("schedule_enabled", self.enableScheduleButton.isChecked())

    def restore_state_from_qsettings(self):
        qs = self.mainwindow.qsettings
        for k, w in zip(
            ("background_duration", "inject_duration", "flush_duration"),
            (self.backgroundSpinBox, self.injectSpinBox, self.flushSpinBox),
        ):
            v = qs.value(k)
            if v is not None:
                w.setValue(int(v))
        background_interval = qs.value("background_interval")
        if background_interval is not None:
            days = int(background_interval.total_seconds() / 3600.0 / 24.0)
            self.backgroundIntervalSpinBox.setValue(days)
        cal_interval = qs.value("cal_interval")
        if cal_interval is not None:
            days = int(cal_interval.total_seconds() / 3600.0 / 24.0)
            self.calibrationIntervalSpinBox.setValue(days)

        t0_background = qs.value("t0_background")
        if t0_background is not None:
            t0_background = t_into_utc(t0_background)
            self.firstScheduledBackgroundDateTimeEdit.setDateTime(t0_background)
        t0_cal = qs.value("t0_cal")
        if t0_cal is not None:
            t0_cal = t_into_utc(t0_cal)
            self.firstScheduledCalibrationDateTimeEdit.setDateTime(t0_cal)
        schedule_state = qs.value("schedule_enabled")
        if schedule_state is not None:
            # instead of using self.enableScheduleButton.setChecked(schedule_state)
            # we 'click' the button so that it emits events
            schedule_state = schedule_state.lower() == "true"
            btn_state = self.enableScheduleButton.isChecked()
            if not btn_state == schedule_state:
                self.enableScheduleButton.click()

    def hideEvent(self, event):
        self.save_state_to_qsettings()
        super(CAndBForm, self).hideEvent(event)
