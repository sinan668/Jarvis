"""
main.py
-------
Entry point for the JARVIS AI Assistant.

Run this file to start the assistant:
    python main.py

What happens at startup:
  1. Load configuration from .env (if present).
  2. Initialise all modules: logging, voice, AI brain, command router.
  3. Print a startup banner with assistant name & wake word.
  4. Calibrate the microphone (if available).
  5. Enter the main interaction loop:
       - Voice mode: Wait for wake word -> "Yes, I'm listening." -> Record command -> Route.
       - Text mode: Fall back to keyboard input if microphone is unavailable.
  6. Exit cleanly when the user says/types "exit" / "quit" / "bye" or presses Ctrl+C.
"""

import sys
from config import Settings
from utils import get_logger, format_response
from utils.helpers import greeting_by_time
from voice import Listener, Speaker, WakeWordDetector
from ai import Brain
from commands import CommandRouter
from system import SystemController


def print_banner(assistant_name: str, wake_word: str) -> None:
    """Print the JARVIS startup banner to the console."""
    banner = f"""
╔══════════════════════════════════════════════════════════╗
║                                                          ║
║   ░░░░░░  ░░░░░  ░░░░░░  ░░  ░░ ░░ ░░░░░░               ║
║     ░░   ░░   ░  ░░   ░  ░░  ░░ ░░ ░░                   ║
║     ░░   ░░░░░░  ░░████   ░░░░  ░░░ ░░░░░                ║
║     ░░   ░░   ░  ░░   ░    ░░   ░░  ░░                   ║
║     ░░   ░░   ░  ░░   ░    ░░   ░░  ░░░░░░               ║
║                                                          ║
║         Personal AI Assistant  •  Step 3 Wake Word       ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝
    """
    print(banner)
    print(f"  Assistant : {assistant_name}")
    print(f"  Wake Word : '{wake_word}'")


def main() -> None:
    """Main entry point — initialise modules and start the interaction loop."""

    # ── 1. Load configuration ──────────────────────────────────────────────────
    cfg = Settings()

    # ── 2. Set up logging ──────────────────────────────────────────────────────
    logger = get_logger(
        name="jarvis.main",
        log_level=cfg.log_level,
        log_file=cfg.log_file,
    )
    logger.info("Starting %s assistant...", cfg.assistant_name)

    # ── 3. Initialise modules ──────────────────────────────────────────────────
    speaker       = Speaker(rate=cfg.tts_rate, volume=cfg.tts_volume)
    listener      = Listener(language=cfg.speech_language)
    wake_detector = WakeWordDetector(listener=listener, wake_word=cfg.wake_word)
    brain         = Brain(assistant_name=cfg.assistant_name)
    router        = CommandRouter(brain=brain, speaker=speaker)
    controller    = SystemController()

    # Log OS info on startup (demonstrates SystemController works)
    os_info = controller.get_os_info()
    logger.info("Running on %s %s (Python %s)",
                os_info["system"], os_info["release"], os_info["python_version"])

    # ── 4. Startup greeting & mic calibration ─────────────────────────────────
    print_banner(cfg.assistant_name, cfg.wake_word)

    # Decide which input mode to use
    voice_mode = listener.is_available()
    if voice_mode:
        print(f"  Mode      : 🎙️  Voice  (say '{cfg.wake_word}' to activate)")
    else:
        print(f"  Mode      : ⌨️  Text   (microphone unavailable)")
    print(f"  Say/type 'help' to list commands.")
    print(f"  Say/type 'exit' to shut down.\n")
    print("─" * 60)

    greeting = f"{greeting_by_time()}, sir. {cfg.assistant_name} is online."
    speaker.speak(format_response(greeting, cfg.assistant_name))

    # Calibrate mic once at startup (harmless if mic not available)
    if voice_mode:
        listener.calibrate()

    # ── 5. Main interaction loop ───────────────────────────────────────────────
    logger.info(
        "Entering main loop — mode=%s, wake_word=%r.",
        "voice" if voice_mode else "text",
        cfg.wake_word,
    )

    while True:
        try:
            if voice_mode:
                # ── Voice path: wait for wake word → voice command input ──────
                detected, command_part = wake_detector.listen_for_wake_word()

                # If wake word not heard, loop back to waiting for wake word
                if not detected:
                    continue

                # Wake word detected! Respond to the user
                response_text = "Yes, I'm listening."
                print(f"[JARVIS] {response_text}")
                speaker.speak(response_text)

                # If command was spoken in the same utterance ("Jarvis what time is it"),
                # execute it immediately. Otherwise listen for the command.
                if command_part:
                    user_input = command_part
                    print(f"[JARVIS] You said: {user_input}")
                else:
                    user_input = listener.listen()

                if not user_input:
                    continue

                logger.info("Voice command received: %r", user_input)

            else:
                # ── Text fallback: keyboard input ─────────────────────────────
                try:
                    user_input = input("\n⌨️  You: ").strip()
                except EOFError:
                    # Piped input finished
                    break

                if not user_input:
                    continue

                logger.info("Text input: %r", user_input)

            # Route the input — returns True when the user wants to exit
            should_exit = router.route(user_input)
            if should_exit:
                logger.info("Exit command received. Shutting down.")
                break

        except KeyboardInterrupt:
            # Ctrl-C → clean shutdown
            print()
            speaker.speak("Interrupted. Shutting down, sir.")
            logger.info("KeyboardInterrupt received. Exiting.")
            break

        except Exception as exc:  # noqa: BLE001
            logger.error("Unexpected error: %s", exc, exc_info=True)
            speaker.speak("I encountered an error. Please check the logs.")

    print("\n" + "─" * 60)
    print(f"  {cfg.assistant_name} has shut down. Goodbye!\n")
    sys.exit(0)


if __name__ == "__main__":
    main()
