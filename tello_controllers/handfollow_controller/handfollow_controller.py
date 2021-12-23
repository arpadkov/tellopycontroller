from tello_controllers.tello_controller import TelloRcController
from tello_controllers.handfollow_controller.UI_camera_widget import HandFollowControlCamera
from tello_controllers.handfollow_controller.UI_control_panel import HandFollowControlPanel
from tello_controllers.handfollow_controller.follower_thread import FollowControlsThread


class HandFollowController(TelloRcController):

    def __init__(self, lateral_speed, yaw_speed):
        super(HandFollowController, self).__init__(lateral_speed, yaw_speed)

        self.control_panel = HandFollowControlPanel()
        self.control_panel.start_following.connect(self.start_control_thread)
        self.control_panel.stop_following.connect(self.stop_control_thread)

        self.camera = HandFollowControlCamera(self.drone)
        self.camera.hand_position_changed.connect(self.set_hand_position)

        self.control_follow_thread = FollowControlsThread(self, threshold=5)
        # self.control_follow_thread.start()

        self.hand_landmark = None
        self.hand_position = None           # (delta_x, delta_y, w, h)
        self.hand_base_size = None          # (w, h)

        self.ui_widget.layout.addWidget(self.camera)
        self.ui_widget.layout.addWidget(self.control_panel)

    def on_tello_takeoff(self):
        pass

    def on_tello_land(self):
        self.stop_control_thread()

    def set_hand_position(self, hand_position, hand_landmark):
        self.hand_position = hand_position
        self.hand_landmark = hand_landmark

    def start_control_thread(self):

        if self.hand_position:

            self.hand_base_size = (self.hand_position[2], self.hand_position[3])
            self.camera.target_rect_size = self.hand_base_size

            self.control_follow_thread.start()

            # print(self.hand_base_size)

        else:
            print('no hand found')

    def stop_control_thread(self):
        self.control_follow_thread.terminate()
        self.set_speed_from_rc_controls([])
        self.hand_base_size = None
        self.camera.target_rect_size = None

    def finish_threads(self):

        self.control_follow_thread.terminate()
