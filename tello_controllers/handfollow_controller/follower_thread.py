from tello_controllers.rc_controls import RcControl

from PyQt5 import QtCore

import time


class FollowControlsThread(QtCore.QThread):

    def __init__(self, controller, threshold: int):
        super(FollowControlsThread, self).__init__()

        self.controller = controller
        self.threshold = threshold

    def get_vertical_control(self):
        delta_y = self.controller.hand_position[1]

        if delta_y > self.threshold*2:
            return RcControl.Up

        elif delta_y < -self.threshold*2:
            return RcControl.Down

    def get_yaw_control(self):
        delta_x = self.controller.hand_position[0]

        if delta_x > self.threshold:
            return RcControl.RotateLeft

        elif delta_x < -self.threshold:
            return RcControl.RotateRight

    def get_horizontal_front_control(self):

        frontal_height_difference = self.controller.hand_position[3] / self.controller.hand_base_size[1]

        if frontal_height_difference > 1.05:
            return RcControl.Backward

        elif frontal_height_difference < 0.95:
            return RcControl.Forward

    def get_horizontal_side_control(self):

        hand_landmark = self.controller.hand_landmark

        # side_difference = self.controller.hand_position[2] / self.controller.hand_base_size[0]

        thumb_z = hand_landmark.landmark[4].z
        pinky_z = hand_landmark.landmark[20].z

        side_difference = thumb_z / pinky_z

        # print(side_difference)

        if side_difference > 1.2:
            return RcControl.Left

        elif side_difference < 0.8:
            return RcControl.Right

        # for point in hand_landmark.landmark:
        #     print(point.x)

    def run(self):
        while True:
            active_rc_controls = []
            # print('running')

            if self.controller.hand_position:

                active_rc_controls.append(self.get_vertical_control())
                active_rc_controls.append(self.get_yaw_control())
                active_rc_controls.append(self.get_horizontal_front_control())
                # active_rc_controls.append(self.get_horizontal_side_control())

                # print(self.controller.hand_position[0], self.controller.hand_position[1])

            self.controller.set_speed_from_rc_controls(active_rc_controls)

            time.sleep(0.1)

