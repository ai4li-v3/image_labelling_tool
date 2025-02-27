from PyQt5.QtWidgets import QLabel
from PyQt5.QtCore import Qt

class TitleDisplay(QLabel):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        """Initialize the title display UI"""
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #2c3e50;
                padding: 10px;
                background-color: #ecf0f1;
                border-radius: 5px;
                margin: 5px;
            }
        """)

    def set_image_name(self, image_path):
        """Display the current image name without extension"""
        if image_path:
            # Extract filename without extension
            image_name = image_path.split('/')[-1].rsplit('.', 1)[0]
            self.setText(f"Image: {image_name}")
        else:
            self.setText("No image selected") 