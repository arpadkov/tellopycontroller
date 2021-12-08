from PyQt5 import QtCore, QtWidgets, QtGui

import cv2 as cv
import mediapipe as mp
import numpy as np


mp_drawing = mp.solutions.drawing_utils
mp_styles = mp.solutions.drawing_styles
mp_hands = mp.solutions.hands


def convert_cv_to_qt(cv_image, display_width, display_height):
    rgb_image = cv.cvtColor(cv_image, cv.COLOR_BGR2RGB)
    h, w, ch = rgb_image.shape
    bytes_per_line = ch * w
    qt_format = QtGui.QImage(rgb_image.data, w, h, bytes_per_line, QtGui.QImage.Format_RGB888)
    pixmap = qt_format.scaled(display_width, display_height, QtCore.Qt.KeepAspectRatio)
    return QtGui.QPixmap.fromImage(pixmap)


def detect_hands(cv_image):

    with mp_hands.Hands(
            model_complexity=0,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5,
            max_num_hands=2) as hands:

        cv_image.flags.writeable = False

        cv_image = cv.cvtColor(cv_image, cv.COLOR_BGR2RGB)
        results = hands.process(cv_image)

        cv_image = cv.cvtColor(cv_image, cv.COLOR_RGB2BGR)
        cv_image.flags.writeable = True

        if results.multi_hand_landmarks:

            for hand_landmark in results.multi_hand_landmarks:
                mp_drawing.draw_landmarks(
                    cv_image,
                    hand_landmark,
                    mp_hands.HAND_CONNECTIONS,
                    mp_styles.get_default_hand_landmarks_style(),
                    mp_styles.get_default_hand_connections_style(),
                )

    return cv_image, results.multi_hand_landmarks, results.multi_handedness


class VideoCaptureThread(QtCore.QThread):

    change_pixmap_signal = QtCore.pyqtSignal(np.ndarray, object, object)

    def run(self):
        cap = cv.VideoCapture(0)

        while True:
            success, cv_image = cap.read()
            if success:
                cv_image = cv.flip(cv_image, 1)
                cv_image, hand_landmarks, handedness = detect_hands(cv_image)
                self.change_pixmap_signal.emit(cv_image, hand_landmarks, handedness)


class CameraWidget(QtWidgets.QLabel):

    change_hand_landmarks = QtCore.pyqtSignal(object, object, object)

    def __init__(self):
        super(CameraWidget, self).__init__()

        # self.setFixedSize(500, 500)

        self.dispaly_width = 640
        self.display_height = 480

        self.video_thread = VideoCaptureThread()

        self.video_thread.change_pixmap_signal.connect(self.update_image)
        self.video_thread.start()

    @QtCore.pyqtSlot(np.ndarray, object, object)
    def update_image(self, cv_image, hand_landmarks, handedness):
        qt_image = convert_cv_to_qt(cv_image, self.display_width, self.display_height)
        self.setPixmap(qt_image)

        # if hand_landmarks:
        self.change_hand_landmarks.emit(hand_landmarks, handedness, cv_image)

