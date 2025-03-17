from PyQt6.QtWidgets import (
    QTextBrowser,
    QPushButton,
    QHBoxLayout,
    QWidget,
    QApplication,
)
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from core.constants import COLORS
import markdown


class TextResponseHandler:
    def __init__(self):
        super().__init__()

    def reset(self, parent):
        parent.show_text_button.setVisible(False)
        parent.copy_button.setVisible(False)
        parent.show_text_button.setText("Show as text")
        parent.response_text.setVisible(False)
        parent.is_expanded = False
        parent.setFixedSize(300, 400)

    def response_text_setup(self, parent, layout):
        parent.response_text = QTextBrowser()
        parent.response_text.setOpenExternalLinks(True)
        parent.response_text.setStyleSheet(f"""
            QTextBrowser {{
                background-color: {COLORS["secondary"]};
                color: {COLORS["white"]};
                border-radius: 5px;
                padding: 5px;
                font-size: 12px;
                line-height: 1.4;
            }}
            QTextBrowser p {{
                margin: 8px 0;
            }}
            QTextBrowser ul, QTextBrowser ol {{
                margin-top: 8px;
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
            QScrollBar::add-line:vertical {{
                height: 0px;
            }}
            QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
                background: none;
            }}
        """)
        parent.response_text.setVisible(False)
        layout.addWidget(parent.response_text)

        buttons_widget = QWidget()
        buttons_layout = QHBoxLayout(buttons_widget)
        buttons_layout.setContentsMargins(0, 0, 0, 0)
        buttons_layout.setSpacing(10)

        parent.show_text_button = QPushButton("Show as text")
        parent.show_text_button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        parent.show_text_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS["primary"]};
                color: {COLORS["white"]};
                border: none;
                border-radius: 15px;
                padding: 8px 15px;
                font-size: 12px;
            }}
            QPushButton:hover {{
                background-color: {COLORS["primary-lighter"]};
            }}
        """)
        parent.show_text_button.setEnabled(True)
        parent.show_text_button.clicked.connect(
            lambda: self.toggle_text_display(parent)
        )
        parent.show_text_button.setVisible(False)
        buttons_layout.addWidget(parent.show_text_button)

        parent.copy_button = QPushButton()
        parent.copy_button.setIcon(QIcon.fromTheme("edit-copy"))
        parent.show_text_button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        parent.copy_button.setToolTip("Copy to clipboard")
        parent.copy_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS["primary"]};
                color: {COLORS["white"]};
                border: none;
                border-radius: 15px;
                padding: 8px;
                min-width: 30px;
                max-width: 30px;
            }}
            QPushButton:hover {{
                background-color: {COLORS["primary-lighter"]};
            }}
        """)
        parent.copy_button.clicked.connect(lambda: self.copy_to_clipboard(parent))
        parent.copy_button.setVisible(False)
        buttons_layout.addWidget(parent.copy_button)

        layout.addWidget(buttons_widget)

    def copy_to_clipboard(self, parent):
        clipboard = QApplication.clipboard()
        clipboard.setText(parent.current_response)

        original_style = parent.copy_button.styleSheet()

        parent.copy_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS["primary-dark"]};
                color: {COLORS["white"]};
                border: none;
                border-radius: 15px;
                padding: 8px;
                min-width: 30px;
                max-width: 30px;
            }}
            QPushButton:hover {{
                background-color: {COLORS["primary-lighter"]};
            }}
        """)

        self.copy_thread = CopyThread()
        self.copy_thread.finished.connect(
            lambda: parent.copy_button.setStyleSheet(original_style)
        )
        self.copy_thread.start()

    def format_markdown(self, text):
        html_content = markdown.markdown(
            text, extensions=["extra", "nl2br", "sane_lists"]
        )

        return f"""
            <div style="white-space: pre-wrap;">
                {html_content}
            </div>
        """

    def toggle_text_display(self, parent):
        parent.is_expanded = not parent.is_expanded

        if parent.is_expanded:
            parent.setFixedSize(300, 600)
            html_content = self.format_markdown(parent.current_response)
            parent.response_text.setHtml(html_content)
            parent.response_text.setVisible(True)
            parent.show_text_button.setText("Hide text")
        else:
            parent.setFixedSize(300, 400)
            parent.response_text.setVisible(False)
            parent.show_text_button.setText("Show as text")

    def update_response(self, parent, response):
        parent.current_response = response
        clipboard = QApplication.clipboard()
        clipboard.setText(response)
        if parent.is_expanded:
            html_content = self.format_markdown(response)
            parent.response_text.setHtml(html_content)
        parent.show_text_button.setVisible(True)
        parent.copy_button.setVisible(True)

class CopyThread(QThread):
    finished = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)

    def run(self):
        self.msleep(1500)
        self.finished.emit()