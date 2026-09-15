"""
test_voice_input.py
-------------------
Standalone test script for JARVIS Step 2 — Voice Input.

Purpose:
  Verify that the microphone and SpeechRecognition library are working
  correctly WITHOUT running the full JARVIS assistant.

What this script does:
  1. Checks that all required libraries are importable.
  2. Lists available audio input devices.
  3. Calibrates the microphone for ambient noise.
  4. Runs a short listen loop (3 attempts by default).
  5. Prints and logs everything it captures.

Run it with:
    python test_voice_input.py

Expected output (when mic and internet are available):
    [JARVIS] Listening...
    [JARVIS] You said: hello jarvis

    [JARVIS] Listening...
    [JARVIS] You said: what time is it
"""

import sys
import platform

# ── Ensure project root is on the path ────────────────────────────────────────
# (Needed when running the script directly, not as a module)
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.logger import get_logger

logger = get_logger("test_voice_input", log_level="DEBUG")

# ── ANSI colour helpers ────────────────────────────────────────────────────────
GREEN  = "\033[92m"
RED    = "\033[91m"
YELLOW = "\033[93m"
RESET  = "\033[0m"

def ok(msg):  print(f"  {GREEN}✓ {msg}{RESET}")
def fail(msg):print(f"  {RED}✗ {msg}{RESET}")
def warn(msg):print(f"  {YELLOW}⚠ {msg}{RESET}")
def header(msg): print(f"\n{'─'*60}\n  {msg}\n{'─'*60}")


# ─────────────────────────────────────────────────────────────────────────────
# Step 1 — Library check
# ─────────────────────────────────────────────────────────────────────────────
header("Step 1/4 — Checking required libraries")

# Check SpeechRecognition
try:
    import speech_recognition as sr
    ok(f"SpeechRecognition {sr.__version__} imported successfully")
except ImportError:
    fail("SpeechRecognition not found.")
    print("\n  Install it with:\n    pip install SpeechRecognition\n")
    sys.exit(1)

# Check PyAudio
try:
    import pyaudio
    ok(f"PyAudio {pyaudio.__version__} imported successfully")
    _pyaudio_ok = True
except ImportError:
    _pyaudio_ok = False
    fail("PyAudio not found.")
    system = platform.system()
    if system == "Linux":
        warn("Fix: sudo apt install python3-pyaudio")
    elif system == "Darwin":
        warn("Fix: brew install portaudio && pip install pyaudio")
    else:
        warn("Fix: pip install pyaudio")

if not _pyaudio_ok:
    print("\n  Cannot test microphone without PyAudio. Exiting.\n")
    sys.exit(1)


# ─────────────────────────────────────────────────────────────────────────────
# Step 2 — List audio devices
# ─────────────────────────────────────────────────────────────────────────────
header("Step 2/4 — Listing audio input devices")

pa = pyaudio.PyAudio()
device_count = pa.get_device_count()
input_devices = []

for i in range(device_count):
    info = pa.get_device_info_by_index(i)
    if info.get("maxInputChannels", 0) > 0:
        input_devices.append(info)
        print(f"  [{i}] {info['name']}  "
              f"(max {info['maxInputChannels']} channels, "
              f"{int(info['defaultSampleRate'])} Hz)")

pa.terminate()

if not input_devices:
    fail("No microphone / audio input device found.")
    print("\n  Connect a microphone and re-run this test.\n")
    sys.exit(1)
else:
    ok(f"{len(input_devices)} input device(s) detected")


# ─────────────────────────────────────────────────────────────────────────────
# Step 3 — Calibrate microphone
# ─────────────────────────────────────────────────────────────────────────────
header("Step 3/4 — Calibrating microphone")

recognizer = sr.Recognizer()
recognizer.dynamic_energy_threshold = True
recognizer.pause_threshold = 0.8

try:
    print("  Please stay quiet for 1.5 seconds...")
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source, duration=1.5)
    ok(f"Calibrated. Energy threshold = {recognizer.energy_threshold:.0f}")
except OSError as e:
    fail(f"Microphone error during calibration: {e}")
    sys.exit(1)


# ─────────────────────────────────────────────────────────────────────────────
# Step 4 — Listen loop (3 attempts)
# ─────────────────────────────────────────────────────────────────────────────
header("Step 4/4 — Voice capture test (3 attempts)")
print("  Speak into the microphone when you see '[JARVIS] Listening...'")
print("  Press Ctrl+C to quit early.\n")

MAX_ATTEMPTS = 3
successes    = 0

for attempt in range(1, MAX_ATTEMPTS + 1):
    print(f"  Attempt {attempt}/{MAX_ATTEMPTS}")
    try:
        print("[JARVIS] Listening...")
        with sr.Microphone() as source:
            audio = recognizer.listen(source, timeout=6, phrase_time_limit=10)

        # Try Google STT
        try:
            text = recognizer.recognize_google(audio, language="en-US")
            text = text.lower().strip()
            ok(f"[JARVIS] You said: {text}")
            logger.info("Recognised: %r", text)
            successes += 1
        except sr.UnknownValueError:
            warn("Could not understand audio — please speak more clearly.")
        except sr.RequestError as e:
            warn(f"Google STT request failed: {e}")
            warn("Make sure you have an internet connection.")

    except sr.WaitTimeoutError:
        warn("No speech detected within 6 seconds — try speaking louder.")
    except OSError as e:
        fail(f"Microphone I/O error: {e}")
        break
    except KeyboardInterrupt:
        print("\n  Interrupted by user.")
        break

    print()

# ─────────────────────────────────────────────────────────────────────────────
# Summary
# ─────────────────────────────────────────────────────────────────────────────
header("Test Summary")
if successes > 0:
    ok(f"Voice input PASSED  ({successes}/{MAX_ATTEMPTS} phrases recognised)")
    print(f"\n  {GREEN}✅ JARVIS voice input is working correctly!{RESET}")
    print("  You can now run the full assistant with:  python main.py\n")
else:
    fail(f"Voice input FAILED  (0/{MAX_ATTEMPTS} phrases recognised)")
    print(f"\n  {YELLOW}Troubleshooting tips:{RESET}")
    print("  • Ensure a microphone is connected and not muted.")
    print("  • Check system microphone permissions.")
    print("  • Verify internet access for Google STT.")
    print("  • Try speaking louder or closer to the mic.\n")
