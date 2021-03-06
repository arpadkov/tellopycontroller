from tello_controllers.rc_controls import RcControl

from PyQt5 import QtCore, QtWidgets, QtGui

import os


class KeyboardControlPanel(QtWidgets.QWidget):

    def __init__(self):
        super(KeyboardControlPanel, self).__init__()

        self.control_buttons = []

        self.layout = QtWidgets.QGridLayout()

        self.up_button = ArrowButton(RcControl.Up, QtCore.Qt.Key_Shift, (0, 1), self)
        self.down_button = ArrowButton(RcControl.Down, QtCore.Qt.Key_Control, (3, 1), self)
        self.forward_button = ArrowButton(RcControl.Forward, QtCore.Qt.Key_W, (1, 1), self)
        self.backward_button = ArrowButton(RcControl.Backward, QtCore.Qt.Key_S, (2, 1), self)
        self.left_button = ArrowButton(RcControl.Left, QtCore.Qt.Key_A, (2, 0), self)
        self.right_button = ArrowButton(RcControl.Right, QtCore.Qt.Key_D, (2, 2), self)
        self.rotate_left_button = ArrowButton(RcControl.RotateLeft, QtCore.Qt.Key_Q, (1, 0), self)
        self.rotate_right_button = ArrowButton(RcControl.RotateRight, QtCore.Qt.Key_E, (1, 2), self)

        self.test_shortcut = QtWidgets.QShortcut(QtGui.QKeySequence('Left'), self)
        self.test_shortcut.activated.connect(self.shortcut)

        self.setFixedSize(300, 300)

        self.setLayout(self.layout)

    def shortcut(self):
        print('hey')

    def keyPressEvent(self, event: QtGui.QKeyEvent) -> None:
        """
        if a key is held down, it is interpreted as repeatedly pressing,
        so keyPress and keyRelease are called repeatedly
        """

        for control_button in self.control_buttons:
            if event.key() == control_button.key:
                # print('setting true')
                control_button.active = True
                control_button.setChecked(True)

    def keyReleaseEvent(self, event: QtGui.QKeyEvent) -> None:

        for control_button in self.control_buttons:
            if event.key() == control_button.key:
                # print('setting false')
                control_button.active = False
                control_button.setChecked(False)


class ArrowButton(QtWidgets.QPushButton):

    # button_click = QtCore.pyqtSignal(object)

    def __init__(self, rc_control: RcControl, key: QtCore.Qt.Key, grid_position, parent: KeyboardControlPanel):
        super().__init__()

        self.rc_control = rc_control
        self.key = key
        self.row_position, self.column_position = grid_position
        self.parent = parent

        self.setFixedSize(50, 50)

        self.active = False

        # self.size = QtCore.QSize(60, 60)
        # self.setFixedSize(self.size)

        self.icon = QtGui.QIcon(os.path.join(os.getcwd(), 'GUI', 'icons', 'arrows', f'arrow_{self.rc_control.name}.png'))
        # self.setIconSize(self.size * 0.9)
        self.setIcon(self.icon)

        # self.setFlat(True)
        self.setCheckable(True)

        self.pressed.connect(self.button_pressed)
        self.released.connect(self.button_released)

        self.parent.layout.addWidget(self, self.row_position, self.column_position)
        self.parent.control_buttons.append(self)

    def button_pressed(self):
        self.active = True

    def button_released(self):
        self.active = False
        self.setChecked(False)

