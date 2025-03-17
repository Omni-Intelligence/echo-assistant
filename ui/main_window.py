from PyQt6.QtWidgets import (
    QMainWindow,
    QVBoxLayout,
    QWidget,
    QLabel,
    QApplication,
    QComboBox,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPalette, QColor
from ui.voice_button import AssistantButton
from core import AudioManager, AIInterface, COLORS
from handlers import TextResponseHandler, TimerCounterHandler


class MainWindow(QMainWindow):
    def __init__(self, audio_manager: AudioManager, ai_interface: AIInterface):
        super().__init__()
        self.audio_manager = audio_manager
        self.ai_interface = ai_interface

        self.trh = TextResponseHandler()
        self.current_response = ""
        self.is_expanded = False

        self.timer = TimerCounterHandler(self)

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
        layout.setContentsMargins(20, 20, 20, 20)

        self.instruction_label = QLabel("Press mic button or Ctrl+Space to start")
        self.instruction_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.instruction_label.setStyleSheet(f"""
            QLabel {{
                color: {COLORS["white"]};
                font-size: 12px;
                margin-bottom: 10px;
            }}
        """)
        layout.addWidget(self.instruction_label)

        layout.addStretch()

        self.assistant_button = AssistantButton()
        layout.addWidget(self.assistant_button, alignment=Qt.AlignmentFlag.AlignCenter)

        layout.addStretch()

        self.trh.response_text_setup(self, layout)
        self.timer.setup_timer_counter(layout)

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
        layout.addWidget(self.voice_selector)

        self.assistant_button.clicked.connect(self.toggle_recording)
        self.assistant_button.setFocus()

        def focusChanged(old, new):
            if new not in [self.assistant_button, None]:
                self.assistant_button.setFocus()
    
        QApplication.instance().focusChanged.connect(focusChanged)

    def toggle_recording(self):
        if not self.audio_manager.is_recording:
            self.start_recording()
        else:
            self.stop_recording()

    def start_recording(self):
        self.trh.reset(self)
        self.assistant_button.set_recording(True)
        self.instruction_label.setText(
            "Press mic button or Ctrl+Space to finish recording"
        )
        self.voice_selector.setEnabled(False)
        self.voice_selector.setVisible(False)
        self.timer.start_timer()
        self.audio_manager.start_recording()

    def stop_recording(self):
        self.timer.stop_timer()
        self.assistant_button.set_recording(False)
        self.assistant_button.set_processing(True)
        self.instruction_label.setText("Processing your request...")
        QApplication.processEvents()

        try:
            audio_data = self.audio_manager.stop_recording()
            self.process_audio(audio_data)
        finally:
            self.voice_selector.setEnabled(True)
            self.voice_selector.setVisible(True)
            self.assistant_button.set_processing(False)
            self.assistant_button.set_answering(False)
            self.instruction_label.setText("Press mic button or Ctrl+Space to start")

    def process_audio(self, audio_data):
        try:
            selected_voice = self.voice_selector.currentText()
            if selected_voice == "Select a voice":
                selected_voice = "alloy"
            response = self.ai_interface.process_command(audio_data, selected_voice)
            self.trh.update_response(self, response["text"])
            self.audio_manager.play_response(response["audio_path"], self)
            self.show_text_button.setVisible(True)
        except Exception as e:
            self.instruction_label.setText("Error processing audio")
            print(f"Error processing audio: {e}")
