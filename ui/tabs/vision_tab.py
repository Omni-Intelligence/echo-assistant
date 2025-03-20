from PyQt6.QtWidgets import QApplication, QPushButton, QVBoxLayout, QTextEdit, QWidget
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QImage, QPixmap
from PIL import ImageGrab
import tempfile
import os
import markdown
from core.constants import COLORS


class VisionTab(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.setup_ui()

    def setup_ui(self):
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(10, 10, 10, 15)
        layout.setSpacing(10)

        self.text_display = QTextEdit()
        self.text_display.setReadOnly(True)
        self.text_display.setStyleSheet(f"""
            QTextEdit {{
                background-color: {COLORS["secondary"]};
                color: {COLORS["white"]};
                border-radius: 5px;
                padding: 0;
                margin: 0;
                font-size: 12px;
                line-height: 1.4;
            }}
            QTextBrowser p {{
                margin: 8px 0;
            }}
            QTextBrowser ul, QTextBrowser ol {{
                margin-bottom: 8px;
            }}
            QTextBrowser li {{
                margin: 4px 0;
            }}
            QScrollBar:vertical {{
                border: none;
                background: {COLORS["secondary"]};
                width: 8px;
                margin: 0px;
                border-radius: 4px;
            }}
            QScrollBar::handle:vertical {{
                background: {COLORS["primary"]};
                min-height: 20px;
                border-radius: 4px;
            }}
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
            QScrollBar::add-page:vertical,
            QScrollBar::sub-page:vertical {{
                background: none;
            }}
        """)

        self.button = QPushButton("Take Screenshot")
        self.button.setFixedSize(200, 30)
        self.button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.button.clicked.connect(self.take_screenshot)
        self.button.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS["primary"]};
                color: {COLORS["white"]};
                border: none;
                border-radius: 8px;
                padding: 8px 15px;
                font-size: 12px;
            }}
            QPushButton:hover {{
                background-color: {COLORS["primary-lighter"]};
            }}
        """)

        layout.addWidget(self.text_display)
        layout.addWidget(self.button, alignment=Qt.AlignmentFlag.AlignCenter)

        main_layout = QVBoxLayout(self)
        main_layout.addWidget(container)
        main_layout.setContentsMargins(0, 0, 0, 0)

    def format_markdown(self, text):
        html_content = markdown.markdown(
            text, extensions=["extra", "nl2br", "sane_lists"]
        )
        return f"""
            <div style="white-space: pre-wrap;">
                {html_content}
            </div>
        """    

    def take_screenshot(self):
        try:
            self.text_display.setText("Screenshot added to your clipboard! Analyzing...")
            self.button.setEnabled(False)
            QApplication.processEvents()

            screenshot = ImageGrab.grab()

            qimage = QImage(
                screenshot.tobytes(),
                screenshot.width,
                screenshot.height,
                QImage.Format.Format_RGB888,
            )

            clipboard = QApplication.clipboard()
            clipboard.setPixmap(QPixmap.fromImage(qimage))

            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as temp_file:
                screenshot.save(temp_file.name)
                response = self.main_window.ai_interface.read_image(temp_file.name)
                html_content = self.format_markdown(response)
                self.text_display.clear()
                self.text_display.setHtml(html_content)

            os.unlink(temp_file.name)

        except Exception as e:
            self.text_display.setText(f"Error: {str(e)}")
        finally:
            self.button.setEnabled(True)