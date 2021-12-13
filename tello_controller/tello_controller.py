from tellopycontroller.tello_controller.rc_controls import RcControl

from djitellopy import Tello
from PyQt5 import QtCore, QtWidgets, QtGui

from collections import deque

import time
import numpy as np
import cv2 as cv

# import mediapipe as mp
# mp_drawing = mp.solutions.drawing_utils
# mp_styles = mp.solutions.drawing_styles
# mp_hands = mp.solutions.hands
# def detect_hands(cv_image):
#
#     with mp_hands.Hands(
#             model_complexity=0,
#             min_detection_confidence=0.5,
#             min_tracking_confidence=0.5,
#             max_num_hands=2) as hands:
#
#         cv_image.flags.writeable = False
#
#         cv_image = cv.cvtColor(cv_image, cv.COLOR_BGR2RGB)
#         results = hands.process(cv_image)
#
#         cv_image = cv.cvtColor(cv_image, cv.COLOR_RGB2BGR)
#         cv_image.flags.writeable = True
#
#         if results.multi_hand_landmarks:
#
#             for hand_landmark in results.multi_hand_landmarks:
#                 mp_drawing.draw_landmarks(
#                     cv_image,
#                     hand_landmark,
#                     mp_hands.HAND_CONNECTIONS,
#                     mp_styles.get_default_hand_landmarks_style(),
#                     mp_styles.get_default_hand_connections_style(),
#                 )
#
#     return cv_image, results.multi_hand_landmarks, results.multi_handedness


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

            # print(rc_controls)

            time.sleep(0.1)


class CvFpsCalc(object):
    def __init__(self, buffer_len=1):
        self._start_tick = cv.getTickCount()
        self._freq = 1000.0 / cv.getTickFrequency()
        self._difftimes = deque(maxlen=buffer_len)

    def get(self):
        current_tick = cv.getTickCount()
        different_time = (current_tick - self._start_tick) * self._freq
        self._start_tick = current_tick

        self._difftimes.append(different_time)

        fps = 1000.0 / (sum(self._difftimes) / len(self._difftimes))
        fps_rounded = round(fps, 2)

        return fps_rounded


class TelloRcController:
    """
    has to be subclassed as a controller
    """

    def __init__(self):
        super(TelloRcController, self).__init__()

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

        self.ui_widget = QtWidgets.QWidget()
        self.ui_widget.layout = QtWidgets.QHBoxLayout()
        self.ui_widget.setLayout(self.ui_widget.layout)
        # main_window.layout.addWidget(self.ui_widget, 0, 1)

    def set_speed_from_rc_controls(self, rc_controls: list[RcControl]):

        for attribute, commands in self.speed_controls.items():

            positive_control, negative_control = commands

            if positive_control in rc_controls:
                setattr(self, attribute, self.speed)

            elif negative_control in rc_controls:
                setattr(self, attribute, -1 * self.speed)

            else:
                setattr(self, attribute, 0)

    def destroy(self):
        pass


class VideoCaptureThread(QtCore.QThread):

    # change_pixmap_signal = QtCore.pyqtSignal(np.ndarray)
    change_pixmap_signal = QtCore.pyqtSignal()

    def __init__(self, camera_widget):
        super(VideoCaptureThread, self).__init__()

        self.camera_widget = camera_widget
        self.cap = cv.VideoCapture(0)
        # self.cap = cv.VideoCapture(0, cv.CAP_DSHOW)

    def run(self):
        # print('STARTING CAMERA')
        while True:
            success, cv_image = self.cap.read()
            if success:
                fps = self.cap.get(cv.CAP_PROP_FPS)
                self.camera_widget.cv_image = cv.flip(cv_image, 1)
                self.camera_widget.handle_image()
                # self.change_pixmap_signal.emit(cv_image)
                self.change_pixmap_signal.emit()
                # time.sleep(0.1)

    def release(self):
        self.cap.release()
        # time.sleep(3)


class TelloCameraWidget(QtWidgets.QLabel):

    fps_count = QtCore.pyqtSignal(float)

    def __init__(self):
        super(TelloCameraWidget, self).__init__()

        # self.setFixedSize(500, 500)
        # self.cv_image = None
        # self.qt_image = None

        self.display_width = 640
        self.display_height = 480

        self.video_thread = VideoCaptureThread(camera_widget=self)

        self.cv_fps_calc = CvFpsCalc(buffer_len=10)

        self.video_thread.change_pixmap_signal.connect(self.update_image)
        self.video_thread.start()

    def handle_image(self):
        raise NotImplementedError

    # @staticmethod
    # def convert_image(cv_image, display_width, display_height):
    #
    #     rgb_image = cv.cvtColor(cv_image, cv.COLOR_BGR2RGB)
    #     h, w, ch = rgb_image.shape
    #     bytes_per_line = ch * w
    #     qt_format = QtGui.QImage(rgb_image.data, w, h, bytes_per_line, QtGui.QImage.Format_RGB888)
    #     pixmap = qt_format.scaled(display_width, display_height, QtCore.Qt.KeepAspectRatio)
    #     return QtGui.QPixmap.fromImage(pixmap)

    def convert_image(self):
        rgb_image = cv.cvtColor(self.cv_image, cv.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        qt_format = QtGui.QImage(rgb_image.data, w, h, bytes_per_line, QtGui.QImage.Format_RGB888)
        pixmap = qt_format.scaled(self.display_width, self.display_height, QtCore.Qt.KeepAspectRatio)
        return QtGui.QPixmap.fromImage(pixmap)

    @QtCore.pyqtSlot()
    def update_image(self):

        fps = self.cv_fps_calc.get()
        self.fps_count.emit(fps)


        # self.cv_image = cv_image

        # self.handle_image(cv_image)

        # _, _, _ = detect_hands(cv_image)

        # if self.cv_image is not None:
        # qt_image = self.convert_image()
        # time.sleep(0.1)

        self.setPixmap(self.convert_image()) # cv_image converted to qt_image




