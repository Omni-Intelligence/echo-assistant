import tempfile
import os
import markdown
from PyQt6.QtWidgets import (
    QApplication,
    QComboBox,
    QHBoxLayout,
    QPushButton,
    QVBoxLayout,
    QTextBrowser,
    QWidget,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QImage, QPixmap, QIcon
from PIL import ImageGrab
from core.constants import COLORS
from handlers.screenshot_maker import ScreenshotMaker

class VisionTab(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.current_response = ""
        self.setup_ui()

    def setup_ui(self):
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(10, 10, 10, 15)
        layout.setSpacing(10)

        self.mode_selector = QComboBox()
        self.mode_selector.addItems(["Instant Capture", "Custom Screenshot"])
        self.mode_selector.setFixedWidth(200)
        self.mode_selector.setStyleSheet(f"""
            QComboBox {{
                background-color: {COLORS["primary"]};
                color: {COLORS["white"]};
                border: none;
                border-radius: 8px;
                padding: 5px 15px;
                font-size: 12px;
            }}
            QComboBox::drop-down {{
                border: none;
                width: 20px;
            }}
            QComboBox::down-arrow {{
                width: 12px;
                height: 12px;
                margin-right: 8px;
            }}
            QComboBox QAbstractItemView {{
                background-color: {COLORS["secondary"]};
                color: {COLORS["white"]};
                selection-background-color: {COLORS["primary"]};
                selection-color: {COLORS["white"]};
                border: none;
            }}
        """)

        selector_layout = QHBoxLayout()
        selector_layout.addWidget(
            self.mode_selector, alignment=Qt.AlignmentFlag.AlignCenter
        )
        layout.addLayout(selector_layout)

        self.text_display = QTextBrowser()
        self.text_display.setOpenExternalLinks(True)
        self.text_display.setStyleSheet(f"""
            QTextBrowser {{
                background-color: {COLORS["secondary"]};
                color: {COLORS["white"]};
                border-radius: 5px;
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

        buttons_widget = QWidget()
        buttons_layout = QHBoxLayout(buttons_widget)
        buttons_layout.setContentsMargins(0, 0, 0, 0)
        buttons_layout.setSpacing(10)

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

        self.copy_button = QPushButton()
        self.copy_button.setIcon(QIcon.fromTheme("edit-copy"))
        self.copy_button.setToolTip("Copy to clipboard")
        self.copy_button.setFixedSize(30, 30)
        self.copy_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS["primary"]};
                color: {COLORS["white"]};
                border: none;
                border-radius: 8px;
                padding: 5px;
            }}
            QPushButton:hover {{
                background-color: {COLORS["primary-lighter"]};
            }}
        """)
        self.copy_button.clicked.connect(self.copy_to_clipboard)
        self.copy_button.setVisible(False)

        buttons_layout.addWidget(self.button)
        buttons_layout.addWidget(self.copy_button)

        layout.addWidget(self.text_display)
        layout.addWidget(buttons_widget, alignment=Qt.AlignmentFlag.AlignCenter)

        main_layout = QVBoxLayout(self)
        main_layout.addWidget(container)
        main_layout.setContentsMargins(0, 0, 0, 0)

    def copy_to_clipboard(self):
        clipboard = QApplication.clipboard()
        clipboard.setText(self.current_response)
        self.copy_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS["primary-dark"]};
                color: {COLORS["white"]};
                border: none;
                border-radius: 8px;
                padding: 5px;
            }}
            QPushButton:hover {{
                background-color: {COLORS["primary-lighter"]};
            }}
        """)    

    def format_markdown(self, text):
        html_content = markdown.markdown(
            text, extensions=["extra", "nl2br", "sane_lists"]
        )
        return f"""
            <div style="white-space: pre-wrap; pre-wrap; margin: 0; padding: 0;">
                {html_content}
            </div>
        """  

    def take_screenshot(self):
        try:
            self.text_display.setHtml("<p>Taking screenshot...</p>")
            self.button.setEnabled(False)
            self.copy_button.setVisible(False)
            QApplication.processEvents()

            screenshot = (
                ImageGrab.grab()
                if self.mode_selector.currentText() == "Instant Capture"
                else ScreenshotMaker.take_screenshot()
            )

            if screenshot:
                qimage = QImage(
                    screenshot.tobytes(),
                    screenshot.width,
                    screenshot.height,
                    QImage.Format.Format_RGB888,
                )

                clipboard = QApplication.clipboard()
                clipboard.setPixmap(QPixmap.fromImage(qimage))

                self.text_display.setHtml(
                    "<p>Screenshot added to clipboard!</p><p>Analyzing...</p>"
                )
                QApplication.processEvents()

                with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as temp_file:
                    screenshot.save(temp_file.name)
                    response = self.main_window.ai_interface.read_image(temp_file.name)
                    self.current_response = response
                    html_content = self.format_markdown(response)
                    self.text_display.clear()
                    self.text_display.setHtml(html_content)
                    self.copy_button.setVisible(True)
                    os.unlink(temp_file.name)
            else:
                self.text_display.setHtml("<p>Screenshot cancelled</p>")        

        except Exception as e:
            self.text_display.setText(f'<p style="color: #ff6b6b;">Error: {str(e)}</p>')
        finally:
            self.button.setEnabled(True)