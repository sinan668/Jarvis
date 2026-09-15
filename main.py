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
  4. Enter the main interaction loop (text-based for now).
  5. Exit cleanly when the user says "exit" / "quit" / "bye".
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
    print(f"  Mode      : Text (voice coming in Step 2)")
    print(f"  Type 'help' to see available commands.")
    print(f"  Type 'exit' to shut down.\n")
    print("─" * 60)


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

    # ── 4. Startup greeting ────────────────────────────────────────────────────
    print_banner(cfg.assistant_name)
    greeting = f"{greeting_by_time()}, sir. {cfg.assistant_name} is online."
    speaker.speak(format_response(greeting, cfg.assistant_name))

    # ── 5. Main interaction loop ───────────────────────────────────────────────
    logger.info("Entering main loop — waiting for input.")
    while True:
        try:
            # In text mode the user types; in voice mode listener.listen() fills this
            user_input = input("\n🎙️  You: ").strip()

            if not user_input:
                continue  # ignore blank lines

            logger.info("User input: %r", user_input)

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
