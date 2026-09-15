"""
main.py
-------
Entry point for the JARVIS AI Assistant.

Run this file to start the assistant:
    python main.py

What happens at startup:
  1. Load configuration from .env (if present).
  2. Initialise all modules: logging, voice, AI brain, command router.
  3. Print a startup banner.
  4. Calibrate the microphone (if available).
  5. Enter the main interaction loop:
       - If microphone is ready  → listen for speech, print + route it.
       - If microphone is absent → fall back to keyboard input.
  6. Exit cleanly when the user says/types "exit" / "quit" / "bye".
"""

import sys
from config import Settings
from utils import get_logger, format_response
from utils.helpers import greeting_by_time
from voice import Listener, Speaker
from ai import Brain
from commands import CommandRouter
from system import SystemController


def print_banner(assistant_name: str) -> None:
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
║         Personal AI Assistant  •  Foundation v0.1        ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝
    """
    print(banner)
    print(f"  Assistant : {assistant_name}")


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
    speaker    = Speaker(rate=cfg.tts_rate, volume=cfg.tts_volume)
    listener   = Listener(language=cfg.speech_language)
    brain      = Brain(assistant_name=cfg.assistant_name)
    router     = CommandRouter(brain=brain, speaker=speaker)
    controller = SystemController()

    # Log OS info on startup (demonstrates SystemController works)
    os_info = controller.get_os_info()
    logger.info("Running on %s %s (Python %s)",
                os_info["system"], os_info["release"], os_info["python_version"])

    # ── 4. Startup greeting & mic calibration ─────────────────────────────────
    print_banner(cfg.assistant_name)

    # Decide which input mode to use
    voice_mode = listener.is_available()
    if voice_mode:
        print(f"  Mode      : 🎙️  Voice  (speak to {cfg.assistant_name})")
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
        "Entering main loop — mode=%s.",
        "voice" if voice_mode else "text",
    )

    while True:
        try:
            if voice_mode:
                # ── Voice path: microphone → speech-to-text ────────────────────
                user_input = listener.listen()

                # If listen() returned empty (silence / error) keep looping
                if not user_input:
                    continue

                logger.info("Voice input: %r", user_input)

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
