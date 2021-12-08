from google.protobuf.json_format import MessageToDict
import copy
import itertools


def pre_process_landmark(landmark_list):
    temp_landmark_list = copy.deepcopy(landmark_list)

    # Convert to relative coordinates
    base_x, base_y = 0, 0
    for index, landmark_point in enumerate(temp_landmark_list):
        if index == 0:
            base_x, base_y = landmark_point[0], landmark_point[1]

        temp_landmark_list[index][0] = temp_landmark_list[index][0] - base_x
        temp_landmark_list[index][1] = temp_landmark_list[index][1] - base_y

    # Convert to a one-dimensional list
    temp_landmark_list = list(
        itertools.chain.from_iterable(temp_landmark_list))

    # Normalization
    max_value = max(list(map(abs, temp_landmark_list)))

    def normalize_(n):
        return n / max_value

    temp_landmark_list = list(map(normalize_, temp_landmark_list))

    return temp_landmark_list


class HandHandler:

    def __init__(self, hand_landmarks=None):

        self.hand_landmarks = hand_landmarks
        self.left_hand_mark = None
        self.right_hand_mark = None

    def hand_landmarks_change(self, hand_landmarks, handedness, cv_image):

        self.hand_landmarks = hand_landmarks
        self.handedness = handedness
        self.image = cv_image   # should be removed, HandHandler does not need the image, only image size

        self.sort_hands()

    def sort_hands(self):
        """not great, must be refactored"""

        if self.hand_landmarks is None:
            self.right_hand_mark = None
            self.left_hand_mark = None

            return

        if len(self.hand_landmarks) == 1:
            if MessageToDict(self.handedness[0])['classification'][0]['label'] == 'Right':
                self.right_hand_mark = self.hand_landmarks[0]
                self.left_hand_mark = None
            else:
                self.right_hand_mark = None
                self.left_hand_mark = self.hand_landmarks[0]

        else:
            for hand_landmark, handedness in zip(self.hand_landmarks, self.handedness):
                handedness = MessageToDict(handedness)['classification'][0]['label']

                if handedness == 'Right':
                    self.right_hand_mark = hand_landmark

                if handedness == 'Left':
                    self.left_hand_mark = hand_landmark

    # @property
    def get_preprocessed_landmark_list(self):

        left_pre_processed_landmark_list = [0] * 42
        right_pre_processed_landmark_list = [0] * 42

        left_landmark_list = self.calc_landmark('Left')
        right_landmark_list = self.calc_landmark('Right')

        if left_landmark_list:
            left_pre_processed_landmark_list = pre_process_landmark(left_landmark_list)
        if right_landmark_list:
            right_pre_processed_landmark_list = pre_process_landmark(right_landmark_list)

        left_pre_processed_landmark_list.extend(right_pre_processed_landmark_list)
        landmark_list = left_pre_processed_landmark_list
        return landmark_list

        # return left_pre_processed_landmark_list.extend(right_pre_processed_landmark_list)

    def calc_landmark(self, hand):

        if hand == 'Left':
            return self.calc_landmark_list(self.left_hand_mark)
        if hand == 'Right':
            return self.calc_landmark_list(self.right_hand_mark)

    def calc_landmark_list(self, landmarks):

        if not landmarks:
            return None

        image_height, image_width, _ = self.image.shape

        landmark_point = []

        # Keypoint
        for _, landmark in enumerate(landmarks.landmark):
            landmark_x = min(int(landmark.x * image_width), image_width - 1)
            landmark_y = min(int(landmark.y * image_height), image_height - 1)
            # landmark_z = landmark.z

            landmark_point.append([landmark_x, landmark_y])

        return landmark_point






