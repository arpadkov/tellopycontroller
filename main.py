from tellopycontroller.GUI.cam_widget import CameraWidget
from tellopycontroller.hand_handler import HandHandler
from tellopycontroller.gesture_data.gestures import Gesture
from tellopycontroller.tello_controller.keyboard_controller import KeyboardController

from PyQt5 import QtCore, QtWidgets

import tensorflow as tf
import sys
import numpy as np


class PredictionThread(QtCore.QThread):

    def __init__(self, parent):
        super(PredictionThread, self).__init__()

        self.parent = parent

    def run(self):

        model = tf.keras.models.load_model('keras_gesture_model')

        while True:
            pre_processed_landmark_list = self.parent.handler.get_preprocessed_landmark_list()

            prediction = model.predict(np.array([pre_processed_landmark_list]))
            gesture_id = np.argmax(prediction)

            if np.amax(prediction) > 0.8:
                gesture = Gesture(gesture_id)
                print(f'{gesture.name} - {round(np.amax(prediction)*100, 2)} %')


class MainWindow(QtWidgets.QMainWindow):

    def __init__(self):
        super(MainWindow, self).__init__()

        self.layout = QtWidgets.QHBoxLayout()

        self.camera_widget = CameraWidget()

        self.handler = HandHandler()

        self.controller = KeyboardController()

        self.prediction_thread = PredictionThread(self)

        self.camera_widget.change_hand_landmarks.connect(self.handler.hand_landmarks_change)

        self.layout.addWidget(self.camera_widget)
        self.layout.addWidget(self.controller.control_panel)

        self.prediction_thread.start()

        window = QtWidgets.QWidget()
        window.setLayout(self.layout)
        self.setCentralWidget(window)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
