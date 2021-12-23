from tello_controllers.rc_controls import GeneralControl

from PyQt5 import QtCore, QtWidgets, QtGui


class ControlButtonsWidget(QtWidgets.QWidget):

    general_control_signal = QtCore.pyqtSignal(GeneralControl, int)

    def __init__(self):
        super(ControlButtonsWidget, self).__init__()

        self.layout = QtWidgets.QGridLayout()

        self.positive_buttons = []
        self.negative_buttons = []

        for control in GeneralControl:
            if control.value in [0, 2, 4, 6]:
                self.positive_buttons.append(ControlButton(control))
            else:
                self.negative_buttons.append(ControlButton(control))

        for num, button in enumerate(self.positive_buttons):
            self.layout.addWidget(button, num, 0)
            button.general_control_signal.connect(self.emit_control)

        for num, button in enumerate(self.negative_buttons):
            self.layout.addWidget(button, num, 1)
            button.general_control_signal.connect(self.emit_control)

        self.setLayout(self.layout)

    def emit_control(self, control: GeneralControl, value: int):
        self.general_control_signal.emit(control, value)


class ControlButton(QtWidgets.QWidget):

    general_control_signal = QtCore.pyqtSignal(GeneralControl, int)

    def __init__(self, control: GeneralControl):
        super(ControlButton, self).__init__()

        self.control = control
        self.value = 20

        # self.setFixedSize(100, 100)

        self.layout = QtWidgets.QHBoxLayout()

        self.button = QtWidgets.QPushButton(self.control.name)
        self.layout.addWidget(self.button)
        self.button.clicked.connect(self.button_clicked)

        self.spin_box = QtWidgets.QSpinBox()
        self.spin_box.setValue(self.value)
        self.spin_box.setMinimum(20)
        self.spin_box.setMaximum(500)
        self.spin_box.valueChanged.connect(self.value_changed)
        self.layout.addWidget(self.spin_box)

        self.setLayout(self.layout)

    def button_clicked(self):

        self.general_control_signal.emit(self.control, self.value)

    def value_changed(self, value: int):
        self.value = value





