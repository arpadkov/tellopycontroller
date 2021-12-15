from tello_controllers.tello_controller import TelloRcController
from tello_controllers.gesture_controller.UI_camera_widget import GestureControlCamera
from tello_controllers.gesture_controller.UI_control_panel import GestureControlPanel, GestureLogger
from tello_controllers.gesture_controller.model_trainer import GestureModelTrainer
from tello_controllers.gesture_controller.prediction_thread import PredictionThread
from tello_controllers.gesture_controller.hand_handler import HandHandler
from tello_controllers.gesture_controller.gesture_data.gestures import Gesture
from tello_controllers.rc_controls import RcControl

import os
from enum import Enum


class GestureControllerState(Enum):

    Waiting = 1
    Controlling = 2
    Logging = 3


class GestureController(TelloRcController):

    def __init__(self):
        super(GestureController, self).__init__()

        self.gesture_dataset_dir =\
            os.path.join(os.getcwd(), 'tello_controllers', 'gesture_controller', 'gesture_data')

        self.keras_model_dir =\
            os.path.join(os.getcwd(), 'tello_controllers', 'gesture_controller', 'keras_gesture_model')



        self.camera = GestureControlCamera()

        self.hand_handler = HandHandler()

        self.logger = GestureLogger(self.hand_handler, self.gesture_dataset_dir)
        self.logger.timer_thread.finished_logging.connect(self.finished_logging)

        self.gesture_model_trainer = GestureModelTrainer(self.gesture_dataset_dir, self.keras_model_dir)
        self.gesture_model_trainer.training_finished.connect(self.gesture_training_finished)

        self.control_panel = GestureControlPanel(self.logger)

        self.control_panel.start_controlling.connect(self.start_controlling)
        self.control_panel.stop_controlling.connect(self.stop_controlling)
        self.control_panel.start_logging.connect(self.start_logging)

        self.control_panel.train_model_signal.connect(self.train_gesture_model)

        self.state = GestureControllerState.Waiting

        self.camera.hand_landmarks_changed.connect(self.hand_handler.hand_landmarks_change)

        self.ui_widget.layout.addWidget(self.camera)
        self.ui_widget.layout.addWidget(self.control_panel)

        self.create_prediction_thread()

    def create_prediction_thread(self):
        self.prediction_thread = PredictionThread(self.hand_handler, self.keras_model_dir)

        self.prediction_thread.gesture_changed.connect(self.translate_gesture)
        self.prediction_thread.no_gesture_recognized.connect(self.zero_rc_controls)

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

    def start_logging(self):
        self.prediction_thread.terminate()
        self.logger.start_logging()

        self.state = GestureControllerState.Logging

    def finished_logging(self):
        self.state = GestureControllerState.Waiting

    def start_controlling(self):
        self.create_prediction_thread()
        self.prediction_thread.start()

        self.state = GestureControllerState.Controlling

    def stop_controlling(self):
        self.prediction_thread.terminate()

        self.state = GestureControllerState.Waiting

    def train_gesture_model(self):
        self.prediction_thread.terminate()
        self.prediction_thread = None
        self.gesture_model_trainer.start()

    def gesture_training_finished(self):
        self.gesture_model_trainer.terminate()
        self.create_prediction_thread()

    def finish_threads(self):
        self.prediction_thread.terminate()

    def __setattr__(self, key, value):
        object.__setattr__(self, key, value)
        # setattr(self, key, value)

        if key == 'state':
            self.control_panel.set_status_label(self.state.name)








