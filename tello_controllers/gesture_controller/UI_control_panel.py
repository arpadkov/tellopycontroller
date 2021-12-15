from tello_controllers.gesture_controller.gesture_data.gestures import Gesture
from tello_controllers.gesture_controller.gesture_logger import GestureLogger

from PyQt5 import QtCore, QtWidgets


class GestureControlPanel(QtWidgets.QWidget):

    start_logging = QtCore.pyqtSignal()
    start_controlling = QtCore.pyqtSignal()
    stop_controlling = QtCore.pyqtSignal()

    def __init__(self, logger: GestureLogger):
        super(GestureControlPanel, self).__init__()

        self.logger = logger

        self.layout = QtWidgets.QVBoxLayout()

        self.gesture_selector = GestureSelector(self.logger)

        self.start_logging_button = QtWidgets.QPushButton('Start Logging')
        self.start_logging_button.clicked.connect(self.start_logging_button_pressed)

        self.start_controlling_button = QtWidgets.QPushButton('Start Controlling')
        self.start_controlling_button.clicked.connect(self.start_controlling_button_pressed)

        self.stop_controlling_button = QtWidgets.QPushButton('Stop Controlling')
        self.stop_controlling_button.clicked.connect(self.stop_controlling_button_pressed)

        self.clear_checkbox = QtWidgets.QCheckBox('Clear existing datapoints')
        self.clear_checkbox.stateChanged.connect(self.checkbox_changed)

        self.layout.addWidget(self.start_controlling_button)
        self.layout.addWidget(self.stop_controlling_button)
        self.layout.addWidget(self.gesture_selector)
        self.layout.addWidget(self.start_logging_button)
        self.layout.addWidget(self.clear_checkbox)

        self.setLayout(self.layout)

    def start_logging_button_pressed(self):
        self.start_logging.emit()

    def start_controlling_button_pressed(self):
        self.start_controlling.emit()

    def stop_controlling_button_pressed(self):
        self.stop_controlling.emit()

    def checkbox_changed(self):
        self.logger.clear_data = self.clear_checkbox.checkState()


class GestureSelector(QtWidgets.QComboBox):

    def __init__(self, logger):
        super().__init__()

        self.logger = logger

        self.names = [option.name.capitalize() for option in Gesture]
        self.options = [option for option in Gesture]

        for name in self.names:
            self.addItem(name)

        self.currentIndexChanged.connect(self.index_changed)

    def index_changed(self, index):
        self.logger.gesture = self.options[index]
        # self.logger.set_controller(self.options[index])
