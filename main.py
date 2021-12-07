from tellopycontroller.GUI.cam_widget import CameraWidget
from tellopycontroller.hand_handler import HandHandler
from tellopycontroller.gesture_data.gestures import Gesture
from tellopycontroller.tello_controller.keyboard_controller import KeyboardController

from PyQt5 import QtCore, QtWidgets, QtGui

import tensorflow as tf
import sys
import os
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

        # self.camera_widget = CameraWidget()

        self.handler = HandHandler()

        self.controller_widget = KeyboardController()

        # self.prediction_thread = PredictionThread(self)

        # self.camera_widget.change_hand_landmarks.connect(self.handler.hand_landmarks_change)

        self.info_panel = InfoPanel()

        self.layout.addWidget(self.info_panel)

        # self.layout.addWidget(self.camera_widget)

        self.layout.addWidget(self.controller_widget)

        # self.prediction_thread.start()

        window = QtWidgets.QWidget()
        window.setLayout(self.layout)
        self.setCentralWidget(window)


class InfoPanel(QtWidgets.QWidget):

    def __init__(self):
        super(InfoPanel, self).__init__()

        # self.drone_command_visual = DroneCommandVisual()

        self.layout = QtWidgets.QGridLayout()





        # self.layout.addWidget(self.drone_command_visual, 0, 0)

        self.setLayout(self.layout)



class DroneCommandVisual(QtWidgets.QWidget):

    def __init__(self):
        super(DroneCommandVisual, self).__init__()

        self.icon_name = QtGui.QPixmap(os.path.join(os.getcwd(), 'GUI', 'icons', 'arrows', f'arrow_up.png'))

        self.setPixmap(self.icon_name)

        self.setScaledContents(True)

        self.setFixedSize(50, 50)





if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
