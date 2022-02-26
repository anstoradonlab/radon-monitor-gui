# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/system_information.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_SystemInformationForm(object):
    def setupUi(self, SystemInformationForm):
        SystemInformationForm.setObjectName("SystemInformationForm")
        SystemInformationForm.resize(270, 470)
        self.verticalLayout = QtWidgets.QVBoxLayout(SystemInformationForm)
        self.verticalLayout.setObjectName("verticalLayout")
        self.notLoggingLabel = QtWidgets.QLabel(SystemInformationForm)
        self.notLoggingLabel.setEnabled(True)
        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(170, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(170, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(120, 120, 120))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.WindowText, brush)
        self.notLoggingLabel.setPalette(palette)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.notLoggingLabel.setFont(font)
        self.notLoggingLabel.setText("")
        self.notLoggingLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.notLoggingLabel.setObjectName("notLoggingLabel")
        self.verticalLayout.addWidget(self.notLoggingLabel)
        self.stopLoggingButton = QtWidgets.QPushButton(SystemInformationForm)
        self.stopLoggingButton.setCheckable(True)
        self.stopLoggingButton.setObjectName("stopLoggingButton")
        self.verticalLayout.addWidget(self.stopLoggingButton)
        self.groupBox = QtWidgets.QGroupBox(SystemInformationForm)
        self.groupBox.setObjectName("groupBox")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.groupBox)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.serialPortComboBox = QtWidgets.QComboBox(self.groupBox)
        self.serialPortComboBox.setObjectName("serialPortComboBox")
        self.gridLayout_2.addWidget(self.serialPortComboBox, 1, 1, 1, 1)
        self.queryButton = QtWidgets.QPushButton(self.groupBox)
        self.queryButton.setObjectName("queryButton")
        self.gridLayout_2.addWidget(self.queryButton, 1, 2, 1, 1)
        self.label = QtWidgets.QLabel(self.groupBox)
        self.label.setObjectName("label")
        self.gridLayout_2.addWidget(self.label, 0, 1, 1, 1)
        self.dataLoggerTextBrowser = QtWidgets.QTextBrowser(self.groupBox)
        self.dataLoggerTextBrowser.setTabChangesFocus(True)
        self.dataLoggerTextBrowser.setObjectName("dataLoggerTextBrowser")
        self.gridLayout_2.addWidget(self.dataLoggerTextBrowser, 2, 1, 1, 2)
        self.verticalLayout.addWidget(self.groupBox)
        self.groupBox_2 = QtWidgets.QGroupBox(SystemInformationForm)
        self.groupBox_2.setObjectName("groupBox_2")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.groupBox_2)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.queryLabjackButton = QtWidgets.QPushButton(self.groupBox_2)
        self.queryLabjackButton.setObjectName("queryLabjackButton")
        self.verticalLayout_2.addWidget(self.queryLabjackButton)
        self.labjackTextBrowser = QtWidgets.QTextBrowser(self.groupBox_2)
        self.labjackTextBrowser.setTabChangesFocus(True)
        self.labjackTextBrowser.setObjectName("labjackTextBrowser")
        self.verticalLayout_2.addWidget(self.labjackTextBrowser)
        self.verticalLayout.addWidget(self.groupBox_2)
        self.label_2 = QtWidgets.QLabel(SystemInformationForm)
        self.label_2.setWordWrap(True)
        self.label_2.setObjectName("label_2")
        self.verticalLayout.addWidget(self.label_2)

        self.retranslateUi(SystemInformationForm)
        QtCore.QMetaObject.connectSlotsByName(SystemInformationForm)

    def retranslateUi(self, SystemInformationForm):
        _translate = QtCore.QCoreApplication.translate
        SystemInformationForm.setWindowTitle(_translate("SystemInformationForm", "Form"))
        self.stopLoggingButton.setText(_translate("SystemInformationForm", "Stop Logging"))
        self.groupBox.setTitle(_translate("SystemInformationForm", "Data Loggers"))
        self.queryButton.setText(_translate("SystemInformationForm", "Query Port"))
        self.label.setText(_translate("SystemInformationForm", "Serial ports:"))
        self.groupBox_2.setTitle(_translate("SystemInformationForm", "Lab Jacks"))
        self.queryLabjackButton.setText(_translate("SystemInformationForm", "Query Labjacks"))
        self.label_2.setText(_translate("SystemInformationForm", "Run tests to identify Campbell Scientific data loggers and Lab Jacks.  If there are other instruments connected to this computer over serial ports or using other Lab Jacks then the tests here could interfere with them. Logging from the radon detector needs to be suspended before the tests can run."))

