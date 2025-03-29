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
        self.question_type_combo.addItem("Existence Checking", "Existence Checking")
        self.question_type_combo.addItem("Others", "Others")
        
        # Log the available question types for debugging
        for i in range(self.question_type_combo.count()):
            data_value = self.question_type_combo.itemData(i)
            display_text = self.question_type_combo.itemText(i)
            logger.info(f"Question type combo option {i}: text='{display_text}', value='{data_value}' (type: {type(data_value).__name__})")
        
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
        
        # Add Revert to Original button (will be visible only when there are original values to revert to)
        self.revert_original_btn = QPushButton("↺  Khôi phục về ban đầu")
        self.revert_original_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                font-weight: bold;
                padding: 6px 12px;
                font-size: 13px;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #2980b9;
                box-shadow: 0 2px 5px rgba(0,0,0,0.2);
            }
            QPushButton:pressed {
                background-color: #1c6ea4;
            }
            QPushButton:disabled {
                background-color: #b3d3ea;
                color: #e6f2f9;
            }
        """)
        self.revert_original_btn.setMinimumHeight(34)
        self.revert_original_btn.setMinimumWidth(150)
        self.revert_original_btn.clicked.connect(self._revert_to_original)
        self.revert_original_btn.setEnabled(False)  # Disabled by default
        self.revert_original_btn.setVisible(False)  # Hidden by default
        buttons_layout.addWidget(self.revert_original_btn)
        
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
        
        # Connect signals for all UI elements that trigger modified state
        # Question text changes
        self.question_text.textChanged.connect(self._on_content_changed)
        
        # Question type changes
        self.question_type_combo.currentIndexChanged.connect(self._on_question_type_changed)
        
        # Answerable checkbox changes 
        self.can_answer_check.stateChanged.connect(self._on_can_answer_changed)
        
        # Tag search field 
        self.tags_search.textChanged.connect(self._on_content_changed)
        
        # QA source changes
        self.source_combo.currentIndexChanged.connect(self._on_source_changed)
        
        # Make sure image source changes are properly connected (already done in _create_image_source_section)
        # self.image_source_input.currentIndexChanged.connect(self._on_image_source_changed)
    
    def _create_default_question(self, answerable=0):
        """Tạo câu hỏi mặc định với ID = 1"""
        self.questions = [{
            'question_id': 1,
            'question': '',
            'question_type': 'existence_checking',  # Default to existence checking
            'answerable': answerable,  # Use the passed in answerable flag (default 0 - not answerable)
            'source': 'manually_annotated',  # Default to "Manually Annotated"
            'answers': [{
                'answer_id': 1,
                'answer_text': 'Không thể trả lời được câu hỏi dựa vào thông tin trong ảnh' if answerable == 0 else '',
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
            
            # Log current state
            logger.info("_update_ui_state called - Updating UI state")
            
            # Kiểm tra xem câu hỏi có nội dung không
            question_has_text = bool(self.question_text.text().strip())
            
            # Check if all required fields are filled
            has_text = bool(self.question_text.text().strip())
            has_tags = bool(self.selected_tags)
            is_answerable = self.can_answer_check.isChecked()
            has_answer = bool(self.answer_text.text().strip())
            
            # Basic validation for form completion
            basic_validation = has_text and has_tags and (not is_answerable or (is_answerable and has_answer))
            logger.info(f"Basic validation: {basic_validation} (has_text={has_text}, has_tags={has_tags}, is_answerable={is_answerable}, has_answer={has_answer})")
            
            # Check if there are any changes from the original state (for modification mode)
            has_changes = True  # Default to True for new questions
            has_original_data = hasattr(self, '_original_state') and self._original_state is not None
            
            # For new unlabeled images, we should always be able to confirm if basic validation passes
            if not has_original_data:
                logger.info("No original state - new unlabeled image")
                has_changes = True  # For new questions, we always want to allow confirmation
            elif has_original_data:
                # Get current question
                question = self.questions[0] if self.questions else None
                if not question:
                    return
                    
                # Get current values for comparison
                question_text = self.question_text.text().strip()
                current_question_type = str(self.question_type_combo.currentData()).lower()
                current_answer = self.answer_text.text().strip()
                if not is_answerable:
                    current_answer = "Không thể trả lời được câu hỏi dựa vào thông tin trong ảnh"
                current_tags = set(self.selected_tags)
                current_source = self.source_combo.currentData()
                current_image_source = self.image_source
                
                # Log current state for debugging
                logger.info(f"Current state: question='{question_text}', type='{current_question_type}', answerable={is_answerable}, answer='{current_answer}', tags={current_tags}, source='{current_source}'")
                
                # Get original values
                orig_question = self._original_state.get('question', '').strip()
                orig_question_type = str(self._original_state.get('question_type', '')).lower()
                orig_answerable = self._original_state.get('answerable', 0) == 1
                
                # Log original state for debugging
                logger.info(f"Original state: question='{orig_question}', type='{orig_question_type}', answerable={orig_answerable}")
                
                # Get original answer
                orig_answer = ""
                if 'answers' in self._original_state and self._original_state['answers']:
                    if isinstance(self._original_state['answers'][0], str):
                        orig_answer = self._original_state['answers'][0].strip()
                    else:
                        orig_answer = self._original_state['answers'][0].get('answer_text', '').strip()
                
                # Log original answer for debugging
                logger.info(f"Original answer: '{orig_answer}'")
                
                # Get original tags
                orig_tags = set(self._original_state.get('tags', []))
                
                # Get original source
                orig_source = self._original_state.get('qa_source', self._original_state.get('source', ''))
                
                # Get original image source
                orig_image_source = getattr(self, '_original_image_source', None)
                
                # Check if any values have changed using a single comparison for clarity
                is_different = (
                    question_text != orig_question or
                    current_question_type != orig_question_type or
                    is_answerable != orig_answerable or
                    current_answer != orig_answer or
                    current_tags != orig_tags or
                    current_source != orig_source or
                    (orig_image_source is not None and current_image_source != orig_image_source)
                )
                
                # Log detailed comparison results for debugging
                logger.info(f"Is different? {is_different}")
                if is_different:
                    logger.info(f"Differences detected in _update_ui_state:")
                    if question_text != orig_question:
                        logger.info(f"  - Question text differs: '{question_text}' vs '{orig_question}'")
                    if current_question_type != orig_question_type:
                        logger.info(f"  - Question type differs: '{current_question_type}' vs '{orig_question_type}'")
                    if is_answerable != orig_answerable:
                        logger.info(f"  - Answerable state differs: {is_answerable} vs {orig_answerable}")
                    if current_answer != orig_answer:
                        logger.info(f"  - Answer differs: '{current_answer}' vs '{orig_answer}'")
                    if current_tags != orig_tags:
                        logger.info(f"  - Tags differ: {current_tags} vs {orig_tags}")
                    if current_source != orig_source:
                        logger.info(f"  - Source differs: '{current_source}' vs '{orig_source}'")
                    if orig_image_source is not None and current_image_source != orig_image_source:
                        logger.info(f"  - Image source differs: '{current_image_source}' vs '{orig_image_source}'")
                
                # Only allow confirmation if there are actual changes
                has_changes = is_different
                
                # Update revert button based on changes
                if hasattr(self, 'revert_original_btn') and self.revert_original_btn:
                    self.revert_original_btn.setVisible(bool(has_original_data))
                    self.revert_original_btn.setEnabled(bool(has_original_data) and is_different)
                    logger.info(f"Revert button: visible={bool(has_original_data)}, enabled={bool(has_original_data) and is_different}")
                
                # Update modified flag based on changes
                self.modified = is_different
            
            # Logic for enabling the confirm button:
            # 1. For new questions (no original data): Enable if basic validation passes
            # 2. For existing questions: Enable if basic validation passes AND there are changes
            
            # For unlabeled images (no original data), we should enable confirm if validation passes
            if not has_original_data:
                can_confirm = basic_validation
            else:
                # For labeled images, only enable if there are changes AND validation passes
                can_confirm = basic_validation and has_changes
            
            # Log the confirm button state decision for debugging
            logger.info(f"Confirm button enabled decision: {can_confirm} (basic_validation={basic_validation}, has_changes={has_changes}, has_original_data={has_original_data})")
            
            if hasattr(self, 'confirm_question_btn') and self.confirm_question_btn:
                self.confirm_question_btn.setEnabled(can_confirm)
                logger.info(f"Confirm button enabled: {can_confirm}")
            
            # Cancel button luôn được bật nếu có bất kỳ nội dung nào 
            has_any_content = bool(self.question_text.text().strip()) or bool(self.selected_tags) or (is_answerable and bool(self.answer_text.text().strip()))
            if hasattr(self, 'cancel_question_btn') and self.cancel_question_btn:
                self.cancel_question_btn.setEnabled(has_any_content)
                logger.info(f"Cancel button enabled: {has_any_content}")
            
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
        question_type_value = self.question_type_combo.currentData()
        
        # Log values for debugging
        logger.info(f"Confirmation dialog - Current question type: value={question_type_value}, text={question_type_text}")
        
        is_answerable = self.can_answer_check.isChecked()
        answer_text = self.answer_text.text().strip()
        if not is_answerable:
            answer_text = "Không thể trả lời được câu hỏi dựa vào thông tin trong ảnh"
        
        tags_text = ", ".join(self.selected_tags)
        qa_source_text = self.source_combo.currentText()
        image_source_text = self.image_source_input.currentText()
        
        # Check if this is a modification of an existing labeled data
        is_modification = hasattr(self, '_original_state') and self._original_state
        
        # Create confirmation message with clear separation between sections and styling for labels/values
        confirmation_message = f"""<h3>Xác nhận thông tin</h3>"""
        
        # IMAGE SOURCE section
        confirmation_message += f"""
<div style="background-color: #f0f2f5; padding: 10px; border-radius: 5px; margin-bottom: 10px;">
<b style="color: #3498db;">IMAGE SOURCE:</b><br>
<b>Nguồn ảnh:</b> <i style="font-weight: normal;">{image_source_text}</i>"""

        # Show original value if it's different
        if is_modification and hasattr(self, '_original_image_source') and self._original_image_source != self.image_source:
            # Find the display text for the original image source
            original_image_source_text = ""
            for i in range(self.image_source_input.count()):
                if self.image_source_input.itemData(i) == self._original_image_source:
                    original_image_source_text = self.image_source_input.itemText(i)
                    break
            
            if original_image_source_text:
                confirmation_message += f"""<br><span style="color: #e74c3c; font-style: italic;">Giá trị ban đầu: {original_image_source_text}</span>"""
                
        confirmation_message += """</div>"""
        
        # QUESTION section
        confirmation_message += f"""
<div style="background-color: #f0f2f5; padding: 10px; border-radius: 5px; margin-bottom: 10px;">
<b style="color: #3498db;">QUESTION:</b><br>
<b>Question ID:</b> <i style="font-weight: normal;">1</i><br>
<b>Câu hỏi:</b> <i style="font-weight: normal;">{question_text}</i>"""

        # Show original question if it's different
        if is_modification and 'question' in self._original_state and self._original_state['question'] != question_text:
            confirmation_message += f"""<br><span style="color: #e74c3c; font-style: italic;">Câu hỏi ban đầu: {self._original_state.get('question', '')}</span>"""
        
        confirmation_message += f"""<br>
<b>Loại câu hỏi:</b> <i style="font-weight: normal;">{question_type_text}</i>"""

        # Show original question type if it's different - highlight changed value
        original_question_type_text = ""
        if is_modification and 'question_type' in self._original_state:
            # Log question type comparison values for debugging
            logger.info(f"Confirmation dialog - Original question type value: {self._original_state['question_type']} (type: {type(self._original_state['question_type']).__name__})")
            logger.info(f"Confirmation dialog - Current question type value: {question_type_value} (type: {type(question_type_value).__name__})")
            
            # Convert both values to lowercase strings for case-insensitive comparison
            original_value_str = str(self._original_state['question_type']).lower()
            current_value_str = str(question_type_value).lower()
            
            # Check if the values are different (ignoring case)
            is_different = original_value_str != current_value_str
            
            logger.info(f"Case-insensitive comparison result: {is_different} ('{original_value_str}' vs '{current_value_str}')")
            
            # Only continue if the values are actually different
            if is_different:
                # Log original question type value for debugging
                logger.info(f"Detected different question type: Original={self._original_state['question_type']} vs Current={question_type_value}")
                
                # Find the display text for the original question type by looking up the value in the combo box
                for i in range(self.question_type_combo.count()):
                    item_data = str(self.question_type_combo.itemData(i)).lower()
                    logger.info(f"Checking combo item {i}: data={item_data}, comparing with: {original_value_str}")
                    
                    # Case-insensitive comparison using lowercase strings
                    if item_data == original_value_str:
                        original_question_type_text = self.question_type_combo.itemText(i)
                        logger.info(f"Found match: {original_question_type_text}")
                        break
                
                # If we still can't find it, try direct mapping of known values
                if not original_question_type_text:
                    logger.info(f"No match found using data value, trying direct text matching...")
                    # Try finding the text directly based on known values
                    if original_value_str == "existence_checking" or original_value_str == "existence checking":
                        original_question_type_text = "Existence Checking"
                    elif original_value_str == "others" or original_value_str == "other":
                        original_question_type_text = "Others"
                    logger.info(f"Direct mapping result: {original_question_type_text}")
                
                # Log the found display text
                logger.info(f"Confirmation dialog - Original question type text: {original_question_type_text}")
                
                # Only add the highlight if we found a valid display text and it's different
                if original_question_type_text and original_question_type_text != question_type_text:
                    logger.info(f"Adding red highlight for original question type: {original_question_type_text}")
                    confirmation_message += f"""<br><span style="color: #e74c3c; font-style: italic;">Loại câu hỏi ban đầu: {original_question_type_text}</span>"""
                elif original_value_str != current_value_str:
                    # If we couldn't find the text but values are different, show the value as fallback
                    original_display = self._original_state['question_type']
                    logger.info(f"Using original value directly: {original_display}")
                    confirmation_message += f"""<br><span style="color: #e74c3c; font-style: italic;">Loại câu hỏi ban đầu: {original_display}</span>"""
            else:
                logger.info("Question types are the same, not highlighting")
        
        confirmation_message += """</div>"""
        
        # ANSWER section
        confirmation_message += f"""
<div style="background-color: #f0f2f5; padding: 10px; border-radius: 5px; margin-bottom: 10px;">
<b style="color: #3498db;">ANSWER:</b><br>
<b>Có thể trả lời:</b> <i style="font-weight: normal;">{'Có' if is_answerable else 'Không'}</i>"""

        # Show original answerable state if it's different
        original_answerable = self._original_state.get('answerable', 0) == 1 if is_modification else False
        if is_modification and original_answerable != is_answerable:
            confirmation_message += f"""<br><span style="color: #e74c3c; font-style: italic;">Có thể trả lời ban đầu: {'Có' if original_answerable else 'Không'}</span>"""
            
        confirmation_message += f"""<br>
<b>Câu trả lời:</b> <i style="font-weight: normal;">{answer_text}</i>"""

        # Show original answer if it's different
        original_answer = ""
        if is_modification and 'answers' in self._original_state and self._original_state['answers']:
            if isinstance(self._original_state['answers'][0], str):
                original_answer = self._original_state['answers'][0]
            elif isinstance(self._original_state['answers'][0], dict):
                original_answer = self._original_state['answers'][0].get('answer_text', '')
                
            # Only show if different
            current_answer_for_comparison = answer_text
            if original_answer != current_answer_for_comparison:
                confirmation_message += f"""<br><span style="color: #e74c3c; font-style: italic;">Câu trả lời ban đầu: {original_answer}</span>"""
                
        confirmation_message += """</div>"""
        
        # METADATA section
        confirmation_message += f"""
<div style="background-color: #f0f2f5; padding: 10px; border-radius: 5px; margin-bottom: 10px;">
<b style="color: #3498db;">METADATA:</b><br>
<b>Tags:</b> <i style="font-weight: normal;">{tags_text}</i>"""

        # Show original tags if they are different
        original_tags = self._original_state.get('tags', []) if is_modification else []
        original_tags_text = ", ".join(original_tags)
        if is_modification and set(original_tags) != set(self.selected_tags):
            confirmation_message += f"""<br><span style="color: #e74c3c; font-style: italic;">Tags ban đầu: {original_tags_text}</span>"""
            
        confirmation_message += f"""<br>
<b>Nguồn QA:</b> <i style="font-weight: normal;">{qa_source_text}</i>"""

        # Show original QA source if it's different
        original_qa_source = ""
        if is_modification:
            # Check both source and qa_source fields
            original_qa_source_value = self._original_state.get('qa_source', self._original_state.get('source', ''))
            
            # Find the display text for the original QA source
            for i in range(self.source_combo.count()):
                if self.source_combo.itemData(i) == original_qa_source_value:
                    original_qa_source = self.source_combo.itemText(i)
                    break
                    
            if original_qa_source and original_qa_source != qa_source_text:
                confirmation_message += f"""<br><span style="color: #e74c3c; font-style: italic;">Nguồn QA ban đầu: {original_qa_source}</span>"""
                
        confirmation_message += """</div>

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
        
        # Always add Revert to Original button (for both first confirmation and modification)
        revertButton = QPushButton("Khôi phục về ban đầu")
        
        # Style the button differently based on whether there's data to revert to
        if is_modification:
            # Normal active style for when there is data to revert to
            revertButton.setStyleSheet("""
                QPushButton {
                    background-color: #3498db;
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
                    background-color: #2980b9;
                    box-shadow: 0 2px 5px rgba(0,0,0,0.2);
                }
                QPushButton:pressed {
                    background-color: #1c6ea4;
                }
            """)
        else:
            # Disabled visual style for when there's no data to revert to
            revertButton.setStyleSheet("""
                QPushButton {
                    background-color: #95a5a6;
                    color: #ecf0f1;
                    font-weight: bold;
                    padding: 8px 16px;
                    font-size: 14px;
                    border: none;
                    border-radius: 5px;
                    min-width: 150px;
                    min-height: 36px;
                }
                QPushButton:hover {
                    background-color: #7f8c8d;
                }
            """)
            
        msgBox.addButton(revertButton, QMessageBox.ResetRole)
        
        # Add buttons to message box
        msgBox.addButton(yesButton, QMessageBox.YesRole)
        msgBox.addButton(noButton, QMessageBox.NoRole)
        msgBox.setDefaultButton(noButton)  # Make "No" the default for safety
        
        # Show the dialog and get response
        reply = msgBox.exec_()
        
        # Check which button was clicked
        clickedButton = msgBox.clickedButton()
        
        if clickedButton == revertButton:
            # If this is a modification of existing data, use the saved original state
            if is_modification:
                # Revert all changes back to original values
                self._revert_to_original()
            else:
                # For first-time entry, show a message explaining that there's nothing to revert
                QMessageBox.information(
                    self,
                    "Không có dữ liệu ban đầu",
                    "Đây là lần đầu tiên bạn nhập thông tin cho câu hỏi này, nên không có dữ liệu ban đầu để khôi phục."
                )
            return
        elif clickedButton != yesButton:
            # User clicked No or closed the dialog
            return
        
        # Continue with confirmation process as before if Yes was clicked
        # Lưu trữ nội dung gốc để khôi phục khi cần
        self.questions[0]['original_text'] = question_text
        
        # Mark question as confirmed
        self.questions[0]['is_confirmed'] = True
        self.questions[0]['question'] = question_text
        
        # IMPORTANT: Explicitly update the answerable state in the model
        is_answerable = self.can_answer_check.isChecked()
        self.questions[0]['answerable'] = 1 if is_answerable else 0
        logger.info(f"Confirmation completed - Explicitly set answerable flag in model to: {self.questions[0]['answerable']}")
        
        # Update the answer text in the model
        answer_text = self.answer_text.text().strip()
        if not is_answerable:
            answer_text = "Không thể trả lời được câu hỏi dựa vào thông tin trong ảnh"
            
        if 'answers' in self.questions[0] and self.questions[0]['answers']:
            self.questions[0]['answers'][0]['answer_text'] = answer_text
            logger.info(f"Updated answer text in model to: '{answer_text}'")
        else:
            self.questions[0]['answers'] = [{
                'answer_id': 1,
                'answer_text': answer_text,
                'is_correct': False
            }]
            logger.info(f"Created new answer in model with text: '{answer_text}'")
        
        # Also update question type and source
        self.questions[0]['question_type'] = self.question_type_combo.currentData()
        self.questions[0]['source'] = self.source_combo.currentData()
        
        # All input fields are already enabled from the start, so no need to enable them here
        # Just preserve the state of the answer field based on can_answer_check
        self.answer_text.setReadOnly(not is_answerable)
        
        # Set modified flag
        self.modified = True
        self.content_changed.emit()
        
        # Emit the question_confirmed signal to trigger save in the parent window
        self.question_confirmed.emit()
        
        # Update the UI state
        self._update_ui_state()
        
        # Finally, ensure model and UI are fully synchronized (this will fix any remaining checkbox state issues)
        logger.info("Explicitly calling _on_content_changed to ensure model and UI are properly synchronized")
        self._on_content_changed()
    
    def _revert_to_original(self):
        """Revert all changes back to the original values"""
        if not hasattr(self, '_original_state') or not self._original_state:
            logger.info("No original state to revert to")
            return
            
        logger.info("Reverting to original state")
            
        # Restore the original state of the question
        if hasattr(self, 'questions') and self.questions:
            # Keep the original structure but update the content
            question = self.questions[0]
            
            # Restore question text
            if 'question' in self._original_state:
                question['question'] = self._original_state['question']
                self.question_text.setText(self._original_state['question'])
                
            # Restore question type
            if 'question_type' in self._original_state:
                # Store the original question type and log it
                original_question_type = self._original_state['question_type']
                logger.info(f"Restoring question type to original value: {original_question_type}")
                
                # First update the model with the original value
                question['question_type'] = original_question_type
                
                # Find the matching index using case-insensitive comparison
                found_index = -1
                for i in range(self.question_type_combo.count()):
                    item_data = self.question_type_combo.itemData(i)
                    logger.info(f"Comparing combo item {i}: {item_data} with original: {original_question_type}")
                    
                    # Use case-insensitive string comparison
                    if str(item_data).lower() == str(original_question_type).lower():
                        found_index = i
                        logger.info(f"Found matching question type at index {i}")
                        break
                        
                # Set the combo box to the found index, or default to first item
                if found_index >= 0:
                    self.question_type_combo.setCurrentIndex(found_index)
                else:
                    # Default to first option
                    self.question_type_combo.setCurrentIndex(0)
                    logger.warning(f"Could not find original question type '{original_question_type}' in combo box, defaulting to index 0")
                    
            # Restore answerable state
            original_answerable = self._original_state.get('answerable', 0) == 1
            logger.info(f"Restoring answerable state to: {original_answerable}")
            question['answerable'] = 1 if original_answerable else 0
            
            # Important: Get original answer text first, before updating UI
            original_answer = ""
            if 'answers' in self._original_state and self._original_state['answers']:
                # Handle both formats
                if isinstance(self._original_state['answers'][0], str):
                    original_answer = self._original_state['answers'][0]
                else:
                    original_answer = self._original_state['answers'][0].get('answer_text', '')
                logger.info(f"Original answer text: '{original_answer}'")
            
            # Block signals when setting the checkbox to prevent _on_can_answer_changed from being triggered
            old_block_state = self.can_answer_check.blockSignals(True)
            self.can_answer_check.setChecked(original_answerable)
            self.can_answer_check.blockSignals(old_block_state)
            logger.info(f"Set answerable checkbox to: {original_answerable} with signals blocked")
            
            # Set the appropriate answer text based on answerable state
            if original_answerable:
                # For answerable questions, restore the original answer
                self.answer_text.setText(original_answer)
                self.answer_text.setReadOnly(False)
                self.answer_text.setStyleSheet("""
                    background-color: white;
                    border: 1px solid #bdc3c7;
                    border-radius: 5px;
                    padding: 8px;
                    font-size: 13px;
                """)
                self.answer_text.setPlaceholderText("Nhập câu trả lời tại đây...")
                logger.info(f"Restored answerable question with answer: '{original_answer}'")
                
                # Update the model with the original answer
                if 'answers' not in question or not question['answers']:
                    question['answers'] = [{
                        'answer_id': 1,
                        'answer_text': original_answer,
                        'is_correct': False
                    }]
                else:
                    question['answers'][0]['answer_text'] = original_answer
            else:
                # For unanswerable questions, set the default text
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
                logger.info("Restored unanswerable question with default text")
                
                # Update the model with the default unanswerable text
                if 'answers' not in question or not question['answers']:
                    question['answers'] = [{
                        'answer_id': 1,
                        'answer_text': "Không thể trả lời được câu hỏi dựa vào thông tin trong ảnh",
                        'is_correct': False
                    }]
                else:
                    question['answers'][0]['answer_text'] = "Không thể trả lời được câu hỏi dựa vào thông tin trong ảnh"
            
            # Restore tags
            if 'tags' in self._original_state:
                question['tags'] = self._original_state['tags'].copy()
                # Clear current tags and add original ones
                self._clear_tags()
                for tag in self._original_state['tags']:
                    self._add_tag(tag)
            
            # Restore QA source
            source_key = 'qa_source' if 'qa_source' in self._original_state else 'source'
            if source_key in self._original_state:
                question[source_key] = self._original_state[source_key]
                # Find the matching index
                for i in range(self.source_combo.count()):
                    if self.source_combo.itemData(i) == self._original_state[source_key]:
                        self.source_combo.setCurrentIndex(i)
                        break
            
            # Restore image source if it was stored
            if hasattr(self, '_original_image_source') and self._original_image_source:
                self.image_source = self._original_image_source
                # Find the matching index
                for i in range(self.image_source_input.count()):
                    if self.image_source_input.itemData(i) == self._original_image_source:
                        self.image_source_input.setCurrentIndex(i)
                        break
        
        # Reset the modified flag
        self.modified = False
        logger.info("Reset modified flag to False after reverting to original")
        
        # Update UI state to reflect the reversion - this will disable buttons as needed
        self._update_ui_state()
        
        # After reverting, explicitly call _on_content_changed to ensure UI and model are synchronized
        # This will also prepare for detecting future changes
        logger.info("Calling _on_content_changed after revert to sync UI and model")
        self._on_content_changed()
        
        # Show a confirmation message
        QMessageBox.information(
            self,
            "Đã khôi phục",
            "Dữ liệu đã được khôi phục về giá trị ban đầu."
        )
    
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
        logger.info(f"Setting questions: {questions}")
        
        # Track whether this is loading an existing question vs creating a new one
        loading_existing_question = questions and len(questions) > 0 and bool(questions[0].get('question', '').strip())
        logger.info(f"Loading existing question: {loading_existing_question}")
        
        # Transform image_source if it's still using the old value
        if image_source == "self_collected":
            image_source = "manually_collected"
            
        # Set image source if provided, otherwise keep default "Manual Collected"
        if image_source:
            self.image_source = image_source
            
            # Find the corresponding index for the image source in the combobox
            found_index = -1
            for i in range(self.image_source_input.count()):
                if self.image_source_input.itemData(i) == image_source:
                    found_index = i
                    break
            
            # If found, update the combobox
            if found_index >= 0:
                self.image_source_input.setCurrentIndex(found_index)
            else:
                # Default to "Manual Collected" if not found
                self.image_source_input.setCurrentIndex(0)
        else:
            # If no image source provided, ensure default is "Manual Collected"
            self.image_source = "manually_collected"
            self.image_source_input.setCurrentIndex(0)
        
        # Only take the first question or create new if none
        if questions and len(questions) > 0:
            # Get the first question and ensure ID = 1
            self.questions = [questions[0]]
            self.questions[0]['question_id'] = 1
            
            # Check if 'answerable' field is present and log it
            if 'answerable' in self.questions[0]:
                answerable_value = self.questions[0]['answerable']
                logger.info(f"Question has answerable field with value: {answerable_value} (type: {type(answerable_value).__name__})")
                
                # Ensure answerable is an integer 0 or 1, not a boolean or string
                if isinstance(answerable_value, bool):
                    self.questions[0]['answerable'] = 1 if answerable_value else 0
                    logger.info(f"Converted boolean answerable to int: {self.questions[0]['answerable']}")
                elif isinstance(answerable_value, str):
                    self.questions[0]['answerable'] = 1 if answerable_value.lower() in ('1', 'true', 'yes') else 0
                    logger.info(f"Converted string answerable to int: {self.questions[0]['answerable']}")
                    
                # Ensure answerable is either 0 or 1
                if answerable_value not in (0, 1):
                    self.questions[0]['answerable'] = 1 if answerable_value else 0
                    logger.info(f"Normalized answerable value to: {self.questions[0]['answerable']}")
            else:
                logger.info("Question does not have 'answerable' field, defaulting to 0")
                self.questions[0]['answerable'] = 0
                
            # Check if 'answers' field is present and log it    
            if 'answers' in self.questions[0] and self.questions[0]['answers']:
                if isinstance(self.questions[0]['answers'][0], str):
                    logger.info(f"Question has answers as string array: {self.questions[0]['answers']}")
                else:
                    logger.info(f"Question has answers as object array: {self.questions[0]['answers']}")
            else:
                logger.info("Question does not have 'answers' field or it's empty")
            
            # Transform source field if it's still using the old value
            if 'source' in self.questions[0] and self.questions[0]['source'] == "self_collected":
                self.questions[0]['source'] = "manually_collected"
                
            # Transform qa_source field if it's still using the old value
            if 'qa_source' in self.questions[0] and self.questions[0]['qa_source'] == "self_collected":
                self.questions[0]['qa_source'] = "manually_collected"
            
            # Convert 'answers' field from array of strings to expected format if needed
            if 'answers' in self.questions[0] and self.questions[0]['answers']:
                if isinstance(self.questions[0]['answers'][0], str):
                    # Convert string array to object array
                    original_answers = self.questions[0]['answers']
                    self.questions[0]['answers'] = []
                    for i, answer_text in enumerate(original_answers):
                        self.questions[0]['answers'].append({
                            'answer_id': i + 1,
                            'answer_text': answer_text,
                            'is_correct': i == 0  # First answer is correct by default
                        })
                    logger.info(f"Converted string answers to object array: {self.questions[0]['answers']}")
            
            # Set confirmed status if not already set
            if 'is_confirmed' not in self.questions[0]:
                self.questions[0]['is_confirmed'] = bool(self.questions[0].get('question', '').strip())
        else:
            # Create default question if none exists
            logger.info("No questions provided, creating default question")
            self._create_default_question()
        
        # Store the original state to track modifications
        if hasattr(self, 'questions') and self.questions:
            # Make a deep copy to track against
            import copy
            self._original_state = copy.deepcopy(self.questions[0])
            
            # Ensure the question type is properly normalized to lowercase string
            if 'question_type' in self._original_state:
                # Fix: Normalize the question type to ensure consistent comparison
                if isinstance(self._original_state['question_type'], str):
                    # Convert to lowercase string to match combo box data values
                    self._original_state['question_type'] = self._original_state['question_type'].lower()
                    
            # Log the stored original state for debugging
            logger.info(f"Original state: {self._original_state}")
            if 'question_type' in self._original_state:
                logger.info(f"Original state - stored question type: {self._original_state['question_type']} (type: {type(self._original_state['question_type']).__name__})")
                
            self._original_image_source = self.image_source
        
        # Explicitly set modified flag to False since we just loaded data
        self.modified = False
        
        # Display question content
        question = self.questions[0]
        self.question_text.setText(question.get('question', ''))
        
        # Set question type
        question_type = question.get('question_type', 'existence_checking')
        index = 0  # Default to first option (Existence Checking)
        
        # Log the loaded question type value
        logger.info(f"Loading question with type value: {question_type}")
        
        # Find the matching index by data value
        for i in range(self.question_type_combo.count()):
            if self.question_type_combo.itemData(i) == question_type:
                index = i
                break
                
        # Log the selected index and text
        logger.info(f"Setting question type combo to index {index}: value={self.question_type_combo.itemData(index)}, text={self.question_type_combo.itemText(index)}")
        
        self.question_type_combo.setCurrentIndex(index)
        
        # IMPORTANT: First determine if the question is answerable
        is_answerable = question.get('answerable', 0) == 1  # Default to 0 (not answerable)
        logger.info(f"Question answerable state from data: {is_answerable}")
        
        # Get answer text BEFORE setting any UI state
        answer_text = ""
        if 'answers' in question and question['answers']:
            # Handle both string array and object array formats
            if isinstance(question['answers'][0], str):
                answer_text = question['answers'][0]
            else:
                answer_text = question['answers'][0].get('answer_text', '')
            logger.info(f"Raw answer text from loaded data: '{answer_text}'")
        
        # CRITICAL FIX: Block signals properly when setting checked state
        old_block_state = self.can_answer_check.blockSignals(True)
        
        # Set the checkbox state
        self.can_answer_check.setChecked(is_answerable)
        logger.info(f"Set can_answer_check to checked={is_answerable} with signals blocked")
        
        # Restore signal blocking state
        self.can_answer_check.blockSignals(old_block_state)
        
        # Now set the UI state based on answerable flag
        if is_answerable:
            # For answerable questions, set the answer text from data and make editable
            logger.info(f"Setting answerable question with answer text: '{answer_text}'")
            self.answer_text.setText(answer_text)
            self.answer_text.setReadOnly(False)
            self.answer_text.setStyleSheet("""
                background-color: white;
                border: 1px solid #bdc3c7;
                border-radius: 5px;
                padding: 8px;
                font-size: 13px;
            """)
            self.answer_text.setPlaceholderText("Nhập câu trả lời tại đây...")
        else:
            # For unanswerable questions, set the default text and make read-only
            logger.info("Setting unanswerable question with default text")
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
            
        # Manually trigger the state update to ensure all internal states are correct
        logger.info(f"Manually triggering _on_can_answer_changed with state={Qt.Checked if is_answerable else Qt.Unchecked}")
        self._on_can_answer_changed(Qt.Checked if is_answerable else Qt.Unchecked)
        
        # Load tags
        self._clear_tags()  # Clear existing tags first
        tags_list = question.get('tags', [])
        for tag in tags_list:
            self._add_tag(tag)
        
        # Display QA source - find by data value
        # First check if we have qa_source field (new format)
        source = question.get('qa_source', question.get('source', 'manually_annotated'))
        
        # Transform source if it's still using the old value
        if source == "self_collected":
            source = "manually_collected"
            
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
        
        # Final reset of modified flag to ensure UI state is fresh
        self.modified = False
        
        # Verify the final state of the UI
        logger.info(f"Final answerable state in UI: {self.can_answer_check.isChecked()}")
        logger.info(f"Final answer text in UI: '{self.answer_text.text()}'")
        
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
        
        # Find the corresponding index for the image source in the combobox
        for i in range(self.image_source_input.count()):
            if self.image_source_input.itemData(i) == source:
                self.image_source_input.setCurrentIndex(i)
                break
        
        self._update_ui_state()
    
    def is_modified(self):
        """Check if content has been modified from its original state"""
        
        # If the modified flag is False, return immediately
        if not self.modified:
            return False
            
        # If there's no _original_state to compare against,
        # rely on the stored modified flag
        if not hasattr(self, '_original_state') or self._original_state is None:
            return self.modified
            
        # Get current values for comparison with original state
        current_question = self.question_text.text().strip()
        current_question_type = str(self.question_type_combo.currentData()).lower()
        is_answerable = self.can_answer_check.isChecked()
        current_answer = self.answer_text.text().strip()
        if not is_answerable:
            current_answer = "Không thể trả lời được câu hỏi dựa vào thông tin trong ảnh"
        current_tags = set(self.selected_tags)
        current_source = self.source_combo.currentData()
        current_image_source = self.image_source
        
        # Get original values
        orig_question = self._original_state.get('question', '').strip()
        orig_question_type = str(self._original_state.get('question_type', '')).lower()
        orig_answerable = self._original_state.get('answerable', 0) == 1
        
        # Get original answer
        orig_answer = ""
        if 'answers' in self._original_state and self._original_state['answers']:
            if isinstance(self._original_state['answers'][0], str):
                orig_answer = self._original_state['answers'][0].strip()
            else:
                orig_answer = self._original_state['answers'][0].get('answer_text', '').strip()
        
        # Get original tags
        orig_tags = set(self._original_state.get('tags', []))
        
        # Get original source
        orig_source = self._original_state.get('qa_source', self._original_state.get('source', ''))
        
        # Get original image source
        orig_image_source = getattr(self, '_original_image_source', None)
        
        # Check if any values have changed
        is_different = (
            current_question != orig_question or
            current_question_type != orig_question_type or
            is_answerable != orig_answerable or
            current_answer != orig_answer or
            current_tags != orig_tags or
            current_source != orig_source or
            (orig_image_source is not None and current_image_source != orig_image_source)
        )
        
        logger.info(f"Detailed modification check: is_different={is_different}")
        if is_different:
            logger.info(f"Changes detected: question: '{current_question}' vs '{orig_question}', "
                      f"type: '{current_question_type}' vs '{orig_question_type}', "
                      f"answerable: {is_answerable} vs {orig_answerable}, "
                      f"answer: '{current_answer}' vs '{orig_answer}', "
                      f"tags: {current_tags} vs {orig_tags}, "
                      f"source: '{current_source}' vs '{orig_source}'")
        
        # Return true only if there are actual differences
        return is_different
    
    def clear(self):
        """Clear all questions and reset image source"""
        try:
            logger.info("Executing clear() method to reset all data for new image")
            
            # For unlabeled images, we always want to start with answerable=0
            # This ensures that the checkbox is unchecked for new unlabeled images
            current_answerable = 0
            logger.info(f"Setting answerable=0 for new unlabeled image")
            
            # Reset the original state to None to ensure the revert functionality works correctly for new images
            if hasattr(self, '_original_state'):
                self._original_state = None
                logger.info("Original state (_original_state) reset to None in clear() method")
                
            if hasattr(self, '_original_image_source'):
                self._original_image_source = None
                logger.info("Original image source (_original_image_source) reset to None")
            
            # Clear the questions array completely before creating a new default question
            if hasattr(self, 'questions'):
                self.questions = []
                logger.info("Questions array cleared")
                
            # Create a new default question with answerable=0
            self._create_default_question(answerable=current_answerable)
            logger.info(f"Created new default question with answerable=0")
            
            # Reset all UI elements
            self.question_text.clear()
            self.answer_text.clear()
            
            # Set the answerable checkbox to unchecked for new unlabeled images
            old_block_state = self.can_answer_check.blockSignals(True)
            self.can_answer_check.setChecked(False)
            self.can_answer_check.blockSignals(old_block_state)
            logger.info("Set answerable checkbox to: False (unchecked)")
            
            # Update UI for unanswerable questions
            # For unanswerable questions, set the default text
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
            logger.info("Set unanswerable UI state with default text")
            
            self._clear_tags()
            self.tags_search.clear()
            self.source_combo.setCurrentIndex(0)  # Reset to "Manually Annotated"
            logger.info("All UI elements reset to default state")
            
            # Default to "Manual Collected" instead of clearing
            self.image_source = "manually_collected"
            
            if hasattr(self, 'image_source_input') and self.image_source_input:
                self.image_source_input.setCurrentIndex(0)  # Đặt lại nguồn ảnh mặc định là "Manual Collected"
                logger.info("Image source input reset to default 'Manual Collected'")
               
            # Ensure revert button is hidden since we have no original state
            if hasattr(self, 'revert_original_btn') and self.revert_original_btn:
                self.revert_original_btn.setVisible(False)
                self.revert_original_btn.setEnabled(False)
                logger.info("Revert button hidden and disabled")
                 
            # Reset the modified flag
            self.modified = False
            logger.info("Modified flag reset to False")
            
            # Update UI state
            self._update_ui_state()
            logger.info("UI state updated after clearing all data")
        except RuntimeError as e:
            # Log the error when objects have been deleted
            logger.error(f"RuntimeError in clear() method: {str(e)}")
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
        
        # Check if this is an actual change from the original
        is_different = True
        if hasattr(self, '_original_image_source') and self._original_image_source is not None:
            is_different = selected_source != self._original_image_source
            
        # Update the image source property
        self.image_source = selected_source
        
        # Set modified flag only if there's a real change
        if is_different:
            self.modified = True
            logger.info(f"Image source changed from original, setting modified flag to True")
        
        # Update UI state - this will reflect the changed state in the UI
        self._update_ui_state()
        
        # Emit content changed signal to notify parent components
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
        logger.info(f"Can answer checkbox changed to: {can_answer} (state parameter: {state}, Qt.Checked={Qt.Checked})")
        
        # Store the current answer text to preserve it when toggling between states
        current_answer = self.answer_text.text().strip()
        stored_answer = current_answer
        
        # Don't store the default unanswerable text
        if current_answer == "Không thể trả lời được câu hỏi dựa vào thông tin trong ảnh":
            stored_answer = ""
        
        logger.info(f"Stored answer text: '{stored_answer}'")
        
        # Get the model question
        if not self.questions or len(self.questions) == 0:
            logger.info("No questions available in model, returning early")
            return
            
        question = self.questions[0]
        
        # Set answerable flag in the model
        old_answerable = question.get('answerable', 0)
        question['answerable'] = 1 if can_answer else 0
        logger.info(f"Updated answerable flag in model: {old_answerable} -> {question['answerable']}")
        
        # Check if we have an existing answer to preserve
        has_existing_answer = False
        existing_answer = ""
        
        if 'answers' in question and question['answers']:
            if isinstance(question['answers'][0], str):
                existing_answer = question['answers'][0]
            else:
                existing_answer = question['answers'][0].get('answer_text', '')
                
            has_existing_answer = (
                existing_answer and 
                existing_answer != "Không thể trả lời được câu hỏi dựa vào thông tin trong ảnh"
            )
            logger.info(f"Existing answer found: '{existing_answer}', has_existing_answer={has_existing_answer}")
        
        # Update UI based on answerable state
        if not can_answer:
            # For unanswerable questions, set the default text
            if stored_answer and stored_answer != "Không thể trả lời được câu hỏi dựa vào thông tin trong ảnh":
                # Store the entered answer for later
                logger.info(f"Saving answer text '{stored_answer}' to temp_answer")
                question['temp_answer'] = stored_answer
            
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
            logger.info("Set unanswerable UI state with default text")
        else:
            # For answerable questions, restore previous answer if available
            restore_text = ""
            
            # First check if we have a previously stored answer from toggling
            if 'temp_answer' in question and question['temp_answer']:
                restore_text = question['temp_answer']
                logger.info(f"Restoring previously stored answer: '{restore_text}'")
                # Clear the temporary answer after using it
                del question['temp_answer']
            # If there's no temp_answer but we have an existing answer in the model, use that
            elif has_existing_answer:
                restore_text = existing_answer
                logger.info(f"Using existing answer from model: '{restore_text}'")
            
            # If we have answer text to restore, use it
            if restore_text:
                self.answer_text.setText(restore_text)
                logger.info(f"Restored answer text: '{restore_text}'")
            else:
                self.answer_text.clear()
                logger.info("No answer text to restore, cleared the field")
                
            self.answer_text.setReadOnly(False)
            self.answer_text.setStyleSheet("""
                background-color: white;
                border: 1px solid #bdc3c7;
                border-radius: 5px;
                padding: 8px;
                font-size: 13px;
            """)
            self.answer_text.setPlaceholderText("Nhập câu trả lời tại đây...")
            logger.info(f"Set answerable UI state")
        
        # Update the answers array in the model
        if 'answers' not in question:
            question['answers'] = []
            
        answer_text = self.answer_text.text().strip()
        
        if not question['answers']:
            # Create a new answer entry
            logger.info(f"Creating new answer entry with text: '{answer_text}'")
            question['answers'].append({
                'answer_id': 1,
                'answer_text': answer_text,
                'is_correct': False
            })
        else:
            # Update existing answer
            logger.info(f"Updating existing answer to: '{answer_text}'")
            question['answers'][0]['answer_text'] = answer_text
            question['answers'][0]['is_correct'] = False
        
        # Check if this is actually a change from the original state
        is_different = True
        if hasattr(self, '_original_state') and self._original_state is not None:
            orig_answerable = self._original_state.get('answerable', 0) == 1
            is_different = orig_answerable != can_answer
            logger.info(f"Comparing with original state - orig_answerable={orig_answerable}, current={can_answer}, different={is_different}")
            
            # If answerable state changed, also check the answer text
            if not is_different and 'answers' in self._original_state and self._original_state['answers']:
                orig_answer = ""
                if isinstance(self._original_state['answers'][0], str):
                    orig_answer = self._original_state['answers'][0].strip()
                else:
                    orig_answer = self._original_state['answers'][0].get('answer_text', '').strip()
                
                # For comparison, use the default text for unanswerable questions
                current_answer_for_comparison = answer_text
                if not can_answer:
                    current_answer_for_comparison = "Không thể trả lời được câu hỏi dựa vào thông tin trong ảnh"
                
                is_different = orig_answer != current_answer_for_comparison
                logger.info(f"Answer text comparison: original='{orig_answer}', current='{current_answer_for_comparison}', different={is_different}")
        
        # Set modified flag only if there's a real change
        if is_different:
            old_modified = self.modified
            self.modified = True
            logger.info(f"Answerable state or answer text changed from original, setting modified flag: {old_modified} -> {self.modified}")
        
        # Update UI state - this will update button states based on changes
        logger.info("Calling _update_ui_state() after answerable state change")
        self._update_ui_state()
        
        # Notify about content change
        logger.info("Emitting content_changed signal")
        self.content_changed.emit()

    def _setup_initial_state(self):
        """Setup the initial state with can_answer_check matching the answerable flag in the model,
        and answer field in the appropriate mode based on answerable state"""
        if hasattr(self, 'can_answer_check'):
            # Make sure this checkbox is enabled
            self.can_answer_check.setEnabled(True)
            
            # Check if we have a question with answerable flag
            is_answerable = False
            if hasattr(self, 'questions') and self.questions and len(self.questions) > 0:
                is_answerable = self.questions[0].get('answerable', 0) == 1
                logger.info(f"Setting initial answerable state from model: {is_answerable}")
            
            # Set the checkbox based on the model data
            self.can_answer_check.setChecked(is_answerable)
            
            # Update UI to match the checked state
            if is_answerable:
                self._on_can_answer_changed(Qt.Checked)
            else:
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
        
        # When navigating between images, we want to consider default values as valid
        # Only enforce stricter validation when actively saving (confirm button)
        
        # Check if this is called for navigation or for confirmation
        # If is_confirmed is True, this is being checked during confirmation process
        if question.get('is_confirmed', False):
            # For confirmed questions, apply strict validation
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
        else:
            # For navigation between images, consider default values as valid
            # This allows users to move between images with default values
            return True

    def _on_content_changed(self):
        """Handle changes to question properties"""
        if not self.questions:
            return
            
        question = self.questions[0]  # Luôn sử dụng câu hỏi đầu tiên
        current_text = self.question_text.text()
        question_text = current_text.strip()
        
        # Debug log to track method calls
        logger.info(f"_on_content_changed called with text: '{question_text}'")
        
        # Store original content if this is first edit and no original_text exists
        if question.get('is_confirmed', False) and 'original_text' not in question:
            question['original_text'] = question.get('question', '')
        
        # Get current values for validation and comparison
        has_text = bool(question_text)
        has_tags = bool(self.selected_tags)
        is_answerable = self.can_answer_check.isChecked()
        question_answerable = question.get('answerable', 0) == 1
        
        # Log states for debugging
        logger.info(f"_on_content_changed - UI checkbox answerable state: {is_answerable}, model question answerable: {question_answerable}")
        
        # Fix mismatch between model and UI checkbox - THIS IS CRITICAL
        if is_answerable != question_answerable:
            has_original_data = hasattr(self, '_original_state') and self._original_state is not None
            
            # For new unlabeled images (no original state), the UI state should take precedence
            if not has_original_data and is_answerable:
                # This is likely a user explicitly checking the checkbox on a new unlabeled image
                logger.info("New unlabeled image: UI checkbox checked, updating model to match")
                question['answerable'] = 1
                question_answerable = True
            elif not has_original_data and not is_answerable:
                # Ensure model is consistent with UI for new unlabeled images
                logger.info("New unlabeled image: UI checkbox unchecked, ensuring model matches")
                question['answerable'] = 0
                question_answerable = False
            # For loaded questions with original state, model should take precedence
            elif has_original_data and question_answerable:
                # Model says answerable=1 but UI checkbox is unchecked
                # Update UI to match the model (this is the case when loading a question)
                logger.info(f"_on_content_changed - Fixing UI checkbox: Model has answerable=1 but UI checkbox is unchecked")
                
                # Block signals to prevent recursion
                old_block_state = self.can_answer_check.blockSignals(True)
                self.can_answer_check.setChecked(True)
                self.can_answer_check.blockSignals(old_block_state)
                
                # Update UI state for answerable question
                current_answer_text = self.answer_text.text().strip()
                if not current_answer_text or current_answer_text == "Không thể trả lời được câu hỏi dựa vào thông tin trong ảnh":
                    # Try to get the answer from the model
                    answer_text = ""
                    if 'answers' in question and question['answers']:
                        if isinstance(question['answers'][0], str):
                            answer_text = question['answers'][0]
                        else:
                            answer_text = question['answers'][0].get('answer_text', '')
                    
                    if not answer_text or answer_text == "Không thể trả lời được câu hỏi dựa vào thông tin trong ảnh":
                        # If we don't have a valid answer, clear the field
                        self.answer_text.clear()
                    else:
                        # Use the answer from the model
                        self.answer_text.setText(answer_text)
                
                # Update UI style for answerable question
                self.answer_text.setReadOnly(False)
                self.answer_text.setStyleSheet("""
                    background-color: white;
                    border: 1px solid #bdc3c7;
                    border-radius: 5px;
                    padding: 8px;
                    font-size: 13px;
                """)
                self.answer_text.setPlaceholderText("Nhập câu trả lời tại đây...")
                
                # Ensure model is consistent
                is_answerable = True
            elif has_original_data and not question_answerable:
                # Model says answerable=0 but UI checkbox is checked
                # For labeled images, prioritize the UI state (user toggled the checkbox)
                logger.info(f"_on_content_changed - Fixing model: Model has answerable=0 but UI checkbox is checked")
                question['answerable'] = 1
                question_answerable = True
        
        has_answer = bool(self.answer_text.text().strip())
        
        # Basic validation for form completion
        basic_validation = has_text and has_tags and (not is_answerable or (is_answerable and has_answer))
        
        # Check for actual changes compared to original state
        has_changes = True
        has_original_data = hasattr(self, '_original_state') and self._original_state is not None
        
        if has_original_data:
            # Get current values for comparison with original
            current_question = question_text
            current_question_type = str(self.question_type_combo.currentData()).lower()
            current_answer = self.answer_text.text().strip()
            if not is_answerable:
                current_answer = "Không thể trả lời được câu hỏi dựa vào thông tin trong ảnh"
            current_tags = set(self.selected_tags)
            current_source = self.source_combo.currentData()
            current_image_source = self.image_source
            
            # Get original values
            orig_question = self._original_state.get('question', '').strip()
            orig_question_type = str(self._original_state.get('question_type', '')).lower()
            orig_answerable = self._original_state.get('answerable', 0) == 1
            
            # Log original answerable state for debugging
            logger.info(f"_on_content_changed - Original answerable state: {orig_answerable} (value: {self._original_state.get('answerable', 0)})")
            
            # Get original answer
            orig_answer = ""
            if 'answers' in self._original_state and self._original_state['answers']:
                if isinstance(self._original_state['answers'][0], str):
                    orig_answer = self._original_state['answers'][0].strip()
                else:
                    orig_answer = self._original_state['answers'][0].get('answer_text', '').strip()
            
            # Get original tags
            orig_tags = set(self._original_state.get('tags', []))
            
            # Get original source
            orig_source = self._original_state.get('qa_source', self._original_state.get('source', ''))
            
            # Get original image source
            orig_image_source = getattr(self, '_original_image_source', None)
            
            # Check if any values have changed using a single comparison for clarity
            is_different = (
                question_text != orig_question or
                current_question_type != orig_question_type or
                is_answerable != orig_answerable or
                current_answer != orig_answer or
                current_tags != orig_tags or
                current_source != orig_source or
                (orig_image_source is not None and current_image_source != orig_image_source)
            )
            
            # Log detailed comparison results for debugging
            logger.info(f"_on_content_changed - Differences detected: {is_different}")
            if is_different:
                logger.info(f"Differences detected in _on_content_changed:")
                if question_text != orig_question:
                    logger.info(f"  - Question text differs: '{question_text}' vs '{orig_question}'")
                if current_question_type != orig_question_type:
                    logger.info(f"  - Question type differs: '{current_question_type}' vs '{orig_question_type}'")
                if is_answerable != orig_answerable:
                    logger.info(f"  - Answerable state differs: {is_answerable} vs {orig_answerable}")
                if current_answer != orig_answer:
                    logger.info(f"  - Answer differs: '{current_answer}' vs '{orig_answer}'")
                if current_tags != orig_tags:
                    logger.info(f"  - Tags differ: {current_tags} vs {orig_tags}")
                if current_source != orig_source:
                    logger.info(f"  - Source differs: '{current_source}' vs '{orig_source}'")
                if orig_image_source is not None and current_image_source != orig_image_source:
                    logger.info(f"  - Image source differs: '{current_image_source}' vs '{orig_image_source}'")
            
            # Only allow confirmation if there are actual changes
            has_changes = is_different
            
            # Update modified flag based on changes
            self.modified = is_different
            
        # Make sure question in model always matches UI state (which might have been updated above)
        question['question'] = question_text
        question['question_type'] = self.question_type_combo.currentData()
        question['answerable'] = 1 if is_answerable else 0
        
        # Đảm bảo có mảng answers để tương thích với mã hiện có
        if 'answers' not in question:
            question['answers'] = []
            
        # Cập nhật thông tin câu trả lời
        answer_text = self.answer_text.text().strip()  # Use text() instead of toPlainText()
        
        # Đảm bảo có ít nhất một câu trả lời
        if not question['answers']:
            question['answers'].append({
                'answer_id': 1,
                'answer_text': answer_text if is_answerable else "Không thể trả lời được câu hỏi dựa vào thông tin trong ảnh",
                'is_correct': False  # Default to False since we removed the checkbox
            })
        else:
            # If 'answers' is an array of strings, convert it to the expected format
            if isinstance(question['answers'][0], str):
                question['answers'] = [{
                    'answer_id': 1,
                    'answer_text': question['answers'][0],
                    'is_correct': False
                }]
            
            # Now we can safely update the answer text
            question['answers'][0]['answer_text'] = answer_text if is_answerable else "Không thể trả lời được câu hỏi dựa vào thông tin trong ảnh"
        
        # Always call _update_ui_state() after content changes to ensure buttons are enabled properly
        self._update_ui_state()
        
        # Emit signal - this will update the UI elsewhere
        self.content_changed.emit()

    def _on_question_type_changed(self, index):
        """Handle changes to the question type"""
        if not self.questions or not self.questions[0]:
            return
            
        # Log old and new values
        old_value = self.questions[0].get('question_type', 'unknown')
        old_text = "unknown"
        
        # Get old text display value by looking up in combo box
        for i in range(self.question_type_combo.count()):
            if self.question_type_combo.itemData(i) == old_value:
                old_text = self.question_type_combo.itemText(i)
                break
                
        new_value = self.question_type_combo.currentData()
        new_text = self.question_type_combo.currentText()
        
        logger.info(f"Question type changed: Old={old_value} ({old_text}) -> New={new_value} ({new_text})")
            
        # Update the question type in the model
        self.questions[0]['question_type'] = new_value
        
        # Check if this is actually a change from the original value
        is_different = True
        if hasattr(self, '_original_state') and self._original_state is not None:
            orig_type = str(self._original_state.get('question_type', '')).lower()
            current_type = str(new_value).lower()
            is_different = orig_type != current_type
            
        # Set modified flag only if there's a real change from original
        if is_different:
            self.modified = True
            logger.info(f"Question type changed from original, setting modified flag to True")
        
        # Update UI state - this will reflect the changed state in the UI
        self._update_ui_state()
        
        # Emit content changed signal to notify parent components
        self.content_changed.emit()
        
    def _on_source_changed(self, index):
        """Handle changes to the QA source"""
        if not self.questions or not self.questions[0]:
            return
            
        # Get the new source value
        new_source = self.source_combo.currentData()
        
        # Update the source in the model
        self.questions[0]['source'] = new_source
        
        # Check if this is actually a change from the original value
        is_different = True
        if hasattr(self, '_original_state') and self._original_state is not None:
            orig_source = self._original_state.get('qa_source', self._original_state.get('source', ''))
            is_different = orig_source != new_source
            
        # Set modified flag only if there's a real change from original
        if is_different:
            self.modified = True
            logger.info(f"Source changed from original, setting modified flag to True")
        
        # Update UI state - this will reflect the changed state in the UI
        self._update_ui_state()
        
        # Emit content changed signal to notify parent components
        self.content_changed.emit()