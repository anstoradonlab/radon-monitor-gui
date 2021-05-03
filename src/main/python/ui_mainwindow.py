# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/main_window.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(765, 920)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.splitter = QtWidgets.QSplitter(self.centralwidget)
        self.splitter.setOrientation(QtCore.Qt.Vertical)
        self.splitter.setObjectName("splitter")
        self.layoutWidget = QtWidgets.QWidget(self.splitter)
        self.layoutWidget.setObjectName("layoutWidget")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.layoutWidget)
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.tabWidget = QtWidgets.QTabWidget(self.layoutWidget)
        self.tabWidget.setEnabled(True)
        self.tabWidget.setTabPosition(QtWidgets.QTabWidget.West)
        self.tabWidget.setObjectName("tabWidget")
        self.tab = QtWidgets.QWidget()
        self.tab.setObjectName("tab")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.tab)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.pastDataTableView = QtWidgets.QTableView(self.tab)
        self.pastDataTableView.setObjectName("pastDataTableView")
        self.horizontalLayout_2.addWidget(self.pastDataTableView)
        self.graph_widget = PlotWidget(self.tab)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.graph_widget.sizePolicy().hasHeightForWidth())
        self.graph_widget.setSizePolicy(sizePolicy)
        self.graph_widget.setObjectName("graph_widget")
        self.horizontalLayout_2.addWidget(self.graph_widget)
        self.tabWidget.addTab(self.tab, "")
        self.tab_2 = QtWidgets.QWidget()
        self.tab_2.setObjectName("tab_2")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.tab_2)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.tabWidget.addTab(self.tab_2, "")
        self.verticalLayout_2.addWidget(self.tabWidget)
        self.groupBox = QtWidgets.QGroupBox(self.layoutWidget)
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
        self.verticalLayout_2.addWidget(self.groupBox)
        self.layoutWidget1 = QtWidgets.QWidget(self.splitter)
        self.layoutWidget1.setObjectName("layoutWidget1")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.layoutWidget1)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.livedataArea = QtWidgets.QTextEdit(self.layoutWidget1)
        font = QtGui.QFont()
        font.setFamily("Monospace")
        self.livedataArea.setFont(font)
        self.livedataArea.setTextInteractionFlags(QtCore.Qt.TextSelectableByKeyboard|QtCore.Qt.TextSelectableByMouse)
        self.livedataArea.setObjectName("livedataArea")
        self.verticalLayout.addWidget(self.livedataArea)
        self.logArea = QtWidgets.QPlainTextEdit(self.layoutWidget1)
        font = QtGui.QFont()
        font.setFamily("Monospace")
        self.logArea.setFont(font)
        self.logArea.setObjectName("logArea")
        self.verticalLayout.addWidget(self.logArea)
        self.verticalLayout_3.addWidget(self.splitter)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 765, 20))
        self.menubar.setObjectName("menubar")
        self.menuFile = QtWidgets.QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.actionLoad_Configuration = QtWidgets.QAction(MainWindow)
        self.actionLoad_Configuration.setObjectName("actionLoad_Configuration")
        self.actionQuit = QtWidgets.QAction(MainWindow)
        self.actionQuit.setObjectName("actionQuit")
        self.menuFile.addAction(self.actionLoad_Configuration)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionQuit)
        self.menubar.addAction(self.menuFile.menuAction())

        self.retranslateUi(MainWindow)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), _translate("MainWindow", "Tab 1"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), _translate("MainWindow", "Tab 2"))
        self.groupBox.setTitle(_translate("MainWindow", "Calibration and background"))
        self.bgDateTimeEdit.setDisplayFormat(_translate("MainWindow", "yyyy-MM-dd hh:mm"))
        self.calibrateButton.setText(_translate("MainWindow", "Calibrate"))
        self.calDateTimeEdit.setDisplayFormat(_translate("MainWindow", "yyyy-MM-dd hh:mm"))
        self.backgroundButton.setText(_translate("MainWindow", "Background"))
        self.calCheckBox.setText(_translate("MainWindow", "later at"))
        self.bgCheckBox.setText(_translate("MainWindow", "later at"))
        self.stopCalPushButton.setText(_translate("MainWindow", "Stop calibration"))
        self.stopBgPushButton.setText(_translate("MainWindow", "Stop background"))
        self.livedataArea.setHtml(_translate("MainWindow", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'Monospace\'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'MS Shell Dlg 2\'; font-size:8pt;\">Radon detector live data</span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:\'MS Shell Dlg 2\'; font-size:8pt;\"><br /></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:\'MS Shell Dlg 2\'; font-size:8pt;\"><br /></p>\n"
"<table border=\"0\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px;\" cellspacing=\"2\" cellpadding=\"0\">\n"
"<tr>\n"
"<td>\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt; font-weight:600;\">Firstname</span><span style=\" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt;\">    </span></p></td>\n"
"<td>\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt; font-weight:600;\">Lastname</span><span style=\" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt;\">    </span></p></td>\n"
"<td>\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt; font-weight:600;\">Age</span><span style=\" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt;\">    </span></p></td></tr>\n"
"<tr>\n"
"<td>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt;\">Jill    </span></p></td>\n"
"<td>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt;\">Smith    </span></p></td>\n"
"<td>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt;\">50    </span></p></td></tr>\n"
"<tr>\n"
"<td>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt;\">Eve    </span></p></td>\n"
"<td>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt;\">Jackson    </span></p></td>\n"
"<td>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt;\">94  </span></p></td></tr></table>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:\'MS Shell Dlg 2\'; font-size:8pt;\"><br /></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:\'MS Shell Dlg 2\'; font-size:8pt;\"><br /></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:\'MS Shell Dlg 2\'; font-size:8pt;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'MS Shell Dlg 2\'; font-size:8pt;\">More</span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:\'MS Shell Dlg 2\'; font-size:8pt;\"><br /></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:\'MS Shell Dlg 2\'; font-size:8pt;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'MS Shell Dlg 2\'; font-size:8pt;\">text</span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:\'MS Shell Dlg 2\'; font-size:8pt;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'MS Shell Dlg 2\'; font-size:8pt;\">to</span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:\'MS Shell Dlg 2\'; font-size:8pt;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'MS Shell Dlg 2\'; font-size:8pt;\">show</span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:\'MS Shell Dlg 2\'; font-size:8pt;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'MS Shell Dlg 2\'; font-size:8pt;\">scrollbar</span></p></body></html>"))
        self.menuFile.setTitle(_translate("MainWindow", "File"))
        self.actionLoad_Configuration.setText(_translate("MainWindow", "Load Configuration"))
        self.actionQuit.setText(_translate("MainWindow", "Quit"))

from pyqtgraph import PlotWidget
