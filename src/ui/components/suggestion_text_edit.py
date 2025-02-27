from PyQt5.QtWidgets import QTextEdit
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QKeyEvent, QTextCursor, QColor, QTextCharFormat, QBrush, QFont
import logging

logger = logging.getLogger(__name__)

class SuggestionTextEdit(QTextEdit):
    """Custom QTextEdit with automatic inline suggestion support"""
    
    suggestionAccepted = pyqtSignal()  # Signal when suggestion is accepted
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_suggestion = None
        self.suggestion_start_pos = None
        self.suggestion_format = self._create_suggestion_format()
        self.is_setting_suggestion = False
        self.setAcceptRichText(True)
        
    def _create_suggestion_format(self):
        """Create the format for suggestion text"""
        fmt = QTextCharFormat()
        # No background, just subtle text styling
        fmt.setBackground(QBrush(QColor(255, 255, 255, 0)))  # Transparent background
        # Slightly gray, semi-transparent text
        fmt.setForeground(QBrush(QColor(70, 70, 70, 180)))  # Semi-transparent dark gray
        font = QFont()
        font.setItalic(True)  # Italic for suggestions
        font.setWeight(QFont.Light)  # Lighter weight for subtle appearance
        fmt.setFont(font)
        return fmt
        
    def set_suggestion(self, suggestion: str):
        """Show suggestion in the text edit"""
        if not suggestion:
            return
            
        self.is_setting_suggestion = True
        try:
            # Store suggestion
            self.current_suggestion = suggestion
            
            # Clear existing content and suggestion
            self.clear()
            
            # Insert and format suggestion
            cursor = self.textCursor()
            self.suggestion_start_pos = 0
            cursor.insertText(suggestion)
            cursor.setPosition(0)
            cursor.movePosition(QTextCursor.End, QTextCursor.KeepAnchor)
            cursor.mergeCharFormat(self.suggestion_format)
            
            # Move cursor to start
            cursor.setPosition(0)
            self.setTextCursor(cursor)
            
        finally:
            self.is_setting_suggestion = False
        
    def clear_suggestion(self):
        """Clear any existing suggestion"""
        if self.current_suggestion:
            self.clear()
            self.current_suggestion = None
            self.suggestion_start_pos = None
            
    def keyPressEvent(self, e: QKeyEvent):
        """Handle key press events"""
        # If Tab is pressed and there's a suggestion, accept it
        if e.key() == Qt.Key_Tab and self.current_suggestion:
            # Accept the suggestion by removing formatting
            cursor = self.textCursor()
            cursor.select(QTextCursor.Document)
            cursor.setCharFormat(QTextCharFormat())
            
            # Move cursor to end
            cursor.movePosition(QTextCursor.End)
            self.setTextCursor(cursor)
            
            # Clear suggestion state but keep the text
            self.current_suggestion = None
            self.suggestion_start_pos = None
            
            # Emit acceptance signal
            self.suggestionAccepted.emit()
            return
            
        # If there's a suggestion and user types something else, clear it
        if e.key() != Qt.Key_Tab and self.current_suggestion:
            if e.key() in (Qt.Key_Left, Qt.Key_Right, Qt.Key_Up, Qt.Key_Down):
                super().keyPressEvent(e)
                return
            self.clear_suggestion()
            
        super().keyPressEvent(e) 