"""
voice/listener.py
-----------------
Handles microphone input and converts speech to text.

Step 2 — Voice Input:
  • Uses the `SpeechRecognition` library as the high-level interface.
  • Uses `PyAudio` / `portaudio` as the microphone hardware driver.
  • Primary recogniser  : Google Web Speech API (free, no key required).
  • Offline fallback    : PocketSphinx (if installed).
  • Handles all common error conditions gracefully so JARVIS never crashes.

Step 3 — Wake Word Integration:
  • Adds `verbose: bool = True` parameter to `listen()`.
  • Adds `listen_passive()` method to record audio silently without printing banners.

Usage:
    listener = Listener(language="en-US")
    listener.calibrate()          # call once at startup
    text = listener.listen()      # active listening (prints prompts)
    text = listener.listen_passive() # passive listening for wake word
"""

import sys
import contextlib
import os
from utils.logger import get_logger

logger = get_logger(__name__)

# ── Try importing the required libraries ──────────────────────────────────────
try:
    import speech_recognition as sr
    _SR_AVAILABLE = True
except ImportError:
    _SR_AVAILABLE = False
    logger.warning(
        "SpeechRecognition library not found. "
        "Install it with: pip install SpeechRecognition"
    )

try:
    import pyaudio  # noqa: F401 — imported only to trigger a clear error early
    _PYAUDIO_AVAILABLE = True
except ImportError:
    _PYAUDIO_AVAILABLE = False
    logger.warning(
        "PyAudio not found. Install it with:\n"
        "  Linux  : sudo apt install python3-pyaudio\n"
        "  macOS  : pip install pyaudio\n"
        "  Windows: pip install pyaudio"
    )


# ── Helper: silences ALSA/JACK low-level driver noise on Linux ────────────────
@contextlib.contextmanager
def _suppress_alsa_stderr():
    """Redirect stderr briefly to suppress harmless ALSA/JACK driver messages."""
    devnull_fd = os.open(os.devnull, os.O_WRONLY)
    old_stderr  = os.dup(2)
    os.dup2(devnull_fd, 2)
    os.close(devnull_fd)
    try:
        yield
    finally:
        os.dup2(old_stderr, 2)
        os.close(old_stderr)


class ListenerError(Exception):
    """Raised when the Listener cannot initialise the microphone."""


class Listener:
    """Captures microphone input and converts speech to text.

    Attributes:
        language        : BCP-47 language code, e.g. "en-US".
        timeout         : Seconds to wait for speech to begin (None = forever).
        phrase_limit    : Max seconds to record a single phrase.
        energy_threshold: Minimum mic energy considered as speech.
        pause_threshold : Seconds of silence that ends a phrase.
        available       : True when all dependencies are ready.
    """

    def __init__(
        self,
        language: str = "en-US",
        timeout: int | None = 5,
        phrase_limit: int = 10,
        pause_threshold: float = 0.8,
    ) -> None:
        self.language = language
        self.timeout = timeout
        self.phrase_limit = phrase_limit
        self.pause_threshold = pause_threshold
        self.available = _SR_AVAILABLE and _PYAUDIO_AVAILABLE

        if self.available:
            self._recognizer = sr.Recognizer()
            self._recognizer.pause_threshold = pause_threshold
            self._recognizer.dynamic_energy_threshold = True
            logger.info(
                "Listener ready (language=%s, timeout=%ss, phrase_limit=%ss)",
                language, timeout, phrase_limit,
            )
        else:
            logger.error(
                "Listener unavailable — missing libraries (SR=%s, PyAudio=%s).",
                _SR_AVAILABLE, _PYAUDIO_AVAILABLE,
            )

    # ── Public API ─────────────────────────────────────────────────────────────

    def calibrate(self, duration: float = 1.5) -> None:
        """Calibrate the recogniser to current ambient noise level."""
        if not self.available:
            logger.warning("calibrate() skipped — Listener not available.")
            return

        print(f"[JARVIS] Calibrating microphone for {duration}s — please stay quiet...")
        try:
            with _suppress_alsa_stderr(), sr.Microphone() as source:
                self._recognizer.adjust_for_ambient_noise(source, duration=duration)
            logger.info(
                "Microphone calibrated. Energy threshold set to %.0f.",
                self._recognizer.energy_threshold,
            )
            print("[JARVIS] Microphone calibrated ✓")
        except OSError as exc:
            logger.error("Microphone not found during calibration: %s", exc)
            print("[JARVIS] ⚠ No microphone detected — running in text-only mode.")
            self.available = False
        except Exception as exc:  # noqa: BLE001
            logger.error("Unexpected error during calibration: %s", exc, exc_info=True)
            self.available = False

    def listen(self, verbose: bool = True) -> str:
        """Listen for a spoken phrase and return the transcribed text.

        Args:
            verbose: If True, print active listening prompts and recognized text.
                     If False (passive/wake-word mode), listen silently.

        Returns:
            Lower-cased transcribed string, or "" if nothing was understood.
        """
        if not self.available:
            logger.debug("listen() skipped — Listener not available.")
            return ""

        if verbose:
            print("[JARVIS] Listening...")
        logger.info("Listening for speech (timeout=%s, phrase_limit=%s, verbose=%s)...",
                    self.timeout, self.phrase_limit, verbose)

        try:
            return self._capture_and_recognise(verbose=verbose)

        except sr.WaitTimeoutError:
            logger.info("No speech detected within timeout.")
            if verbose:
                print("[JARVIS] No speech detected.")
            return ""

        except OSError as exc:
            logger.error("Microphone I/O error: %s", exc)
            if verbose:
                print("[JARVIS] ⚠ Microphone error — check connection and permissions.")
            self.available = False
            return ""

        except Exception as exc:  # noqa: BLE001
            logger.error("Unexpected listen() error: %s", exc, exc_info=True)
            return ""

    def listen_passive(self) -> str:
        """Listen for speech silently without printing active banners.

        Used by WakeWordDetector to listen for the wake word in the background.

        Returns:
            Lower-cased transcribed string, or "" if nothing was understood.
        """
        return self.listen(verbose=False)

    def is_available(self) -> bool:
        """Return True if the listener is ready to capture audio."""
        return self.available

    # ── Private helpers ────────────────────────────────────────────────────────

    def _capture_and_recognise(self, verbose: bool = True) -> str:
        """Open the mic, record a phrase, and send it to a recogniser."""
        with _suppress_alsa_stderr(), sr.Microphone() as source:
            audio = self._recognizer.listen(
                source,
                timeout=self.timeout,
                phrase_time_limit=self.phrase_limit,
            )

        logger.debug("Audio captured (%d bytes). Sending to recogniser...",
                     len(audio.frame_data))

        return self._try_google(audio, verbose=verbose)

    def _try_google(self, audio, verbose: bool = True) -> str:
        """Attempt recognition using the free Google Web Speech API."""
        try:
            text = self._recognizer.recognize_google(audio, language=self.language)
            text = text.lower().strip()
            logger.info("Google STT recognised: %r", text)
            if verbose:
                print(f"[JARVIS] You said: {text}")
            return text

        except sr.UnknownValueError:
            logger.info("Google STT: speech unintelligible.")
            if verbose:
                print("[JARVIS] Sorry, I didn't understand that. Please try again.")
            return ""

        except sr.RequestError as exc:
            logger.warning("Google STT unavailable: %s. Trying offline fallback...", exc)
            if verbose:
                print("[JARVIS] ⚠ Google STT unreachable — trying offline recogniser...")
            return self._try_sphinx(audio, verbose=verbose)

    def _try_sphinx(self, audio, verbose: bool = True) -> str:
        """Offline fallback using PocketSphinx (if installed)."""
        try:
            text = self._recognizer.recognize_sphinx(audio)
            text = text.lower().strip()
            logger.info("PocketSphinx recognised: %r", text)
            if verbose:
                print(f"[JARVIS] You said (offline): {text}")
            return text

        except sr.UnknownValueError:
            logger.info("PocketSphinx: speech unintelligible.")
            if verbose:
                print("[JARVIS] Sorry, I couldn't understand that.")
            return ""

        except sr.RequestError:
            logger.warning("PocketSphinx not installed. No offline fallback.")
            if verbose:
                print(
                    "[JARVIS] ⚠ No internet and no offline recogniser available.\n"
                    "         Install PocketSphinx for offline support: pip install pocketsphinx"
                )
            return ""
