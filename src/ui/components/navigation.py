from PyQt5.QtWidgets import QWidget, QHBoxLayout, QPushButton
from PyQt5.QtCore import pyqtSignal

class NavigationButtons(QWidget):
    next_clicked = pyqtSignal()
    back_clicked = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        """Initialize the navigation buttons UI"""
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        # Create buttons
        self.back_button = QPushButton("Back")
        self.next_button = QPushButton("Next")

        # Connect signals
        self.back_button.clicked.connect(self.back_clicked.emit)
        self.next_button.clicked.connect(self.next_clicked.emit)

        # Add buttons to layout
        layout.addWidget(self.back_button)
        layout.addWidget(self.next_button)

        self.setLayout(layout)
        self.apply_styles()

    def apply_styles(self):
        """Apply styles to the navigation buttons"""
        button_style = """
            QPushButton {
                font-size: 20px;
                padding: 15px;
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 5px;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
        """
        self.back_button.setStyleSheet(button_style)
        self.next_button.setStyleSheet(button_style)

    def set_back_enabled(self, enabled):
        """Enable/disable the back button"""
        self.back_button.setEnabled(enabled)

    def set_next_enabled(self, enabled):
        """Enable/disable the next button"""
        self.next_button.setEnabled(enabled) 