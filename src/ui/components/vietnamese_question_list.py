from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                           QTextEdit, QPushButton, QListWidget, QListWidgetItem,
                           QComboBox, QCheckBox, QLineEdit, QInputDialog, QMessageBox,
                           QFrame, QGroupBox, QGridLayout)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QKeyEvent

import logging

logger = logging.getLogger(__name__)

# Maximum number of questions allowed per image
MAX_QUESTIONS = 1  # Giới hạn chỉ 1 câu hỏi

# Question type configuration - easy to modify later
QUESTION_TYPES = [
    "Existence Checking",
    "Others"
]

# Predefined tags for tag suggestions
PREDEFINED_TAGS = [
    "WATER_BOTTLE",
    "CUP",
    "WALLET"
]

class TagButton(QPushButton):
    """Custom button for displaying a selected tag with a remove option"""
    
    removed = pyqtSignal(str)
    
    def __init__(self, tag_text):
        super().__init__()
        self.tag = tag_text
        self.setText(f"{tag_text} ✕")
        self.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border-radius: 12px;
                padding: 4px 8px;
                margin: 2px;
                font-size: 12px;
                max-height: 24px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        self.clicked.connect(self._on_remove)
        
    def _on_remove(self):
        """Emit signal when tag is removed"""
        self.removed.emit(self.tag)

class TagSuggestionList(QListWidget):
    """List widget for displaying tag suggestions"""
    
    tag_selected = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.Popup)
        self.setStyleSheet("""
            QListWidget {
                border: 1px solid #bdc3c7;
                border-radius: 5px;
                background-color: white;
                font-size: 13px;
            }
            QListWidget::item {
                padding: 5px;
                border-bottom: 1px solid #ecf0f1;
            }
            QListWidget::item:selected {
                background-color: #3498db;
                color: white;
            }
            QListWidget::item:hover {
                background-color: #ecf0f1;
            }
        """)
        self.itemClicked.connect(self._on_item_clicked)
        
    def _on_item_clicked(self, item):
        """Emit signal when tag is selected"""
        self.tag_selected.emit(item.text())
        self.hide()

class VietnameseQuestionList(QWidget):
    """Component for displaying and editing Vietnamese questions"""
    
    # Signal emitted when any content changes
    content_changed = pyqtSignal()
    # Signal emitted when a question is confirmed and should be saved
    question_confirmed = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.questions = []
        self.modified = False
        self.image_source = "manually_collected"  # Default to "Manually Collected"
        self.init_ui()
        
        # Set default state after initialization
        QTimer.singleShot(100, self._setup_initial_state)
        
    def init_ui(self):
        """Initialize the UI components"""
        # Main layout - completely vertical with no nesting for main sections
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)  # Revert to original margins
        main_layout.setSpacing(10)  # Revert to original spacing
        
        # Set background color for the entire widget
        self.setStyleSheet("""
            background-color: #ebeef2;
            font-family: 'Segoe UI', 'Arial', sans-serif;
        """)
        
        # Image source section - at the top
        self._create_image_source_section(main_layout)
        
        # Question section - in the middle
        self._create_question_section(main_layout)
        
        # Answer section - after question
        self._create_answer_section(main_layout)
        
        # Create bottom section with confirmation buttons
        self._create_bottom_buttons(main_layout)

        # Set the layout
        self.setLayout(main_layout)
        
        # Khởi tạo câu hỏi mặc định
        self._create_default_question()
        
        # Cập nhật trạng thái UI
        self._update_ui_state()
        
    def _create_image_source_section(self, parent_layout):
        """Create the image source section at the top"""
        # Title
        title_label = QLabel("<h3>Thông Tin Ảnh</h3>")  # Smaller heading
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setMaximumHeight(30)  # Limit height
        title_label.setStyleSheet("color: #2c3e50; margin-bottom: 5px;")
        parent_layout.addWidget(title_label)
        
        # Image source section container with background
        image_source_container = QGroupBox()
        image_source_container.setStyleSheet("""
            QGroupBox {
                background-color: #f0f2f5;
                border-radius: 8px;
                border: 1px solid #ddd;
                margin-top: 0px;
                padding: 10px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
        """)
        image_source_layout = QVBoxLayout(image_source_container)
        image_source_layout.setContentsMargins(8, 8, 8, 8)  # Use smaller padding to avoid overlap
        image_source_layout.setSpacing(8)  # Use original spacing
        
        # Simple image source input in horizontal layout - without group box
        source_layout = QHBoxLayout()
        source_layout.setSpacing(10)
        source_layout.setContentsMargins(0, 0, 0, 0)  # Remove margins
        
        source_label = QLabel("Nguồn ảnh:")
        source_label.setStyleSheet("font-weight: bold; color: #2c3e50;")
        source_layout.addWidget(source_label)
        
        self.image_source_input = QComboBox()
        self.image_source_input.addItem("Manual Collected", "manually_collected")
        self.image_source_input.addItem("Image Crowdsourcing", "image_crowdsourcing")
        self.image_source_input.addItem("Filtered Dataset", "filtered_dataset")
        self.image_source_input.addItem("Others", "others")  # Add "Others" option
        self.image_source_input.setCurrentIndex(0)  # Always set default to "Manual Collected"
        self.image_source_input.setStyleSheet("""
            QComboBox {
                border: 1px solid #bdc3c7; 
                border-radius: 5px;
                padding: 5px 10px;
                background-color: white;
                min-width: 200px;
                min-height: 28px;
                font-size: 13px;
                color: #34495e;
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 20px;
                border-left: 1px solid #bdc3c7;
                border-top-right-radius: 5px;
                border-bottom-right-radius: 5px;
            }
            QComboBox:hover {
                border: 1px solid #3498db;
                background-color: #f8f9fa;
            }
            QComboBox QAbstractItemView {
                border: 1px solid #bdc3c7;
                border-radius: 5px;
                background-color: white;
                selection-background-color: #3498db;
                selection-color: white;
            }
        """)
        self.image_source_input.currentIndexChanged.connect(self._on_image_source_changed)
        source_layout.addWidget(self.image_source_input)
        
        # Add an asterisk with a note that it's pre-selected
        note_label = QLabel("* (Mặc định)")
        note_label.setStyleSheet("color: #7f8c8d; font-style: italic; font-size: 11px;")
        source_layout.addWidget(note_label)
        
        image_source_layout.addLayout(source_layout)
        parent_layout.addWidget(image_source_container)
        
        # Add a thin divider
        divider = QFrame()
        divider.setFrameShape(QFrame.HLine)
        divider.setFrameShadow(QFrame.Sunken)
        divider.setStyleSheet("background-color: #cccccc; margin-top: 5px;")
        divider.setMaximumHeight(1)
        parent_layout.addWidget(divider)
    
    def _create_question_section(self, parent_layout):
        """Create the question section"""
        # Question title
        question_title = QLabel("<h3>Câu Hỏi</h3>")  # Smaller heading
        question_title.setAlignment(Qt.AlignCenter)
        question_title.setMaximumHeight(30)  # Limit height
        question_title.setStyleSheet("color: #2c3e50; margin-bottom: 5px;")
        parent_layout.addWidget(question_title)
        
        # Question details group
        question_details_group = QGroupBox("Chi tiết câu hỏi")
        question_details_group.setStyleSheet("""
            QGroupBox { 
                font-weight: bold; 
                font-size: 14px; 
                margin-top: 3px;
                padding-top: 10px;
                background-color: #f0f2f5;
                border-radius: 8px;
                border: 1px solid #ddd;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                color: #2c3e50;
                min-height: 135px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: #3498db;
            }
            QLabel {
                font-weight: bold;
                margin-top: 0px;
                background: transparent;
                color: #2c3e50;
            }
            QLineEdit {
                border: 1px solid #bdc3c7;
                padding: 3px;
                background-color: white;
                min-height: 25px;
                border-radius: 5px;
                font-size: 13px;
            }
            QLineEdit:focus {
                border: 1px solid #3498db;
            }
            QComboBox {
                padding: 3px;
            }
        """)
        question_details_layout = QVBoxLayout(question_details_group)
        question_details_layout.setContentsMargins(8, 8, 8, 8)  # Revert to original padding
        question_details_layout.setSpacing(8)  # Revert to original spacing
        
        # Question text field with ID integrated on the same row
        question_header_layout = QHBoxLayout()
        question_header_layout.setSpacing(10)
        
        # Question label
        question_label = QLabel("Câu hỏi:")
        question_label.setMinimumWidth(60)
        question_header_layout.addWidget(question_label)
        
        # ID field made more compact
        id_label = QLabel("ID:")
        id_label.setMaximumWidth(20)
        question_header_layout.addWidget(id_label)
        
        self.question_id = QLineEdit("1")  # Luôn đặt ID = 1
        self.question_id.setReadOnly(True)
        self.question_id.setMaximumWidth(30)
        self.question_id.setStyleSheet("""
            background-color: #ecf0f1;
            padding: 1px;
            border-radius: 4px;
            font-weight: bold;
            text-align: center;
            border: 1px solid #bdc3c7;
        """)
        self.question_id.setAlignment(Qt.AlignCenter)
        question_header_layout.addWidget(self.question_id)
        
        # Help text for keyboard shortcuts (moved here to save space)
        help_text = QLabel("(Enter để xác nhận)")
        help_text.setStyleSheet("font-size: 11px; color: #7f8c8d; font-style: italic; font-weight: normal;")
        question_header_layout.addWidget(help_text)
        
        # Add stretch to push elements to the left
        question_header_layout.addStretch()
        
        # Add the header layout to the main layout
        question_details_layout.addLayout(question_header_layout)
        
        # Replace QTextEdit with QLineEdit for single line question input
        self.question_text = QLineEdit()
        self.question_text.setPlaceholderText("Nhập câu hỏi tại đây...")
        self.question_text.setStyleSheet("""
            background-color: white;
            border: 1px solid #bdc3c7;
            border-radius: 5px;
            padding: 8px;
            font-size: 13px;
        """)
        self.question_text.setMinimumHeight(32)  # Increased height for better usability
        self.question_text.textChanged.connect(self._on_content_changed)
        
        # Connect Enter key press to confirm question
        self.question_text.returnPressed.connect(self._confirm_question)
        
        question_details_layout.addWidget(self.question_text)
        
        # Question type selection - simplified layout
        type_layout = QHBoxLayout()
        type_layout.setSpacing(10)
        
        type_label = QLabel("Loại câu hỏi:")
        type_label.setStyleSheet("font-weight: bold;")
        type_layout.addWidget(type_label)
        
        self.question_type_combo = QComboBox()
        self.question_type_combo.addItem("Existence Checking", "existence_checking")
        self.question_type_combo.addItem("Others", "others")
        self.question_type_combo.setMinimumWidth(150)
        self.question_type_combo.setStyleSheet("""
            QComboBox {
                border: 1px solid #bdc3c7; 
                border-radius: 5px;
                padding: 5px 10px;
                background-color: white;
                min-height: 28px;
                font-size: 13px;
                color: #34495e;
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 20px;
                border-left: 1px solid #bdc3c7;
                border-top-right-radius: 3px;
                border-bottom-right-radius: 3px;
            }
            QComboBox:hover {
                border: 1px solid #3498db;
                background-color: #f8f9fa;
            }
            QComboBox QAbstractItemView {
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                background-color: white;
                selection-background-color: #3498db;
                selection-color: white;
            }
        """)
        type_layout.addWidget(self.question_type_combo)
        
        # Add stretch to push elements to the left
        type_layout.addStretch()
        
        question_details_layout.addLayout(type_layout)

        # Add to parent layout
        parent_layout.addWidget(question_details_group)
        
        # Add a thin divider
        divider = QFrame()
        divider.setFrameShape(QFrame.HLine)
        divider.setFrameShadow(QFrame.Sunken)
        divider.setMaximumHeight(1)
        divider.setStyleSheet("background-color: #cccccc; margin-top: 5px;")
        parent_layout.addWidget(divider)
    
    def _create_answer_section(self, parent_layout):
        """Create the answer section"""
        # Answer title
        answer_title = QLabel("<h3>Câu Trả Lời</h3>")  # Smaller heading
        answer_title.setAlignment(Qt.AlignCenter)
        answer_title.setMaximumHeight(30)  # Limit height
        answer_title.setStyleSheet("color: #2c3e50; margin-bottom: 5px;")
        parent_layout.addWidget(answer_title)
        
        # Answer details group
        answer_details_group = QGroupBox("Chi tiết câu trả lời")
        answer_details_group.setStyleSheet("""
            QGroupBox { 
                font-weight: bold;
                font-size: 14px; 
                margin-top: 3px;
                padding-top: 10px;
                background-color: #f0f2f5;
                border-radius: 8px;
                border: 1px solid #ddd;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                color: #2c3e50;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: #3498db;
            }
            QLabel {
                font-weight: bold;
                background: transparent;
                color: #2c3e50;
            }
            QLineEdit {
                border: 1px solid #bdc3c7;
                padding: 3px;
                background-color: white;
                min-height: 25px;
                border-radius: 5px;
                font-size: 13px;
            }
            QLineEdit:focus {
                border: 1px solid #3498db;
            }
            QCheckBox {
                color: #2c3e50;
            }
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
            }
            QCheckBox::indicator:checked {
                color: #27ae60;
            }
        """)
        answer_layout = QVBoxLayout(answer_details_group)
        answer_layout.setContentsMargins(8, 8, 8, 8)  # Revert to original padding
        answer_layout.setSpacing(8)  # Revert to original spacing
        
        # Answerable check - this will determine if the question can be answered based on image info
        answerable_layout = QHBoxLayout()
        
        self.can_answer_check = QCheckBox("Có thể trả lời dựa vào thông tin trong ảnh")
        self.can_answer_check.setChecked(False)  # Default to NOT answerable
        self.can_answer_check.setEnabled(True)  # Ensure the checkbox is enabled
        self.can_answer_check.stateChanged.connect(self._on_can_answer_changed)
        answerable_layout.addWidget(self.can_answer_check)
        
        answerable_layout.addStretch()
        answer_layout.addLayout(answerable_layout)
        
        # Answer input field
        answer_label = QLabel("Câu trả lời:")
        answer_layout.addWidget(answer_label)
        
        # Replace QTextEdit with QLineEdit for single line answer input
        self.answer_text = QLineEdit()
        self.answer_text.setPlaceholderText("Nhập câu trả lời tại đây...")
        self.answer_text.setStyleSheet("""
            background-color: white;
            border: 1px solid #bdc3c7;
            border-radius: 5px;
            padding: 8px;
            font-size: 13px;
        """)
        self.answer_text.setMinimumHeight(32)  # Increased height for better usability
        self.answer_text.textChanged.connect(self._on_content_changed)
        answer_layout.addWidget(self.answer_text)
        
        # Add to parent layout
        parent_layout.addWidget(answer_details_group)
        
        # Metadata section in a compact grid layout
        metadata_group = QGroupBox("Thông tin bổ sung")
        metadata_group.setStyleSheet("""
            QGroupBox { 
                font-weight: bold;
                font-size: 14px;
                margin-top: 3px;
                padding-top: 10px;
                background-color: #f0f2f5;
                border-radius: 8px;
                border: 1px solid #ddd;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                color: #2c3e50;
                min-height: 120px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: #3498db;
            }
            QLabel {
                font-weight: bold;
                background: transparent;
                color: #2c3e50;
            }
            QCheckBox {
                color: #2c3e50;
            }
            QLineEdit {
                border: 1px solid #bdc3c7;
                border-radius: 5px;
                padding: 3px;
                background-color: white;
                font-size: 13px;
            }
            QLineEdit:focus {
                border: 1px solid #3498db;
            }
        """)
        
        # Create a grid layout for metadata
        metadata_grid = QGridLayout(metadata_group)
        metadata_grid.setContentsMargins(8, 8, 8, 8)  # Revert to original padding
        metadata_grid.setSpacing(8)  # Revert to original spacing
        metadata_grid.setVerticalSpacing(5)  # Revert to original spacing
        
        # Tags input with search and multi-selection
        tags_label = QLabel("Tags:")
        metadata_grid.addWidget(tags_label, 0, 0)
        
        # Create a container for the tag search and display area
        tags_container = QWidget()
        tags_container.setStyleSheet("""
            background-color: white;
            border: 1px solid #bdc3c7;
            border-radius: 5px;
        """)
        tags_container_layout = QVBoxLayout(tags_container)
        tags_container_layout.setContentsMargins(5, 5, 5, 5)
        tags_container_layout.setSpacing(3)
        
        # Create flow layout for displaying selected tags
        self.tags_display = QWidget()
        self.tags_display.setMinimumHeight(30)  # Give the tags display area specifically more height
        self.tags_display_layout = QHBoxLayout(self.tags_display)
        self.tags_display_layout.setContentsMargins(0, 0, 0, 0)
        self.tags_display_layout.setSpacing(3)
        self.tags_display_layout.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        
        # Make the tags section wider by setting a minimum width
        tags_container.setMinimumWidth(270)
        
        # Create tag search field
        self.tags_search = QLineEdit()
        self.tags_search.setPlaceholderText("Tìm kiếm trong danh sách tags...")
        self.tags_search.setStyleSheet("""
            border: none;
            padding: 5px;
            background-color: transparent;
        """)
        self.tags_search.textChanged.connect(self._on_tag_search_changed)
        self.tags_search.returnPressed.connect(self._on_tag_search_enter)
        
        # Create tag suggestions list
        self.tag_suggestions = TagSuggestionList()
        self.tag_suggestions.tag_selected.connect(self._on_tag_selected)
        
        # Add the components to the container
        tags_container_layout.addWidget(self.tags_display)
        tags_container_layout.addWidget(self.tags_search)
        
        # Current selected tags list (in-memory)
        self.selected_tags = []
        
        metadata_grid.addWidget(tags_container, 0, 1, 1, 2)  # Span 2 columns
        
        # QA Source selection
        source_label = QLabel("Nguồn QA:")
        metadata_grid.addWidget(source_label, 1, 0)
        
        self.source_combo = QComboBox()
        self.source_combo.addItem("Manually Annotated", "manually_annotated")
        self.source_combo.addItem("Dataset Translation", "translated_from_dataset")
        self.source_combo.addItem("AI Generation", "generated_by_ai")
        self.source_combo.addItem("Others", "others")
        self.source_combo.setStyleSheet("""
            QComboBox {
                border: 1px solid #bdc3c7; 
                border-radius: 5px;
                padding: 5px 10px;
                background-color: white;
                min-height: 28px;
                font-size: 13px;
                color: #34495e;
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 20px;
                border-left: 1px solid #bdc3c7;
                border-top-right-radius: 3px;
                border-bottom-right-radius: 3px;
            }
            QComboBox:hover {
                border: 1px solid #3498db;
                background-color: #f8f9fa;
            }
            QComboBox QAbstractItemView {
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                background-color: white;
                selection-background-color: #3498db;
                selection-color: white;
            }
        """)
        metadata_grid.addWidget(self.source_combo, 1, 1, 1, 2)
        
        # Ẩn các widget câu trả lời cũ (để tương thích với mã hiện có)
        self.answer_list = QListWidget()
        self.answer_list.hide()
        self.add_answer_btn = QPushButton("Thêm câu trả lời")
        self.add_answer_btn.hide()
        self.edit_answer_btn = QPushButton("Sửa câu trả lời")
        self.edit_answer_btn.hide()
        self.mark_correct_btn = QPushButton("Đánh dấu đúng/sai")
        self.mark_correct_btn.hide()
        self.delete_answer_btn = QPushButton("Xóa câu trả lời")
        self.delete_answer_btn.hide()
        
        # Add to parent layout
        parent_layout.addWidget(metadata_group)
        
        # Add a thin divider
        divider = QFrame()
        divider.setFrameShape(QFrame.HLine)
        divider.setFrameShadow(QFrame.Sunken)
        divider.setMaximumHeight(1)
        divider.setStyleSheet("background-color: #cccccc; margin-top: 5px;")
        parent_layout.addWidget(divider)
    
    def _create_bottom_buttons(self, parent_layout):
        """Create the bottom section with confirm and cancel buttons"""
        # Create button layout
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(15)  # Revert to original spacing
        buttons_layout.setContentsMargins(0, 5, 0, 0)  # Revert to original margins
        
        # Add a stretch to push buttons to the center
        buttons_layout.addStretch()
        
        # Cancel button
        self.cancel_question_btn = QPushButton("✕  Hủy bỏ")
        self.cancel_question_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                font-weight: bold;
                padding: 6px 12px;
                font-size: 13px;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #c0392b;
                box-shadow: 0 2px 5px rgba(0,0,0,0.2);
            }
            QPushButton:pressed {
                background-color: #a93226;
            }
            QPushButton:disabled {
                background-color: #f5b7b1;
                color: #fadbd8;
            }
        """)
        self.cancel_question_btn.setMinimumHeight(34)  # Revert to original height
        self.cancel_question_btn.setMinimumWidth(120)  # Revert to original width
        self.cancel_question_btn.clicked.connect(self._cancel_question)
        self.cancel_question_btn.setEnabled(False)
        buttons_layout.addWidget(self.cancel_question_btn)
        
        # Confirm button
        self.confirm_question_btn = QPushButton("✓  Xác nhận")
        self.confirm_question_btn.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                color: white;
                font-weight: bold;
                padding: 6px 12px;
                font-size: 13px;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #27ae60;
                box-shadow: 0 2px 5px rgba(0,0,0,0.2);
            }
            QPushButton:pressed {
                background-color: #229954;
            }
            QPushButton:disabled {
                background-color: #a7dfb9;
                color: #e8f5e9;
            }
        """)
        self.confirm_question_btn.setMinimumHeight(34)  # Revert to original height
        self.confirm_question_btn.setMinimumWidth(120)  # Revert to original width
        self.confirm_question_btn.clicked.connect(self._confirm_question)
        self.confirm_question_btn.setEnabled(False)
        buttons_layout.addWidget(self.confirm_question_btn)
        
        # Add a stretch to push buttons to the center
        buttons_layout.addStretch()
        
        # Add button layout to parent layout
        parent_layout.addLayout(buttons_layout)
        
        # Connect signals for all UI elements
        self.question_text.textChanged.connect(self._on_content_changed)
        self.question_type_combo.currentIndexChanged.connect(self._on_content_changed)
        self.can_answer_check.stateChanged.connect(self._on_content_changed)
        self.tags_search.textChanged.connect(self._on_content_changed)
        self.source_combo.currentIndexChanged.connect(self._on_content_changed)
    
    def _create_default_question(self):
        """Tạo câu hỏi mặc định với ID = 1"""
        self.questions = [{
            'question_id': 1,
            'question': '',
            'question_type': 'existence_checking',  # Default to existence checking
            'answerable': 0,  # Default to 0 (not answerable)
            'source': 'manually_annotated',  # Default to "Manually Annotated"
            'answers': [{
                'answer_id': 1,
                'answer_text': 'Không thể trả lời được câu hỏi dựa vào thông tin trong ảnh',
                'is_correct': False
            }],
            'tags': [],
            'is_confirmed': False
        }]
        
        # Ensure image source is "Manual Collected" by default
        if not self.image_source:
            self.image_source = "manually_collected"
            if hasattr(self, 'image_source_input'):
                self.image_source_input.setCurrentIndex(0)
        
        # Cập nhật UI
        self._on_content_changed()
    
    def _update_ui_state(self):
        """Update UI state based on selection"""
        try:
            # Question details section - luôn bật vì chỉ có 1 câu hỏi cố định
            enabled = True
            
            # Kiểm tra xem câu hỏi có nội dung không
            question_has_text = bool(self.question_text.text().strip())
            
            # Check if all required fields are filled to enable confirm button
            can_confirm = question_has_text
            
            if hasattr(self, 'confirm_question_btn') and self.confirm_question_btn:
                self.confirm_question_btn.setEnabled(can_confirm)
            
            # Cancel button luôn được bật nếu có bất kỳ nội dung nào 
            has_any_content = bool(self.question_text.text().strip()) or bool(self.selected_tags) or bool(self.answer_text.text().strip())
            if hasattr(self, 'cancel_question_btn') and self.cancel_question_btn:
                self.cancel_question_btn.setEnabled(has_any_content)
            
            # Make sure can_answer_check is always enabled from the start
            if hasattr(self, 'can_answer_check') and self.can_answer_check:
                self.can_answer_check.setEnabled(True)

            # Always enable question type combo box
            if hasattr(self, 'question_type_combo') and self.question_type_combo:
                self.question_type_combo.setEnabled(True)
            
            # Always enable tags field from the start
            if hasattr(self, 'tags_search') and self.tags_search:
                self.tags_search.setEnabled(True)
                
            # Always enable source combo from the start
            if hasattr(self, 'source_combo') and self.source_combo:
                self.source_combo.setEnabled(True)
            
            # Set answer text area state based only on can_answer_check state, not on confirmation
            if hasattr(self, 'can_answer_check') and hasattr(self, 'answer_text'):
                can_answer = self.can_answer_check.isChecked()
                # Set read-only state based on can_answer
                self.answer_text.setReadOnly(not can_answer)
                # Always enable the answer field, regardless of confirmation status
                self.answer_text.setEnabled(True)
        except RuntimeError:
            # Bỏ qua lỗi khi các đối tượng đã bị xóa
            pass
    
    def _on_content_changed(self):
        """Handle changes to question properties"""
        if not self.questions:
            return
            
        question = self.questions[0]  # Luôn sử dụng câu hỏi đầu tiên
        current_text = self.question_text.text()
        question_text = current_text.strip()
        
        # Store original content if this is first edit and no original_text exists
        if question.get('is_confirmed', False) and 'original_text' not in question:
            question['original_text'] = question.get('question', '')
        
        # Confirm button is enabled only when question text, tags, and potentially answer are provided
        has_text = bool(question_text)
        has_tags = bool(self.selected_tags)
        is_answerable = self.can_answer_check.isChecked()
        has_answer = bool(self.answer_text.text().strip())
        
        # Enable confirm button based on validation rules
        can_confirm = has_text and has_tags and (not is_answerable or (is_answerable and has_answer))
        self.confirm_question_btn.setEnabled(can_confirm)
        
        # Chỉ bật nút hủy bỏ nếu có bất kỳ nội dung nào
        has_any_content = bool(question_text) or bool(self.selected_tags) or bool(self.answer_text.text().strip())
        self.cancel_question_btn.setEnabled(has_any_content)
        
        # Temporarily update the question text (will be fully saved on confirmation)
        question['question'] = current_text
        
        # Update the question type
        question['question_type'] = self.question_type_combo.currentData()
        
        # Cập nhật trạng thái có thể trả lời
        question['answerable'] = 1 if self.can_answer_check.isChecked() else 0
        
        # Tags are now updated in _add_tag and _remove_tag methods
        
        # Cập nhật nguồn QA - use data value instead of text
        question['source'] = self.source_combo.currentData()
        
        # Đảm bảo có mảng answers để tương thích với mã hiện có
        if 'answers' not in question:
            question['answers'] = []
            
        # Cập nhật thông tin câu trả lời
        answer_text = self.answer_text.text().strip()  # Use text() instead of toPlainText()
        
        # Đảm bảo có ít nhất một câu trả lời
        if not question['answers']:
            question['answers'].append({
                'answer_id': 1,
                'answer_text': answer_text,
                'is_correct': False  # Default to False since we removed the checkbox
            })
        else:
            # Cập nhật câu trả lời đầu tiên
            question['answers'][0]['answer_text'] = answer_text
        
        # Set modified flag
        self.modified = True
        self.content_changed.emit()
    
    def _confirm_question(self):
        """Confirm the current question after typing"""
        if not self.questions:
            return
        
        # Get the question text
        question_text = self.question_text.text().strip()  # Changed from toPlainText() to text()
        
        # Validate that all required fields are filled
        if not self._validate_and_check_required_fields():
            return
        
        # Get selected values for confirmation dialog
        question_type_text = self.question_type_combo.currentText()
        is_answerable = self.can_answer_check.isChecked()
        answer_text = self.answer_text.text().strip()
        if not is_answerable:
            answer_text = "Không thể trả lời được câu hỏi dựa vào thông tin trong ảnh"
        
        tags_text = ", ".join(self.selected_tags)
        qa_source_text = self.source_combo.currentText()
        image_source_text = self.image_source_input.currentText()
        
        # Create confirmation message with clear separation between sections and styling for labels/values
        confirmation_message = f"""<h3>Xác nhận thông tin</h3>
<div style="background-color: #f0f2f5; padding: 10px; border-radius: 5px; margin-bottom: 10px;">
<b style="color: #3498db;">IMAGE SOURCE:</b><br>
<b>Nguồn ảnh:</b> <i style="font-weight: normal;">{image_source_text}</i>
</div>

<div style="background-color: #f0f2f5; padding: 10px; border-radius: 5px; margin-bottom: 10px;">
<b style="color: #3498db;">QUESTION:</b><br>
<b>Question ID:</b> <i style="font-weight: normal;">1</i><br>
<b>Câu hỏi:</b> <i style="font-weight: normal;">{question_text}</i><br>
<b>Loại câu hỏi:</b> <i style="font-weight: normal;">{question_type_text}</i>
</div>

<div style="background-color: #f0f2f5; padding: 10px; border-radius: 5px; margin-bottom: 10px;">
<b style="color: #3498db;">ANSWER:</b><br>
<b>Có thể trả lời:</b> <i style="font-weight: normal;">{'Có' if is_answerable else 'Không'}</i><br>
<b>Câu trả lời:</b> <i style="font-weight: normal;">{answer_text}</i>
</div>

<div style="background-color: #f0f2f5; padding: 10px; border-radius: 5px; margin-bottom: 10px;">
<b style="color: #3498db;">METADATA:</b><br>
<b>Tags:</b> <i style="font-weight: normal;">{tags_text}</i><br>
<b>Nguồn QA:</b> <i style="font-weight: normal;">{qa_source_text}</i>
</div>

<p style="font-weight: bold; font-size: 14px; color: #e74c3c;">Bạn có chắc chắn muốn lưu những thông tin này không?</p>
"""
        
        # Create a custom message box for better looking buttons
        msgBox = QMessageBox(self)
        msgBox.setWindowTitle("Xác nhận thông tin")
        msgBox.setText(confirmation_message)
        msgBox.setTextFormat(Qt.RichText)
        
        # Create custom styled Yes button (green)
        yesButton = QPushButton("Có, lưu thông tin")
        yesButton.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                color: white;
                font-weight: bold;
                padding: 8px 16px;
                font-size: 14px;
                border: none;
                border-radius: 5px;
                min-width: 150px;
                min-height: 36px;
            }
            QPushButton:hover {
                background-color: #27ae60;
                box-shadow: 0 2px 5px rgba(0,0,0,0.2);
            }
            QPushButton:pressed {
                background-color: #229954;
            }
        """)
        
        # Create custom styled No button (red)
        noButton = QPushButton("Không, chỉnh sửa lại")
        noButton.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                font-weight: bold;
                padding: 8px 16px;
                font-size: 14px;
                border: none;
                border-radius: 5px;
                min-width: 150px;
                min-height: 36px;
            }
            QPushButton:hover {
                background-color: #c0392b;
                box-shadow: 0 2px 5px rgba(0,0,0,0.2);
            }
            QPushButton:pressed {
                background-color: #a93226;
            }
        """)
        
        # Add buttons to message box
        msgBox.addButton(yesButton, QMessageBox.YesRole)
        msgBox.addButton(noButton, QMessageBox.NoRole)
        msgBox.setDefaultButton(noButton)  # Make "No" the default for safety
        
        # Show the dialog and get response
        reply = msgBox.exec_()
        
        # Check which button was clicked
        if msgBox.clickedButton() != yesButton:
            return
        
        # Continue with confirmation process as before
        # Lưu trữ nội dung gốc để khôi phục khi cần
        self.questions[0]['original_text'] = question_text
        
        # Mark question as confirmed
        self.questions[0]['is_confirmed'] = True
        self.questions[0]['question'] = question_text
        
        # All input fields are already enabled from the start, so no need to enable them here
        # Just preserve the state of the answer field based on can_answer_check
        can_answer = self.can_answer_check.isChecked()
        self.answer_text.setReadOnly(not can_answer)
        
        # Set modified flag
        self.modified = True
        self.content_changed.emit()
        
        # Emit the question_confirmed signal to trigger save in the parent window
        self.question_confirmed.emit()
        
        # Update the UI state
        self._update_ui_state()
    
    def _cancel_question(self):
        """Cancel the current question edit and reset all fields"""
        if not self.questions:
            return
        
        # Confirm with user before canceling
        reply = QMessageBox.question(
            self,
            "Xác nhận hủy bỏ",
            "Bạn có chắc chắn muốn hủy bỏ? Tất cả thông tin sẽ bị xóa và không được lưu trữ.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.No:
            return
        
        # Reset tất cả các trường về trạng thái ban đầu bất kể trạng thái hiện tại
        # Xóa nội dung câu hỏi
        self.question_text.clear()
        
        # Xóa nội dung câu trả lời và set unanswerable by default
        self.answer_text.clear()
        self.can_answer_check.setChecked(False)  # Reset to NOT answerable
        
        # Đặt lại loại câu hỏi
        self.question_type_combo.setCurrentIndex(0)
        
        # Clear tags
        self._clear_tags()
        
        # Đặt lại các thông tin khác
        self.tags_search.clear()
        self.source_combo.setCurrentIndex(0)  # Default to "Manually Annotated"
        
        # Reset trạng thái câu hỏi
        question = self.questions[0]
        question['question'] = ''
        question['question_type'] = 'existence_checking'
        question['answerable'] = 0  # Default to NOT answerable
        question['tags'] = []
        question['source'] = 'manually_annotated'  # Default to "Manually Annotated"
        question['is_confirmed'] = False
        
        # Giữ lại mảng answers trống để tương thích với mã hiện có
        if 'answers' in question and question['answers']:
            question['answers'][0]['answer_text'] = 'Không thể trả lời được câu hỏi dựa vào thông tin trong ảnh'
            question['answers'][0]['is_correct'] = False
            
        # Thông báo cho người dùng
        QMessageBox.information(
            self,
            "Đã hủy bỏ",
            "Tất cả thông tin đã được xóa và không được lưu trữ."
        )
        
        # Cập nhật UI
        self._update_ui_state()
        
        # Reset modified flag
        self.modified = False
    
    def set_questions(self, questions, image_source=""):
        """Set questions data from loaded file
        
        Args:
            questions: List of question dictionaries
            image_source: The source of the image (optional)
        """
        # Set image source if provided, otherwise keep default "Manual Collected"
        if image_source:
            self.image_source = image_source
            
            # Tìm index tương ứng cho nguồn ảnh trong combobox
            found_index = -1
            for i in range(self.image_source_input.count()):
                if self.image_source_input.itemData(i) == image_source:
                    found_index = i
                    break
            
            # Nếu tìm thấy, cập nhật combobox
            if found_index >= 0:
                self.image_source_input.setCurrentIndex(found_index)
            else:
                # Mặc định là "Manual Collected" nếu không tìm thấy
                self.image_source_input.setCurrentIndex(0)
        else:
            # If no image source provided, ensure default is "Manual Collected"
            self.image_source = "manually_collected"
            self.image_source_input.setCurrentIndex(0)
        
        # Chỉ lấy câu hỏi đầu tiên hoặc tạo mới nếu không có
        if questions and len(questions) > 0:
            # Lấy câu hỏi đầu tiên và đảm bảo ID = 1
            self.questions = [questions[0]]
            self.questions[0]['question_id'] = 1
            
            # Set confirmed status if not already set
            if 'is_confirmed' not in self.questions[0]:
                self.questions[0]['is_confirmed'] = bool(self.questions[0].get('question', '').strip())
        else:
            # Tạo câu hỏi mặc định nếu không có
            self._create_default_question()
        
        self.modified = False
        
        # Hiển thị nội dung câu hỏi
        question = self.questions[0]
        self.question_text.setText(question.get('question', ''))
        
        # Set question type
        question_type = question.get('question_type', 'existence_checking')
        index = 0  # Default to first option (Existence Checking)
        
        # Find the matching index by data value
        for i in range(self.question_type_combo.count()):
            if self.question_type_combo.itemData(i) == question_type:
                index = i
                break
                
        self.question_type_combo.setCurrentIndex(index)
        
        # Hiển thị trạng thái có thể trả lời
        is_answerable = question.get('answerable', 0) == 1  # Default to 0 (not answerable)
        self.can_answer_check.setChecked(is_answerable)
        
        # Kích hoạt handler để cập nhật giao diện câu trả lời dựa vào trạng thái có thể trả lời
        self._on_can_answer_changed(Qt.Checked if is_answerable else Qt.Unchecked)
        
        # Load tags
        self._clear_tags()  # Clear existing tags first
        tags_list = question.get('tags', [])
        for tag in tags_list:
            self._add_tag(tag)
        
        # Hiển thị nguồn QA - find by data value
        source = question.get('source', 'manually_annotated')  # Default to "Manually Annotated"
        source_index = -1
        for i in range(self.source_combo.count()):
            if self.source_combo.itemData(i) == source:
                source_index = i
                break
        
        if source_index >= 0:
            self.source_combo.setCurrentIndex(source_index)
        else:
            # Default to first option if not found
            self.source_combo.setCurrentIndex(0)
            
        # Hiển thị câu trả lời
        if 'answers' in question and question['answers']:
            answer = question['answers'][0]
            self.answer_text.setText(answer.get('answer_text', ''))
        else:
            self.answer_text.clear()
        
        # Update UI state
        self._update_ui_state()
    
    def get_questions(self):
        """Get the current questions data"""
        return self.questions
    
    def get_image_source(self):
        """Get the current image source"""
        return self.image_source
    
    def set_image_source(self, source):
        """Set the image source
        
        Args:
            source: The source of the image
        """
        self.image_source = source
        
        # Tìm index tương ứng trong combobox
        for i in range(self.image_source_input.count()):
            if self.image_source_input.itemData(i) == source:
                self.image_source_input.setCurrentIndex(i)
                break
        
        self._update_ui_state()
    
    def is_modified(self):
        """Check if content has been modified"""
        return self.modified
    
    def clear(self):
        """Clear all questions and reset image source"""
        try:
            self._create_default_question()
            self.question_text.clear()
            self.answer_text.clear()
            self.can_answer_check.setChecked(False)  # Default to NOT answerable
            self._clear_tags()
            self.tags_search.clear()
            self.source_combo.setCurrentIndex(0)  # Reset to "Manually Annotated"
            
            # Default to "Manual Collected" instead of clearing
            self.image_source = "manually_collected"
            
            if hasattr(self, 'image_source_input') and self.image_source_input:
                self.image_source_input.setCurrentIndex(0)  # Đặt lại nguồn ảnh mặc định là "Manual Collected"
                
            self.modified = False
            self._update_ui_state()
        except RuntimeError:
            # Bỏ qua lỗi khi các đối tượng đã bị xóa
            pass
    
    def _validate_and_check_required_fields(self):
        """Validate that all required fields are filled"""
        # Check if question has content
        question_text = self.question_text.text().strip()
        if not question_text:
            QMessageBox.warning(
                self,
                "Câu hỏi trống",
                "Vui lòng nhập nội dung câu hỏi trước khi xác nhận."
            )
            self.question_text.setFocus()
            return False
        
        # Check if at least one tag is selected
        if not self.selected_tags:
            QMessageBox.warning(
                self,
                "Tags trống",
                "Vui lòng chọn ít nhất một tag trước khi xác nhận."
            )
            self.tags_search.setFocus()
            return False
            
        # If answerable is checked, check if answer has content
        if self.can_answer_check.isChecked():
            answer_text = self.answer_text.text().strip()
            if not answer_text:
                QMessageBox.warning(
                    self,
                    "Câu trả lời trống",
                    "Vì bạn đã đánh dấu rằng câu hỏi có thể trả lời, vui lòng nhập câu trả lời trước khi xác nhận."
                )
                self.answer_text.setFocus()
                return False
        
        # All validations passed
        return True

    def _on_image_source_changed(self):
        """Handle changes to the image source input field"""
        # Update the stored image source
        selected_source = self.image_source_input.currentData()
        self.image_source = selected_source
        
        # Check if question has text to determine if confirm button should be enabled
        question_has_text = bool(self.question_text.text().strip())
        self.confirm_question_btn.setEnabled(question_has_text)
        
        # Set modified flag
        self.modified = True
        self.content_changed.emit()
        
    def _update_actions(self):
        """Update the state of action buttons based on current selection and state"""
        # Check if there are questions and if a question is selected
        has_questions = len(self.questions) > 0
        
        # Enable confirm button based on question text only
        if has_questions:
            question_has_text = bool(self.question_text.text().strip())
            self.confirm_question_btn.setEnabled(question_has_text)
            
            # Enable cancel button if there's any content
            has_any_content = bool(self.question_text.text().strip()) or bool(self.selected_tags) or bool(self.answer_text.text().strip())
            self.cancel_question_btn.setEnabled(has_any_content)

    def _update_question_counter(self):
        """Update the question counter label with current counts"""
        try:
            if not hasattr(self, 'question_counter') or not self.question_counter:
                return
                
            total_questions = len(self.questions)
            self.question_counter.setText(f"{total_questions}/{MAX_QUESTIONS} câu hỏi")
            
            # Change color based on number of questions
            if total_questions == MAX_QUESTIONS:
                # At maximum, show in red
                self.question_counter.setStyleSheet("color: #f44336; font-weight: bold;")
            elif total_questions > MAX_QUESTIONS * 0.7:
                # Getting close to maximum, show in orange
                self.question_counter.setStyleSheet("color: #FF9800; font-weight: bold;")
            else:
                # Normal display
                self.question_counter.setStyleSheet("color: #000000;")
        except RuntimeError:
            # Bỏ qua lỗi khi các đối tượng đã bị xóa
            pass

    def _on_can_answer_changed(self, state):
        """Handle changes when the can_answer checkbox state changes"""
        can_answer = state == Qt.Checked
        
        if not can_answer:
            # If question cannot be answered based on image, set default message
            self.answer_text.setText("Không thể trả lời được câu hỏi dựa vào thông tin trong ảnh")
            self.answer_text.setReadOnly(True)
            self.answer_text.setStyleSheet("""
                background-color: #f0f2f5;
                border: 1px solid #bdc3c7;
                border-radius: 5px;
                padding: 8px;
                font-size: 13px;
                color: #7f8c8d;
                font-style: italic;
            """)
        else:
            # If question can be answered, allow user input
            self.answer_text.clear()
            self.answer_text.setReadOnly(False)
            self.answer_text.setStyleSheet("""
                background-color: white;
                border: 1px solid #bdc3c7;
                border-radius: 5px;
                padding: 8px;
                font-size: 13px;
            """)
            self.answer_text.setPlaceholderText("Nhập câu trả lời tại đây...")
        
        # Update the model
        if self.questions and len(self.questions) > 0:
            question = self.questions[0]
            
            # Set answerable flag
            question['answerable'] = 1 if can_answer else 0
            
            # Update answers array if it exists
            if 'answers' in question and question['answers']:
                if not can_answer:
                    # If not answerable, set default message
                    question['answers'][0]['answer_text'] = "Không thể trả lời được câu hỏi dựa vào thông tin trong ảnh"
                    question['answers'][0]['is_correct'] = False
            
            # Set modified flag
            self.modified = True
            self.content_changed.emit()

    def _setup_initial_state(self):
        """Setup the initial state with can_answer_check unchecked and answer field in read-only mode,
        but all fields are editable from the start"""
        if hasattr(self, 'can_answer_check'):
            # Make sure this checkbox is enabled
            self.can_answer_check.setEnabled(True)
            # Set the initial state
            self.can_answer_check.setChecked(False)
            self._on_can_answer_changed(Qt.Unchecked)
            
            # Make sure all fields are enabled from the start
            if hasattr(self, 'question_type_combo'):
                self.question_type_combo.setEnabled(True)
            if hasattr(self, 'tags_search'):
                self.tags_search.setEnabled(True)
            if hasattr(self, 'source_combo'):
                self.source_combo.setEnabled(True) 

    def _on_tag_search_changed(self, text):
        """Handle changes to the tag search field"""
        if not text:
            self.tag_suggestions.hide()
            return
            
        # Filter predefined tags based on input
        filtered_tags = [tag for tag in PREDEFINED_TAGS if text.lower() in tag.lower()]
        
        # Also filter out already selected tags
        filtered_tags = [tag for tag in filtered_tags if tag not in self.selected_tags]
        
        if not filtered_tags:
            self.tag_suggestions.hide()
            return
            
        # Show suggestions
        self.tag_suggestions.clear()
        for tag in filtered_tags:
            self.tag_suggestions.addItem(tag)
            
        # Position suggestions below the search field
        pos = self.tags_search.mapToGlobal(self.tags_search.rect().bottomLeft())
        self.tag_suggestions.move(pos)
        self.tag_suggestions.setFixedWidth(self.tags_search.width())
        self.tag_suggestions.setMaximumHeight(150)  # Limit height to a reasonable value
        self.tag_suggestions.show()
    
    def _on_tag_search_enter(self):
        """Handle when user presses Enter in the tag search field"""
        text = self.tags_search.text().strip()
        if not text:
            self.tag_suggestions.hide()
            return
            
        # If suggestions are visible and have items, select the first one
        if self.tag_suggestions.isVisible() and self.tag_suggestions.count() > 0:
            # Get the first suggestion
            first_tag = self.tag_suggestions.item(0).text()
            if first_tag not in self.selected_tags:
                self._add_tag(first_tag)
                self.tags_search.clear()
                self.tag_suggestions.hide()
                return
                
        # If we get here, check for exact match with a predefined tag
        exact_match = next((tag for tag in PREDEFINED_TAGS if tag.lower() == text.lower()), None)
        
        if exact_match and exact_match not in self.selected_tags:
            # If there's an exact match with a predefined tag, add it
            self._add_tag(exact_match)
            self.tags_search.clear()
            self.tag_suggestions.hide()
        else:
            # Show warning message
            QMessageBox.warning(
                self,
                "Chỉ cho phép các tags có sẵn",
                "Bạn chỉ có thể chọn từ danh sách tags có sẵn. Vui lòng tìm kiếm và chọn một tag từ danh sách gợi ý."
            )
            # Keep the search field and suggestions visible
            if self.tag_suggestions.count() > 0:
                self.tag_suggestions.show()
            else:
                self.tags_search.clear()
                self.tag_suggestions.hide()

    def _on_tag_selected(self, tag):
        """Handle selection of a tag from the suggestions"""
        if tag not in self.selected_tags:
            self._add_tag(tag)
            self.tags_search.clear()
            
    def _add_tag(self, tag):
        """Add a new tag to the selected tags"""
        if tag in self.selected_tags:
            return
            
        # Add to the in-memory list
        self.selected_tags.append(tag)
        
        # Create a visual tag button
        tag_button = TagButton(tag)
        tag_button.removed.connect(self._remove_tag)
        self.tags_display_layout.addWidget(tag_button)
        
        # Update the question model
        if self.questions and len(self.questions) > 0:
            self.questions[0]['tags'] = self.selected_tags.copy()
            self.modified = True
            self.content_changed.emit()
            
    def _remove_tag(self, tag):
        """Remove a tag from the selected tags"""
        if tag in self.selected_tags:
            self.selected_tags.remove(tag)
            
            # Remove the visual button
            for i in range(self.tags_display_layout.count()):
                widget = self.tags_display_layout.itemAt(i).widget()
                if isinstance(widget, TagButton) and widget.tag == tag:
                    widget.setParent(None)
                    widget.deleteLater()
                    break
                    
            # Update the question model
            if self.questions and len(self.questions) > 0:
                self.questions[0]['tags'] = self.selected_tags.copy()
                self.modified = True
                self.content_changed.emit()

    def _clear_tags(self):
        """Clear all selected tags"""
        # Clear the in-memory list
        self.selected_tags = []
        
        # Clear the visual display
        for i in reversed(range(self.tags_display_layout.count())):
            widget = self.tags_display_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)
                widget.deleteLater() 

    def has_questions(self):
        """Check if there are any confirmed questions with content.
        
        Returns:
            bool: True if there are valid questions, False otherwise
        """
        # First check if there are any questions at all
        if not self.questions:
            return False
            
        # Check if the first question has content
        question = self.questions[0]
        
        # A question is valid if it has text content and has tags
        has_text = bool(question.get('question', '').strip())
        has_tags = bool(question.get('tags', []))
        
        # If answerable, it must have an answer
        is_answerable = question.get('answerable', 0) == 1
        has_answer = False
        
        if is_answerable and 'answers' in question and question['answers']:
            has_answer = bool(question['answers'][0].get('answer_text', '').strip())
        
        # For an answerable question, it must have an answer
        # For a non-answerable question, we don't require an answer
        is_valid = has_text and has_tags and (not is_answerable or (is_answerable and has_answer))
        
        return is_valid 