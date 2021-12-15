from tello_controllers.keyboard_controller.keyboard_controller import KeyboardController
from tello_controllers.gesture_controller.gesture_controller import GestureController
from tello_controllers.handfollow_controller.handfollow_controller import HandFollowController
from tellopycontroller.tello_controllers.tello_controller import TelloRcController

from PyQt5 import QtCore, QtWidgets, QtGui
from enum import Enum


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

        self.controller_type = ControllerType.KeyboardController
        self.controller = KeyboardController()

        self.drone_command_visual = DroneCommandVisual(self.controller)

        self.fps_label = QtWidgets.QLabel()
        self.fps_label.setFont(QtGui.QFont('Arial', 12))
        self.controller.camera.fps_count.connect(self.update_fps_label)

        self.controller_selection = ControllerSelector(self)
        # self.controller_selection.controller_changed.connect(self.set_controller)

        self.layout.addWidget(self.drone_command_visual, 0, 0)
        self.layout.addWidget(self.fps_label)
        self.layout.addWidget(self.controller_selection)

        self.layout.addWidget(self.controller.ui_widget)

        self.controller.sender_thread.rc_controls_command.connect(self.drone_command_visual.update_rc_control)

        self.setLayout(self.layout)

        self.set_controller(ControllerType.KeyboardController)

    def update_fps_label(self, fps_count):
        self.fps_label.setText(f'FPS: {round(fps_count, 2)}')

    def set_controller(self, controller_type: ControllerType):
        if hasattr(self, 'controller') and self.controller:
            self.controller.destroy()

        self.controller = self.controllers.get(controller_type)()
        self.controller_type = controller_type

        self.layout.addWidget(self.controller.ui_widget)
        self.controller.sender_thread.rc_controls_command.connect(self.drone_command_visual.update_rc_control)
        self.controller.camera.fps_count.connect(self.update_fps_label)

        self.data_changed.emit()


class ControllerSelector(QtWidgets.QComboBox):

    # controller_changed = QtCore.pyqtSignal(ControllerType)

    def __init__(self, control_panel: MainControlPanel):
        super().__init__()

        self.control_panel = control_panel

        self.names = [option.name.capitalize() for option in ControllerType]
        self.options = [option for option in ControllerType]

        for name in self.names:
            self.addItem(name)

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

    def __init__(self, controller: TelloRcController):
        super(DroneCommandVisual, self).__init__()

        self.controller = controller

        self.layout = QtWidgets.QGridLayout()

        self.forward_info = RcControlFeedback(self.controller, ('Forward', 'Backward'))
        self.layout.addWidget(self.forward_info)

        self.leftrigth_info = RcControlFeedback(self.controller, ('Left', 'Right'))
        self.layout.addWidget(self.leftrigth_info)

        self.updown_info = RcControlFeedback(self.controller, ('Up', 'Down'))
        self.layout.addWidget(self.updown_info)

        self.yaw_info = RcControlFeedback(self.controller, ('RotateLeft', 'RotateRight'))
        self.layout.addWidget(self.yaw_info)

        self.speed_setting = QtWidgets.QSpinBox()
        self.speed_setting.setMinimum(0)
        self.speed_setting.setMaximum(100)
        self.speed_setting.setValue(self.controller.speed)
        self.speed_setting.valueChanged.connect(self.set_control_speed)

        self.layout.addWidget(self.speed_setting)

        self.setLayout(self.layout)

    @QtCore.pyqtSlot(tuple)
    def update_rc_control(self, rc_control):

        forw, leftr, updown, yaw = rc_control

        self.forward_info.highlight_control(forw)
        self.leftrigth_info.highlight_control(leftr)
        self.updown_info.highlight_control(updown)
        self.yaw_info.highlight_control(yaw)

    def set_control_speed(self, value):
        self.controller.speed = value


class RcControlFeedback(QtWidgets.QWidget):

    def __init__(self, controller: TelloRcController, name: tuple):
        super(RcControlFeedback, self).__init__()

        self.controller = controller
        self.positive_name, self.negative_name = name

        self.layout = QtWidgets.QHBoxLayout()

        self.positive_label = QtWidgets.QLabel(self.positive_name)
        self.positive_label.setFixedWidth(120)

        self.negative_label = QtWidgets.QLabel(self.negative_name)
        self.negative_label.setFixedWidth(120)

        self.negative_label.setFont(QtGui.QFont('Arial', 14))
        self.positive_label.setFont(QtGui.QFont('Arial', 14))

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


