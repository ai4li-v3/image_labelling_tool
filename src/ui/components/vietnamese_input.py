from PyQt5.QtWidgets import QGroupBox, QVBoxLayout, QLabel, QLineEdit, QGraphicsOpacityEffect
from PyQt5.QtCore import Qt

class VietnameseInput(QGroupBox):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        """Initialize the Vietnamese input UI"""
        self.setContentsMargins(0, 0, 0, 0)
        self.setStyleSheet("""
            QGroupBox {
                border: none;
                margin-top: 0;
                padding-top: 0;
                background: transparent;
            }
        """)

        layout = QVBoxLayout()
        layout.setContentsMargins(10, 0, 10, 10)
        layout.setSpacing(10)

        # Create title label
        self.title_label = QLabel("Vietnamese")
        self.title_label.setStyleSheet("""
            font-size: 34px;
            font-weight: bold;
            color: #333;
            background: transparent;
        """)

        # Create question input
        self.question_label = QLabel("Question (VN):")
        self.question_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #2c3e50;")
        self.question_input = QLineEdit()
        self.question_input.setPlaceholderText("Enter Vietnamese question...")
        
        # Create answer input
        self.answer_label = QLabel("Answer (VN):")
        self.answer_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #2c3e50;")
        self.answer_input = QLineEdit()
        self.answer_input.setPlaceholderText("Enter Vietnamese answer...")

        # Style the input fields
        input_style = """
            QLineEdit {
                font-size: 20px;
                padding: 10px;
                border: 1px solid #bdc3c7;
                border-radius: 5px;
                background-color: white;
                margin-bottom: 5px;
            }
            QLineEdit:focus {
                border: 2px solid #3498db;
            }
        """
        self.question_input.setStyleSheet(input_style)
        self.answer_input.setStyleSheet(input_style)

        # Add widgets to layout
        layout.addWidget(self.title_label)
        layout.addWidget(self.question_label)
        layout.addWidget(self.question_input)
        layout.addWidget(self.answer_label)
        layout.addWidget(self.answer_input)
        self.setLayout(layout)

        # Apply opacity effect
        opacity_effect = QGraphicsOpacityEffect()
        opacity_effect.setOpacity(0.9)
        self.setGraphicsEffect(opacity_effect)

    def get_inputs(self):
        """Get the current question and answer"""
        return {
            'question': self.question_input.text().strip(),
            'answer': self.answer_input.text().strip()
        }

    def set_inputs(self, question='', answer=''):
        """Set the question and answer inputs"""
        self.question_input.setText(question)
        self.answer_input.setText(answer)

    def clear_inputs(self):
        """Clear both inputs"""
        self.question_input.clear()
        self.answer_input.clear()

    def has_both_inputs(self):
        """Check if both question and answer are filled"""
        inputs = self.get_inputs()
        return bool(inputs['question'] and inputs['answer']) 