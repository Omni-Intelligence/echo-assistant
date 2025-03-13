from PyQt6.QtWidgets import QTextEdit, QPushButton
from core.constants import COLORS

class TextResponseHandler:

    def __init__(self):
        super().__init__()

    def reset(self, parent):
        parent.show_text_button.setVisible(False)
        parent.response_text.setVisible(False)
        # parent.is_expanded = False
        parent.setFixedSize(300, 400)    

    def response_text_setup(self, parent, layout):
        parent.response_text = QTextEdit()
        parent.response_text.setReadOnly(True)
        parent.response_text.setStyleSheet(f"""
            QTextEdit {{
                background-color: {COLORS["secondary"]};
                color: {COLORS["white"]};
                border-radius: 5px;
                padding: 10px;
                font-size: 12px;
            }}
        """)
        parent.response_text.setVisible(False)
        layout.addWidget(parent.response_text)

        parent.show_text_button = QPushButton("Show as text")
        parent.show_text_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS["primary"]};
                color: {COLORS["white"]};
                border: none;
                border-radius: 15px;
                padding: 8px 15px;
                font-size: 12px;
            }}
            QPushButton:hover {{
                background-color: {COLORS["primary-lighter"]};
            }}
        """)
        parent.show_text_button.setEnabled(True)
        parent.show_text_button.clicked.connect(lambda: self.toggle_text_display(parent))
        parent.show_text_button.setVisible(False)
        layout.addWidget(parent.show_text_button)

    def toggle_text_display(self, parent):
        parent.is_expanded = not parent.is_expanded
        
        if parent.is_expanded:
            parent.setFixedSize(300, 600)  
            parent.response_text.setText(parent.current_response)
            parent.response_text.setVisible(True)
            parent.show_text_button.setText("Hide text")
        else:
            parent.setFixedSize(300, 400)  
            parent.response_text.setVisible(False)
            parent.show_text_button.setText("Show as text")    

    def update_response(self, parent, response):
        parent.current_response = response
        if parent.is_expanded:
            parent.response_text.setText(response)
        # parent.show_text_button.setVisible(True)   