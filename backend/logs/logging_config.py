import logging
import sys
from datetime import datetime

def setup_logging():
    """Centralized logging configuration for the backend"""

    # Create logs directory if it doesn't exist
    import os
    # Use parent directory of this file (which is backend/logs/) as the logs directory
    logs_dir = os.path.dirname(__file__)
    os.makedirs(logs_dir, exist_ok=True)

    # Configure logging format
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # File handler for all logs
    log_file_path = os.path.join(logs_dir, f"backend_{datetime.now().strftime('%Y%m%d')}.log")
    file_handler = logging.FileHandler(log_file_path)
    file_handler.setFormatter(formatter)

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)

    # Root logger configuration
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)

    return root_logger