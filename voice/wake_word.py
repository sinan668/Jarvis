"""
voice/wake_word.py
------------------
Wake-word detection module for JARVIS.

Step 3 — Wake Word Detection:
  • Monitors microphone input until the configured wake word (default: "jarvis") is spoken.
  • Reuses the `Listener` class from Step 2 for audio capture and speech recognition.
  • Case-insensitive matching.
  • Ignores ambient conversation that does not contain the wake word.
  • Configurable wake word via the settings system.
"""

from utils.logger import get_logger
from voice.listener import Listener

logger = get_logger(__name__)


class WakeWordDetector:
    """Detects when the user speaks the configured wake word.

    Attributes:
        listener : Instance of `Listener` used to record audio and perform STT.
        wake_word: Target phrase to wake JARVIS up (case-insensitive).
    """

    def __init__(self, listener: Listener, wake_word: str = "jarvis") -> None:
        """
        Args:
            listener : Configured `Listener` instance from Step 2.
            wake_word: Wake word to trigger activation (default: "jarvis").
        """
        self.listener = listener
        self.wake_word = wake_word.strip().lower()
        logger.info("WakeWordDetector initialized with wake_word=%r", self.wake_word)

    def set_wake_word(self, wake_word: str) -> None:
        """Update the wake word configuration dynamically.

        Args:
            wake_word: New wake word string.
        """
        self.wake_word = wake_word.strip().lower()
        logger.info("Wake word updated to: %r", self.wake_word)

    def is_wake_word_present(self, text: str) -> bool:
        """Check if the wake word is present in the given text string.

        Matching is case-insensitive.

        Args:
            text: Transcribed text from microphone.

        Returns:
            True if wake word is found, False otherwise.
        """
        if not text:
            return False
        return self.wake_word in text.lower()

    def listen_for_wake_word(self) -> tuple[bool, str]:
        """Listen passively for audio and check if it contains the wake word.

        Ignores normal conversation that does not contain the wake word.
        If the wake word is detected along with a command in a single utterance
        (e.g., "Jarvis what time is it"), the remaining command is extracted.

        Returns:
            Tuple of (detected: bool, remaining_command: str)
            - detected         : True if the wake word was detected.
            - remaining_command: Command portion spoken after wake word, or "" if none.
        """
        if not self.listener.is_available():
            logger.debug("listen_for_wake_word() skipped — listener not available.")
            return False, ""

        print("[JARVIS] Waiting for wake word...")
        logger.info("Waiting for wake word: %r...", self.wake_word)

        # Listen passively without printing standard active listening banners
        raw_text = self.listener.listen_passive()

        if not raw_text:
            return False, ""

        raw_lower = raw_text.lower()
        if self.wake_word in raw_lower:
            logger.info("Wake word %r detected in input: %r", self.wake_word, raw_text)
            print("[JARVIS] Wake word detected.")

            # Extract any command text spoken right after the wake word in the same sentence
            idx = raw_lower.find(self.wake_word)
            command_part = raw_text[idx + len(self.wake_word):].strip()
            # Clean leading punctuation
            command_part = command_part.lstrip(",.!? ")

            return True, command_part

        logger.info("Ignored speech (no wake word %r): %r", self.wake_word, raw_text)
        return False, ""
