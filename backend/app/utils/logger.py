"""
Centralized logging configuration
"""
import logging
import sys
from app.config import settings

# Create logger
logger = logging.getLogger("inclutalk")
logger.setLevel(getattr(logging, settings.LOG_LEVEL.upper()))

# Create console handler
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(getattr(logging, settings.LOG_LEVEL.upper()))

# Create file handler
file_handler = logging.FileHandler(settings.LOG_FILE)
file_handler.setLevel(getattr(logging, settings.LOG_LEVEL.upper()))

# Create formatter
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

console_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)

# Add handlers to logger
logger.addHandler(console_handler)
logger.addHandler(file_handler)


def log_info(message: str):
    """Log info message"""
    logger.info(message)


def log_warning(message: str):
    """Log warning message"""
    logger.warning(message)


def log_error(message: str, exc_info=False):
    """Log error message"""
    logger.error(message, exc_info=exc_info)


def log_debug(message: str):
    """Log debug message"""
    logger.debug(message)
