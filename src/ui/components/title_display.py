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
            .labeled {
                color: #27ae60;
            }
            .unlabeled {
                color: #c0392b;
            }
        """)

    def set_image_name(self, image_path, status):
        """Display the current image name and status"""
        if image_path:
            # Extract filename without extension
            image_name = image_path.split('/')[-1].rsplit('.', 1)[0]
            status_color = "#27ae60" if status == "LABELED" else "#c0392b"
            self.setText(f"Current Image: {image_name} <span style='color: {status_color}'>{status}</span>")
        else:
            self.setText("No image selected") 