from PyQt5.QtWidgets import QLabel
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt

class ImageViewer(QLabel):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        """Initialize the image viewer UI"""
        self.setFixedSize(600, 600)
        self.setScaledContents(True)
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet("""
            QLabel {
                background-color: white;
                border: 1px solid #ccc;
                border-radius: 5px;
            }
        """)

    def load_image(self, image_path):
        """Load and display an image"""
        if image_path and image_path.strip():
            pixmap = QPixmap(image_path)
            if not pixmap.isNull():
                self.setPixmap(pixmap)
            else:
                self.setText("Error loading image")
        else:
            self.setText("No image available") 