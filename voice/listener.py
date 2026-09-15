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

Error conditions handled:
  - Microphone not found / no permission
  - No speech detected (silence / timeout)
  - Google API unreachable (network error)
  - Unintelligible audio
  - Any unexpected hardware exception

Usage:
    listener = Listener(language="en-US")
    listener.calibrate()          # call once at startup
    text = listener.listen()      # blocks until speech is heard (or timeout)
    print(text)                   # "" on failure, transcribed text on success
"""

import sys
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
import contextlib
import os

@contextlib.contextmanager
def _suppress_alsa_stderr():
    """Redirect stderr briefly to suppress harmless ALSA/JACK driver messages.

    PyAudio enumerates every possible audio backend on open, which floods
    the terminal with 'Unknown PCM' and 'Cannot connect to JACK' lines.
    These are not errors — the primary HDA Intel device still works fine.
    """
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

    The class degrades gracefully when libraries are missing or when the
    microphone is unavailable — it logs a warning and returns "" instead
    of crashing the assistant.

    Attributes:
        language        : BCP-47 language code, e.g. "en-US".
        timeout         : Seconds to wait for speech to begin (None = forever).
        phrase_limit    : Max seconds to record a single phrase.
        energy_threshold: Minimum mic energy considered as speech (auto-set
                          after calibrate()).
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
        """
        Args:
            language      : BCP-47 speech recognition language code.
            timeout       : Seconds to wait before giving up (None = wait forever).
            phrase_limit  : Maximum length of a single captured phrase in seconds.
            pause_threshold: Seconds of silence that mark the end of a phrase.
        """
        self.language = language
        self.timeout = timeout
        self.phrase_limit = phrase_limit
        self.pause_threshold = pause_threshold
        self.available = _SR_AVAILABLE and _PYAUDIO_AVAILABLE

        if self.available:
            self._recognizer = sr.Recognizer()
            self._recognizer.pause_threshold = pause_threshold
            # Reduce false activations in noisy environments
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
        """Calibrate the recogniser to current ambient noise level.

        Call this once at startup before the first listen() call.
        It measures the background noise for `duration` seconds and sets
        the energy threshold accordingly, so speech is detected accurately
        in the current environment.

        Args:
            duration: How many seconds to sample ambient noise.
        """
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
            # OSError is raised when no input device is found
            logger.error("Microphone not found during calibration: %s", exc)
            print("[JARVIS] ⚠ No microphone detected — running in text-only mode.")
            self.available = False
        except Exception as exc:  # noqa: BLE001
            logger.error("Unexpected error during calibration: %s", exc, exc_info=True)
            self.available = False

    def listen(self) -> str:
        """Listen for a spoken phrase and return the transcribed text.

        Workflow:
          1. Open the microphone.
          2. Wait for speech to begin (up to `timeout` seconds).
          3. Record until a pause of `pause_threshold` seconds.
          4. Send audio to Google Web Speech API for transcription.
          5. Return the lower-cased text, or "" on any failure.

        Returns:
            Lower-cased transcribed string, or "" if nothing was understood.
        """
        if not self.available:
            logger.debug("listen() skipped — Listener not available.")
            return ""

        print("[JARVIS] Listening...")
        logger.info("Listening for speech (timeout=%s, phrase_limit=%s)...",
                    self.timeout, self.phrase_limit)

        try:
            return self._capture_and_recognise()

        except sr.WaitTimeoutError:
            # No speech detected within `timeout` seconds
            logger.info("No speech detected within timeout.")
            print("[JARVIS] No speech detected.")
            return ""

        except OSError as exc:
            # Microphone was unplugged or permissions revoked mid-session
            logger.error("Microphone I/O error: %s", exc)
            print("[JARVIS] ⚠ Microphone error — check connection and permissions.")
            self.available = False
            return ""

        except Exception as exc:  # noqa: BLE001
            logger.error("Unexpected listen() error: %s", exc, exc_info=True)
            return ""

    def is_available(self) -> bool:
        """Return True if the listener is ready to capture audio."""
        return self.available

    # ── Private helpers ────────────────────────────────────────────────────────

    def _capture_and_recognise(self) -> str:
        """Open the mic, record a phrase, and send it to a recogniser.

        Returns:
            Transcribed text string (lower-cased), or "" on failure.
        """
        with _suppress_alsa_stderr(), sr.Microphone() as source:
            # Record audio — blocks until speech ends or timeout fires
            audio = self._recognizer.listen(
                source,
                timeout=self.timeout,
                phrase_time_limit=self.phrase_limit,
            )

        logger.debug("Audio captured (%d bytes). Sending to recogniser...",
                     len(audio.frame_data))

        # ── Try Google Web Speech API (free, requires internet) ────────────────
        return self._try_google(audio)

    def _try_google(self, audio) -> str:
        """Attempt recognition using the free Google Web Speech API.

        Args:
            audio: sr.AudioData object from the microphone.

        Returns:
            Recognised text (lower-cased), or "" on failure.
        """
        try:
            text = self._recognizer.recognize_google(audio, language=self.language)
            text = text.lower().strip()
            logger.info("Google STT recognised: %r", text)
            print(f"[JARVIS] You said: {text}")
            return text

        except sr.UnknownValueError:
            # Audio was captured but could not be understood
            logger.info("Google STT: speech unintelligible.")
            print("[JARVIS] Sorry, I didn't understand that. Please try again.")
            return ""

        except sr.RequestError as exc:
            # Network error, quota exceeded, or API unavailable
            logger.warning("Google STT unavailable: %s. Trying offline fallback...", exc)
            print("[JARVIS] ⚠ Google STT unreachable — trying offline recogniser...")
            return self._try_sphinx(audio)

    def _try_sphinx(self, audio) -> str:
        """Offline fallback using PocketSphinx (if installed).

        PocketSphinx works without internet but requires the
        `pocketsphinx` package:  pip install pocketsphinx

        Args:
            audio: sr.AudioData object from the microphone.

        Returns:
            Recognised text (lower-cased), or "" if Sphinx is unavailable.
        """
        try:
            text = self._recognizer.recognize_sphinx(audio)
            text = text.lower().strip()
            logger.info("PocketSphinx recognised: %r", text)
            print(f"[JARVIS] You said (offline): {text}")
            return text

        except sr.UnknownValueError:
            logger.info("PocketSphinx: speech unintelligible.")
            print("[JARVIS] Sorry, I couldn't understand that.")
            return ""

        except sr.RequestError:
            # PocketSphinx not installed — no offline fallback available
            logger.warning("PocketSphinx not installed. No offline fallback.")
            print(
                "[JARVIS] ⚠ No internet and no offline recogniser available.\n"
                "         Install PocketSphinx for offline support: pip install pocketsphinx"
            )
            return ""
