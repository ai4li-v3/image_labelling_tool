from PyQt5.QtWidgets import QLineEdit

class AnswerInput(QLineEdit):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        """Initialize the answer input UI"""
        self.setPlaceholderText("Enter Vietnamese answer...")
        self.setStyleSheet("""
            QLineEdit {
                font-size: 20px;
                padding: 10px;
                border: 1px solid #ccc;
                border-radius: 5px;
                background-color: white;
            }
            QLineEdit:focus {
                border: 2px solid #4CAF50;
            }
        """)

    def get_answer(self):
        """Get the current answer text"""
        return self.text().strip()

    def clear_answer(self):
        """Clear the current answer"""
        self.clear() 