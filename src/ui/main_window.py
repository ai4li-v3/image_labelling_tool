import os
import sys
import json
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QMessageBox
from PyQt5.QtCore import Qt

from .components.image_viewer import ImageViewer
from .components.answer_input import AnswerInput
from .components.navigation import NavigationButtons
from .components.english_display import EnglishDisplay

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_data_paths()
        self.load_image_files()
        self.init_ui()
        self.connect_signals()
        self.load_current_image()

    def setup_data_paths(self):
        """Setup data directory paths"""
        self.image_folder = "data/image"
        self.label_folder_eng = "data/text_eng"
        self.label_folder_vn = "data/text_vn"
        
        # Create directories if they don't exist
        os.makedirs(self.image_folder, exist_ok=True)
        os.makedirs(self.label_folder_eng, exist_ok=True)
        os.makedirs(self.label_folder_vn, exist_ok=True)

    def load_image_files(self):
        """Load and validate image files"""
        self.image_files = sorted([
            f for f in os.listdir(self.image_folder)
            if f.lower().endswith(('.png', '.jpg', '.jpeg'))
        ])
        self.current_index = 0

        if not self.image_files:
            QMessageBox.critical(self, "Error", "No images found in the 'data/image' folder!")
            sys.exit()

    def init_ui(self):
        """Initialize the main UI components"""
        # Create components
        self.image_viewer = ImageViewer()
        self.english_display = EnglishDisplay()
        self.answer_input = AnswerInput()
        self.navigation = NavigationButtons()

        # Setup layouts
        image_layout = QVBoxLayout()
        image_layout.setContentsMargins(0, 0, 0, 0)
        image_layout.addWidget(self.image_viewer)
        image_layout.addStretch()

        question_layout = QVBoxLayout()
        question_layout.setContentsMargins(0, 0, 0, 0)
        question_layout.setSpacing(10)
        question_layout.setAlignment(Qt.AlignTop | Qt.AlignRight)
        question_layout.addWidget(self.english_display)
        question_layout.addWidget(self.answer_input)
        question_layout.addWidget(self.navigation)
        question_layout.addStretch()

        # Main layout
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(20)
        main_layout.addLayout(image_layout, 1)
        main_layout.addLayout(question_layout, 1)
        
        self.setLayout(main_layout)
        self.setWindowTitle("Image Labeling Tool")
        self.apply_styles()

    def connect_signals(self):
        """Connect component signals to slots"""
        self.navigation.next_clicked.connect(self.next_image)
        self.navigation.back_clicked.connect(self.prev_image)

    def apply_styles(self):
        """Apply global styles to the main window"""
        self.setStyleSheet("""
            QWidget {
                background-color: #f0f0f0;
            }
        """)

    def load_current_image(self):
        """Load and display the current image and its data"""
        if self.current_index < len(self.image_files):
            image_name = self.image_files[self.current_index]
            image_path = os.path.join(self.image_folder, image_name)
            json_path_eng = os.path.join(
                self.label_folder_eng,
                image_name.rsplit('.', 1)[0] + '.json'
            )

            # Load English data
            if os.path.exists(json_path_eng):
                with open(json_path_eng, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                question_text = data.get('question_eng', 'No question available')
                answer_text = data.get('answer_eng', 'No answer available')
            else:
                question_text = 'No question available'
                answer_text = 'No answer available'

            # Update UI
            self.image_viewer.load_image(image_path)
            self.english_display.set_content(question_text, answer_text)
            self.answer_input.clear_answer()

            # Update navigation buttons
            self.navigation.set_back_enabled(self.current_index > 0)
            self.navigation.set_next_enabled(True)

    def save_current_answer(self):
        """Save the current answer to a JSON file"""
        answer_text = self.answer_input.get_answer()
        if not answer_text:
            return False

        image_name = self.image_files[self.current_index]
        json_path_vn = os.path.join(
            self.label_folder_vn,
            image_name.rsplit('.', 1)[0] + '.json'
        )

        data = {
            'question_vn': 'Vietnamese question',  # You might want to modify this
            'answer_vn': answer_text
        }

        with open(json_path_vn, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

        return True

    def next_image(self):
        """Handle next image button click"""
        if not self.save_current_answer():
            QMessageBox.warning(self, "Warning", "Please enter a Vietnamese answer before proceeding.")
            return

        if self.current_index < len(self.image_files) - 1:
            self.current_index += 1
            self.load_current_image()
        else:
            QMessageBox.information(self, "Completed", "All images have been labeled!")
            self.close()

    def prev_image(self):
        """Handle previous image button click"""
        if self.current_index > 0:
            self.current_index -= 1
            self.load_current_image() 