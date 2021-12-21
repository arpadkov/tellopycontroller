from tellopycontroller.GUI.GUIInfoPanel import MainControlPanel, ControllerType
from tellopycontroller.GUI.GUIConsole import ConsoleWidget
from tellopycontroller.GUI.GUILogging import GUILogging

from PyQt5 import QtCore, QtWidgets, QtGui

import sys
import logging

logging.basicConfig(level='INFO')

logger = logging.getLogger('Tello controller')


class MainWindow(QtWidgets.QMainWindow):

    def __init__(self):
        super(MainWindow, self).__init__()

        self.layout = QtWidgets.QGridLayout()

        # self.controller = GestureController()

        self.control_panel = MainControlPanel()
        self.control_panel.controller_changed.connect(self.connect_controller)

        # self.console_widget = Console()

        self.layout.addWidget(self.control_panel, 0, 0, QtCore.Qt.AlignLeft)
        # self.layout.addWidget(self.console_widget)

        self.createMenus()
        self.createDockWindows()

        self.control_panel.set_controller(ControllerType.KeyboardController)

        self.move(500, 100)

        # self.layout.addWidget(self.control_panel.controller.ui_widget, )

        window = QtWidgets.QWidget()
        window.setLayout(self.layout)
        self.setCentralWidget(window)

    def createDockWindows(self):

        dock_logging = QtWidgets.QDockWidget("Logging", self)
        dock_logging.setAllowedAreas(QtCore.Qt.BottomDockWidgetArea)
        self.logging_widget = GUILogging()
        dock_logging.setWidget(self.logging_widget)
        self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, dock_logging)
        self.viewMenu.addAction(dock_logging.toggleViewAction())

        dock_console = QtWidgets.QDockWidget("Console", self)
        dock_console.setAllowedAreas(QtCore.Qt.BottomDockWidgetArea)
        self.console_widget = ConsoleWidget()
        # self.console_widget.push_vars({"data": self.model})
        dock_console.setWidget(self.console_widget)

        self.addDockWidget(QtCore.Qt.BottomDockWidgetArea, dock_console)
        # self.tabifyDockWidget(dock_logging, dock_console)
        dock_logging.raise_()

        self.setTabPosition(QtCore.Qt.BottomDockWidgetArea, QtWidgets.QTabWidget.North)

        self.viewMenu.addAction(dock_console.toggleViewAction())

    def createMenus(self):

        self.fileMenu = self.menuBar().addMenu("&File")
        self.viewMenu = self.menuBar().addMenu("&View")

    def connect_controller(self, controller, controller_type):
        logger.info(f'{controller_type.ui_name} connected')
        self.console_widget.push_local_ns('drone', controller.drone)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    # window.showMaximized()
    window.show()
    sys.exit(app.exec_())
