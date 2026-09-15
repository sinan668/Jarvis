"""
config/settings.py
------------------
Loads configuration from environment variables and the .env file.
All tunable parameters live here so the rest of the codebase never
has to import `os` or call `dotenv` directly.
"""

import os
from pathlib import Path

# ── Locate the project root ────────────────────────────────────────────────────
ROOT_DIR = Path(__file__).resolve().parent.parent

# ── Optionally load .env (requires python-dotenv, installed in Step 1) ────────
try:
    from dotenv import load_dotenv
    load_dotenv(ROOT_DIR / ".env", override=True)  # silently ignored if .env doesn't exist
except ImportError:
    pass


class Settings:
    """Central configuration object.

    Add new config keys here as the project grows.
    Usage:
        from config import Settings
        cfg = Settings()
        print(cfg.assistant_name)
    """

    def __init__(self) -> None:
        # Reload dotenv on init if present
        try:
            from dotenv import load_dotenv
            load_dotenv(ROOT_DIR / ".env", override=True)
        except ImportError:
            pass

        # ── Identity ───────────────────────────────────────────────────────────
        self.assistant_name: str = os.getenv("ASSISTANT_NAME", "JARVIS")
        self.wake_word: str = os.getenv("WAKE_WORD", "jarvis").strip().lower()

        # ── AI backend (filled in when you add a real LLM) ────────────────────
        self.openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
        self.openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        self.huggingface_model: str = os.getenv("HUGGINGFACE_MODEL", "microsoft/DialoGPT-medium")

        # ── Voice ──────────────────────────────────────────────────────────────
        self.speech_language: str = os.getenv("SPEECH_LANGUAGE", "en-US")
        self.tts_rate: int = int(os.getenv("TTS_RATE", "180"))
        self.tts_volume: float = float(os.getenv("TTS_VOLUME", "1.0"))

        # ── Logging ────────────────────────────────────────────────────────────
        self.log_level: str = os.getenv("LOG_LEVEL", "INFO")
        self.log_file: str = os.getenv("LOG_FILE", str(ROOT_DIR / "jarvis.log"))

        # ── Paths ──────────────────────────────────────────────────────────────
        self.root_dir: Path = ROOT_DIR
        self.data_dir: Path = ROOT_DIR / "data"

    def __repr__(self) -> str:
        return (
            f"<Settings assistant={self.assistant_name!r} "
            f"wake_word={self.wake_word!r} "
            f"log_level={self.log_level!r}>"
        )
