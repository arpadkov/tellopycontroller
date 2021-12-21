from PyQt5 import QtCore, QtWidgets, QtGui
from enum import Enum


class DroneCommandVisual(QtWidgets.QWidget):
    speed_setting_changed = QtCore.pyqtSignal(str, int)

    def __init__(self, lateral_speed, yaw_speed):
        super(DroneCommandVisual, self).__init__()

        self.lateral_speed = lateral_speed
        self.yaw_speed = yaw_speed

        self.layout = QtWidgets.QGridLayout()

        self.forward_info = RcControlFeedback(('Forward', 'Backward'))
        self.layout.addWidget(self.forward_info)

        self.leftright_info = RcControlFeedback(('Left', 'Right'))
        self.layout.addWidget(self.leftright_info)

        self.updown_info = RcControlFeedback(('Up', 'Down'))
        self.layout.addWidget(self.updown_info)

        self.yaw_info = RcControlFeedback(('RotateLeft', 'RotateRight'))
        self.layout.addWidget(self.yaw_info)

        self.lateral_speed_setting = DirectionalSpeedSet(SpeedDirection.Lateral, self.lateral_speed)
        self.lateral_speed_setting.speed_setting_changed.connect(self.set_control_speed)

        self.yaw_speed_setting = DirectionalSpeedSet(SpeedDirection.Yaw, self.yaw_speed)
        self.yaw_speed_setting.speed_setting_changed.connect(self.set_control_speed)

        self.layout.addWidget(self.lateral_speed_setting)
        self.layout.addWidget(self.yaw_speed_setting)

        self.setLayout(self.layout)

    @QtCore.pyqtSlot(tuple)
    def update_rc_control(self, rc_control):
        forw, leftr, updown, yaw = rc_control

        self.forward_info.highlight_control(forw)
        self.leftright_info.highlight_control(leftr)
        self.updown_info.highlight_control(updown)
        self.yaw_info.highlight_control(yaw)

    def set_control_speed(self, controller_speed, value):
        self.speed_setting_changed.emit(controller_speed, value)

    def update_speeds(self):
        self.lateral_speed_setting.spin_box.setValue(self.lateral_speed)
        self.yaw_speed_setting.spin_box.setValue(self.yaw_speed)


class SpeedDirection(Enum):
    Lateral = 1
    Yaw = 2


class DirectionalSpeedSet(QtWidgets.QWidget):
    speed_setting_changed = QtCore.pyqtSignal(str, int)

    controller_speeds = {
        SpeedDirection.Lateral: 'lateral_speed',
        SpeedDirection.Yaw: 'yaw_speed'
    }

    def __init__(self, direction: SpeedDirection, initial_speed):
        super(DirectionalSpeedSet, self).__init__()

        self.direction = direction

        self.layout = QtWidgets.QHBoxLayout()

        self.label = QtWidgets.QLabel(self.direction.name)
        # self.label.setFont(main_font)

        self.spin_box = QtWidgets.QSpinBox()
        # self.spin_box.setFont(main_font)

        # initial_speed = getattr(self.controller, self.controller_speeds[self.direction])
        self.spin_box.setValue(initial_speed)

        self.spin_box.setMinimum(0)
        self.spin_box.setMaximum(100)
        self.spin_box.valueChanged.connect(self.set_control_speed)

        self.layout.addWidget(self.label)
        self.layout.addWidget(self.spin_box)

        self.setLayout(self.layout)

    def set_control_speed(self, value):
        controller_speed = self.controller_speeds[self.direction]
        self.speed_setting_changed.emit(controller_speed, value)


class RcControlFeedback(QtWidgets.QWidget):

    def __init__(self, name: tuple):
        super(RcControlFeedback, self).__init__()

        self.positive_name, self.negative_name = name

        self.layout = QtWidgets.QHBoxLayout()

        self.positive_label = QtWidgets.QLabel(self.positive_name)
        self.positive_label.setFixedWidth(120)

        self.negative_label = QtWidgets.QLabel(self.negative_name)
        self.negative_label.setFixedWidth(120)

        # self.negative_label.setFont(main_font)
        # self.positive_label.setFont(main_font)

        self.layout.addWidget(self.positive_label)
        self.layout.addWidget(self.negative_label)

        self.setLayout(self.layout)

    def highlight_control(self, speed):
        # print(speed)
        if speed:
            self.highlight_positive() if speed > 0 else self.highlight_negative()
        else:
            # self.negative_label.setFont(QtGui.QFont('Arial', 10))
            # self.positive_label.setFont(QtGui.QFont('Arial', 10))

            self.negative_label.setStyleSheet("background-color: """)
            self.positive_label.setStyleSheet("background-color: """)

    def highlight_positive(self):
        # self.negative_label.setFont(QtGui.QFont('Arial', 10))
        self.negative_label.setStyleSheet("background-color: """)

        # self.positive_label.setFont(QtGui.QFont('Arial', 14))
        self.positive_label.setStyleSheet("background-color: lightgreen; border: 1px solid black;")

    def highlight_negative(self):
        # self.negative_label.setFont(QtGui.QFont('Arial', 14))
        self.negative_label.setStyleSheet("background-color: lightgreen; border: 1px solid black;")

        # self.positive_label.setFont(QtGui.QFont('Arial', 10))
        self.positive_label.setStyleSheet("background-color: """)

