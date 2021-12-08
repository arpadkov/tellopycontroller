from tellopycontroller.tello_controller.keyboard_controller import KeyboardController
from tellopycontroller.tello_controller.gesture_controller import GestureController
from tellopycontroller.tello_controller.tello_controller import TelloRcController

from PyQt5 import QtCore, QtWidgets, QtGui
from enum import Enum


class ControllerType(Enum):

    KeyboardController = 1
    GestureController = 2


class MainControlPanel(QtWidgets.QWidget):

    def __init__(self):
        super(MainControlPanel, self).__init__()

        self.controllers = {
            ControllerType.KeyboardController: KeyboardController,
            ControllerType.GestureController: GestureController
        }

        # self.controller_type = ControllerType.GestureController
        self.controller = KeyboardController()

        self.drone_command_visual = DroneCommandVisual(self)
        self.controller.sender_thread.rc_controls_command.connect(self.drone_command_visual.update_rc_control)

        self.layout = QtWidgets.QGridLayout()

        self.fps_label = QtWidgets.QLabel()
        self.controller.camera.fps_count.connect(self.update_fps_label)

        self.controller_selection = ControllerSelector()
        self.controller_selection.controller_changed.connect(self.set_controller)

        self.layout.addWidget(self.drone_command_visual, 0, 0)
        self.layout.addWidget(self.fps_label)
        self.layout.addWidget(self.controller_selection)

        self.layout.addWidget(self.controller.ui_widget)

        self.setLayout(self.layout)

    def update_fps_label(self, fps_count):
        self.fps_label.setText(f'FPS: {round(fps_count, 2)}')

    def set_controller(self, controller_type: ControllerType):
        # self.controller_type = controller_type
        self.controller.destroy()
        # self.controller = None

        # del self.controller
        self.controller = self.controllers.get(controller_type)()

        self.layout.addWidget(self.controller.ui_widget)
        self.controller.sender_thread.rc_controls_command.connect(self.drone_command_visual.update_rc_control)
        # self.controller.ui_widget.addWidget(self.controller.camera)


# class ControllerSelector(QtWidgets.QComboBox):
#
#     def __init__(self, controllers: list[TelloRcController]):
#         super(ControllerSelector, self).__init__()
#
#         self.addItems([type(controller).__name__ for controller in controllers])


class ControllerSelector(QtWidgets.QComboBox):

    controller_changed = QtCore.pyqtSignal(ControllerType)

    def __init__(self):
        super().__init__()

        self.names = [option.name.capitalize() for option in ControllerType]
        self.options = [option for option in ControllerType]

        for name in self.names:
            self.addItem(name)

        self.currentIndexChanged.connect(self.index_changed)
        # self.model.message_obj.selection_changed.connect(self.value_changed)

    def index_changed(self, index):
        self.controller_changed.emit(self.options[index])
        # self.control_panel.set_controller(self.options[index])

    # def value_changed(self):
    #     index = self.options.index(getattr(self.model, self.attr))
    #     self.setCurrentIndex(index)





class DroneCommandVisual(QtWidgets.QWidget):

    def __init__(self, parent: MainControlPanel):
        super(DroneCommandVisual, self).__init__(parent)

        # self.parent().controller.sender_thread.rc_controls_command.connect(self.update_rc_control)

        self.layout = QtWidgets.QGridLayout()

        self.forward_label = QtWidgets.QLabel('Forward')
        self.leftright_label = QtWidgets.QLabel('Left/Right')
        self.up_label = QtWidgets.QLabel('Up/Down')
        self.yaw_label = QtWidgets.QLabel('Yaw')

        self.layout.addWidget(self.forward_label, 0, 0)
        self.layout.addWidget(self.leftright_label, 1, 0)
        self.layout.addWidget(self.up_label, 2, 0)
        self.layout.addWidget(self.yaw_label, 3, 0)

        self.forward_value = QtWidgets.QLabel()
        self.leftright_value = QtWidgets.QLabel()
        self.up_value = QtWidgets.QLabel()
        self.yaw_value = QtWidgets.QLabel()

        self.layout.addWidget(self.forward_value, 0, 1)
        self.layout.addWidget(self.leftright_value, 1, 1)
        self.layout.addWidget(self.up_value, 2, 1)
        self.layout.addWidget(self.yaw_value, 3, 1)

        self.setLayout(self.layout)



    @QtCore.pyqtSlot(tuple)
    def update_rc_control(self, rc_control):

        forw, leftr, updown, yaw = rc_control

        self.forward_value.setText(str(forw))
        self.leftright_value.setText(str(leftr))
        self.up_value.setText(str(updown))
        self.yaw_value.setText(str(yaw))