"""
system/controller.py
--------------------
Provides OS-level controls: launching applications, file operations,
clipboard management, and system information queries.

Current state (foundation only):
  - All methods are scaffolded with clear docstrings and TODOs.
  - `get_os_info()` is the one live method — it returns real data now.
  - Everything else is a safe, no-op stub.

Future steps:
  - Implement app launching with `subprocess`.
  - Implement file search with `pathlib`.
  - Implement clipboard and screen control with `pyperclip` / `pyautogui`.
"""

import platform
import os
from utils.logger import get_logger

logger = get_logger(__name__)


class SystemController:
    """Provides safe, high-level OS interaction methods.

    Usage:
        controller = SystemController()
        info = controller.get_os_info()
        controller.open_application("notepad")
    """

    def __init__(self) -> None:
        logger.info("SystemController initialised on %s.", platform.system())

    # ── System information ─────────────────────────────────────────────────────

    def get_os_info(self) -> dict:
        """Return basic information about the operating system.

        Returns:
            Dict with keys: system, node, release, machine, python_version.
        """
        info = {
            "system":         platform.system(),
            "node":           platform.node(),
            "release":        platform.release(),
            "machine":        platform.machine(),
            "python_version": platform.python_version(),
            "cpu_count":      os.cpu_count(),
        }
        logger.debug("OS info: %s", info)
        return info

    # ── Application control ────────────────────────────────────────────────────

    def open_application(self, app_name: str) -> bool:
        """Launch an application by name.

        Args:
            app_name: Name or path of the application to open.

        Returns:
            True on success, False on failure.

        Note:
            Stub — implement with `subprocess.Popen` in the system step.
        """
        # ── TODO ───────────────────────────────────────────────────────────────
        # import subprocess
        # subprocess.Popen([app_name])
        logger.info("open_application(%r) — stub called.", app_name)
        return False

    def close_application(self, app_name: str) -> bool:
        """Terminate a running application.

        Args:
            app_name: Process name to kill.

        Returns:
            True on success, False on failure.

        Note:
            Stub — implement with `psutil` in the system step.
        """
        logger.info("close_application(%r) — stub called.", app_name)
        return False

    # ── File operations ────────────────────────────────────────────────────────

    def search_files(self, query: str, directory: str = ".") -> list[str]:
        """Find files matching a query in a directory tree.

        Args:
            query:     Filename pattern or substring to search for.
            directory: Root directory for the search (default: cwd).

        Returns:
            List of matching file paths.

        Note:
            Stub — implement with `pathlib.Path.rglob` in the file step.
        """
        logger.info("search_files(%r, %r) — stub called.", query, directory)
        return []

    def read_file(self, path: str) -> str:
        """Read and return the contents of a text file.

        Args:
            path: Absolute or relative path to the file.

        Returns:
            File contents as a string, or empty string on error.
        """
        logger.info("read_file(%r) — stub called.", path)
        return ""

    def write_file(self, path: str, content: str) -> bool:
        """Write content to a file (creates if not exists, overwrites if it does).

        Args:
            path:    Target file path.
            content: Text to write.

        Returns:
            True on success, False on failure.
        """
        logger.info("write_file(%r) — stub called.", path)
        return False

    # ── Clipboard ──────────────────────────────────────────────────────────────

    def get_clipboard(self) -> str:
        """Return the current clipboard text.

        Note:
            Stub — implement with `pyperclip` in the automation step.
        """
        logger.info("get_clipboard() — stub called.")
        return ""

    def set_clipboard(self, text: str) -> None:
        """Copy text to the clipboard.

        Args:
            text: String to place on the clipboard.

        Note:
            Stub — implement with `pyperclip` in the automation step.
        """
        logger.info("set_clipboard(%r) — stub called.", text)
