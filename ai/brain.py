"""
ai/brain.py
-----------
The conversational "brain" of JARVIS.

Current state (foundation only):
  - `Brain` holds a conversation history list and a system prompt.
  - `chat()` returns a hard-coded reply so the project runs with
    zero external dependencies right now.

Future steps:
  - Plug in a free Hugging Face model (DialoGPT, etc.) for offline use.
  - Optionally connect to OpenAI / Gemini if an API key is present.
  - Add memory / context compression for long conversations.
"""

from utils.logger import get_logger

logger = get_logger(__name__)


class Brain:
    """Manages conversation context and generates AI responses.

    Usage:
        brain = Brain(assistant_name="JARVIS")
        reply = brain.chat("What time is it?")
        print(reply)
    """

    # System prompt injected at the start of every conversation
    SYSTEM_PROMPT = (
        "You are JARVIS, an advanced AI assistant inspired by Iron Man. "
        "You are helpful, precise, and occasionally witty. "
        "Keep answers concise unless asked for detail."
    )

    def __init__(self, assistant_name: str = "JARVIS") -> None:
        """
        Args:
            assistant_name: Name used in greetings and logs.
        """
        self.assistant_name = assistant_name
        # Conversation history: list of {"role": "user"|"assistant", "content": str}
        self.history: list[dict] = []
        logger.info("Brain initialised for assistant=%r", assistant_name)

    def chat(self, user_input: str) -> str:
        """Process user input and return a response.

        Args:
            user_input: Text typed or spoken by the user.

        Returns:
            Assistant reply string.

        Note:
            Currently returns a placeholder. Swap the stub block
            with a real LLM call in the AI-integration step.
        """
        if not user_input.strip():
            return "I didn't catch that. Could you repeat?"

        # Store the user's message in history
        self.history.append({"role": "user", "content": user_input})

        # ── TODO: replace stub with a real LLM call ────────────────────────────
        # Example (OpenAI):
        #   from openai import OpenAI
        #   client = OpenAI(api_key=settings.openai_api_key)
        #   messages = [{"role": "system", "content": self.SYSTEM_PROMPT}] + self.history
        #   response = client.chat.completions.create(model=settings.openai_model, messages=messages)
        #   reply = response.choices[0].message.content
        reply = (
            f"I'm {self.assistant_name}, currently running in foundation mode. "
            "My AI brain will be connected in the next step."
        )
        # ── End stub ────────────────────────────────────────────────────────────

        # Store the assistant's reply in history
        self.history.append({"role": "assistant", "content": reply})
        logger.debug("Brain replied: %r", reply)
        return reply

    def reset_history(self) -> None:
        """Clear the conversation history to start a fresh session."""
        self.history.clear()
        logger.info("Conversation history cleared.")

    def get_history(self) -> list[dict]:
        """Return the full conversation history.

        Returns:
            List of message dicts with 'role' and 'content' keys.
        """
        return list(self.history)
