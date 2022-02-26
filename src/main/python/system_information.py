import datetime
import math
import time
from pycampbellcr1000 import CR1000

from PyQt5 import QtCore, QtWidgets

from ui_system_information import Ui_SystemInformationForm

from ansto_radon_monitor.labjack_interface import list_all_u12

class SystemInformationForm(QtWidgets.QWidget, Ui_SystemInformationForm):
    def __init__(self, mainwindow, *args, **kwargs):
        super(SystemInformationForm, self).__init__(*args, **kwargs)
        self.setupUi(self)
        self._controls_to_disable = [
            self.serialPortComboBox,
            self.queryButton,
            self.queryLabjackButton,
        ]
        self._serial_port_info = {}
        self.mainwindow = mainwindow
        self.connect_signals()

    def connect_signals(self):
        self.stopLoggingButton.clicked.connect(self.onStopLogging)
        self.queryButton.clicked.connect(self.on_query)
        self.queryLabjackButton.clicked.connect(self.on_query_labjack)
        self.serialPortComboBox.currentIndexChanged.connect(self.on_combobox_changed)

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
            self.notLoggingLabel.setText('WARNING: logging is paused')
            self.stopLoggingButton.setText('Resume logging')
        else:
            # resume logging and deactivate diagnostic controls
            for itm in self._controls_to_disable:
                itm.setEnabled(False)
            self.notLoggingLabel.setText('')
            self.stopLoggingButton.setText('Stop logging')
            self.mainwindow.start_logging()
    
    def enumerate_serial_ports(self):
        import serial.tools.list_ports
        n = 0
        self._serial_port_info = {}
        for info in sorted(serial.tools.list_ports.comports()):
            print(
                f"{info.device}\n    description: {info.description}\n           hwid: {info.hwid}"
            )
            n += 1
            k = info.device
            self._serial_port_info[k] = info
        self.serialPortComboBox.addItems(list(self._serial_port_info.keys()))
        self._n_com_ports = n
        if n == 0:
            self.dataLoggerTextBrowser.setPlainText("No COM ports detected.")

    def on_combobox_changed(self):
        self.dataLoggerTextBrowser.setPlainText('')
        
    def on_query(self):
        if self._n_com_ports == 0:
            return
        k = self.serialPortComboBox.currentText()
        info = self._serial_port_info[k]
        s = ''
        try:
            # attempt to connect to a Data Logger
            # -- TODO: run this in a thread because it can take ages
            serial_port_url = f"serial:/{info.device}:115200"
            s += f"Attempting to connect using {serial_port_url}...\n"
            self.dataLoggerTextBrowser.setPlainText(s)
            cr1000 = CR1000.from_url(
                serial_port_url, timeout=2
            )
            logger_info = self._datalogger.getprogstat()
            s += f'{logger_info}'
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
            s += (
                f"Labjack\n    local ID: {info['localIDList'][ii]}\n      serial: {info['serialnumList'][ii]}\n"
            )
        if n == 1:
            s+= f"{n} LabJack found"
        else:
            s+=f"{n} LabJacks found"
        self.labjackTextBrowser.setPlainText(s)










