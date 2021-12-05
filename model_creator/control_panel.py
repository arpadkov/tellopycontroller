from tellopycontroller.gesture_data.gestures import Gesture

from PyQt5 import QtCore, QtWidgets, QtGui


class ControlPanel(QtWidgets.QWidget):

    start_logging = QtCore.pyqtSignal()

    def __init__(self):
        super(ControlPanel, self).__init__()

        self.layout = QtWidgets.QVBoxLayout()

        self.gesture_selector = GestureSelector(Gesture)

        self.start_button = QtWidgets.QPushButton('Start')
        self.start_button.clicked.connect(self.start)

        self.clear_checkbox = QtWidgets.QCheckBox('Clear existing datapoints')

        self.layout.addWidget(self.gesture_selector)
        self.layout.addWidget(self.start_button)
        self.layout.addWidget(self.clear_checkbox)

        self.setLayout(self.layout)

    def start(self):
        self.start_logging.emit()


class GestureSelector(QtWidgets.QComboBox):

    def __init__(self, model):
        super().__init__()

        self.model = model

        self.names = [option.name.capitalize() for option in model]
        self.options = [option for option in model]

        for name in self.names:
            self.addItem(name)

