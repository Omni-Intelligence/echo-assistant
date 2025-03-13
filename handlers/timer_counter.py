from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import QLabel
from core.constants import COLORS

class TimerCounterHandler:
    def __init__(self, parent):
        self.parent = parent
        self.remaining_time = 120
        self.timer = QTimer()
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.update_timer) 

    def setup_timer_counter(self, layout):
        self.parent.timer_label = QLabel("")
        self.parent.timer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.parent.timer_label.setStyleSheet(f"""
            QLabel {{
                color: {COLORS["white"]};
                font-size: 14px;
                margin-top: 10px;
            }}
        """)
        self.parent.timer_label.setVisible(False)
        layout.addWidget(self.parent.timer_label)

    def start_timer(self):
        self.remaining_time = 120
        self.parent.timer_label.setVisible(True)
        self.parent.timer_label.setText(f"Time remaining: {self.remaining_time} seconds")
        self.timer.start()       

    def stop_timer(self):
        self.timer.stop()    
        self.parent.timer_label.setVisible(False)

    def update_timer(self):
        self.remaining_time -= 1
        self.parent.timer_label.setText(f"Time remaining: {self.remaining_time} seconds")
        if self.remaining_time <= 0:
            self.parent.stop_recording()       