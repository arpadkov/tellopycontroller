from tellopycontroller.tello_controller.tello_controller import TelloRcController, TelloCameraWidget
from tellopycontroller.hand_handler import HandHandler
from tellopycontroller.gesture_data.gestures import Gesture
from tellopycontroller.tello_controller.rc_controls import RcControl

from PyQt5 import QtCore, QtWidgets, QtGui

import os
import time
import cv2 as cv
import mediapipe as mp
import numpy as np
import tensorflow as tf
import threading
import copy


mp_drawing = mp.solutions.drawing_utils
mp_styles = mp.solutions.drawing_styles
mp_hands = mp.solutions.hands


class PredictionThread(QtCore.QThread):

    gesture_changed = QtCore.pyqtSignal(Gesture, object)
    no_gesture_recognized = QtCore.pyqtSignal()

    def __init__(self, handler):
        super(PredictionThread, self).__init__()

        self.handler = handler

    def run(self):

        model = tf.keras.models.load_model('keras_gesture_model')

        while True:
            pre_processed_landmark_list = self.handler.get_preprocessed_landmark_list()

            prediction = model.predict(np.array([pre_processed_landmark_list]))
            gesture_id = np.argmax(prediction)

            if np.amax(prediction) > 0.8:
                gesture = Gesture(gesture_id)
                self.gesture_changed.emit(gesture, prediction)
                # print(f'{gesture.name} - {round(np.amax(prediction) * 100, 2)} %')
            else:
                self.no_gesture_recognized.emit()



class GestureController(TelloRcController):

    def __init__(self):
        super(GestureController, self).__init__()

        self.control_panel = GestureControlPanel()
        self.camera = GestureControlCamera()

        self.handler = HandHandler()

        self.prediction_thread = PredictionThread(self.handler)

        self.camera.hand_landmarks_changed.connect(self.handler.hand_landmarks_change)

        self.prediction_thread.gesture_changed.connect(self.translate_gesture)
        self.prediction_thread.no_gesture_recognized.connect(self.zero_rc_controls)

        self.ui_widget.layout.addWidget(self.control_panel)
        self.ui_widget.layout.addWidget(self.camera)

        self.prediction_thread.start()

    def translate_gesture(self, gesture: Gesture, prediction):
        # print(f'{gesture.name} - {round(np.amax(prediction) * 100, 2)} %')

        gesture_control_connections = {
            Gesture.Up: RcControl.Up,
            Gesture.Down: RcControl.Down,
            Gesture.Left: RcControl.Left,
            Gesture.Right: RcControl.Right,
            Gesture.Backward: RcControl.Backward,
            Gesture.Forward: RcControl.Forward,
            Gesture.RotateLeft: RcControl.RotateLeft,
            Gesture.RotateRight: RcControl.RotateRight,
            Gesture.Land: RcControl.Land,
        }

        rc_control = gesture_control_connections.get(gesture)
        self.set_speed_from_rc_controls([rc_control])

    def zero_rc_controls(self):
        self.set_speed_from_rc_controls([])

    def finish_threads(self):

        self.prediction_thread.terminate()


class GestureControlPanel(QtWidgets.QWidget):

    def __init__(self):
        super(GestureControlPanel, self).__init__()


class GestureControlCamera(TelloCameraWidget):

    hand_landmarks_changed = QtCore.pyqtSignal(object, object, object)

    def __init__(self):
        super(GestureControlCamera, self).__init__()


    def detect_hands(self):

        cv_image_copy = copy.deepcopy(self.cv_image)
        # x = id(cv_image_copy)
        # y = id(self.cv_image)
        #
        # print('')


        with mp_hands.Hands(
                model_complexity=0,
                min_detection_confidence=0.5,
                min_tracking_confidence=0.5,
                max_num_hands=2) as hands:

            cv_image_copy.flags.writeable = False

            cv_image_copy = cv.cvtColor(cv_image_copy, cv.COLOR_BGR2RGB)
            results = hands.process(cv_image_copy)



            # cv_image = cv.cvtColor(cv_image, cv.COLOR_RGB2BGR)
            # cv_image.flags.writeable = True

            if results.multi_hand_landmarks:

                for hand_landmark in results.multi_hand_landmarks:
                    mp_drawing.draw_landmarks(
                        self.cv_image,
                        hand_landmark,
                        mp_hands.HAND_CONNECTIONS,
                        mp_styles.get_default_hand_landmarks_style(),
                        mp_styles.get_default_hand_connections_style(),
                    )

        self.hand_landmarks_changed.emit(results.multi_hand_landmarks, results.multi_handedness, cv_image_copy)

        # return cv_image, results.multi_hand_landmarks, results.multi_handedness
        # self.cv_image = cv_image

    def handle_image(self):
        self.detect_hands()






