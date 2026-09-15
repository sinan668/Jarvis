"""
commands/router.py
------------------
Maps user text to specific commands/actions.

Current state (foundation only):
  - Recognises a small set of built-in commands (greet, time, help, exit).
  - Falls back to the AI brain for everything else.
  - No NLP/intent-detection yet — uses simple keyword matching.

Future steps:
  - Add intent classification (regex rules → ML model).
  - Register external command handlers (web search, app launch, file ops).
  - Support multi-step / chained commands.
"""

import datetime
from utils.logger import get_logger

logger = get_logger(__name__)


class CommandRouter:
    """Routes user text to the appropriate handler.

    Usage:
        router = CommandRouter(brain=brain_instance, speaker=speaker_instance)
        should_exit = router.route("what time is it")
    """

    def __init__(self, brain, speaker) -> None:
        """
        Args:
            brain:   An instance of ai.Brain for fallback AI responses.
            speaker: An instance of voice.Speaker to speak replies.
        """
        self.brain = brain
        self.speaker = speaker

        # ── Command registry ───────────────────────────────────────────────────
        # Each key is a tuple of trigger keywords; value is a handler method.
        # Add new commands here as the project grows.
        self._commands = {
            ("hello", "hi", "hey", "greet"):       self._handle_greet,
            ("time", "clock", "what time"):         self._handle_time,
            ("date", "today", "what day"):          self._handle_date,
            ("help", "commands", "what can you do"): self._handle_help,
            ("exit", "quit", "bye", "goodbye"):     self._handle_exit,
        }
        logger.info("CommandRouter initialised with %d command groups.", len(self._commands))

    # ── Public interface ───────────────────────────────────────────────────────

    def route(self, user_input: str) -> bool:
        """Dispatch `user_input` to the right handler.

        Args:
            user_input: Cleaned text from the user.

        Returns:
            True if the application should exit, False otherwise.
        """
        text = user_input.lower().strip()
        if not text:
            return False

        handler = self._match_command(text)
        return handler(text)

    # ── Private: command matching ──────────────────────────────────────────────

    def _match_command(self, text: str):
        """Find the best handler for `text`.

        Checks each keyword tuple in the registry; if any keyword is a
        substring of the user text, return the associated handler.
        Falls back to the AI brain handler.

        Args:
            text: Lower-cased user input.

        Returns:
            A callable handler(text) -> bool.
        """
        for keywords, handler in self._commands.items():
            if any(kw in text for kw in keywords):
                logger.debug("Matched command group %s", keywords)
                return handler
        return self._handle_ai_fallback

    # ── Private: individual handlers ──────────────────────────────────────────

    def _handle_greet(self, _text: str) -> bool:
        reply = "Hello! All systems online and ready. How can I assist you?"
        self.speaker.speak(reply)
        return False

    def _handle_time(self, _text: str) -> bool:
        now = datetime.datetime.now().strftime("%I:%M %p")
        reply = f"The current time is {now}."
        self.speaker.speak(reply)
        return False

    def _handle_date(self, _text: str) -> bool:
        today = datetime.datetime.now().strftime("%A, %B %d, %Y")
        reply = f"Today is {today}."
        self.speaker.speak(reply)
        return False

    def _handle_help(self, _text: str) -> bool:
        reply = (
            "Here's what I can do right now:\n"
            "  • Greet you\n"
            "  • Tell the time and date\n"
            "  • Answer general questions (AI mode)\n"
            "  • Exit on command\n"
            "More capabilities are coming in future steps!"
        )
        self.speaker.speak(reply)
        return False

    def _handle_exit(self, _text: str) -> bool:
        reply = "Goodbye. Powering down, sir."
        self.speaker.speak(reply)
        return True  # signal main loop to stop

    def _handle_ai_fallback(self, text: str) -> bool:
        reply = self.brain.chat(text)
        self.speaker.speak(reply)
        return False
