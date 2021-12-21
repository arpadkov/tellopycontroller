from tello_controllers.rc_controls import RcControl

from djitellopy import Tello
from PyQt5 import QtCore, QtWidgets, QtGui

import time
import logging

logger = logging.getLogger('Tello controller')


class SendControlThread(QtCore.QThread):

    rc_controls_command = QtCore.pyqtSignal(object)

    def __init__(self, controller):
        super(SendControlThread, self).__init__()

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

            # print(rc_controls)

            time.sleep(0.1)


class TelloRcController:
    """
    has to be subclassed as a controller
    """

    def __init__(self, lateral_speed, yaw_speed):
        super(TelloRcController, self).__init__()

        self.drone = Tello()

        self.for_back_velocity = 0
        self.left_right_velocity = 0
        self.up_down_velocity = 0
        self.yaw_velocity = 0

        self.lateral_speed = lateral_speed
        self.yaw_speed = yaw_speed

        self.sender_thread = SendControlThread(self)

        self.speed_controls = {
            'for_back_velocity': (RcControl.Forward, RcControl.Backward),           # (positive value, negative value)
            'left_right_velocity': (RcControl.Left, RcControl.Right),
            'up_down_velocity': (RcControl.Up, RcControl.Down),
            'yaw_velocity': (RcControl.RotateLeft, RcControl.RotateRight)
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

        self.sender_thread.start()

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



    def destroy(self):

        self.sender_thread.terminate()

        if self.camera:
            self.camera.video_thread.release()
            self.camera.video_thread.terminate()

        if self.ui_widget:
            self.ui_widget.deleteLater()

        self.finish_threads()








