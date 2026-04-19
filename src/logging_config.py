"""
Project-wide logging configuration.

This module provides a single place to configure logging for the entire
application. Import and call ``setup_logging()`` once at startup (e.g. in
``main.py``) before other modules do any logging.
"""

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

from src.config import get_config


def setup_logging() -> None:
    """
    Configure root logger with console and file handlers.

    - Console: INFO and above
    - File: DEBUG and above, rotating log file under output/logs
    """
    config = get_config()

    # Ensure log directory exists
    logs_dir = Path(config.output_dir) / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)

    log_file = logs_dir / "application.log"

    # Basic formatter
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    # File handler (rotating)
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=5 * 1024 * 1024,  # 5 MB
        backupCount=3,
        encoding="utf-8",
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)

    # Avoid adding duplicate handlers if called multiple times
    if not any(isinstance(h, RotatingFileHandler) for h in root_logger.handlers):
        root_logger.addHandler(file_handler)
    if not any(isinstance(h, logging.StreamHandler) for h in root_logger.handlers):
        root_logger.addHandler(console_handler)

