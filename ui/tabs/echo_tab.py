from PyQt6.QtWidgets import QComboBox
from PyQt6.QtCore import Qt
from .base_tab import BaseTab
from core import COLORS


class EchoTab(BaseTab):
    def __init__(self, main_window):
        super().__init__(main_window)
        self.instruction_label.setText("Press mic button or Ctrl+Space to start")

    def setup_ui(self):
        super().setup_ui()

        self.voice_selector = QComboBox()
        self.voice_selector.addItem("Select a voice")
        self.voice_selector.setItemData(0, 0, role=Qt.ItemDataRole.UserRole - 1)
        self.voice_selector.addItems(
            ["alloy", "ash", "ballad", "coral", "echo", "sage", "shimmer"]
        )
        self.voice_selector.setStyleSheet(f"""
            QComboBox {{
                background-color: {COLORS["primary"]};
                color: {COLORS["white"]};
                border: 1px solid {COLORS["white"]};
                border-radius: 4px;
                padding: 5px;
                margin-top: 10px;
            }}
            QComboBox QListView {{
                background-color: {COLORS["primary"]};
                color: {COLORS["white"]};
                border: 1px solid {COLORS["white"]};
                selection-background-color: {COLORS["secondary"]};
            }}
            QComboBox QAbstractItemView::item:hover {{
                background-color: {COLORS["secondary"]};
                color: {COLORS["white"]};
            }}
            QComboBox::drop-down {{
                border: none;
            }}
            QComboBox::down-arrow {{
                image: none;
            }}
        """)
        self.layout.addWidget(self.voice_selector)

        self.button.clicked.connect(lambda: self.main_window.toggle_recording(self))

    def start_recording(self):
        super().start_recording()
        self.voice_selector.setEnabled(False)
        self.voice_selector.setVisible(False)
        self.main_window.audio_manager.start_recording()

    def stop_recording(self):
        super().stop_recording()

        audio_data = self.main_window.audio_manager.stop_recording()
        self.process_audio(audio_data)

    def process_audio(self, audio_data):
        try:
            selected_voice = self.voice_selector.currentText()
            if selected_voice == "Select a voice":
                selected_voice = "alloy"
            response = self.main_window.ai_interface.speak(
                audio_data, selected_voice
            )
            self.text_handler.update_response(self, response["text"])
            self.main_window.audio_manager.play_response(
                response["audio_path"], self
            )
        except Exception as e:
            self.instruction_label.setText("Error processing audio")
            self.button.set_processing(False)
            print(f"Error processing audio: {e}")    
