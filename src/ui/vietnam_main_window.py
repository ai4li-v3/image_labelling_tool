import os
import sys
import json
import logging
import uuid
from datetime import datetime
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QMessageBox, QPushButton, QLabel, QComboBox
from PyQt5.QtCore import Qt

logger = logging.getLogger(__name__)

# Using absolute imports instead of relative
from src.ui.components.image_viewer import ImageViewer
from src.ui.components.navigation import NavigationButtons
from src.ui.components.title_display import TitleDisplay
from src.ui.components.vietnamese_question_list import VietnameseQuestionList

class VietnamMainWindow(QWidget):
    """Main window for Vietnamese-only mode"""
    
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
        self.label_folder = "data/labels"
        
        # Create directories if they don't exist
        os.makedirs(self.image_folder, exist_ok=True)
        os.makedirs(self.label_folder, exist_ok=True)

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
        self.question_list = VietnameseQuestionList()
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

        # Setup right side layout with increased space for questions
        right_layout = QVBoxLayout()
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(20)
        right_layout.setAlignment(Qt.AlignTop | Qt.AlignRight)
        
        # Add the question list with more vertical space
        right_layout.addWidget(self.question_list, 1)
        
        # Add navigation buttons
        right_layout.addWidget(self.navigation)
        
        # Add layouts to content layout - give more space to the question list
        content_layout.addLayout(image_layout, 1)
        content_layout.addLayout(right_layout, 1)

        # Add content layout to main layout
        main_layout.addLayout(content_layout)
        
        self.setLayout(main_layout)
        self.setWindowTitle("Vietnamese Image Labeling Tool - Câu Hỏi")
        self.setMinimumSize(1200, 800)
        self.apply_styles()

    def connect_signals(self):
        """Connect component signals to slots"""
        self.navigation.next_clicked.connect(self.next_image)
        self.navigation.back_clicked.connect(self.prev_image)
        self.question_list.content_changed.connect(self._on_content_changed)
        # Connect the question_confirmed signal to trigger save_current_data
        self.question_list.question_confirmed.connect(self._on_question_confirmed)

    def apply_styles(self):
        """Apply global styles to the main window"""
        self.setStyleSheet("""
            QWidget {
                background-color: #f0f0f0;
                font-family: Arial, sans-serif;
            }
            QLabel {
                font-size: 14px;
            }
            QPushButton {
                padding: 6px 12px;
                background-color: #4a90e2;
                color: white;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #357ab7;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
            QTextEdit, QLineEdit {
                border: 1px solid #ccc;
                border-radius: 4px;
                padding: 6px;
                background-color: white;
            }
            QListWidget {
                border: 1px solid #ccc;
                border-radius: 4px;
                background-color: white;
            }
        """)

    def load_current_image(self):
        """Load and display the current image and its data"""
        if self.current_index < len(self.image_files):
            image_name = self.image_files[self.current_index]
            image_path = os.path.join(self.image_folder, image_name)
            base_name = image_name.rsplit('.', 1)[0]
            
            json_path = os.path.join(self.label_folder, f"{base_name}.json")

            # Check if image is already labeled
            is_labeled = os.path.exists(json_path)
            status_text = "LABELED" if is_labeled else "UNLABELED"
            
            # Update title display with status
            self.title_display.set_image_name(image_path, status_text)

            # Load question data if exists
            if is_labeled:
                try:
                    with open(json_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    # Lấy nguồn ảnh từ file JSON
                    image_source = data.get('image_source', 'image_crowdsourcing')
                    
                    questions = data.get('questions', [])
                    # Truyền cả nguồn ảnh và câu hỏi vào component
                    self.question_list.set_questions(questions, image_source)
                except Exception as e:
                    logger.error(f"Error loading label data: {str(e)}")
                    self.question_list.clear()
            else:
                self.question_list.clear()

            # Update UI
            self.image_viewer.load_image(image_path)

            # Update navigation buttons
            self.navigation.set_back_enabled(self.current_index > 0)
            self.navigation.set_next_enabled(True)

            # Update window title with status
            self.setWindowTitle(f"Vietnamese Image Labeling Tool - Câu Hỏi - {status_text}")

    def save_current_data(self):
        """Save the current data to a JSON file
        
        Returns:
            bool: True if save was successful, False otherwise
        """
        logger.info("Starting save_current_data...")
        
        if not self.question_list.has_questions():
            # This will already handle the validation of confirmed questions
            logger.warning("No questions to save - has_questions returned False")
            return False

        original_questions = self.question_list.get_questions()
        logger.info(f"Original questions to save: {original_questions}")
        
        # Format questions according to the specified structure with the exact field order
        formatted_questions = []
        for question in original_questions:
            # Create a dictionary with ordered keys to ensure they appear in the correct order in JSON
            answers = []
            if question.get('answerable', 0) == 1 and 'answers' in question and question['answers']:
                answer_text = question['answers'][0].get('answer_text', '')
                if answer_text:
                    answers = [answer_text]
            else:
                # Default answer for unanswerable questions
                answers = ["Không thể trả lời được câu hỏi dựa vào thông tin trong ảnh"]
                
            # Replace source value if it's self_collected
            qa_source = question.get('source', 'manually_annotated')
            if qa_source == 'self_collected':
                qa_source = 'manually_collected'
                
            # Use OrderedDict to maintain the exact field order in the JSON output
            from collections import OrderedDict
            formatted_question = OrderedDict([
                ("question_id", question.get('question_id', 1)),
                ("question", question.get('question', '')),
                ("question_type", self.question_list.question_type_combo.currentText()),  # Use display text instead of data value
                ("answerable", question.get('answerable', 0)),
                ("answers", answers),
                ("tags", question.get('tags', [])),
                ("qa_source", qa_source)  # Renamed from source to qa_source and updated value
            ])
            
            formatted_questions.append(formatted_question)
        
        logger.info(f"Formatted questions: {formatted_questions}")
        
        image_name = self.image_files[self.current_index]
        base_name = image_name.rsplit('.', 1)[0]
        
        logger.info(f"Saving for image: {image_name}, base name: {base_name}")
        
        # Path for JSON file
        json_path = os.path.join(
            self.label_folder,
            base_name + '.json'
        )
        
        logger.info(f"JSON path: {json_path}")
        logger.info(f"Label folder exists: {os.path.exists(self.label_folder)}")
        logger.info(f"Label folder path: {os.path.abspath(self.label_folder)}")

        # Get the selected image source type and update if it's self_collected
        selected_source = self.question_list.get_image_source()
        if selected_source == 'self_collected':
            selected_source = 'manually_collected'
        logger.info(f"Selected image source: {selected_source}")

        # Create the data structure for JSON following the exact format from the example
        from collections import OrderedDict
        data = OrderedDict([
            ('image_id', base_name),
            ('image_source', selected_source),
            ('questions', formatted_questions)
        ])

        try:
            # Save JSON file
            logger.info(f"Attempting to save JSON to: {json_path}")
            os.makedirs(os.path.dirname(json_path), exist_ok=True)  # Ensure directory exists
            
            with open(json_path, 'w', encoding='utf-8') as f:
                json_content = json.dumps(data, indent=2, ensure_ascii=False)
                f.write(json_content)
                logger.info(f"Successfully wrote JSON file: {json_path}")
            
            # Update status to LABELED
            self.title_display.set_image_name(
                os.path.join(self.image_folder, image_name), 
                "LABELED"
            )
            
            # Update window title
            self.setWindowTitle(f"Vietnamese Image Labeling Tool - Câu Hỏi - LABELED")
            
            # Show confirmation message
            QMessageBox.information(
                self,
                "Đã lưu",
                "Dữ liệu đã được lưu thành công!"
            )
            
            # Reset modified flag
            self.question_list.modified = False
            logger.info("Save completed successfully!")
            
            return True
        except Exception as e:
            logger.error(f"Error saving data: {str(e)}")
            logger.exception("Detailed error:")
            QMessageBox.critical(
                self, 
                "Error", 
                f"Failed to save label data: {str(e)}"
            )
            return False

    def next_image(self):
        """Handle next image button click"""
        # First check if we have questions
        if self.question_list.has_questions():
            # If content was modified, ask about saving
            if self.question_list.is_modified():
                reply = QMessageBox.question(
                    self,
                    "Save Changes",
                    "Do you want to save your changes?",
                    QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel
                )
                
                if reply == QMessageBox.Cancel:
                    return
                elif reply == QMessageBox.Yes:
                    if not self.save_current_data():
                        return
            
            # Move to next image
            if self.current_index < len(self.image_files) - 1:
                self.current_index += 1
                self.load_current_image()
            else:
                QMessageBox.information(self, "Completed", "All images have been labeled!")
                self.close()
        else:
            # No questions with content, ask if user wants to skip
            if QMessageBox.question(
                self,
                "No Questions",
                "You haven't added any questions for this image. Do you want to skip it anyway?",
                QMessageBox.Yes | QMessageBox.No
            ) == QMessageBox.Yes:
                if self.current_index < len(self.image_files) - 1:
                    self.current_index += 1
                    self.load_current_image()
                else:
                    QMessageBox.information(self, "Completed", "All images have been labeled!")
                    self.close()

    def prev_image(self):
        """Handle previous image button click"""
        # Check for unsaved changes
        if self.question_list.is_modified():
            reply = QMessageBox.question(
                self,
                "Save Changes",
                "Do you want to save your changes?",
                QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel
            )
            
            if reply == QMessageBox.Cancel:
                return
            elif reply == QMessageBox.Yes:
                if not self.save_current_data():
                    return
        
        # Move to previous image
        if self.current_index > 0:
            self.current_index -= 1
            self.load_current_image()

    def _on_content_changed(self):
        """Handle content changes in the question list"""
        # Update status if needed
        image_name = self.image_files[self.current_index]
        base_name = image_name.rsplit('.', 1)[0]
        json_path = os.path.join(self.label_folder, f"{base_name}.json")
        
        status = "MODIFIED" if os.path.exists(json_path) else "UNLABELED*"
        
        # Use set_image_name instead of set_status
        current_image_path = os.path.join(self.image_folder, self.image_files[self.current_index])
        self.title_display.set_image_name(current_image_path, status) 
        
        # Update window title
        self.setWindowTitle(f"Vietnamese Image Labeling Tool - Câu Hỏi - {status}") 

    def _on_question_confirmed(self):
        """Handle question confirmed signal by saving the data and moving to next image"""
        logger.info("Question confirmed, initiating save...")
        if self.save_current_data():
            logger.info("Save successful, moving to next image...")
            # Move to next image if available
            if self.current_index < len(self.image_files) - 1:
                self.next_image()
            else:
                QMessageBox.information(
                    self,
                    "End of Images",
                    "You have reached the end of the image set."
                ) 