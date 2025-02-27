from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QFrame)
from PyQt5.QtCore import Qt

class ConfirmationDialog(QDialog):
    def __init__(self, eng_question, eng_answer, vn_question, vn_answer, parent=None):
        super().__init__(parent)
        self.init_ui(eng_question, eng_answer, vn_question, vn_answer)

    def init_ui(self, eng_question, eng_answer, vn_question, vn_answer):
        """Initialize the confirmation dialog UI"""
        self.setWindowTitle("Confirm Translation")
        self.setModal(True)
        self.setStyleSheet("""
            QDialog {
                background-color: #f5f6fa;
                min-width: 500px;
                max-width: 600px;
            }
            QLabel.header {
                font-size: 20px;
                font-weight: bold;
                color: #2c3e50;
                padding: 5px;
            }
            QLabel.content {
                font-size: 14px;
                color: #2c3e50;
                padding: 8px;
                background-color: white;
                border: 1px solid #bdc3c7;
                border-radius: 5px;
                margin: 2px;
            }
            QLabel.label {
                font-size: 14px;
                font-weight: bold;
                margin-top: 5px;
            }
            QPushButton {
                font-size: 14px;
                padding: 8px 25px;
                border-radius: 5px;
                border: none;
                min-width: 120px;
                margin: 5px;
            }
            QPushButton#confirm {
                background-color: #2ecc71;
                color: white;
                font-weight: bold;
            }
            QPushButton#confirm:hover {
                background-color: #27ae60;
            }
            QPushButton#edit {
                background-color: #e74c3c;
                color: white;
                font-weight: bold;
            }
            QPushButton#edit:hover {
                background-color: #c0392b;
            }
        """)

        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(15, 15, 15, 15)

        # Title
        title = QLabel("Please Confirm Your Translation")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("""
            font-size: 22px;
            font-weight: bold;
            color: #2c3e50;
            padding: 5px;
            margin-bottom: 10px;
        """)
        layout.addWidget(title)

        # Question Section
        question_section = self._create_section(
            "Question Mapping",
            eng_question,
            vn_question,
            "Question"
        )
        layout.addWidget(question_section)

        # Answer Section
        answer_section = self._create_section(
            "Answer Mapping",
            eng_answer,
            vn_answer,
            "Answer"
        )
        layout.addWidget(answer_section)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)
        button_layout.setContentsMargins(0, 5, 0, 0)

        self.edit_button = QPushButton("← Edit")
        self.edit_button.setObjectName("edit")
        self.edit_button.clicked.connect(self.reject)

        self.confirm_button = QPushButton("Confirm →")
        self.confirm_button.setObjectName("confirm")
        self.confirm_button.clicked.connect(self.accept)
        self.confirm_button.setDefault(True)  # Make it the default button (responds to Enter key)

        button_layout.addStretch()
        button_layout.addWidget(self.edit_button)
        button_layout.addWidget(self.confirm_button)
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def _create_section(self, title, eng_content, vn_content, type_label):
        """Create a section with two pairs of labels"""
        section = QFrame()
        section.setFrameShape(QFrame.StyledPanel)
        section.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 8px;
                padding: 10px;
                margin: 3px;
            }
        """)
        
        layout = QVBoxLayout()
        layout.setSpacing(8)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Section title
        header = QLabel(title)
        header.setProperty("class", "header")
        layout.addWidget(header)

        # Content
        content_layout = QVBoxLayout()
        content_layout.setSpacing(8)

        # English content
        eng_layout = QVBoxLayout()
        eng_layout.setSpacing(3)
        eng_label = QLabel()
        eng_label.setProperty("class", "label")
        eng_label.setText(f'<span style="color: #e74c3c;">English</span> {type_label}:')
        eng_content_label = QLabel(eng_content)
        eng_content_label.setProperty("class", "content")
        eng_content_label.setWordWrap(True)
        eng_layout.addWidget(eng_label)
        eng_layout.addWidget(eng_content_label)

        # Vietnamese content
        vn_layout = QVBoxLayout()
        vn_layout.setSpacing(3)
        vn_label = QLabel()
        vn_label.setProperty("class", "label")
        vn_label.setText(f'<span style="color: #2ecc71;">Vietnamese</span> {type_label}:')
        vn_content_label = QLabel(vn_content)
        vn_content_label.setProperty("class", "content")
        vn_content_label.setWordWrap(True)
        vn_layout.addWidget(vn_label)
        vn_layout.addWidget(vn_content_label)

        content_layout.addLayout(eng_layout)
        content_layout.addLayout(vn_layout)
        layout.addLayout(content_layout)

        section.setLayout(layout)
        return section 