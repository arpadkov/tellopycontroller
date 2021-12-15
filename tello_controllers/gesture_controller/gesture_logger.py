from tello_controllers.gesture_controller.gesture_data.gestures import Gesture

from PyQt5 import QtCore, QtWidgets

import time
import os
import csv
import cv2 as cv


def log_to_csv(number, land_list, csv_file):

    with open(csv_file, 'a', newline="") as f:
        writer = csv.writer(f)
        writer.writerow([number, *land_list])


class LogThreadPulse(QtCore.QThread):

    write_time = QtCore.pyqtSignal(int)
    finished_logging = QtCore.pyqtSignal()

    def __init__(self, datapoints, sleep_time, wait_time):
        super(LogThreadPulse, self).__init__()

        self.datapoints = datapoints
        self.sleep_time = sleep_time
        self.wait_time = wait_time

    def run(self):

        for remaining in range(self.wait_time):
            print(f'Recording starts in {self.wait_time - remaining} seconds ...')
            time.sleep(1)

        # point = 0
        #
        # while point < self.datapoints:
        #
        #     self.write_time.emit(point)
        #
        #     time.sleep(self.sleep_time)
        #
        #     point += 1

        for point in range(self.datapoints):
            self.write_time.emit(point)
            time.sleep(self.sleep_time)

        self.finished_logging.emit()


class GestureLogger:

    def __init__(self, hand_handler, gesture_dataset_dir):

        self.hand_handler = hand_handler

        self.gesture = Gesture.Up
        self.clear_data = False

        self.gesture_dataset_dir = gesture_dataset_dir
        self.csv_file = None

        self.datapoints = 20

        self.timer_thread = LogThreadPulse(self.datapoints, 0.2, 3)
        self.timer_thread.write_time.connect(self.log_datapoint)

    def start_logging(self):

        # self.index = self.control_panel.gesture_selector.currentIndex()
        # self.gesture = self.control_panel.gesture_selector.options[self.index]

        self.csv_file = os.path.join(self.gesture_dataset_dir, self.gesture.name.capitalize() + '.csv')

        # clear = self.control_panel.clear_checkbox.checkState()

        if self.clear_data:
            os.remove(self.csv_file)

        self.timer_thread.start()

    def log_datapoint(self, point):
        # print('LOGGING')

        if point == 1:
            cv.imwrite(os.path.join(self.gesture_dataset_dir, self.gesture.name.capitalize()+'.png'), self.hand_handler.image)

        print(f'Logged point {point + 1}/{self.datapoints}')

        pre_processed_landmark_list = self.hand_handler.get_preprocessed_landmark_list()

        log_to_csv(
            number=self.gesture.value,
            land_list=pre_processed_landmark_list,
            csv_file=self.csv_file
        )

