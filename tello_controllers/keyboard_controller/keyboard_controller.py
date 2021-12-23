from tello_controllers.tello_controller import TelloRcController
from tello_controllers.keyboard_controller.UI_control_panel import KeyboardControlPanel
from tello_controllers.keyboard_controller.UI_camera_widget import KeyboardControlCamera

from PyQt5 import QtCore

import time
import logging

logger = logging.getLogger('Keyboard controller')


class KeyboardController(TelloRcController):

    def __init__(self, lateral_speed, yaw_speed):
        super(KeyboardController, self).__init__(lateral_speed, yaw_speed)

        self.control_panel = KeyboardControlPanel()

        self.camera = KeyboardControlCamera(self.drone)

        self.control_read_thread = ControlsReadThread(self)
        self.control_read_thread.start()

        self.ui_widget.layout.addWidget(self.camera)
        self.ui_widget.layout.addWidget(self.control_panel)

        # self.ui_widget.setFixedWidth(800)

    def finish_threads(self):

        self.control_read_thread.terminate()


class ControlsReadThread(QtCore.QThread):

    def __init__(self, controller: KeyboardController):
        super(ControlsReadThread, self).__init__()

        self.controller = controller

    def run(self):

        while True:

            active_rc_controls = []
            for control_button in self.controller.control_panel.control_buttons:
                if control_button.active:
                    active_rc_controls.append(control_button.rc_control)

            # print(active_rc_controls)
            self.controller.set_speed_from_rc_controls(active_rc_controls)

            time.sleep(0.1)





