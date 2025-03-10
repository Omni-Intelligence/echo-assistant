import sys
from PyQt6.QtWidgets import QApplication
from ui.main_window import MainWindow
from core.audio_manager import AudioManager
from core.ai_interface import AIInterface
from utils.logger import configure_logging

def main():
    app = QApplication(sys.argv)
    configure_logging()

    audio_manager = AudioManager()
    ai_interface = AIInterface()
    window = MainWindow(audio_manager, ai_interface)
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
