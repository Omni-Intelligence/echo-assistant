import speech_recognition as sr
from openai import OpenAI
from utils.api import ApiService


class AIInterface:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        api_service = ApiService()
        self.api_key = api_service.api_key

    def process_command(self, audio_file):
        text = self._speech_to_text(audio_file)
        if not text:
            return "Sorry, I couldn't understand that."

        response = self._get_ai_response(text)
        return response

    def _speech_to_text(self, audio_file):
        try:
            with sr.AudioFile(audio_file) as source:
                audio = self.recognizer.record(source)
                return self.recognizer.recognize_google(audio)
        except Exception as e:
            print(f"Error in speech recognition: {e}")
            return None

    def _get_ai_response(self, text):
        try: 
            client = OpenAI(api_key=self.api_key)

            system_prompt = "You are a helpful, friendly assistant. \
                Provide concise, accurate, and helpful responses that can be read with voice. \
                Avoid unnecessary details or lengthy explanations unless specifically requested."
            
            response = client.chat.completions.create(
                model="o3-mini",  
                messages=[
                    {"role": "developer", "content": system_prompt},
                    {"role": "user", "content": text}
                ],
            )

            return response.choices[0].message.content.strip()
        
        except Exception as e:
            self.logger.error(f"Error getting AI response: {str(e)}")
            return "Sorry, I encountered an error while processing your request."
