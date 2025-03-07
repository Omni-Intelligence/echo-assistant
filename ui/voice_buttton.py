from PyQt6.QtWidgets import QPushButton
from PyQt6.QtCore import Qt, QPropertyAnimation
from PyQt6.QtGui import QPainter, QColor

class AssistantButton(QPushButton):
    def __init__(self):
        super().__init__()
        self.setFixedSize(100, 100)
        self.setStyleSheet("border-radius: 50px; background-color: #2196F3;")
        self._animation = QPropertyAnimation(self, b"size")
        self._is_recording = False

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        if self._is_recording:
            color = QColor("#F44336")
        else:
            color = QColor("#2196F3")
            
        painter.setBrush(color)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(self.rect())

    def set_recording(self, is_recording):
        self._is_recording = is_recording
        self.update()