from tello_controllers.keyboard_controller.keyboard_controller import KeyboardController
from tello_controllers.gesture_controller.gesture_controller import GestureController
from tello_controllers.handfollow_controller.handfollow_controller import HandFollowController
from tellopycontroller.tello_controllers.tello_controller import TelloRcController

from PyQt5 import QtCore, QtWidgets, QtGui
from enum import Enum

main_font = QtGui.QFont('Arial', 14)


class ControllerType(Enum):

    KeyboardController = 1
    GestureController = 2
    HandFollowController = 3


class MainControlPanel(QtWidgets.QWidget):

    data_changed = QtCore.pyqtSignal()

    def __init__(self):
        super(MainControlPanel, self).__init__()

        self.layout = QtWidgets.QGridLayout()

        self.controllers = {
            ControllerType.KeyboardController: KeyboardController,
            ControllerType.GestureController: GestureController,
            ControllerType.HandFollowController: HandFollowController
        }

        self.lateral_speed = 50
        self.yaw_speed = 50

        self.controller_type = ControllerType.KeyboardController
        self.controller = KeyboardController(self.lateral_speed, self.yaw_speed)

        self.drone_command_visual = DroneCommandVisual(self.lateral_speed, self.yaw_speed)
        self.drone_command_visual.speed_setting_changed.connect(self.set_control_speed)

        self.fps_label = QtWidgets.QLabel()
        self.fps_label.setFont(main_font)
        self.controller.camera.fps_count.connect(self.update_fps_label)

        self.controller_selection = ControllerSelector(self)
        # self.controller_selection.controller_changed.connect(self.set_controller)

        self.layout.addWidget(self.drone_command_visual, 0, 0)
        self.layout.addWidget(self.fps_label)
        self.layout.addWidget(self.controller_selection)

        self.layout.addWidget(self.controller.ui_widget)

        self.controller.sender_thread.rc_controls_command.connect(self.drone_command_visual.update_rc_control)

        self.setLayout(self.layout)

        # self.set_controller(ControllerType.KeyboardController)

    def update_fps_label(self, fps_count):
        self.fps_label.setText(f'FPS: {round(fps_count, 2)}')

    def set_controller(self, controller_type: ControllerType):
        if hasattr(self, 'controller') and self.controller:
            self.controller.destroy()
            del self.controller

        self.controller = self.controllers.get(controller_type)(self.lateral_speed, self.yaw_speed)
        self.controller_type = controller_type

        self.layout.addWidget(self.controller.ui_widget)
        self.controller.sender_thread.rc_controls_command.connect(self.drone_command_visual.update_rc_control)
        self.controller.camera.fps_count.connect(self.update_fps_label)

        self.drone_command_visual.update_speeds()

        self.data_changed.emit()

    def set_control_speed(self, controller_speed, value):
        setattr(self.controller, controller_speed, value)


class ControllerSelector(QtWidgets.QComboBox):

    # controller_changed = QtCore.pyqtSignal(ControllerType)

    def __init__(self, control_panel: MainControlPanel):
        super().__init__()

        self.control_panel = control_panel

        self.names = [option.name.capitalize() for option in ControllerType]
        self.options = [option for option in ControllerType]

        for name in self.names:
            self.addItem(name)

        self.setFont(main_font)

        self.currentIndexChanged.connect(self.index_changed)
        self.control_panel.data_changed.connect(self.value_changed)

        self.value_changed()

    def index_changed(self, index):
        # self.controller_changed.emit(self.options[index])
        self.control_panel.set_controller(self.options[index])

    def value_changed(self):
        index = self.options.index(getattr(self.control_panel, 'controller_type'))
        self.setCurrentIndex(index)


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
        self.label.setFont(main_font)

        self.spin_box = QtWidgets.QSpinBox()
        self.spin_box.setFont(main_font)

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

        self.negative_label.setFont(main_font)
        self.positive_label.setFont(main_font)

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


