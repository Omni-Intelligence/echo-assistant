from PyQt6.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QLabel, QApplication, QTextEdit, QPushButton
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPalette, QColor
from ui.voice_button import AssistantButton
from core.constants import COLORS
from utils.text_response_handler import TextResponseHandler

class MainWindow(QMainWindow):
    def __init__(self, audio_manager, ai_interface):
        super().__init__()
        self.audio_manager = audio_manager
        self.ai_interface = ai_interface

        self.trh = TextResponseHandler()
        self.current_response = ""
        self.is_expanded = False

        self.remaining_time = 120
        self.timer = QTimer()
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.update_timer)

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

        layout.addStretch()

        self.assistant_button = AssistantButton()
        layout.addWidget(self.assistant_button, alignment=Qt.AlignmentFlag.AlignCenter)

        layout.addStretch()

        self.trh.response_text_setup(self, layout)

        self.timer_label = QLabel("")
        self.timer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.timer_label.setStyleSheet(f"""
            QLabel {{
                color: {COLORS["white"]};
                font-size: 14px;
                margin-top: 10px;
            }}
        """)
        self.timer_label.setVisible(False)
        layout.addWidget(self.timer_label)
        
        self.assistant_button.clicked.connect(self.toggle_recording)
        self.assistant_button.setFocus()

    def update_timer(self):
        self.remaining_time -= 1
        self.timer_label.setText(f"Time remaining: {self.remaining_time} seconds")
        if self.remaining_time <= 0:
            self.stop_recording()    

    def answering(self):
        self.assistant_button.set_processing(False)
        self.assistant_button.set_answering(True)
        self.instruction_label.setText("Answering...")
        QApplication.processEvents()    

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Space:
            self.toggle_recording()  

    def toggle_recording(self):
        if not self.audio_manager.is_recording:
            self.start_recording()
        else:
            self.stop_recording()

    def start_recording(self):
        self.trh.reset(self)

        self.assistant_button.set_recording(True)
        self.instruction_label.setText("Press button or space key to finish recording")
        self.remaining_time = 120
        self.timer_label.setVisible(True)
        self.timer_label.setText(f"Time remaining: {self.remaining_time} seconds")
        self.timer.start()
        self.audio_manager.start_recording()

    def stop_recording(self):
        self.timer.stop()
        self.timer_label.setVisible(False)
        self.assistant_button.set_recording(False)
        self.assistant_button.set_processing(True)
        self.instruction_label.setText("Processing your request...")
        QApplication.processEvents()

        try:    
            audio_data = self.audio_manager.stop_recording()
            self.process_audio(audio_data)
        finally:
            self.assistant_button.set_processing(False)
            self.assistant_button.set_answering(False)
            self.instruction_label.setText("Press button or space key to start")


    def process_audio(self, audio_data):
        try:
            response = self.ai_interface.process_command(audio_data)
            self.trh.update_response(self, response)
            self.audio_manager.play_response(response, self)
            self.show_text_button.setVisible(True)
        except Exception as e:
            self.instruction_label.setText("Error processing audio")
            print(f"Error processing audio: {e}")
