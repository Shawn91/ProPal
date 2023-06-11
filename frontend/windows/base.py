from PySide6.QtCore import Qt
from PySide6.QtGui import QMouseEvent
from PySide6.QtWidgets import QWidget


class FramelessWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setMouseTracking(True)
        self.mouse_pos = None

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            # Capture the current mouse position
            self.mouse_pos = event.globalPos() - self.pos()
            event.accept()

    def mouseMoveEvent(self, event: QMouseEvent):
        if event.buttons() == Qt.LeftButton:
            # Calculate the new position of the window
            new_pos = event.globalPos() - self.mouse_pos
            self.move(new_pos)
            event.accept()
