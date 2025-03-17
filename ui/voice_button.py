from PyQt6.QtWidgets import QPushButton
from PyQt6.QtCore import Qt, QPropertyAnimation, QRectF
from PyQt6.QtGui import QPainter, QColor
from PyQt6.QtSvg import QSvgRenderer
from core.constants import COLORS
import os
import sys

class AssistantButton(QPushButton):
    def __init__(self):
        super().__init__()
        self.setFixedSize(120, 120)
        self.setStyleSheet(f"border-radius: 50px; background-color: {COLORS['primary']};")
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self._animation = QPropertyAnimation(self, b"size")
        self._is_recording = False
        self._is_processing = False
        self._is_answering = False
        self._is_hovered = False
        
        icon_path = os.path.join(os.path.dirname(__file__), "..", "resources")
        if getattr(sys, 'frozen', False):
            icon_path = os.path.join(sys._MEIPASS, "resources")
        self.icon_renderer = QSvgRenderer(os.path.join(icon_path, "microphone.svg"))

    def keyPressEvent(self, event):
        if (
            event.key() == Qt.Key.Key_Space
            and event.modifiers() & Qt.KeyboardModifier.ControlModifier
            and not (event.modifiers() & ~Qt.KeyboardModifier.ControlModifier)
        ):
            self.clicked.emit()
            event.accept()
            return
        
        event.ignore()  

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        if self._is_recording:
            painter.setBrush(QColor(COLORS["warning"]))
        elif self._is_processing:    
            painter.setBrush(QColor(COLORS["helper"]))
        elif self._is_answering:
            painter.setBrush(QColor(COLORS["helper-intense"]))
        elif self._is_hovered:
            painter.setBrush(QColor(COLORS["primary-lighter"]))
        else:
            painter.setBrush(QColor(COLORS["primary"]))
            
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(self.rect())
        
        icon_size = min(self.width(), self.height()) * 0.5  
        x = (self.width() - icon_size) / 2
        y = (self.height() - icon_size) / 2
        icon_rect = QRectF(x, y, icon_size, icon_size) 
        self.icon_renderer.render(painter, icon_rect)

    def set_recording(self, is_recording):
        self._is_recording = is_recording
        self.update()

    def set_processing(self, is_processing):
        self._is_processing = is_processing
        self.update()  

    def set_answering(self, is_answering):
        self._is_answering = is_answering
        self.update()       
