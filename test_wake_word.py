"""
test_wake_word.py
-----------------
Test script for JARVIS Step 3 — Wake Word Detection.

Purpose:
  1. Unit test WakeWordDetector matching, case-insensitivity, trailing command extraction,
     and configuration.
  2. Perform live microphone test for wake-word detection when run interactively.

Run unit tests:
    python test_wake_word.py --unit

Run live interactive mic test:
    python test_wake_word.py
"""

import sys
import os
import argparse
from unittest.mock import MagicMock

# ── Ensure project root is on Python path ──────────────────────────────────────
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import Settings
from voice import Listener, WakeWordDetector
from utils.logger import get_logger

logger = get_logger("test_wake_word", log_level="DEBUG")

# ── ANSI colour helpers ────────────────────────────────────────────────────────
GREEN  = "\033[92m"
RED    = "\033[91m"
YELLOW = "\033[93m"
RESET  = "\033[0m"

def ok(msg: str) -> None:
    print(f"  {GREEN}✓ {msg}{RESET}")

def fail(msg: str) -> None:
    print(f"  {RED}✗ {msg}{RESET}")

def warn(msg: str) -> None:
    print(f"  {YELLOW}⚠ {msg}{RESET}")

def header(msg: str) -> None:
    print(f"\n{'─'*60}\n  {msg}\n{'─'*60}")


# ─────────────────────────────────────────────────────────────────────────────
# 1. Unit Tests (Non-interactive)
# ─────────────────────────────────────────────────────────────────────────────
def run_unit_tests() -> bool:
    header("Step 1/2 — Running WakeWordDetector Unit Tests")
    passed = 0
    total = 0

    mock_listener = MagicMock(spec=Listener)
    mock_listener.is_available.return_value = True

    detector = WakeWordDetector(listener=mock_listener, wake_word="jarvis")

    # Test 1: Case-insensitive presence check
    total += 1
    if (detector.is_wake_word_present("jarvis") and
        detector.is_wake_word_present("JARVIS") and
        detector.is_wake_word_present("Hello Jarvis") and
        not detector.is_wake_word_present("Hello world")):
        ok("Case-insensitive wake word detection (is_wake_word_present)")
        passed += 1
    else:
        fail("is_wake_word_present failed")

    # Test 2: Custom wake word configuration
    total += 1
    detector.set_wake_word("computer")
    if detector.is_wake_word_present("computer status") and not detector.is_wake_word_present("jarvis"):
        ok("Configurable wake word setting ('computer')")
        passed += 1
    else:
        fail("Custom wake word configuration failed")

    # Reset back to "jarvis"
    detector.set_wake_word("jarvis")

    # Test 3: Ignores text without wake word
    total += 1
    mock_listener.listen_passive.return_value = "hello how are you"
    detected, cmd = detector.listen_for_wake_word()
    if not detected and cmd == "":
        ok("Ignores text without wake word ('hello how are you')")
        passed += 1
    else:
        fail("Failed to ignore text without wake word")

    # Test 4: Detects standalone wake word
    total += 1
    mock_listener.listen_passive.return_value = "jarvis"
    detected, cmd = detector.listen_for_wake_word()
    if detected and cmd == "":
        ok("Detects standalone wake word ('jarvis')")
        passed += 1
    else:
        fail("Failed to detect standalone wake word")

    # Test 5: Extracts trailing command in same utterance
    total += 1
    mock_listener.listen_passive.return_value = "jarvis what time is it"
    detected, cmd = detector.listen_for_wake_word()
    if detected and cmd == "what time is it":
        ok("Extracts trailing command in same phrase ('jarvis what time is it' -> 'what time is it')")
        passed += 1
    else:
        fail(f"Trailing command extraction failed: got cmd={cmd!r}")

    # Test 6: Settings config integration
    total += 1
    cfg = Settings()
    if cfg.wake_word == "jarvis":
        ok(f"Settings wake_word default is 'jarvis'")
        passed += 1
    else:
        fail(f"Settings wake_word unexpected: {cfg.wake_word!r}")

    print(f"\n  Unit Test Result: {passed}/{total} passed.")
    return passed == total


# ─────────────────────────────────────────────────────────────────────────────
# 2. Live Microphone Test (Interactive / Hardware)
# ─────────────────────────────────────────────────────────────────────────────
def run_live_test() -> bool:
    header("Step 2/2 — Live Microphone Wake Word Test")

    cfg = Settings()
    listener = Listener(language=cfg.speech_language)

    if not listener.is_available():
        warn("Microphone or speech recognition libraries not available.")
        warn("Skipping live mic test (unit tests passed).")
        return True

    listener.calibrate(duration=1.0)
    wake_detector = WakeWordDetector(listener=listener, wake_word=cfg.wake_word)

    print(f"\n  Say '{cfg.wake_word}' into your microphone to trigger activation.")
    print("  Or say something else first to test rejection.")
    print("  Press Ctrl+C to stop the test.\n")

    max_attempts = 3
    success = False

    for attempt in range(1, max_attempts + 1):
        print(f"  Attempt {attempt}/{max_attempts}:")
        try:
            detected, command_part = wake_detector.listen_for_wake_word()
            if detected:
                ok("Wake word successfully detected!")
                print(f"  [JARVIS] Yes, I'm listening.")
                if command_part:
                    ok(f"Recognised command in same phrase: {command_part!r}")
                else:
                    cmd = listener.listen()
                    if cmd:
                        ok(f"Recognised command: {cmd!r}")
                success = True
                break
            else:
                warn("Wake word not detected in this attempt.")
        except KeyboardInterrupt:
            print("\n  Live test cancelled by user.")
            break

    return success


def main() -> None:
    parser = argparse.ArgumentParser(description="Test JARVIS Wake Word Detection")
    parser.add_argument("--unit", action="store_true", help="Run non-interactive unit tests only")
    args = parser.parse_args()

    unit_ok = run_unit_tests()

    if args.unit or not unit_ok:
        sys.exit(0 if unit_ok else 1)

    print("\nStarting live mic test...")
    live_ok = run_live_test()

    header("Test Summary")
    if unit_ok and live_ok:
        ok("Step 3 Wake Word Detection tests PASSED!")
    elif unit_ok:
        warn("Unit tests PASSED, live mic test was inconclusive or skipped.")
    else:
        fail("Wake Word Detection tests FAILED!")


if __name__ == "__main__":
    main()
