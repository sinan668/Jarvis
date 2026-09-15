"""
voice/speaker.py
----------------
Handles text-to-speech output (JARVIS speaks back to the user).

Current state (foundation only):
  - The Speaker class is scaffolded and ready to use.
  - `speak()` prints the text to the console so the project runs
    without a sound card or TTS library during early development.

Future steps:
  - Replace the print stub with pyttsx3 (offline) or gTTS (online).
  - Add SSML support for more natural-sounding speech.
"""

from utils.logger import get_logger

logger = get_logger(__name__)


class Speaker:
    """Converts text to audible speech.

    Usage:
        speaker = Speaker(rate=180, volume=1.0)
        speaker.speak("All systems online, sir.")
    """

    def __init__(self, rate: int = 180, volume: float = 1.0) -> None:
        """
        Args:
            rate:   Speech rate in words per minute.
            volume: Volume level 0.0 – 1.0.
        """
        self.rate = rate
        self.volume = volume
        logger.info("Speaker initialised (rate=%d, volume=%.1f)", rate, volume)

    def speak(self, text: str) -> None:
        """Convert `text` to speech and play it.

        Args:
            text: The string to be spoken aloud.

        Note:
            Currently prints to console. Replace with pyttsx3 in the
            next voice-output step.
        """
        if not text:
            return

        # ── TODO: replace with real TTS ────────────────────────────────────────
        # import pyttsx3
        # engine = pyttsx3.init()
        # engine.setProperty("rate", self.rate)
        # engine.setProperty("volume", self.volume)
        # engine.say(text)
        # engine.runAndWait()

        logger.debug("speak() called with: %r", text)
        print(f"🔊 {text}")   # placeholder — console output for now

    def set_voice(self, voice_id: str) -> None:
        """Select a specific TTS voice by its ID.

        Args:
            voice_id: Platform-specific voice identifier.
        """
        # ── TODO: engine.setProperty("voice", voice_id) ───────────────────────
        logger.info("set_voice() placeholder called with id=%r", voice_id)
