from tello_controllers.keyboard_controller.keyboard_controller import KeyboardController
from tello_controllers.gesture_controller.gesture_controller import GestureController
from tello_controllers.handfollow_controller.handfollow_controller import HandFollowController
from tellopycontroller.GUI.GUICommandVisual import DroneCommandVisual
from tellopycontroller.GUI.GUICommandButtons import CommandButtonsWidget
from tellopycontroller.GUI.GUIControlButtons import ControlButtonsWidget

from PyQt5 import QtCore, QtWidgets, QtGui
from enum import Enum

# main_font = QtGui.QFont('Arial', 11)


class ControllerType(Enum):

    KeyboardController = 1
    GestureController = 2
    HandFollowController = 3

    @property
    def ui_name(self):

        ui_names = {
            ControllerType.KeyboardController: 'Keyboard Controller',
            ControllerType.GestureController: 'Gesture Controller',
            ControllerType.HandFollowController: 'Hand-Follow Controller'
        }

        return ui_names[self]


class MainControlPanel(QtWidgets.QWidget):

    # controller_changed = QtCore.pyqtSignal(object, object)
    controller_changed_signal = QtCore.pyqtSignal(object, object)

    tello_takeoff_signal = QtCore.pyqtSignal()
    tello_land_signal = QtCore.pyqtSignal()

    def __init__(self):
        super(MainControlPanel, self).__init__()

        self.layout = QtWidgets.QGridLayout()

        self.controllers = {
            ControllerType.KeyboardController: KeyboardController,
            ControllerType.GestureController: GestureController,
            ControllerType.HandFollowController: HandFollowController
        }

        self.lateral_speed = 20
        self.yaw_speed = 30

        self.controller_type = ControllerType.KeyboardController
        # self.controller = KeyboardController(self.lateral_speed, self.yaw_speed)

        self.drone_command_visual = DroneCommandVisual(self.lateral_speed, self.yaw_speed)
        self.drone_command_visual.speed_setting_changed.connect(self.set_control_speed)

        self.fps_label = QtWidgets.QLabel()
        self.fps_label.setFixedSize(100, 20)
        # self.fps_label.setFont(main_font)
        # self.controller.camera.fps_count.connect(self.update_fps_label)

        self.controller_selection = ControllerSelector(self)
        # self.controller_selection.controller_changed.connect(self.set_controller)

        self.layout.addWidget(self.drone_command_visual, 0, 0, QtCore.Qt.AlignCenter)
        self.layout.addWidget(self.controller_selection, 1, 0, QtCore.Qt.AlignLeft)
        self.layout.addWidget(self.fps_label, 2, 0, QtCore.Qt.AlignLeft)

        # self.layout.addWidget(self.controller.ui_widget, 3, 0, QtCore.Qt.AlignLeft)

        # self.controller.sender_thread.rc_controls_command.connect(self.drone_command_visual.update_rc_control)

        self.command_buttons = CommandButtonsWidget()
        self.control_buttons = ControlButtonsWidget()

        self.layout.addWidget(self.command_buttons, 0, 1, 1, 1)
        self.layout.addWidget(self.control_buttons, 0, 2, 1, 1)

        self.setLayout(self.layout)

    def update_fps_label(self, fps_count):
        self.fps_label.setText(f'FPS: {round(fps_count, 2)}')

    def set_controller(self, controller_type: ControllerType):
        if hasattr(self, 'controller') and self.controller:
            self.controller.destroy()
            del self.controller

        self.controller = self.controllers.get(controller_type)(self.lateral_speed, self.yaw_speed)
        self.controller_type = controller_type

        # self.layout.addWidget(self.controller.ui_widget)
        self.controller.control_thread.rc_controls_command.connect(self.drone_command_visual.update_rc_control)
        self.controller.camera.fps_count.connect(self.update_fps_label)

        self.layout.addWidget(self.controller.ui_widget, 3, 0, QtCore.Qt.AlignLeft)

        self.tello_takeoff_signal.connect(self.controller.on_tello_takeoff)
        self.tello_land_signal.connect(self.controller.on_tello_land)

        self.drone_command_visual.update_speeds()

        self.command_buttons.general_command_signal.connect(self.controller.send_command)
        self.control_buttons.general_control_signal.connect(self.controller.send_control)

        self.controller.control_thread.rc_controls_command.connect(self.drone_command_visual.update_rc_control)

        self.controller.camera.video_thread.start()

        # self.controller_changed.emit(self.controller, self.controller_type)
        self.controller_changed_signal.emit(self.controller, self.controller_type)

    def set_control_speed(self, controller_speed, value):
        setattr(self.controller, controller_speed, value)




class ControllerSelector(QtWidgets.QComboBox):

    # controller_changed = QtCore.pyqtSignal(ControllerType)

    def __init__(self, control_panel: MainControlPanel):
        super().__init__()

        self.control_panel = control_panel

        self.names = [option.ui_name for option in ControllerType]
        self.options = [option for option in ControllerType]

        for name in self.names:
            self.addItem(name)

        # self.setFont(main_font)

        # self.currentIndexChanged.connect(self.index_changed)
        self.control_panel.controller_changed_signal.connect(self.value_changed)

        # self.value_changed()

    def index_changed(self, index):
        # self.controller_changed.emit(self.options[index])
        # self.control_panel.set_controller(self.options[index])
        pass

    def value_changed(self):
        index = self.options.index(getattr(self.control_panel, 'controller_type'))
        self.setCurrentIndex(index)




