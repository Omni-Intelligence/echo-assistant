import platform
import threading
import tempfile
import os
import time
import subprocess
import sounddevice as sd
import soundfile as sf
import logging
from datetime import datetime
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QThread, pyqtSignal

class AudioManager:
    def __init__(self):
        self.is_recording = False
        self.temp_file = None
        self.system = platform.system()
        self.playback_thread = None

        self.max_duration = 120  
        self.recording_start_time = None
        self.sample_rate = 44100

        self.logger = logging.getLogger(__name__)
        logging.basicConfig(level=logging.DEBUG)

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
                try:
                    self.logger.debug("Starting Windows audio recording...")
                    recording = sd.rec(
                        int(self.max_duration * self.sample_rate),
                        samplerate=self.sample_rate,
                        channels=1,
                        dtype="float32",
                    )

                    while self.is_recording and sd.get_stream().active:
                        time.sleep(0.1)

                    sd.stop()
                    
                    if len(recording) > 0:
                        duration = (
                            datetime.now() - self.recording_start_time
                        ).total_seconds()
                        samples = int(duration * self.sample_rate)
                        self.logger.debug(
                            f"Saving {samples} samples to {self.temp_file.name}"
                        )
                        sf.write(
                            self.temp_file.name, recording[:samples], self.sample_rate
                        )
                        sf.SoundFile(self.temp_file.name).close()
                except Exception as e:
                    self.logger.error(f"Error in Windows recording: {str(e)}")
                    self.is_recording = False
                    print(f"Error recording audio: {e}")
                    
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

    def stop_playback(self):
        """Stop current audio playback"""
        if self.playback_thread and self.playback_thread.isRunning():
            if self.system == "Linux":
                subprocess.run(["pkill", "-f", "ffplay"])
            elif self.system == "Windows":
                sd.stop()
            elif self.system == "Darwin":
                subprocess.run(["pkill", "-f", "afplay"])
            self.playback_thread.terminate()
            self.playback_thread.wait()    

    def stop_recording(self):
        """Stop recording and return the temporary file path"""
        if not self.is_recording:
            return None
            
        self.is_recording = False
        
        if self.system == "Linux":
            subprocess.run(['pkill', '-f', 'arecord'])
        elif self.system == "Windows":
            self.logger.debug("Stopping Windows recording...")
            sd.stop()
        elif self.system == "Darwin":
            subprocess.run(['pkill', '-f', 'rec'])
            
        time.sleep(0.5)
        
        if os.path.exists(self.temp_file.name):
            self.logger.debug(f"Recording saved to: {self.temp_file.name}")
            return self.temp_file.name
        else:
            self.logger.error("Recording file was not created")
            return None

    def play_response(self, audio_path, parent):
        """Play audio file using platform-specific methods"""

        parent.button.set_processing(False)
        parent.button.set_answering(True)
        parent.instruction_label.setText("Answering...")
        QApplication.processEvents() 

        def cleanup():
            try:
                if os.path.exists(audio_path):
                    os.remove(audio_path)
                if os.path.exists(self.temp_file.name):
                    os.remove(self.temp_file.name)    
            except Exception as e:
                print(f"Error removing audio file: {e}")

        self.playback_thread = PlaybackThread(self.system, audio_path, parent)
        self.playback_thread.finished.connect(cleanup)
        self.playback_thread.error.connect(
            lambda e: self.logger.error(f"Error playing audio: {e}")
        )
        self.playback_thread.start()        
    

class PlaybackThread(QThread):
    finished = pyqtSignal()
    error = pyqtSignal(str)

    def __init__(self, system, audio_path, parent=None):
        super().__init__(parent)
        self.system = system
        self.audio_path = audio_path
        self.parent = parent

    def run(self):
        try:
            if self.system == "Linux":
                subprocess.run(
                    [
                        "ffplay",
                        "-nodisp",
                        "-autoexit",
                        "-loglevel",
                        "error",
                        self.audio_path,
                    ],
                    check=True,
                )
            elif self.system == "Windows":
                data, samplerate = sf.read(self.audio_path)
                sd.play(data, samplerate)
                sd.wait()
            elif self.system == "Darwin":
                subprocess.run(["afplay", self.audio_path], check=True)
            self.finished.emit()
        except Exception as e:
            self.error.emit(str(e))  
        finally:
            self.parent.button.set_processing(False)
            self.parent.button.set_answering(False)
            self.parent.instruction_label.setText("Press mic button or Ctrl+Space to start")

            print('AM: ' + self.parent.__class__.__name__)
            if self.parent.__class__.__name__ == "EchoTab":
                self.parent.voice_selector.setEnabled(True)
                self.parent.voice_selector.setVisible(True)
            self.finished.emit()              
    
