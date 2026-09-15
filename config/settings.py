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
    load_dotenv(ROOT_DIR / ".env")  # silently ignored if .env doesn't exist
except ImportError:
    # python-dotenv not installed yet — environment variables still work fine
    pass


class Settings:
    """Central configuration object.

    Add new config keys here as the project grows.
    Usage:
        from config import Settings
        cfg = Settings()
        print(cfg.assistant_name)
    """

    # ── Identity ───────────────────────────────────────────────────────────────
    assistant_name: str = os.getenv("ASSISTANT_NAME", "JARVIS")
    wake_word: str = os.getenv("WAKE_WORD", "jarvis")

    # ── AI backend (filled in when you add a real LLM) ────────────────────────
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    # Hugging Face (free, local models in later steps)
    huggingface_model: str = os.getenv("HUGGINGFACE_MODEL", "microsoft/DialoGPT-medium")

    # ── Voice ──────────────────────────────────────────────────────────────────
    speech_language: str = os.getenv("SPEECH_LANGUAGE", "en-US")
    tts_rate: int = int(os.getenv("TTS_RATE", "180"))   # words-per-minute
    tts_volume: float = float(os.getenv("TTS_VOLUME", "1.0"))

    # ── Logging ────────────────────────────────────────────────────────────────
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    log_file: str = os.getenv("LOG_FILE", str(ROOT_DIR / "jarvis.log"))

    # ── Paths ──────────────────────────────────────────────────────────────────
    root_dir: Path = ROOT_DIR
    data_dir: Path = ROOT_DIR / "data"

    def __repr__(self) -> str:
        return (
            f"<Settings assistant={self.assistant_name!r} "
            f"wake_word={self.wake_word!r} "
            f"log_level={self.log_level!r}>"
        )
