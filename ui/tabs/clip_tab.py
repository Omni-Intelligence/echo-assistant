from .base_tab import BaseTab


class ClipTab(BaseTab):
    def __init__(self, main_window):
        super().__init__(main_window)
        self.instruction_label.setText(
            "Press mic button or Ctrl+Space to start"
        )
        self.button.clicked.connect(lambda: self.main_window.toggle_recording(self))

    def start_recording(self):
        super().start_recording()
        self.main_window.audio_manager.start_recording()

    def stop_recording(self):
        super().stop_recording()

        audio_data = self.main_window.audio_manager.stop_recording()
        self.process_audio(audio_data)

    def process_audio(self, audio_data):
        try:
            response = self.main_window.ai_interface.process_audio(audio_data)
            self.text_handler.update_response(self, response)
            self.button.set_processing(False)
            self.instruction_label.setText(
                "The text was added to your clipboard!"
            )
        except Exception as e:
            self.instruction_label.setText("Error processing dictation")
            self.button.set_processing(False)
            print(f"Error processing dictation: {e}") 
