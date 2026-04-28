# This file shows the logging implementation to be integrated

import logging
from pathlib import Path

# Configure logging
def setup_logging():
    """Configure and return a logger for the application."""
    logger = logging.getLogger('AssetScanner')
    logger.setLevel(logging.DEBUG)
    
    # Create log file path
    log_file = Path("asset_scanner.log")
    
    # File handler - logs everything
    try:
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_format = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - [%(funcName)s] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_format)
        logger.addHandler(file_handler)
    except Exception as e:
        print(f"Warning: Could not create log file: {e}")
    
    # Console handler - logs warnings and above
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.WARNING)
    console_format = logging.Formatter('%(levelname)s: %(message)s')
    console_handler.setFormatter(console_format)
    logger.addHandler(console_handler)
    
    return logger

logger = setup_logging()
