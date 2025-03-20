from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt
from ui.voice_button import AssistantButton
from handlers import TextResponseHandler, TimerCounterHandler
from core import COLORS


class BaseTab(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.is_expanded = False
        self.text_handler = TextResponseHandler()
        self.timer_handler = TimerCounterHandler(self)
        self.button = AssistantButton()
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.focusInEvent = self.on_focus_in
        self.setup_ui()

    def setup_ui(self):
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)

        self.instruction_label = QLabel()
        self.instruction_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.instruction_label.setStyleSheet(f"""
            QLabel {{
                color: {COLORS["white"]};
                font-size: 12px;
                margin-bottom: 10px;
            }}
        """)
        self.layout.addWidget(self.instruction_label)

        self.layout.addStretch()
        self.layout.addWidget(self.button, alignment=Qt.AlignmentFlag.AlignCenter)
        self.layout.addStretch()

        self.button.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        self.text_handler.response_text_setup(self, self.layout)
        self.timer_handler.setup_timer_counter(self.layout)

    def start_recording(self):
        self.main_window.audio_manager.stop_playback()
        self.text_handler.reset(self)
        self.button.set_recording(True)
        self.instruction_label.setText(
            "Press mic button or Ctrl+Space to end recording"
        )
        self.timer_handler.start_timer()

    def stop_recording(self):
        self.timer_handler.stop_timer()
        self.button.set_recording(False)
        self.button.set_processing(True)
        self.instruction_label.setText("Processing your request...")
        QApplication.processEvents()  

    def on_focus_in(self, event):
        self.button.setFocus()
        super().focusInEvent(event)    
