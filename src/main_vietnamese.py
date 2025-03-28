import sys
import os
import logging
from PyQt5.QtWidgets import QApplication

# Add the src directory to the path to allow absolute imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.ui.vietnam_main_window import VietnamMainWindow

def setup_logging():
    """Setup application logging"""
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(f"{log_dir}/app.log"),
            logging.StreamHandler()
        ]
    )

if __name__ == "__main__":
    setup_logging()
    logger = logging.getLogger(__name__)
    logger.info("Starting Vietnamese Image Labeling Tool")
    
    app = QApplication(sys.argv)
    window = VietnamMainWindow()
    window.showMaximized()
    
    sys.exit(app.exec_()) 