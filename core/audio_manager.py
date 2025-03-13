import platform
import threading
import tempfile
import os
import time
import subprocess
from datetime import datetime
from PyQt6.QtWidgets import QApplication

class AudioManager:
    def __init__(self, api_service):
        self.is_recording = False
        self.temp_file = None
        self.system = platform.system()
        self.max_duration = 120  
        self.recording_start_time = None

    def start_recording(self):
        """Start recording audio using platform-specific methods"""
        self.is_recording = True
        self.temp_file = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
        self.recording_start_time = datetime.now()
        
        def record_thread():
            if self.system == "Linux":
                subprocess.run([
                    'arecord',
                    '-f', 'cd',
                    '-t', 'wav',
                    '-d', str(self.max_duration), 
                    self.temp_file.name
                ], capture_output=True)
            elif self.system == "Windows":
                ps_script = '''
                Add-Type -AssemblyName System.Speech
                $rec = New-Object System.Speech.Recognition.SpeechRecognitionEngine
                $rec.SetInputToDefaultAudioDevice()
                $rec.Record()
                Start-Sleep -Seconds 60
                '''
                subprocess.run(['powershell', '-Command', ps_script], capture_output=True)
            elif self.system == "Darwin":
                subprocess.run([
                    'rec',
                    '-r', '44100',
                    self.temp_file.name,
                    'trim', '0', str(self.max_duration)  
                ], capture_output=True)

            if self.is_recording and (datetime.now() - self.recording_start_time).total_seconds() >= self.max_duration:
                self.stop_recording()

        self.record_thread = threading.Thread(target=record_thread)
        self.record_thread.daemon = True
        self.record_thread.start()

        threading.Timer(self.max_duration, self.stop_recording).start()

    def stop_recording(self):
        """Stop recording and return the temporary file path"""
        if not self.is_recording:
            return None
            
        self.is_recording = False
        
        if self.system == "Linux":
            subprocess.run(['pkill', '-f', 'arecord'])
        elif self.system == "Windows":
            subprocess.run(['taskkill', '/IM', 'powershell.exe', '/F'])
        elif self.system == "Darwin":
            subprocess.run(['pkill', '-f', 'rec'])
            
        time.sleep(0.5)
        return self.temp_file.name

    def play_response(self, audio_path, parent):
        """Play audio file using platform-specific methods"""

        parent.assistant_button.set_processing(False)
        parent.assistant_button.set_answering(True)
        parent.instruction_label.setText("Answering...")
        QApplication.processEvents() 
                
        try:
            if self.system == "Linux":
                subprocess.run(['ffplay', '-nodisp', '-autoexit', audio_path], check=True)
            elif self.system == "Windows":
                from winsound import PlaySound, SND_FILENAME
                PlaySound(audio_path, SND_FILENAME)
            elif self.system == "Darwin": 
                subprocess.run(['afplay', audio_path], check=True)
        except Exception as e:
            print(f"Error playing audio file: {e}")

        os.remove(self.temp_file.name)
        os.remove(audio_path)        
