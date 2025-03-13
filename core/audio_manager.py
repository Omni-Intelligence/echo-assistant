import platform
import threading
import tempfile
import os
import time
import pyttsx3
import subprocess
from datetime import datetime
from openai import OpenAI
from utils.api import ApiService
from PyQt6.QtWidgets import QApplication

class AudioManager:
    def __init__(self):
        self.is_recording = False
        self.tts_engine = pyttsx3.init()
        self.system = platform.system()
        self.max_duration = 120  
        self.recording_start_time = None
        api_service = ApiService()

        try:
            self.openai_client = OpenAI(api_key=api_service.api_key)
            self.use_openai_tts = True
            self.openai_voice = "alloy"  #(options: alloy, echo, fable, onyx, nova, shimmer)
        except Exception as e:
            print(f"OpenAI TTS initialization failed: {e}")
            self.use_openai_tts = False

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
    
    def play_audio_file(self, file_path):
        """Play audio file using platform-specific methods"""
        try:
            if self.system == "Linux":
                subprocess.run(['ffplay', '-nodisp', '-autoexit', file_path], check=True)
            elif self.system == "Windows":
                from winsound import PlaySound, SND_FILENAME
                PlaySound(file_path, SND_FILENAME)
            elif self.system == "Darwin": 
                subprocess.run(['afplay', file_path], check=True)
        except Exception as e:
            print(f"Error playing audio file: {e}")

    def play_response(self, text, parent):
        """Play response using OpenAI TTS or fall back to pyttsx3"""

        print(text, self.use_openai_tts)
        if self.use_openai_tts:
            try:
                with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as temp_audio:
                    temp_audio_path = temp_audio.name
                
                response = self.openai_client.audio.speech.create(
                    model="tts-1",
                    voice=self.openai_voice,
                    input=text
                )
                
                response.stream_to_file(temp_audio_path)

                parent.assistant_button.set_processing(False)
                parent.assistant_button.set_answering(True)
                parent.instruction_label.setText("Answering...")
                QApplication.processEvents() 
                
                self.play_audio_file(temp_audio_path)

                os.remove(temp_audio_path)
                    
            except Exception as e:
                print(f"OpenAI TTS failed: {e}, falling back to pyttsx3")
  
                try:
                    self.tts_engine.say(text)
                    self.tts_engine.runAndWait()
                except Exception as e2:
                    print(f"Assistant: {text}")
        else:
 
            try:
                self.tts_engine.say(text)
                self.tts_engine.runAndWait()
            except Exception as e:
                print(f"Assistant: {text}")
