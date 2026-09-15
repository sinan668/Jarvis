# system/__init__.py
# Exposes system-level controls (apps, OS info, file operations, etc.)

from .controller import SystemController

__all__ = ["SystemController"]
