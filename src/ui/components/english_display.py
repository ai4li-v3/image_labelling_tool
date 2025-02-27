from PyQt5.QtWidgets import QGroupBox, QVBoxLayout, QLabel, QGraphicsOpacityEffect
from PyQt5.QtCore import Qt

class EnglishDisplay(QGroupBox):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        """Initialize the English display UI"""
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
        layout.setSpacing(0)

        # Create title label
        self.title_label = QLabel("English")
        self.title_label.setStyleSheet("""
            font-size: 34px;
            font-weight: bold;
            color: #333;
            background: transparent;
        """)

        # Create content label
        self.content_label = QLabel()
        self.content_label.setTextFormat(Qt.RichText)
        self.content_label.setStyleSheet("""
            font-size: 24px;
            color: #000;
            background: transparent;
        """)
        self.content_label.setWordWrap(True)

        # Add labels to layout
        layout.addWidget(self.title_label)
        layout.addWidget(self.content_label)
        self.setLayout(layout)

        # Apply opacity effect
        opacity_effect = QGraphicsOpacityEffect()
        opacity_effect.setOpacity(0.7)
        self.setGraphicsEffect(opacity_effect)

    def set_content(self, question, answer):
        """Set the English question and answer"""
        content = f"<b>Question (EN):</b> {question}<br><b>Answer (EN):</b> {answer}"
        self.content_label.setText(content)

    def clear_content(self):
        """Clear the content"""
        self.content_label.clear() 