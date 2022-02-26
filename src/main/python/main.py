import sys
import logging

import pyqtgraph
from ansto_radon_monitor.main import setup_logging
from fbs_runtime.application_context.PyQt5 import ApplicationContext

# from PyQt5.QtWidgets import QMainWindow
from PyQt5 import QtCore, QtWidgets, uic

from mainwindow import MainWindow

setup_logging(loglevel=logging.INFO)


if __name__ == "__main__":

    # Ref for this idea: https://stackoverflow.com/questions/8786136/pyqt-how-to-detect-and-close-ui-if-its-already-running
    lockfile = QtCore.QLockFile(
        QtCore.QDir.tempPath() + "/ansto_radon_monitor_gui.lock"
    )

    if lockfile.tryLock(100):
        appctxt = ApplicationContext()  # 1. Instantiate ApplicationContext
        window = MainWindow(appctxt)
        # window.resize(250, 150)
        window.show()
        exit_code = appctxt.app.exec_()  # 2. Invoke appctxt.app.exec_()
        sys.exit(exit_code)
    else:
        sys.exit("app is already running")
