from tellopycontroller.tello_controllers.tello_controller import TelloCameraWidget

from PyQt5 import QtCore, QtWidgets

import copy
import cv2 as cv
import mediapipe as mp


mp_drawing = mp.solutions.drawing_utils
mp_styles = mp.solutions.drawing_styles
mp_hands = mp.solutions.hands


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

