from tello_controllers.gesture_controller.gesture_data.gestures import Gesture

from PyQt5 import QtCore

import numpy as np
import tensorflow as tf
import os


class PredictionThread(QtCore.QThread):

    gesture_changed = QtCore.pyqtSignal(Gesture, object)
    no_gesture_recognized = QtCore.pyqtSignal()

    def __init__(self, handler, keras_model_dir):
        super(PredictionThread, self).__init__()

        self.handler = handler
        self.keras_model = tf.keras.models.load_model(keras_model_dir)

    def run(self):

        # model_dir = os.path.join(os.getcwd(), 'tello_controllers', 'gesture_controller', 'keras_gesture_model')
        # keras_model = tf.keras.models.load_model(model_dir)

        while True:
            pre_processed_landmark_list = self.handler.get_preprocessed_landmark_list()

            prediction = self.keras_model.predict(np.array([pre_processed_landmark_list]))
            gesture_id = np.argmax(prediction)

            if np.amax(prediction) > 0.8:
                gesture = Gesture(gesture_id)
                self.gesture_changed.emit(gesture, prediction)
                # print(f'{gesture.name} - {round(np.amax(prediction) * 100, 2)} %')
            else:
                self.no_gesture_recognized.emit()