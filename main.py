import sys
import json
import os
from PyQt5.QtWidgets import (
    QApplication, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QWidget,
    QLineEdit, QMessageBox, QGroupBox, QGraphicsOpacityEffect
)
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtCore import Qt

class ImageLabelingApp(QWidget):
    def __init__(self):
        super().__init__()

        self.image_folder = "data/image"
        self.label_folder_eng = "data/text_eng"
        self.label_folder_vn = "data/text_vn"

        # Load and sort image files
        self.image_files = sorted([f for f in os.listdir(self.image_folder) if f.endswith(('.png', '.jpg', '.jpeg'))])
        self.current_index = 0

        if not self.image_files:
            QMessageBox.critical(self, "Error", "No images found in the 'image' folder!")
            sys.exit()

        # UI Elements
        self.image_label = QLabel(self)
        self.answer_input = QLineEdit(self)
        self.answer_input.setPlaceholderText("Enter Vietnamese answer...")

        self.next_button = QPushButton("Next")
        self.next_button.clicked.connect(self.next_image)

        self.back_button = QPushButton("Back")
        self.back_button.clicked.connect(self.prev_image)

        # English Group Box
        # English Group Box
        self.english_group_box = QGroupBox()
        self.english_group_box.setContentsMargins(0, 0, 0, 0)  # Remove internal margins
        self.english_group_box.setStyleSheet("""
            QGroupBox {
                border: none;  /* Remove the default border */
                margin-top: 0; /* Remove top margin */
                padding-top: 0; /* Remove top padding */
                background: transparent; /* Make background transparent */
            }
        """)
        
        english_layout = QVBoxLayout()
        english_layout.setContentsMargins(10, 0, 10, 10)  # Adjust these values as needed
        english_layout.setSpacing(0)  # Minimize spacing between elements
        
        english_title = QLabel("English")
        english_title.setStyleSheet("""
            font-size: 34px; 
            font-weight: bold; 
            color: #333;
            background: transparent;
        """)

        # Apply opacity effect to the entire group box
        opacity_effect = QGraphicsOpacityEffect()
        opacity_effect.setOpacity(0.7)
        self.english_group_box.setGraphicsEffect(opacity_effect)

        english_layout.addWidget(english_title)
        self.english_content = QLabel()
        self.english_content.setTextFormat(Qt.RichText)
        self.english_content.setStyleSheet("""
            font-size: 24px; 
            color: #000;
            background: transparent;
        """)  # Adjusted style
        english_layout.addWidget(self.english_content)
        self.english_group_box.setLayout(english_layout)

        # Apply styles
        self.setStyleSheet("""
            QWidget {
                background-color: #f0f0f0;
            }
            QLabel {
                font-size: 24px;  /* Increased font size */
                color: #333;
            }
            QLineEdit {
                font-size: 20px;  /* Increased font size */
                padding: 10px;  /* Increased padding */
                border: 1px solid #ccc;
                border-radius: 5px;
            }
            QPushButton {
                font-size: 20px;  /* Increased font size */
                padding: 15px;  /* Increased padding */
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QGroupBox {
                font-size: 24px;  /* Increased font size */
                font-weight: bold;
                margin-top: 20px;
                background-color: rgba(255, 255, 255, 0.7); /* Semi-transparent background */
            }
        """)

        # Layout
        # Layout
        image_layout = QVBoxLayout()
        image_layout.setContentsMargins(0, 0, 0, 0)  # Remove margins around image
        image_layout.addWidget(self.image_label)
        image_layout.addStretch()

        question_layout = QVBoxLayout()
        question_layout.setContentsMargins(0, 0, 0, 0)  # Remove all margins
        question_layout.setSpacing(10)  # Adjust spacing between elements
        question_layout.setAlignment(Qt.AlignTop | Qt.AlignRight)  # Align to top and right
        question_layout.addWidget(self.english_group_box, 0, Qt.AlignTop | Qt.AlignRight)  # Explicitly align the group box
        question_layout.addWidget(self.answer_input)
        question_layout.addWidget(self.back_button)
        question_layout.addWidget(self.next_button)
        question_layout.addStretch()

        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)  # Add margins to main layout instead
        main_layout.setSpacing(20)  # Adjust spacing between image and question section
        main_layout.addLayout(image_layout, 1)
        main_layout.addLayout(question_layout, 1)  # Give the question layout a stretch factor
        self.setLayout(main_layout)

        self.setWindowTitle("Image Labeling Tool")
        self.load_image()  # Load first image

    def load_image(self):
        """ Load and display the current image along with its question and answer. """
        if self.current_index < len(self.image_files):
            image_name = self.image_files[self.current_index]
            image_path = os.path.join(self.image_folder, image_name)
            json_path_eng = os.path.join(self.label_folder_eng, image_name.replace(".png", ".json").replace(".jpg", ".json").replace(".jpeg", ".json"))

            if os.path.exists(json_path_eng):
                with open(json_path_eng, "r", encoding="utf-8") as f:
                    data = json.load(f)
                question_text = data.get("question_eng", "No question available")
                answer_text = data.get("answer_eng", "No answer available")
            else:
                question_text = "No question available"
                answer_text = "No answer available"

            # Load Image
            if os.path.exists(image_path):
                pixmap = QPixmap(image_path)
                self.image_label.setPixmap(pixmap)
                self.image_label.setScaledContents(True)
                self.image_label.setFixedSize(600, 600)  # Increased image size
            else:
                self.image_label.setText("Image not found")

            # Update English content
            self.english_content.setText(f"<b>Question (EN):</b> {question_text}<br><b>Answer (EN):</b> {answer_text}")

            # Clear Input
            self.answer_input.setText("")

    def next_image(self):
        """ Save input label and move to the next image """
        if self.current_index < len(self.image_files):
            answer_text = self.answer_input.text().strip()
            image_name = self.image_files[self.current_index]
            json_path_vn = os.path.join(self.label_folder_vn, image_name.replace(".png", ".json").replace(".jpg", ".json").replace(".jpeg", ".json"))

            # Save Answer
            if answer_text:
                self.save_json(json_path_vn, answer_text)
            else:
                QMessageBox.warning(self, "Warning", "Please enter a Vietnamese answer before proceeding.")
                return  # Prevent moving forward if input is empty

            self.current_index += 1  # Move to next image
            if self.current_index < len(self.image_files):
                self.load_image()
            else:
                QMessageBox.information(self, "Completed", "All images have been labeled!")
                self.close()  # Close app when done

    def prev_image(self):
        """ Move back to the previous image """
        if self.current_index > 0:
            self.current_index -= 1
            self.load_image()

    def save_json(self, file_path, answer_vn):
        """ Save labeled data to a JSON file in text_vn/ """
        os.makedirs(self.label_folder_vn, exist_ok=True)
        data = {
            "question_vn": self.english_content.text().split("<br>")[1].replace("<b>Question (EN):</b> ", ""),
            "answer_vn": answer_vn
        }
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

# Run Application
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ImageLabelingApp()
    window.show()
    sys.exit(app.exec_())