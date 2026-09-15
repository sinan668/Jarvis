"""
voice/listener.py
-----------------
Handles microphone input and speech-to-text conversion.

Current state  (foundation only):
  - The Listener class is scaffolded and ready to use.
  - `listen()` returns a stub string so the project runs without
    a microphone or internet connection during development.

Future steps:
  - Replace the stub with real `speech_recognition` calls.
  - Add wake-word detection (e.g. using pvporcupine or pocketsphinx).
"""

from utils.logger import get_logger

logger = get_logger(__name__)


class Listener:
    """Captures voice input and converts it to text.

    Usage:
        listener = Listener(language="en-US")
        text = listener.listen()
    """

    def __init__(self, language: str = "en-US") -> None:
        """
        Args:
            language: BCP-47 language code for speech recognition.
        """
        self.language = language
        logger.info("Listener initialised (language=%s)", language)

    def listen(self) -> str:
        """Record audio from the microphone and return transcribed text.

        Returns:
            Transcribed string, or empty string if nothing was heard.

        Note:
            Currently returns a placeholder. Wire up `speech_recognition`
            here in the next voice-input step.
        """
        # ── TODO: replace with real microphone capture ─────────────────────────
        # import speech_recognition as sr
        # recognizer = sr.Recognizer()
        # with sr.Microphone() as source:
        #     audio = recognizer.listen(source, timeout=5)
        # return recognizer.recognize_google(audio, language=self.language)
        logger.debug("listen() called — stub returns empty string")
        return ""

    def calibrate(self) -> None:
        """Calibrate microphone for ambient noise.

        Call this once at startup before the main listen loop.
        """
        # ── TODO: sr.Recognizer().adjust_for_ambient_noise(source) ────────────
        logger.info("Microphone calibration placeholder called.")
