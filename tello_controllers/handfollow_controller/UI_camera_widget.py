from tello_controllers.UI_camera_widget import TelloCameraWidget

from PyQt5 import QtCore, QtWidgets, QtGui

import cv2 as cv
import numpy as np
import mediapipe as mp
import copy

mp_drawing = mp.solutions.drawing_utils
mp_styles = mp.solutions.drawing_styles
mp_hands = mp.solutions.hands

class HandFollowControlCamera(TelloCameraWidget):

    hand_position_changed = QtCore.pyqtSignal(object, object)       # hand_position, hand_landmark

    def __init__(self):
        super(HandFollowControlCamera, self).__init__()

        self.target_rect_size = None

    def detect_hand(self):

        cv_image_copy = copy.deepcopy(self.cv_image)

        with mp_hands.Hands(
                model_complexity=0,
                min_detection_confidence=0.5,
                min_tracking_confidence=0.5,
                max_num_hands=1) as hands:

            cv_image_copy.flags.writeable = False

            cv_image_copy = cv.cvtColor(cv_image_copy, cv.COLOR_BGR2RGB)
            results = hands.process(cv_image_copy)

            # cv_image = cv.cvtColor(cv_image, cv.COLOR_RGB2BGR)
            # cv_image.flags.writeable = True

            if results.multi_hand_landmarks:

                hand_landmark = results.multi_hand_landmarks[0]

                # mp_drawing.draw_landmarks(
                #     self.cv_image,
                #     hand_landmark,
                #     mp_hands.HAND_CONNECTIONS,
                #     mp_styles.get_default_hand_landmarks_style(),
                #     mp_styles.get_default_hand_connections_style(),
                # )

                self._calc_bounding_rect(hand_landmark)
                self._draw_bounding_rect()

                self._calc_hand_position(hand_landmark)
                self._draw_centering_arrow()

            else:
                self.hand_position_changed.emit(None, None)

            self._draw_target_rect()

    @property
    def image_size(self):
        if self.cv_image is not None:
            return int(round(self.cv_image.shape[1])), int(round(self.cv_image.shape[0]))

    def _calc_bounding_rect(self, landmarks):
        # image_width, image_height = self.cv_image.shape[1], self.cv_image.shape[0]

        landmark_array = np.empty((0, 2), int)

        for _, landmark in enumerate(landmarks.landmark):
            landmark_x = min(int(landmark.x * self.image_size[0]), self.image_size[0] - 1)
            landmark_y = min(int(landmark.y * self.image_size[1]), self.image_size[1] - 1)

            landmark_point = [np.array((landmark_x, landmark_y))]

            landmark_array = np.append(landmark_array, landmark_point, axis=0)

        x, y, w, h = cv.boundingRect(landmark_array)

        self.bounding_rectangle = [x, y, x + w, y + h]

        # self.bounding_rectangle_changed.emit()

        # return [x, y, x + w, y + h]

    def _draw_bounding_rect(self):
        cv.rectangle(
            img=self.cv_image,
            pt1=(self.bounding_rectangle[0], self.bounding_rectangle[1]),
            pt2=(self.bounding_rectangle[2], self.bounding_rectangle[3]),
            color=(0, 0, 0),
            thickness=2
        )

        cv.line(
            img=self.cv_image,
            pt1=(self.bounding_rectangle[0], self.bounding_rectangle[1]),
            pt2=(self.bounding_rectangle[2], self.bounding_rectangle[3]),
            color=(0, 0, 0),
            thickness=2
        )

        cv.line(
            img=self.cv_image,
            pt1=(self.bounding_rectangle[2], self.bounding_rectangle[1]),
            pt2=(self.bounding_rectangle[0], self.bounding_rectangle[3]),
            color=(0, 0, 0),
            thickness=2
        )

    def _calc_hand_position(self, hand_landmark):
        # image_width, image_height = self.cv_image.shape[1], self.cv_image.shape[0]

        x0, y0, x1, y1 = self.bounding_rectangle

        hand_width = x1 - x0
        hand_height = y1 - y0

        delta_x = int(round(x0 + hand_width/2 - self.image_size[0]/2))
        delta_y = int(round( (y0 + hand_height/2 - self.image_size[1]/2) * -1 ))

        self.hand_position = (delta_x, delta_y, hand_width, hand_height)

        self.hand_position_changed.emit(self.hand_position, hand_landmark)

    def _draw_centering_arrow(self):
        center_p = (int(self.image_size[0]/2)+self.hand_position[0], int(self.image_size[1]/2)-self.hand_position[1])

        cv.arrowedLine(
            img=self.cv_image,
            pt1=center_p,
            pt2=(int(self.image_size[0]/2), int(self.image_size[1]/2)),
            color=(255, 0, 0),
            thickness=2
        )

    def _draw_target_rect(self):
        if self.target_rect_size:

            pt1 = (
                int(round(self.image_size[0]/2 - self.target_rect_size[0]/2)),
                int(round(self.image_size[1] / 2 - self.target_rect_size[1] / 2))
            )

            pt2 = (
                int(round(self.image_size[0] / 2 + self.target_rect_size[0] / 2)),
                int(round(self.image_size[1] / 2 + self.target_rect_size[1] / 2))
            )

            cv.rectangle(
                img=self.cv_image,
                pt1=pt1,
                pt2=pt2,
                color=(0, 255, 0),
                thickness=1
            )

    def handle_image(self):
        self.detect_hand()

