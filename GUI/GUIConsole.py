import sys

from qtpy.QtWidgets import QApplication
from pyqtconsole.console import PythonConsole
from pyqtconsole.highlighter import format


class ConsoleWidget(PythonConsole):

    def __init__(self):
        super(ConsoleWidget, self).__init__()

        self.eval_in_thread()

        self.setMinimumHeight(200)
