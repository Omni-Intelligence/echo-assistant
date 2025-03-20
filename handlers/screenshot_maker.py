from PyQt6.QtWidgets import QWidget, QRubberBand, QApplication, QLabel
from PyQt6.QtCore import Qt, QRect, QPoint, QBuffer
from PyQt6.QtGui import QColor, QPainter
from PIL import Image
import io

class ScreenshotMaker:
    @staticmethod
    def take_screenshot():
        selection_window = SelectionWindow()
        selection_window.showFullScreen()
        QApplication.processEvents()

        while selection_window.isVisible():
            QApplication.processEvents()

        if hasattr(selection_window, "screenshot"):
            buffer = QBuffer()
            buffer.open(QBuffer.OpenModeFlag.ReadWrite)
            selection_window.screenshot.save(buffer, "PNG")

            data = buffer.data().data()
            buffer.close()

            return Image.open(io.BytesIO(data))
        return None
    
class SelectionWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setCursor(Qt.CursorShape.CrossCursor)

        self.rubberband = None
        self.origin = QPoint()

        self.guide = QLabel(self)
        self.guide.setText("Click and drag to select area\nPress ESC to cancel")
        self.guide.setStyleSheet("""
            QLabel {
                color: white;
                background-color: rgba(0, 0, 0, 150);
                padding: 10px;
                border-radius: 5px;
            }
        """)
        self.guide.adjustSize()
        self.guide.move(10, 10)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(0, 0, 0, 100))

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.close()

    def mousePressEvent(self, event):
        self.origin = event.pos()
        if not self.rubberband:
            self.rubberband = QRubberBand(QRubberBand.Shape.Rectangle, self)
            self.rubberband.setStyleSheet("""
                QRubberBand {
                    border: 2px solid white;
                    background-color: rgba(255, 255, 255, 30);
                }
            """)
        self.rubberband.setGeometry(QRect(self.origin, QPoint()))
        self.rubberband.show()
        self.guide.hide()

    def mouseMoveEvent(self, event):
        if self.rubberband:
            self.rubberband.setGeometry(QRect(self.origin, event.pos()).normalized())

    def mouseReleaseEvent(self, event):
        if self.rubberband:
            selection = QRect(self.origin, event.pos()).normalized()
            if selection.width() > 10 and selection.height() > 10:
                self.hide()
                QApplication.processEvents()

                screen = QApplication.primaryScreen()
                self.screenshot = screen.grabWindow(
                    0,
                    selection.x(),
                    selection.y(),
                    selection.width(),
                    selection.height(),
                )
            self.close()