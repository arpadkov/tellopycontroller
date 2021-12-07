from tellopycontroller.tello_controller.rc_controls import RcControl

from djitellopy import Tello
from PyQt5 import QtCore, QtWidgets, QtGui

import time
import numpy as np
import cv2 as cv


class SendControlThread(QtCore.QThread):

    rc_controls_command = QtCore.pyqtSignal(object)

    def __init__(self, controller):
        super(SendControlThread, self).__init__()

        self.controller = controller

    def run(self):
        while True:

            rc_controls = (
                self.controller.for_back_velocity,
                self.controller.left_right_velocity,
                self.controller.up_down_velocity,
                self.controller.yaw_velocity)

            self.rc_controls_command.emit(rc_controls)

            print(rc_controls)

            time.sleep(0.1)


class TelloRcController(QtWidgets.QWidget):
    """
    has to be subclassed as a controller
    """

    def __init__(self):
        super(TelloRcController, self).__init__()

        self.layout = QtWidgets.QHBoxLayout()
        self.setLayout(self.layout)

        self.drone = Tello()

        self.for_back_velocity = 0
        self.left_right_velocity = 0
        self.up_down_velocity = 0
        self.yaw_velocity = 0

        self.speed = 20

        self.sender_thread = SendControlThread(self)
        self.sender_thread.start()

        self.speed_controls = {
            'for_back_velocity': (RcControl.Forward, RcControl.Backward),           # (positive value, negative value)
            'left_right_velocity': (RcControl.Left, RcControl.Right),
            'up_down_velocity': (RcControl.Up, RcControl.Down),
            'yaw_velocity': (RcControl.RotateLeft, RcControl.RotateRight)
        }

    def set_speed_from_rc_controls(self, rc_controls: list[RcControl]):

        for attribute, commands in self.speed_controls.items():

            positive_control, negative_control = commands

            if positive_control in rc_controls:
                setattr(self, attribute, self.speed)

            elif negative_control in rc_controls:
                setattr(self, attribute, -1 * self.speed)

            else:
                setattr(self, attribute, 0)


class VideoCaptureThread(QtCore.QThread):

    change_pixmap_signal = QtCore.pyqtSignal(np.ndarray)

    def run(self):
        cap = cv.VideoCapture(0)

        while True:
            success, cv_image = cap.read()
            if success:
                cv_image = cv.flip(cv_image, 1)
                self.change_pixmap_signal.emit(cv_image)


class TelloCameraWidget(QtWidgets.QLabel):

    def __init__(self):
        super(TelloCameraWidget, self).__init__()

        # self.setFixedSize(500, 500)

        self.disply_width = 640
        self.display_height = 480

        self.video_thread = VideoCaptureThread()

        self.video_thread.change_pixmap_signal.connect(self.update_image)
        self.video_thread.start()

    @staticmethod
    def convert_cv_to_qt(cv_image, display_width, display_height):
        rgb_image = cv.cvtColor(cv_image, cv.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        qt_format = QtGui.QImage(rgb_image.data, w, h, bytes_per_line, QtGui.QImage.Format_RGB888)
        pixmap = qt_format.scaled(display_width, display_height, QtCore.Qt.KeepAspectRatio)
        return QtGui.QPixmap.fromImage(pixmap)

    def draw_on_image(self):
        self.qt_image = self.convert_cv_to_qt(self.cv_image, self.disply_width, self.display_height)

    @QtCore.pyqtSlot(np.ndarray)
    def update_image(self, cv_image):

        self.cv_image = cv_image

        self.draw_on_image()

        self.setPixmap(self.qt_image)




