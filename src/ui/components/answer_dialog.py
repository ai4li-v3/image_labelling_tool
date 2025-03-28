from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QLabel, 
                           QTextEdit, QPushButton, QHBoxLayout)
from PyQt5.QtCore import Qt

class AnswerEditDialog(QDialog):
    """Dialog for editing an answer"""
    
    def __init__(self, answer_text="", parent=None):
        super().__init__(parent)
        self.answer_text = answer_text
        self.init_ui()
        
    def init_ui(self):
        """Initialize the UI"""
        self.setWindowTitle("Chỉnh sửa câu trả lời")
        self.setMinimumSize(400, 200)
        
        # Main layout
        layout = QVBoxLayout(self)
        
        # Instruction label
        label = QLabel("Nhập câu trả lời:")
        layout.addWidget(label)
        
        # Answer text edit
        self.text_edit = QTextEdit()
        self.text_edit.setText(self.answer_text)
        self.text_edit.setPlaceholderText("Nhập câu trả lời tại đây...")
        layout.addWidget(self.text_edit)
        
        # Buttons
        btn_layout = QHBoxLayout()
        
        self.cancel_btn = QPushButton("Hủy")
        self.cancel_btn.clicked.connect(self.reject)
        
        self.save_btn = QPushButton("Lưu")
        self.save_btn.clicked.connect(self.accept)
        self.save_btn.setDefault(True)
        
        btn_layout.addWidget(self.cancel_btn)
        btn_layout.addWidget(self.save_btn)
        
        layout.addLayout(btn_layout)
        
    def get_answer(self):
        """Get the entered answer text"""
        return self.text_edit.toPlainText().strip() 