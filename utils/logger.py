"""
utils/logger.py
---------------
Configures a single, shared logger for the entire project.
Every module calls `get_logger(__name__)` to get its own logger
that feeds into the same handlers (console + optional file).
"""

import logging
import sys
from pathlib import Path


def get_logger(name: str, log_level: str = "INFO", log_file: str | None = None) -> logging.Logger:
    """Return a configured logger.

    Args:
        name:      Usually __name__ of the calling module.
        log_level: One of DEBUG / INFO / WARNING / ERROR / CRITICAL.
        log_file:  Optional path to write logs to disk.

    Returns:
        A logging.Logger instance.
    """
    logger = logging.getLogger(name)

    # Don't add handlers twice if logger already configured
    if logger.handlers:
        return logger

    logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))

    # ── Console handler ────────────────────────────────────────────────────────
    console_fmt = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%H:%M:%S",
    )
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(console_fmt)
    logger.addHandler(console_handler)

    # ── Optional file handler ──────────────────────────────────────────────────
    if log_file:
        Path(log_file).parent.mkdir(parents=True, exist_ok=True)
        file_fmt = logging.Formatter(
            fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setFormatter(file_fmt)
        logger.addHandler(file_handler)

    return logger
