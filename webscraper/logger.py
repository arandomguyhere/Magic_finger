"""
Logging configuration for WebScraper.

Provides centralized logging with file rotation and console output.
"""

import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional

from .config import Config


def setup_logger(
    name: str = 'webscraper',
    log_file: Optional[str] = None,
    log_level: Optional[str] = None,
    console_output: bool = True
) -> logging.Logger:
    """
    Set up a logger with file rotation and optional console output.

    Args:
        name: Logger name
        log_file: Path to log file (default from Config)
        log_level: Logging level (default from Config)
        console_output: Whether to output to console

    Returns:
        Configured logger instance
    """
    # Get or create logger
    logger = logging.getLogger(name)

    # Avoid adding handlers multiple times
    if logger.handlers:
        return logger

    # Set log level
    level = getattr(logging, (log_level or Config.LOG_LEVEL).upper(), logging.INFO)
    logger.setLevel(level)

    # Create formatter
    formatter = logging.Formatter(Config.LOG_FORMAT)

    # File handler with rotation
    if log_file or Config.LOG_FILE:
        log_path = Path(log_file or Config.LOG_FILE)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        file_handler = RotatingFileHandler(
            log_path,
            maxBytes=Config.LOG_MAX_BYTES,
            backupCount=Config.LOG_BACKUP_COUNT
        )
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    # Console handler
    if console_output:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    return logger


def get_logger(name: str = 'webscraper') -> logging.Logger:
    """
    Get or create a logger instance.

    Args:
        name: Logger name

    Returns:
        Logger instance
    """
    logger = logging.getLogger(name)
    if not logger.handlers:
        return setup_logger(name)
    return logger


# Create default loggers for each module
harvester_logger = setup_logger('webscraper.harvester')
validator_logger = setup_logger('webscraper.validator')
scraper_logger = setup_logger('webscraper.scraper')
