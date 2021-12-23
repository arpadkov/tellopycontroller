from tello_controllers.rc_controls import GeneralCommand

from PyQt5 import QtCore, QtWidgets, QtGui


class CommandButtonsWidget(QtWidgets.QWidget):

    general_command_signal = QtCore.pyqtSignal(GeneralCommand)

    def __init__(self):
        super(CommandButtonsWidget, self).__init__()

        self.layout = QtWidgets.QVBoxLayout()

        self.command_buttons = []

        for command in GeneralCommand:
            self.command_buttons.append(CommandButton(command))

        for button in self.command_buttons:
            self.layout.addWidget(button)
            button.general_command_signal.connect(self.emit_command)

        self.setLayout(self.layout)

    def emit_command(self, command: GeneralCommand):
        self.general_command_signal.emit(command)


class CommandButton(QtWidgets.QPushButton):

    general_command_signal = QtCore.pyqtSignal(GeneralCommand)

    def __init__(self, command: GeneralCommand):
        super(CommandButton, self).__init__()

        self.command = command

        self.setText(command.name)

        self.clicked.connect(self.button_clicked)

    def button_clicked(self):
        self.general_command_signal.emit(self.command)





