
from PyQt5 import QtCore, QtWidgets, QtGui

from collections import deque
import cv2 as cv


class CvFpsCalc(object):
    def __init__(self, buffer_len=1):
        self._start_tick = cv.getTickCount()
        self._freq = 1000.0 / cv.getTickFrequency()
        self._difftimes = deque(maxlen=buffer_len)

    def get(self):
        current_tick = cv.getTickCount()
        different_time = (current_tick - self._start_tick) * self._freq
        self._start_tick = current_tick

        self._difftimes.append(different_time)

        fps = 1000.0 / (sum(self._difftimes) / len(self._difftimes))
        fps_rounded = round(fps, 2)

        return fps_rounded


class DroneVideoCaptureThread(QtCore.QThread):

    # change_pixmap_signal = QtCore.pyqtSignal(np.ndarray)
    change_pixmap_signal = QtCore.pyqtSignal()

    def __init__(self, camera_widget):
        super(DroneVideoCaptureThread, self).__init__()

        self.camera_widget = camera_widget
        self.cap = cv.VideoCapture(0)
        # self.cap = cv.VideoCapture(0, cv.CAP_DSHOW)

    def run(self):
        # print('STARTING CAMERA')
        while True:
            success, cv_image = self.cap.read()
            if success:
                fps = self.cap.get(cv.CAP_PROP_FPS)
                self.camera_widget.cv_image = cv.flip(cv_image, 1)
                self.camera_widget.handle_image()
                # self.change_pixmap_signal.emit(cv_image)
                self.change_pixmap_signal.emit()
                # time.sleep(0.1)

    def release(self):
        self.cap.release()


class VideoCaptureThread(QtCore.QThread):

    # change_pixmap_signal = QtCore.pyqtSignal(np.ndarray)
    change_pixmap_signal = QtCore.pyqtSignal()

    def __init__(self, camera_widget):
        super(VideoCaptureThread, self).__init__()

        self.camera_widget = camera_widget
        self.cap = cv.VideoCapture(0)
        # self.cap = cv.VideoCapture(0, cv.CAP_DSHOW)

    def run(self):
        # print('STARTING CAMERA')
        while True:
            success, cv_image = self.cap.read()
            if success:
                fps = self.cap.get(cv.CAP_PROP_FPS)
                self.camera_widget.cv_image = cv.flip(cv_image, 1)
                self.camera_widget.handle_image()
                # self.change_pixmap_signal.emit(cv_image)
                self.change_pixmap_signal.emit()
                # time.sleep(0.1)

    def release(self):
        self.cap.release()


class TelloCameraWidget(QtWidgets.QLabel):

    fps_count = QtCore.pyqtSignal(float)

    def __init__(self):
        super(TelloCameraWidget, self).__init__()

        # self.setFixedSize(500, 500)
        # self.cv_image = None
        # self.qt_image = None

        self.display_width = 640
        # self.display_height = 480

        self.video_thread = VideoCaptureThread(camera_widget=self)

        self.cv_fps_calc = CvFpsCalc(buffer_len=10)

        self.video_thread.change_pixmap_signal.connect(self.update_image)
        self.video_thread.start()

    def handle_image(self):
        raise NotImplementedError

    def convert_image(self):
        rgb_image = cv.cvtColor(self.cv_image, cv.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        qt_format = QtGui.QImage(rgb_image.data, w, h, bytes_per_line, QtGui.QImage.Format_RGB888)
        pixmap = qt_format.scaledToWidth(self.display_width)
        return QtGui.QPixmap.fromImage(pixmap)

    @QtCore.pyqtSlot()
    def update_image(self):

        fps = self.cv_fps_calc.get()
        self.fps_count.emit(fps)


        # self.cv_image = cv_image

        # self.handle_image(cv_image)

        # _, _, _ = detect_hands(cv_image)

        # if self.cv_image is not None:
        # qt_image = self.convert_image()
        # time.sleep(0.1)

        self.setPixmap(self.convert_image())    # cv_image converted to qt_image

