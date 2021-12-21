from PyQt5 import QtGui, QtWidgets, QtCore
import logging
import os


class GUILogging(QtWidgets.QMainWindow):

    def __init__(self, *args):
        """
        Simple QtGui.QTextEdit extension that can be used as output stream for logging.
        Error Messages are marked red.
        """

        super(GUILogging, self).__init__(*args)

        self.text_widget = QtWidgets.QTextEdit()
        self.setCentralWidget(self.text_widget)

        self.text_widget.setReadOnly(True)

        fmt = logging.Formatter('%(asctime)s === %(name)s ===\n%(levelname)s: %(message)s\n', "%H:%M:%S")

        stream_handler = logging.StreamHandler(stream=self)
        stream_handler.setFormatter(fmt)
        stream_handler.setLevel(logging.INFO)

        logging.getLogger('djitellopy').addHandler(stream_handler)
        logging.getLogger('Tello controller').addHandler(stream_handler)
        logging.getLogger('keyboard_controller').addHandler(stream_handler)
        #logging.getLogger().addHandler(stream_handler)

        self.color_default = QtGui.QColor(0, 0, 0)
        self.color_warning = QtGui.QColor(255, 0, 0)
        self.color_error = QtGui.QColor(255, 0, 0)

        self.setMinimumWidth(400)

        self.create_toolbar()

    def create_toolbar(self):

        self.clear_logging_action = QtWidgets.QAction(
            QtGui.QIcon(os.path.join(os.getcwd(), 'GUI', 'icons', 'clear.png')), 'Clear', self)
        self.clear_logging_action.triggered.connect(self.on_clear_logging)
        self.clear_logging_action.setIconText('Clear')
        self.clear_logging_action.setToolTip('Clear logging')

        # self.debug_logging_action = QtWidgets.QAction(
        #     QtGui.QIcon(os.path.join(os.path.dirname(__file__), 'icons', 'debug.png')), 'Debug', self, checkable=True)

        # self.debug_logging_action = QtWidgets.QAction(QtGui.QIcon(
        #     os.path.join(os.getcwd(), 'GUI', 'icons', 'clear.png')),
        #     'Clear',
        #     self,
        #     checkable=True
        # )

        self._logging_tools = QtWidgets.QToolBar()
        self._logging_tools.addAction(self.clear_logging_action)
        # self._logging_tools.addAction(self.debug_logging_action)
        self._logging_tools.setIconSize(QtCore.QSize(16, 16))
        self.addToolBar(QtCore.Qt.LeftToolBarArea, self._logging_tools)

        self._logging_tools.setMovable(False)

    def write(self, m):
        if m.find('ERROR') >= 0 or m.find('CRITICAL') >= 0:
            text_color = self.color_error
        elif m.find('WARNING') >= 0 or m.find('CRITICAL') >= 0:
            text_color = self.color_warning
        else:
            text_color = self.color_default

        self.text_widget.moveCursor(QtGui.QTextCursor.End)
        cursor = self.text_widget.textCursor()

        text_format = QtGui.QTextCharFormat()
        text_format.setFont(QtGui.QFont("Courier", 8))
        text_format.setForeground(QtGui.QBrush(text_color))

        cursor.setCharFormat(text_format)
        cursor.insertText(m)

    @QtCore.pyqtSlot()
    def on_clear_logging(self):
        self.text_widget.clear()
