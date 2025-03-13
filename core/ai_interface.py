import base64
import logging
import os
import tempfile
import speech_recognition as sr
from openai import OpenAI

class AIInterface:
    def __init__(self, api_service):
        self.recognizer = sr.Recognizer()
        self.api_key = api_service.api_key
        self.logger = logging.getLogger(__name__)

    def process_command(self, audio_file):
        # text = self._speech_to_text(audio_file)
        # if not text:
        #     return "Sorry, I couldn't understand that."

        response = self._get_ai_response(audio_file)
        return response

    def _speech_to_text(self, audio_file):
        try:
            with sr.AudioFile(audio_file) as source:
                audio = self.recognizer.record(source)
                return self.recognizer.recognize_google(audio)
        except Exception as e:
            print(f"Error in speech recognition: {e}")
            return None

    def _get_ai_response(self, file_path):
        try: 
            client = OpenAI(api_key=self.api_key)

            system_prompt = "You are a helpful, friendly assistant. \
                Provide concise, accurate, and helpful responses that can be read with voice. \
                Avoid unnecessary details or lengthy explanations unless specifically requested."
            
            with open(file_path, "rb") as f:
                audio = f.read()

            audio_format = os.path.splitext(file_path)[1].lower().lstrip(".")
            print("audio format: ", audio_format)

            response = client.chat.completions.create(
                model="gpt-4o-mini-audio-preview",  
                modalities=["text", "audio"],
                audio={
                    "format": "wav",
                    "voice": "ballad",
                },
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": [{
                        "type": "input_audio",
                        "input_audio": {
                            "data": base64.b64encode(audio).decode("utf-8"),
                            "format": audio_format,
                        }
                    }]}
                ],
            )

            with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as temp_audio:
                temp_audio_path = temp_audio.name

            audio = response.choices[0].message.audio.data
            text = response.choices[0].message.audio.transcript   

            print(text, temp_audio_path)

            with open(temp_audio_path, "wb") as f:
                f.write(base64.b64decode(audio))
            
            return {
                "text": text,
                "audio_path": temp_audio_path
            }
        
        except Exception as e:
            self.logger.error(f"Error getting AI response: {str(e)}")
            return "Sorry, I encountered an error while processing your request."
