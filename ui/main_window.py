from PyQt6.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QLabel
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPalette, QColor
from ui.voice_button import AssistantButton
from core.constants import COLORS

class MainWindow(QMainWindow):
    def __init__(self, audio_manager, ai_interface):
        super().__init__()
        self.audio_manager = audio_manager
        self.ai_interface = ai_interface
        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle("Echo Assistant")
        self.setFixedSize(300, 400)  # Make window more square

        # Set dark background
        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor(COLORS["secondary"]))
        self.setPalette(palette)
        self.setAutoFillBackground(True)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(20, 20, 20, 20)  # Add margins around all elements

        # Add instruction label
        self.instruction_label = QLabel("Press button or space key to start")
        self.instruction_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.instruction_label.setStyleSheet(f"""
            QLabel {{
                color: {COLORS["white"]};
                font-size: 12px;
                margin-bottom: 10px;
            }}
        """)
        layout.addWidget(self.instruction_label)

        # Add stretch before button
        layout.addStretch()

        # Assistant button
        self.assistant_button = AssistantButton()
        layout.addWidget(self.assistant_button, alignment=Qt.AlignmentFlag.AlignCenter)

        # Add stretch after button
        layout.addStretch()
        
        self.assistant_button.clicked.connect(self.toggle_recording)
        self.assistant_button.setFocus()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Space:
            self.toggle_recording()

    def toggle_recording(self):
        if not self.audio_manager.is_recording:
            self.start_recording()
        else:
            self.stop_recording()

    def start_recording(self):
        self.assistant_button.set_recording(True)
        self.instruction_label.setText("Press button or space key to finish recording")
        self.audio_manager.start_recording()

    def stop_recording(self):
        self.assistant_button.set_recording(False)
        self.instruction_label.setText("Press button or space key to start")
        audio_data = self.audio_manager.stop_recording()
        self.process_audio(audio_data)

    def process_audio(self, audio_data):
        response = self.ai_interface.process_command(audio_data)
        self.audio_manager.play_response(response)
