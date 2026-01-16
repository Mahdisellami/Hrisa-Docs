"""Logging configuration for the document processor application."""

import logging
import sys
from pathlib import Path
from typing import Optional


def setup_logger(
    name: str = "docprocessor",
    level: int = logging.INFO,
    log_file: Optional[Path] = None,
    rich_formatting: bool = True,
) -> logging.Logger:
    """
    Configure and return a logger instance.

    Args:
        name: Logger name
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional file path for logging output
        rich_formatting: Use Rich for colorful console output

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    logger.handlers.clear()

    # Disable Rich formatting in PyInstaller builds (causes issues)
    is_frozen = getattr(sys, 'frozen', False)
    if is_frozen:
        rich_formatting = False

    if rich_formatting:
        try:
            from rich.logging import RichHandler
        except ImportError:
            rich_formatting = False

    if rich_formatting:
        try:
            console_handler = RichHandler(
                rich_tracebacks=True,
                markup=True,
                show_time=True,
                show_level=True,
                show_path=True,
            )
            console_handler.setLevel(level)
            logger.addHandler(console_handler)
        except Exception:
            # Fall back to basic logging if Rich fails
            rich_formatting = False

    if not rich_formatting:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        console_format = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        console_handler.setFormatter(console_format)
        logger.addHandler(console_handler)

    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setLevel(level)
        file_format = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        file_handler.setFormatter(file_format)
        logger.addHandler(file_handler)

    logger.propagate = False

    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger by name. If not configured, returns a basic logger.

    Args:
        name: Logger name

    Returns:
        Logger instance
    """
    logger = logging.getLogger(name)
    if not logger.handlers:
        return setup_logger(name)
    return logger
