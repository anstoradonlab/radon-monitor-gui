# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/c_and_b.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_CAndBForm(object):
    def setupUi(self, CAndBForm):
        CAndBForm.setObjectName("CAndBForm")
        CAndBForm.resize(459, 114)
        self.verticalLayout = QtWidgets.QVBoxLayout(CAndBForm)
        self.verticalLayout.setObjectName("verticalLayout")
        self.groupBox = QtWidgets.QGroupBox(CAndBForm)
        self.groupBox.setObjectName("groupBox")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.groupBox)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.bgDateTimeEdit = QtWidgets.QDateTimeEdit(self.groupBox)
        self.bgDateTimeEdit.setEnabled(False)
        self.bgDateTimeEdit.setCalendarPopup(True)
        self.bgDateTimeEdit.setObjectName("bgDateTimeEdit")
        self.gridLayout_2.addWidget(self.bgDateTimeEdit, 1, 2, 1, 1)
        self.calibrateButton = QtWidgets.QPushButton(self.groupBox)
        self.calibrateButton.setObjectName("calibrateButton")
        self.gridLayout_2.addWidget(self.calibrateButton, 0, 0, 1, 1)
        self.calDateTimeEdit = QtWidgets.QDateTimeEdit(self.groupBox)
        self.calDateTimeEdit.setEnabled(False)
        self.calDateTimeEdit.setCalendarPopup(True)
        self.calDateTimeEdit.setObjectName("calDateTimeEdit")
        self.gridLayout_2.addWidget(self.calDateTimeEdit, 0, 2, 1, 1)
        self.backgroundButton = QtWidgets.QPushButton(self.groupBox)
        self.backgroundButton.setObjectName("backgroundButton")
        self.gridLayout_2.addWidget(self.backgroundButton, 1, 0, 1, 1)
        self.calCheckBox = QtWidgets.QCheckBox(self.groupBox)
        self.calCheckBox.setObjectName("calCheckBox")
        self.gridLayout_2.addWidget(self.calCheckBox, 0, 1, 1, 1)
        self.bgCheckBox = QtWidgets.QCheckBox(self.groupBox)
        self.bgCheckBox.setObjectName("bgCheckBox")
        self.gridLayout_2.addWidget(self.bgCheckBox, 1, 1, 1, 1)
        self.stopCalPushButton = QtWidgets.QPushButton(self.groupBox)
        self.stopCalPushButton.setObjectName("stopCalPushButton")
        self.gridLayout_2.addWidget(self.stopCalPushButton, 0, 3, 1, 1)
        self.stopBgPushButton = QtWidgets.QPushButton(self.groupBox)
        self.stopBgPushButton.setObjectName("stopBgPushButton")
        self.gridLayout_2.addWidget(self.stopBgPushButton, 1, 3, 1, 1)
        self.verticalLayout.addWidget(self.groupBox)

        self.retranslateUi(CAndBForm)
        QtCore.QMetaObject.connectSlotsByName(CAndBForm)

    def retranslateUi(self, CAndBForm):
        _translate = QtCore.QCoreApplication.translate
        CAndBForm.setWindowTitle(_translate("CAndBForm", "Form"))
        self.groupBox.setTitle(_translate("CAndBForm", "Calibration and background"))
        self.bgDateTimeEdit.setDisplayFormat(_translate("CAndBForm", "yyyy-MM-dd hh:mm"))
        self.calibrateButton.setText(_translate("CAndBForm", "Calibrate"))
        self.calDateTimeEdit.setDisplayFormat(_translate("CAndBForm", "yyyy-MM-dd hh:mm"))
        self.backgroundButton.setText(_translate("CAndBForm", "Background"))
        self.calCheckBox.setText(_translate("CAndBForm", "later at"))
        self.bgCheckBox.setText(_translate("CAndBForm", "later at"))
        self.stopCalPushButton.setText(_translate("CAndBForm", "Stop calibration"))
        self.stopBgPushButton.setText(_translate("CAndBForm", "Stop background"))

