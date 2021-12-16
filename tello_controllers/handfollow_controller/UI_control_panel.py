from PyQt5 import QtCore, QtWidgets


class HandFollowControlPanel(QtWidgets.QWidget):

    start_following = QtCore.pyqtSignal()
    stop_following = QtCore.pyqtSignal()

    def __init__(self):
        super(HandFollowControlPanel, self).__init__()

        self.layout = QtWidgets.QGridLayout()

        self.follow_button = QtWidgets.QPushButton('Follow!')
        self.follow_button.clicked.connect(self.follow_button_pressed)

        self.stop_button = QtWidgets.QPushButton('Stop!')
        self.stop_button.clicked.connect(self.stop_button_pressed)

        self.layout.addWidget(self.follow_button)
        self.layout.addWidget(self.stop_button)

        self.setLayout(self.layout)

    def follow_button_pressed(self):
        self.start_following.emit()

    def stop_button_pressed(self):
        self.stop_following.emit()
