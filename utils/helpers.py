"""
utils/helpers.py
----------------
Small, reusable utility functions shared across the project.
Add generic helpers here — keep them pure and side-effect-free
so they are easy to unit-test later.
"""

import re
from datetime import datetime


def format_response(text: str, assistant_name: str = "JARVIS") -> str:
    """Wrap an assistant reply with a consistent prefix.

    Args:
        text:           The raw reply text.
        assistant_name: Name printed before the reply.

    Returns:
        Formatted string like: "[JARVIS] Hello, sir."
    """
    return f"[{assistant_name}] {text.strip()}"


def sanitize_input(text: str) -> str:
    """Strip leading/trailing whitespace and collapse internal spaces.

    Args:
        text: Raw user input string.

    Returns:
        Cleaned string.
    """
    return re.sub(r"\s+", " ", text).strip()


def current_timestamp() -> str:
    """Return a human-readable current timestamp.

    Returns:
        String like "2026-09-15 14:30:00"
    """
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def greeting_by_time() -> str:
    """Return an appropriate greeting based on the current hour.

    Returns:
        'Good morning', 'Good afternoon', or 'Good evening'.
    """
    hour = datetime.now().hour
    if hour < 12:
        return "Good morning"
    elif hour < 18:
        return "Good afternoon"
    else:
        return "Good evening"
