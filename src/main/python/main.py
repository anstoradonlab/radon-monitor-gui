from fbs_runtime.application_context.PyQt5 import ApplicationContext
#from PyQt5.QtWidgets import QMainWindow
from PyQt5 import QtWidgets
from PyQt5 import uic

import sys

import pyqtgraph

from mainwindow import MainWindow


from ansto_radon_monitor.main import setup_logging
setup_logging()


if __name__ == '__main__':
    appctxt = ApplicationContext()       # 1. Instantiate ApplicationContext
    window = MainWindow(appctxt)
    window.resize(250, 150)
    window.show()
    exit_code = appctxt.app.exec_()      # 2. Invoke appctxt.app.exec_()
    sys.exit(exit_code)