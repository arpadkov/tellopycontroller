from tello_controllers.UI_camera_widget import TelloCameraWidget


class KeyboardControlCamera(TelloCameraWidget):

    def __init__(self, drone):
        super(KeyboardControlCamera, self).__init__(drone)

    def handle_image(self):
        pass

