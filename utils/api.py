import os
import sys
import logging
from dotenv import load_dotenv
from PyQt6.QtWidgets import (QInputDialog, QLineEdit, QMessageBox)

class ApiService:
    def __init__(self, parent=None):
        self.logger = logging.getLogger(__name__)
        self.parent = parent
        self.api_key = self._get_api_key()

    def _get_api_key(self):
        """
        Load the OpenAI API key from .env file, compatible with both normal Python execution
        and PyInstaller executable.
        
        Returns:
            str: The API key or None if not found
        """
        try:
            if getattr(sys, 'frozen', False):
                env_path = os.path.join(sys._MEIPASS, ".env")
            else:
                current_path = os.path.dirname(os.path.abspath(__file__))
                application_path = os.path.dirname(current_path)
                env_path = os.path.join(application_path, ".env")
            
            self.logger.info(f"Looking for .env at: {env_path}")

            if os.path.exists(env_path):
                self.logger.info(f"Loading .env from: {env_path}")
                load_dotenv(env_path)
                env_key = os.getenv('OPENAI_API_KEY')
                if env_key and env_key.strip():
                    return env_key.strip()
            
            self.logger.warning("No valid API key found in .env file")
            return self.get_api_key_from_user()
                
        except Exception as e:
            self.logger.error(f"Error loading API key: {str(e)}")
            return self.get_api_key_from_user()

    def get_api_key_from_user(self):
        while True:
            api_key, ok = QInputDialog.getText(
                self.parent,
                "OpenAI API Key Required",
                "Please enter your OpenAI API Key:\n\nYou can get it from: https://platform.openai.com/api-keys",
                QLineEdit.EchoMode.Password
            )
            
            if not ok:
                if QMessageBox.question(
                    self.parent,
                    "Exit Confirmation",
                    "The application requires an API key to function. Do you want to exit?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                ) == QMessageBox.StandardButton.Yes:
                    sys.exit(0)
                continue
            
            if not api_key.strip():
                QMessageBox.warning(self, "Invalid Input", "API key cannot be empty.")
                continue
            
            try:
                if getattr(sys, 'frozen', False):
                    app_dir = os.path.dirname(sys.executable)
                else:
                    app_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                
                env_path = os.path.join(app_dir, ".env")
                self.logger.info(f"Saving API key to {env_path}")
                
                with open(env_path, "w") as f:
                    f.write(f"OPENAI_API_KEY={api_key}")
                
                return api_key
            
            except Exception as e:
                self.logger.error(f"Failed to save API key: {str(e)}")
                QMessageBox.warning(
                    self.parent, 
                    "Error", 
                    f"Failed to save API key: {str(e)}"
                )
