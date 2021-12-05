from tellopycontroller.GUI.cam_widget import CameraWidget
from model_creator.control_panel import ControlPanel
from tellopycontroller.hand_handler import HandHandler
# from gesture_tellocontroll.model.gestures import Gesture

from PyQt5 import QtCore, QtWidgets

import time
import sys
import cv2 as cv
import csv
import os


def log_to_csv(number, land_list, csv_file):

    with open(csv_file, 'a', newline="") as f:
        writer = csv.writer(f)
        writer.writerow([number, *land_list])


class LogThreadPulse(QtCore.QThread):

    write_time = QtCore.pyqtSignal(int)

    def __init__(self, datapoints, sleep_time, wait_time):
        super(LogThreadPulse, self).__init__()

        self.datapoints = datapoints
        self.sleep_time = sleep_time
        self.wait_time = wait_time

    def run(self):

        for remaining in range(self.wait_time):
            print(f'Recording starts in {self.wait_time - remaining} seconds ...')
            time.sleep(1)

        point = 0

        while point < self.datapoints:

            self.write_time.emit(point)

            time.sleep(self.sleep_time)

            point += 1


class MainWindow(QtWidgets.QMainWindow):

    def __init__(self):
        super(MainWindow, self).__init__()

        self.layout = QtWidgets.QHBoxLayout()

        self.handler = HandHandler()

        self.csv_path = os.path.join(os.path.dirname(os.getcwd()), 'model')

        self.datapoints = 20
        self.timer_thread = LogThreadPulse(self.datapoints, 0.2, 3)
        self.timer_thread.write_time.connect(self.log_datapoint)

        self.camera_widget = CameraWidget()

        self.control_panel = ControlPanel()
        self.control_panel.start_logging.connect(self.start_logging)

        self.layout.addWidget(self.camera_widget)
        self.layout.addWidget(self.control_panel)

        self.camera_widget.change_hand_landmarks.connect(self.handler.hand_landmarks_change)

        window = QtWidgets.QWidget()
        window.setLayout(self.layout)
        self.setCentralWidget(window)

    def start_logging(self):

        self.index = self.control_panel.gesture_selector.currentIndex()
        self.gesture = self.control_panel.gesture_selector.options[self.index]

        self.csv_file = os.path.join(self.csv_path, self.gesture.name.capitalize() + '.csv')

        clear = self.control_panel.clear_checkbox.checkState()

        if clear:
            os.remove(self.csv_file)

        self.timer_thread.start()

    def log_datapoint(self, point):

        # index = self.control_panel.gesture_selector.currentIndex()
        # gesture = self.control_panel.gesture_selector.options[index]
        #
        # csv_file = os.path.join(self.csv_path, gesture.name.capitalize() + '.csv')
        #
        # clear = self.control_panel.clear_checkbox.checkState()

        if point == 1:
            cv.imwrite(os.path.join(self.csv_path, self.gesture.name.capitalize()+'.png'), self.handler.image)

        # left_pre_processed_landmark_list = [0] * 42
        # right_pre_processed_landmark_list = [0] * 42
        #
        # left_landmark_list = self.handler.calc_landmark('Left')
        # right_landmark_list = self.handler.calc_landmark('Right')
        #
        # if left_landmark_list:
        #     left_pre_processed_landmark_list = pre_process_landmark(left_landmark_list)
        # if right_landmark_list:
        #     right_pre_processed_landmark_list = pre_process_landmark(right_landmark_list)
        #
        # logged_left = ' Left ' if left_pre_processed_landmark_list != [0] * 42 else ''
        # logged_right = ' Right ' if right_pre_processed_landmark_list != [0] * 42 else ''
        # print(f'Datapoint {point+1}/{self.datapoints}: {logged_left + logged_right}')
        #
        # left_pre_processed_landmark_list.extend(right_pre_processed_landmark_list)

        print(f'Logged point {point+1}/{self.datapoints}')

        pre_processed_landmark_list = self.handler.get_preprocessed_landmark_list()

        log_to_csv(
            number=self.gesture.value,
            land_list=pre_processed_landmark_list,
            csv_file=self.csv_file
        )



if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
