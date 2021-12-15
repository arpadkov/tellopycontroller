from tello_controllers.tello_controller import TelloRcController
from tello_controllers.gesture_controller.UI_camera_widget import GestureControlCamera
from tello_controllers.gesture_controller.UI_control_panel import GestureControlPanel, GestureLogger
from tello_controllers.gesture_controller.prediction_thread import PredictionThread
from tello_controllers.gesture_controller.hand_handler import HandHandler
from tello_controllers.gesture_controller.gesture_data.gestures import Gesture
from tello_controllers.rc_controls import RcControl

from PyQt5 import QtCore, QtWidgets


class GestureController(TelloRcController):

    def __init__(self):
        super(GestureController, self).__init__()

        self.camera = GestureControlCamera()

        self.hand_handler = HandHandler()

        self.logger = GestureLogger(self.hand_handler)

        self.control_panel = GestureControlPanel(self.logger)

        self.control_panel.start_controlling.connect(self.start_controlling)
        self.control_panel.stop_controlling.connect(self.stop_controlling)
        self.control_panel.start_logging.connect(self.logger.start_logging)

        self.prediction_thread = PredictionThread(self.hand_handler)

        self.camera.hand_landmarks_changed.connect(self.hand_handler.hand_landmarks_change)

        self.prediction_thread.gesture_changed.connect(self.translate_gesture)
        self.prediction_thread.no_gesture_recognized.connect(self.zero_rc_controls)

        self.ui_widget.layout.addWidget(self.camera)
        self.ui_widget.layout.addWidget(self.control_panel)

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

    def start_controlling(self):
        self.prediction_thread.start()

    def stop_controlling(self):
        self.prediction_thread.terminate()

    def finish_threads(self):
        self.prediction_thread.terminate()







