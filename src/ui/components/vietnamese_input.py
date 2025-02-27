from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel, QMessageBox)
from PyQt5.QtCore import Qt
from ...services.translation_service import TranslationService
from .suggestion_text_edit import SuggestionTextEdit
import logging
from PyQt5.QtWidgets import QGraphicsOpacityEffect

logger = logging.getLogger(__name__)

class VietnameseInput(QWidget):
    def __init__(self):
        super().__init__()
        self.translation_service = TranslationService()
        self.init_ui()
        # Cache for translations to avoid repeated calls
        self.translation_cache = {}
        # Track if this is a labeled image and if it's been modified
        self.is_labeled = False
        self.has_changes = False
        self._original_question = ""
        self._original_answer = ""

    def init_ui(self):
        """Initialize the Vietnamese input UI"""
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 0, 10, 10)
        layout.setSpacing(0)

        # Create title label
        title_label = QLabel("Vietnamese")
        title_label.setStyleSheet("""
            font-size: 34px;
            font-weight: bold;
            color: #333;
            background: transparent;
        """)

        # Question section
        question_layout = QVBoxLayout()
        question_layout.setSpacing(5)
        question_label = QLabel("<b>Question (VN):</b>")
        question_label.setStyleSheet("""
            font-size: 24px;
            color: #000;
            background: transparent;
        """)
        self.question_input = SuggestionTextEdit()
        self.question_input.setPlaceholderText("Enter Vietnamese question here...")
        self.question_input.setStyleSheet("""
            QTextEdit {
                border: 1px solid #bdc3c7;
                border-radius: 5px;
                padding: 8px;
                background-color: white;
                font-size: 24px;
                color: #000;
            }
        """)
        
        question_layout.addWidget(question_label)
        question_layout.addWidget(self.question_input)

        # Answer section
        answer_layout = QVBoxLayout()
        answer_layout.setSpacing(5)
        answer_label = QLabel("<b>Answer (VN):</b>")
        answer_label.setStyleSheet("""
            font-size: 24px;
            color: #000;
            background: transparent;
        """)
        self.answer_input = SuggestionTextEdit()
        self.answer_input.setPlaceholderText("Enter Vietnamese answer here...")
        self.answer_input.setStyleSheet("""
            QTextEdit {
                border: 1px solid #bdc3c7;
                border-radius: 5px;
                padding: 8px;
                background-color: white;
                font-size: 24px;
                color: #000;
            }
        """)
        
        answer_layout.addWidget(answer_label)
        answer_layout.addWidget(self.answer_input)

        # Add all sections to main layout
        layout.addWidget(title_label)
        layout.addSpacing(10)
        layout.addLayout(question_layout)
        layout.addSpacing(15)
        layout.addLayout(answer_layout)
        
        self.setLayout(layout)
        
        # Apply opacity effect
        opacity_effect = QGraphicsOpacityEffect()
        opacity_effect.setOpacity(0.7)
        self.setGraphicsEffect(opacity_effect)

        # Connect signals after setup to avoid initial triggers
        self.question_input.textChanged.connect(self._on_question_changed)
        self.answer_input.textChanged.connect(self._on_answer_changed)

    def set_english_content(self, question, answer):
        """Store the English content for translation and show suggestions"""
        self.current_eng_question = question
        self.current_eng_answer = answer

    def _is_valid_translation(self, english: str, vietnamese: str) -> bool:
        """Validate if the translation seems reasonable"""
        if not vietnamese:
            return False
            
        # Skip if translation is too different in length (likely wrong)
        if len(vietnamese) < len(english) * 0.3 or len(vietnamese) > len(english) * 3:
            return False
            
        # Skip if translation contains non-Vietnamese characters
        if any(ord(c) > 127 and c not in 'àáạảãâầấậẩẫăằắặẳẵèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹđ' for c in vietnamese.lower()):
            return False
            
        # Skip if translation is just repeating the English
        if english.lower() in vietnamese.lower() or vietnamese.lower() in english.lower():
            return False
            
        return True

    def _get_cached_translation(self, text: str) -> str:
        """Get translation from cache or translate and cache it"""
        if text in self.translation_cache:
            return self.translation_cache[text]
            
        suggestion = self.translation_service.get_suggestion(text)
        if suggestion and self._is_valid_translation(text, suggestion):
            self.translation_cache[text] = suggestion
            return suggestion
        return None

    def _handle_translation_error(self, error):
        """Handle translation errors"""
        logger.error(f"Translation error: {str(error)}")
        # Don't show error message to user for automatic suggestions

    def _show_question_suggestion(self):
        """Show translation suggestion for question"""
        if not hasattr(self, 'current_eng_question'):
            return
            
        if self.current_eng_question == 'No question available':
            return
            
        try:
            suggestion = self._get_cached_translation(self.current_eng_question)
            if suggestion:  # Only show if we got a valid translation
                self.question_input.set_suggestion(suggestion)
        except Exception as e:
            self._handle_translation_error(str(e))

    def _show_answer_suggestion(self):
        """Show translation suggestion for answer"""
        if not hasattr(self, 'current_eng_answer'):
            return
            
        if self.current_eng_answer == 'No answer available':
            return
            
        try:
            suggestion = self._get_cached_translation(self.current_eng_answer)
            if suggestion:  # Only show if we got a valid translation
                self.answer_input.set_suggestion(suggestion)
        except Exception as e:
            self._handle_translation_error(str(e))

    def _on_question_changed(self):
        """Handle question text changes"""
        if not self.question_input.is_setting_suggestion:
            current_text = self.question_input.toPlainText().strip()
            # Check if content changed from original
            if current_text != self._original_question:
                self.has_changes = True
                logger.debug("Question changed from original")
            if not current_text and hasattr(self, 'current_eng_question'):
                self._show_question_suggestion()

    def _on_answer_changed(self):
        """Handle answer text changes"""
        if not self.answer_input.is_setting_suggestion:
            current_text = self.answer_input.toPlainText().strip()
            # Check if content changed from original
            if current_text != self._original_answer:
                self.has_changes = True
                logger.debug("Answer changed from original")
            if not current_text and hasattr(self, 'current_eng_answer'):
                self._show_answer_suggestion()

    def get_inputs(self):
        """Get the current Vietnamese inputs"""
        return {
            'question': self.question_input.toPlainText().strip(),
            'answer': self.answer_input.toPlainText().strip()
        }

    def set_inputs(self, question, answer):
        """Set the Vietnamese inputs"""
        # Store original content
        self._original_question = question.strip()
        self._original_answer = answer.strip()
        
        # Set labeled status based on original content
        self.is_labeled = bool(self._original_question and self._original_answer)
        # Reset change tracking
        self.has_changes = False
        
        logger.debug(f"Setting inputs - is_labeled: {self.is_labeled}, has_changes: {self.has_changes}")
        self.question_input.setText(question)
        self.answer_input.setText(answer)

    def clear_inputs(self):
        """Clear both input fields and show suggestions if English content is available"""
        self.question_input.clear()
        self.answer_input.clear()
        # Reset all flags when clearing
        self.is_labeled = False
        self.has_changes = False
        self._original_question = ""
        self._original_answer = ""
        logger.debug("Cleared all inputs and reset flags")
        
        # Only show suggestions after manual clearing
        if hasattr(self, 'current_eng_question') and self.current_eng_question != 'No question available':
            self._show_question_suggestion()
        if hasattr(self, 'current_eng_answer') and self.current_eng_answer != 'No answer available':
            self._show_answer_suggestion()

    def has_both_inputs(self):
        """Check if both inputs have content (including suggestions)"""
        return bool(self.question_input.toPlainText().strip() and 
                   self.answer_input.toPlainText().strip())

    def should_show_confirmation(self):
        """Check if confirmation dialog should be shown
        Returns:
            - False if this is a labeled image and no changes made
            - True if unlabeled or changes made
        """
        # Skip confirmation only for labeled images with no changes
        if self.is_labeled and not self.has_changes:
            logger.debug("Skipping confirmation - labeled image with no changes")
            return False
        
        logger.debug("Showing confirmation - unlabeled or has changes")
        return True 