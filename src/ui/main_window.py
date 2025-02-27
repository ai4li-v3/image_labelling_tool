import os
import sys
import json
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QMessageBox
from PyQt5.QtCore import Qt

from .components.image_viewer import ImageViewer
from .components.navigation import NavigationButtons
from .components.english_display import EnglishDisplay
from .components.title_display import TitleDisplay
from .components.vietnamese_input import VietnameseInput
from .components.confirmation_dialog import ConfirmationDialog

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
        self.title_display = TitleDisplay()
        self.image_viewer = ImageViewer()
        self.english_display = EnglishDisplay()
        self.vietnamese_input = VietnameseInput()
        self.navigation = NavigationButtons()

        # Main vertical layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        # Add title at the top
        main_layout.addWidget(self.title_display)

        # Create horizontal layout for image and controls
        content_layout = QHBoxLayout()
        content_layout.setSpacing(20)

        # Setup image layout
        image_layout = QVBoxLayout()
        image_layout.setContentsMargins(0, 0, 0, 0)
        image_layout.addWidget(self.image_viewer)
        image_layout.addStretch()

        # Setup right side layout
        right_layout = QVBoxLayout()
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(20)
        right_layout.setAlignment(Qt.AlignTop | Qt.AlignRight)
        right_layout.addWidget(self.english_display)
        right_layout.addWidget(self.vietnamese_input)
        right_layout.addWidget(self.navigation)
        right_layout.addStretch()

        # Add layouts to content layout
        content_layout.addLayout(image_layout, 1)
        content_layout.addLayout(right_layout, 1)

        # Add content layout to main layout
        main_layout.addLayout(content_layout)
        
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
            base_name = image_name.rsplit('.', 1)[0]
            
            json_path_eng = os.path.join(self.label_folder_eng, f"{base_name}.json")
            json_path_vn = os.path.join(self.label_folder_vn, f"{base_name}.json")

            # Update title display
            self.title_display.set_image_name(image_path)

            # Load English data
            if os.path.exists(json_path_eng):
                with open(json_path_eng, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                question_text = data.get('question_eng', 'No question available')
                answer_text = data.get('answer_eng', 'No answer available')
            else:
                question_text = 'No question available'
                answer_text = 'No answer available'

            # Load Vietnamese data if exists
            if os.path.exists(json_path_vn):
                with open(json_path_vn, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                vn_question = data.get('question_vn', '')
                vn_answer = data.get('answer_vn', '')
                self.vietnamese_input.set_inputs(vn_question, vn_answer)
            else:
                self.vietnamese_input.clear_inputs()

            # Update UI
            self.image_viewer.load_image(image_path)
            self.english_display.set_content(question_text, answer_text)

            # Update navigation buttons
            self.navigation.set_back_enabled(self.current_index > 0)
            self.navigation.set_next_enabled(True)

    def save_current_answer(self):
        """Save the current answer to a JSON file"""
        if not self.vietnamese_input.has_both_inputs():
            QMessageBox.warning(
                self, 
                "Warning", 
                "Please enter both Vietnamese question and answer before proceeding."
            )
            return False

        inputs = self.vietnamese_input.get_inputs()
        image_name = self.image_files[self.current_index]
        json_path_vn = os.path.join(
            self.label_folder_vn,
            image_name.rsplit('.', 1)[0] + '.json'
        )

        data = {
            'question_vn': inputs['question'],
            'answer_vn': inputs['answer']
        }

        with open(json_path_vn, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

        return True

    def next_image(self):
        """Handle next image button click"""
        # First check if both inputs are provided
        if not self.vietnamese_input.has_both_inputs():
            QMessageBox.warning(
                self, 
                "Warning", 
                "Please enter both Vietnamese question and answer before proceeding."
            )
            return

        # Get current English and Vietnamese content
        eng_data = self.get_current_english_data()
        vn_data = self.vietnamese_input.get_inputs()

        # Show confirmation dialog
        dialog = ConfirmationDialog(
            eng_data['question'],
            eng_data['answer'],
            vn_data['question'],
            vn_data['answer'],
            self
        )

        if dialog.exec_() == ConfirmationDialog.Accepted:
            # Save and proceed if confirmed
            if self.save_current_answer():
                if self.current_index < len(self.image_files) - 1:
                    self.current_index += 1
                    self.load_current_image()
                else:
                    QMessageBox.information(self, "Completed", "All images have been labeled!")
                    self.close()

    def get_current_english_data(self):
        """Get the current English question and answer"""
        image_name = self.image_files[self.current_index]
        json_path_eng = os.path.join(
            self.label_folder_eng,
            image_name.rsplit('.', 1)[0] + '.json'
        )

        if os.path.exists(json_path_eng):
            with open(json_path_eng, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return {
                'question': data.get('question_eng', 'No question available'),
                'answer': data.get('answer_eng', 'No answer available')
            }
        return {
            'question': 'No question available',
            'answer': 'No answer available'
        }

    def prev_image(self):
        """Handle previous image button click"""
        if self.current_index > 0:
            self.current_index -= 1
            self.load_current_image() 