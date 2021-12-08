from tellopycontroller.GUI.GUIInfoPanel import MainControlPanel

from PyQt5 import QtCore, QtWidgets, QtGui

import sys


class MainWindow(QtWidgets.QMainWindow):

    def __init__(self):
        super(MainWindow, self).__init__()

        self.layout = QtWidgets.QGridLayout()

        # self.controller = GestureController()

        self.control_panel = MainControlPanel()

        self.layout.addWidget(self.control_panel, 0, 0)

        # self.layout.addWidget(self.control_panel.controller.ui_widget, )

        window = QtWidgets.QWidget()
        window.setLayout(self.layout)
        self.setCentralWidget(window)
















if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
