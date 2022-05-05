import datetime
import math
import time

import serial.tools.list_ports
from ansto_radon_monitor.labjack_interface import list_all_u12
from pycampbellcr1000 import CR1000
from PyQt5 import QtCore, QtWidgets
from ui_system_information import Ui_SystemInformationForm


# TODO: move these two funcs elsewhere (e.g. cr1000_interface.py?) and refactor
# (so that it's usable from scheduler_threads.py too)
def get_clock_offset(cr1000):
    """
    return datalogger time minus computer time, in seconds, as well
    as 1/2 the time it took to query the datalogger
    """
    # measure the length of time required to query the datalogger clock
    # -- first query it, in case of slow response due to power saving
    # -- mode or some such
    t_datalogger = cr1000.gettime().replace(tzinfo=datetime.timezone.utc)
    tick = time.time()
    t_datalogger = cr1000.gettime().replace(tzinfo=datetime.timezone.utc)
    t_computer = datetime.datetime.now(datetime.timezone.utc)
    tock = time.time()
    time_required_for_query = tock - tick
    halfquery = datetime.timedelta(seconds=time_required_for_query / 2.0)
    # estimate that the actual time on the datalogger probably happend
    # a short time ago
    t_datalogger = t_datalogger - halfquery
    clock_offset = (t_datalogger - t_computer).total_seconds()

    return clock_offset, halfquery


def synchronise_clock(cr1000):
    s = ""
    """Attempt to synchronise the clock on the datalogger with computer."""
    # NOTE: the api for adjusting the datalogger clock isn't accurate beyond 1 second
    # TODO: maybe improve this situation
    minimum_time_difference_seconds = 1
    # TODO: check that the computer time is reliable, i.e. NTP sync
    #
    clock_offset, halfquery = get_clock_offset(cr1000)
    s += f"Time difference (datalogger minus computer): {clock_offset}"

    if abs(clock_offset) < minimum_time_difference_seconds:
        s += f"Datalogger and computer clocks are out of synchronisation by less than {minimum_time_difference_seconds} seconds, not adjusting time"

    else:
        new_time = datetime.datetime.now(datetime.timezone.utc) + halfquery
        cr1000.settime(new_time)
        clock_offset, halfquery = self.get_clock_offset()
        s += f"Synchronised datalogger clock with computer clock, time difference (datalogger minus computer): {clock_offset}, detector: {self.detectorName}"
    return s


class SystemInformationForm(QtWidgets.QWidget, Ui_SystemInformationForm):
    def __init__(self, mainwindow, *args, **kwargs):
        super(SystemInformationForm, self).__init__(*args, **kwargs)
        self.setupUi(self)
        self._controls_to_disable = [
            self.serialPortComboBox,
            self.queryButton,
            self.queryLabjackButton,
            self.sendProgramButton,
            self.downloadButton,
            self.timeSyncButton,
        ]
        self._controls_needing_connection = [
            self.sendProgramButton,
            self.downloadButton,
            self.timeSyncButton,
        ]
        self._serial_port_info = {}
        self.mainwindow = mainwindow
        self.connect_signals()

        t = QtCore.QTimer()
        t.setInterval(1000)
        t.timeout.connect(self.enumerate_serial_ports)
        t.start()
        self.serial_port_watcher_timer = t
        self.detected_serial_ports = []
        self.cr1000 = None

    def connect_signals(self):
        self.stopLoggingButton.clicked.connect(self.onStopLogging)
        self.queryButton.clicked.connect(self.on_query)
        self.queryLabjackButton.clicked.connect(self.on_query_labjack)
        self.serialPortComboBox.currentIndexChanged.connect(self.on_combobox_changed)
        self.downloadButton.clicked.connect(self.on_download)
        self.timeSyncButton.clicked.connect(self.on_time_sync)

        # Disable controls if we're already logging
        # TODO: check logging status first
        for itm in self._controls_to_disable:
            itm.setEnabled(False)

    def onStopLogging(self):
        if self.stopLoggingButton.isChecked():
            # stop logging and activate diagnostic controls
            self.mainwindow.stop_logging()
            for itm in self._controls_to_disable:
                itm.setEnabled(True)
            self.enumerate_serial_ports()
            self.notLoggingLabel.setText("WARNING: logging is paused")
            self.stopLoggingButton.setText("Resume logging")
        else:
            # resume logging and deactivate diagnostic controls
            for itm in self._controls_to_disable:
                itm.setEnabled(False)
            self.notLoggingLabel.setText("")
            self.stopLoggingButton.setText("Stop logging")
            self.mainwindow.start_logging()

    def enumerate_serial_ports(self):
        if self.stopLoggingButton.isChecked():
            n = 0

            self._serial_port_info = {}
            for info in sorted(serial.tools.list_ports.comports()):
                # print(
                #    f"{info.device}\n    description: {info.description}\n           hwid: {info.hwid}"
                # )
                n += 1
                k = info.device
                self._serial_port_info[k] = info
            serial_ports = list(self._serial_port_info.keys())
            if not serial_ports == self.detected_serial_ports:
                self.detected_serial_ports = serial_ports
                while len(self.serialPortComboBox) > 0:
                    self.serialPortComboBox.removeItem(0)
                self.serialPortComboBox.addItems(serial_ports)
                self._n_com_ports = n
            if n == 0:
                self.dataLoggerTextBrowser.setPlainText("No COM ports detected.")

            for itm in self._controls_needing_connection:
                enable = self.cr1000 is not None
                itm.setEnabled(enable)

    def on_combobox_changed(self):
        self.dataLoggerTextBrowser.setPlainText("")
        if self.cr1000 is not None:
            # TODO: 'close' doesn't really exist
            self.cr1000.close()
            self.cr1000 = None

    def on_query(self):
        if self._n_com_ports == 0:
            return
        k = self.serialPortComboBox.currentText()
        info = self._serial_port_info[k]
        s = ""
        try:
            # attempt to connect to a Data Logger
            # -- TODO: run this in a thread because it can take ages
            s += f"Attempting to connect using {info.device}...\n"
            self.dataLoggerTextBrowser.setPlainText(s)
            ser = serial.Serial(
                port=None,
                baudrate=115200,
                timeout=2,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=1,
            )
            ser.port = info.device
            cr1000 = CR1000(ser)
            logger_info = cr1000.getprogstat()
            s += f"{logger_info}"
            self.cr1000 = cr1000
        except Exception as e:
            s += f'Error occured: "{e}"'
        self.dataLoggerTextBrowser.setPlainText(s)

    def on_download(self):
        s = ""
        try:
            if self.cr1000 is None:
                self.on_query()
            if self.cr1000 is None:
                return
            cr1000 = self.cr1000
            logger_info = cr1000.getprogstat()
            currently_running_file = str(logger_info["ProgName"], "utf-8")
            s += f"{currently_running_file}\n\n"
            file_contents = str(cr1000.getfile(currently_running_file), "utf-8")
            s += f"{file_contents}"
        except Exception as e:
            s += f'Error occured: "{e}"'
        self.dataLoggerTextBrowser.setPlainText(s)

    def on_time_sync(self):
        s = ""
        try:
            if self.cr1000 is None:
                self.on_query()
            if self.cr1000 is None:
                return
            cr1000 = self.cr1000
            s += synchronise_clock(cr1000)
        except Exception as e:
            s += f'Error occured: "{e}"'
        self.dataLoggerTextBrowser.setPlainText(s)

    def on_query_labjack(self):
        # TODO: refactor this into the base library (to remove code duplication)
        info = list_all_u12()
        # info: {'serialnumList': <u12.c_long_Array_127 object at 0x00E2AD50>,
        #       'numberFound': 1, '
        #        localIDList': <u12.c_long_Array_127 object at 0x00E2Au12.DA0>}
        s = ""
        try:
            n = len(info["localIDList"])
        except IndexError:
            n = 0
        for ii in range(n):
            s += f"Labjack\n    local ID: {info['localIDList'][ii]}\n      serial: {info['serialnumList'][ii]}\n"
        if n == 1:
            s += f"{n} LabJack found"
        else:
            s += f"{n} LabJacks found"
        self.labjackTextBrowser.setPlainText(s)

    def hideEvent(self, event):
        if self.stopLoggingButton.isChecked():
            self.stopLoggingButton.click()
