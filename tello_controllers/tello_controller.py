from tello_controllers.rc_controls import RcControl, GeneralCommand, GeneralControl

from djitellopy import Tello
from PyQt5 import QtCore, QtWidgets, QtGui

import time
import logging

logger = logging.getLogger('Tello controller')


class SendRcControlThread(QtCore.QThread):

    rc_controls_command = QtCore.pyqtSignal(object)

    def __init__(self, controller):
        super(SendRcControlThread, self).__init__()

        self.controller = controller

    def run(self):

        logger.info('Sending controls started')

        while True:

            rc_controls = (
                self.controller.for_back_velocity,
                self.controller.left_right_velocity,
                self.controller.up_down_velocity,
                self.controller.yaw_velocity)

            self.rc_controls_command.emit(rc_controls)

            # if self.controller.left_right_velocity != 0 or \
            #         self.controller.left_right_velocity != 0 or \
            #         self.controller.up_down_velocity != 0 or \
            #         self.controller.yaw_velocity != 0:
            #     pass

            self.controller.drone.send_rc_control(
                self.controller.left_right_velocity,
                self.controller.for_back_velocity,
                self.controller.up_down_velocity,
                self.controller.yaw_velocity
            )



            # print(rc_controls)

            time.sleep(0.1)


class SendCommandThread(QtCore.QThread):

    received_response = QtCore.pyqtSignal(str)

    def __init__(self, controller, command: GeneralCommand):
        super(SendCommandThread, self).__init__()

        self.controller = controller
        self.command = command

        self.general_commands = {
            GeneralCommand.Connect: self.controller.drone.connect,
            GeneralCommand.Takeoff: self.controller.drone.takeoff,
            GeneralCommand.Land: self.controller.drone.land,
            GeneralCommand.Emergency: self.controller.drone.emergency
        }

    def run(self):

        try:
            self.general_commands[self.command]()
            self.received_response.emit('RESPONSE')

        except Exception as ex:
            logger.error(ex)
            self.received_response.emit('NO_RESPONSE')


class SendControlThread(QtCore.QThread):

    received_response = QtCore.pyqtSignal(str)

    def __init__(self, controller, control: GeneralControl, value: int):
        super(SendControlThread, self).__init__()

        self.controller = controller
        self.control = control
        self.value = value

        self.general_controls = {
            GeneralControl.Up: self.controller.drone.move_up,
            GeneralControl.Down: self.controller.drone.move_down,
            GeneralControl.Left: self.controller.drone.move_left,
            GeneralControl.Right: self.controller.drone.move_right,
            GeneralControl.Backward: self.controller.drone.move_forward,
            GeneralControl.Forward: self.controller.drone.move_back,
            GeneralControl.RotateLeft: self.controller.drone.rotate_clockwise,
            GeneralControl.RotateRight: self.controller.drone.rotate_counter_clockwise,
        }

    def run(self):

        try:
            self.general_controls[self.control](self.value)
            self.received_response.emit('RESPONSE')

        except Exception as ex:
            logger.error(ex)
            self.received_response.emit('NO_RESPONSE')


class TelloRcController:
    """
    has to be subclassed as a controller
    """

    def __init__(self, lateral_speed, yaw_speed):
        super(TelloRcController, self).__init__()

        self.drone = Tello()
        self.drone.connect()
        self.drone.streamon()
        # self.drone.RESPONSE_TIMEOUT = 2
        # self.drone.RETRY_COUNT = 2
        # self.drone.TAKEOFF_TIMEOUT = 3

        self.for_back_velocity = 0
        self.left_right_velocity = 0
        self.up_down_velocity = 0
        self.yaw_velocity = 0

        self.lateral_speed = lateral_speed
        self.yaw_speed = yaw_speed

        self.control_thread = SendRcControlThread(self)

        self.speed_controls = {
            'for_back_velocity': (RcControl.Forward, RcControl.Backward),           # (positive value, negative value)
            'left_right_velocity': (RcControl.Right, RcControl.Left),
            'up_down_velocity': (RcControl.Up, RcControl.Down),
            'yaw_velocity': (RcControl.RotateRight, RcControl.RotateLeft)
        }

        self.directional_speeds = {
            'for_back_velocity': 'lateral_speed',
            'left_right_velocity': 'lateral_speed',
            'up_down_velocity': 'lateral_speed',
            'yaw_velocity': 'yaw_speed',
        }

        self.ui_widget = QtWidgets.QWidget()
        self.ui_widget.layout = QtWidgets.QHBoxLayout()
        self.ui_widget.setLayout(self.ui_widget.layout)
        # main_window.layout.addWidget(self.ui_widget, 0, 1)

        # self.drone.connect(wait_for_state=False)

        # self.control_thread.start()

    def set_speed_from_rc_controls(self, rc_controls: list[RcControl]):

        for attribute, commands in self.speed_controls.items():

            positive_control, negative_control = commands

            directional_speed = getattr(self, self.directional_speeds[attribute])

            if positive_control in rc_controls:
                setattr(self, attribute, directional_speed)

            elif negative_control in rc_controls:
                setattr(self, attribute, -1 * directional_speed)

            else:
                setattr(self, attribute, 0)

    def on_tello_takeoff(self):
        pass

    def on_tello_land(self):
        pass

    def send_command(self, command: GeneralCommand):

        self.command_thread = SendCommandThread(self, command)
        self.command_thread.received_response.connect(self.finish_command_thread)
        self.command_thread.start()

        if command == GeneralCommand.Takeoff:
            self.control_thread.start()

        if command == GeneralCommand.Land:
            self.control_thread.terminate()

        # self.general_commands[command]()
    def send_control(self, control: GeneralControl, value: int):
        self.command_thread = SendControlThread(self, control, value)
        self.command_thread.received_response.connect(self.finish_command_thread)
        self.command_thread.start()

    def finish_command_thread(self, response: str):
        print(response)
        self.command_thread.terminate()

    def destroy(self):

        self.control_thread.terminate()

        if self.camera:
            self.camera.video_thread.release()
            self.camera.video_thread.terminate()

        if self.ui_widget:
            self.ui_widget.deleteLater()

        self.finish_threads()

        del self.drone








