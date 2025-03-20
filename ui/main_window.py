from turtle import st
from PyQt6.QtWidgets import (
    QMainWindow,
    QVBoxLayout,
    QWidget,
    QLabel,
    QApplication,
    QComboBox,
    QTabWidget,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPalette, QColor
from ui.voice_button import AssistantButton
from ui.tabs.echo_tab import EchoTab
from ui.tabs.clip_tab import ClipTab
from core import AudioManager, AIInterface, COLORS
from handlers import TextResponseHandler, TimerCounterHandler


class MainWindow(QMainWindow):
    def __init__(self, audio_manager: AudioManager, ai_interface: AIInterface):
        super().__init__()
        self.audio_manager = audio_manager
        self.ai_interface = ai_interface
        self.current_response = ""
        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle("Echo Assistant")
        self.setFixedSize(300, 400)

        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor(COLORS["secondary"]))
        self.setPalette(palette)
        self.setAutoFillBackground(True)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)

        tab_widget = QTabWidget()
        tab_widget.setStyleSheet(f"""
            QTabWidget::pane {{
                border: none;
                background: {COLORS["secondary"]};
            }}
            QTabBar::tab {{
                background: {COLORS["primary"]};
                color: {COLORS["white"]};
                padding: 8px 20px;
                border: none;
            }}
            QTabBar::tab:selected {{
                background: {COLORS["secondary"]};
            }}
        """)

        self.echo_tab = EchoTab(self)
        self.clip_tab = ClipTab(self)

        tab_widget.addTab(self.echo_tab, "Echo")
        tab_widget.addTab(self.clip_tab, "Clip")
        layout.addWidget(tab_widget)

        tab_widget.currentChanged.connect(self.on_tab_changed)

    def toggle_recording(self, tab):
        if not self.audio_manager.is_recording:
            tab.start_recording()
        else:
            tab.stop_recording()

    def on_tab_changed(self, index):
        current_tab = self.centralWidget().findChild(QTabWidget).widget(index)
        current_tab.setFocus()
        current_tab.button.setFocus()        
