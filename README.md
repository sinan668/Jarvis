# JARVIS — Personal AI Assistant

> A modular, extensible personal AI assistant inspired by Tony Stark's JARVIS.
> Built step-by-step in Python, starting from a clean foundation.

---

## 🗂 Project Structure

```
jarvis-assistant/
│
├── main.py               ← Entry point — run this to start JARVIS
│
├── config/               ← Configuration & environment variables
│   ├── __init__.py
│   └── settings.py       ← All tunable parameters in one place
│
├── voice/                ← Voice input (listener) & output (speaker)
│   ├── __init__.py
│   ├── listener.py       ← Microphone → text (stub → SpeechRecognition)
│   └── speaker.py        ← Text → speech (stub → pyttsx3 / gTTS)
│
├── ai/                   ← AI conversation engine
│   ├── __init__.py
│   └── brain.py          ← Chat history & LLM calls (stub → OpenAI / HF)
│
├── commands/             ← Command routing & intent handling
│   ├── __init__.py
│   └── router.py         ← Keyword → handler mapping with AI fallback
│
├── system/               ← OS-level controls
│   ├── __init__.py
│   └── controller.py     ← App launch, file ops, clipboard (stubs)
│
├── utils/                ← Shared helpers
│   ├── __init__.py
│   ├── logger.py         ← Configurable console + file logging
│   └── helpers.py        ← Text formatting, timestamps, greetings
│
├── data/                 ← Runtime data (auto-created, git-ignored)
│
├── requirements.txt      ← Python dependencies
├── .env.example          ← Environment variable template
├── .gitignore            ← Git ignore rules
└── README.md             ← This file
```

---

## ⚡ Quick Start

### 1. Prerequisites

- Python **3.10 or newer** (uses `str | None` type syntax)
- `pip` package manager
- A working microphone (for voice mode)

### 2. Clone / Download the project

```bash
git clone <your-repo-url> jarvis-assistant
cd jarvis-assistant
```

### 3. Install Step 1 dependencies (core)

```bash
pip install python-dotenv
```

### 4. Install Step 2 dependencies (voice input)

**Linux (Debian / Ubuntu):**
```bash
# PyAudio — must be installed via apt (pip alone won't work without portaudio headers)
sudo apt install python3-pyaudio

# SpeechRecognition — install via pip
pip install SpeechRecognition
```

**macOS:**
```bash
brew install portaudio
pip install SpeechRecognition pyaudio
```

**Windows:**
```bash
pip install SpeechRecognition pyaudio
```

> **Optional (offline speech recognition — no internet needed):**
> ```bash
> pip install pocketsphinx
> ```

### 5. Configure environment variables (optional)

```bash
cp .env.example .env
# Edit .env if you want to change the assistant name, log level, etc.
```

### 6. Test voice input (recommended first step)

Run the dedicated voice test **before** starting the full assistant:

```bash
python test_voice_input.py
```

Expected output:
```
────────────────────────────────────────────────────────────
  Step 1/4 — Checking required libraries
────────────────────────────────────────────────────────────
  ✓ SpeechRecognition 3.17.0 imported successfully
  ✓ PyAudio 0.2.13 imported successfully

────────────────────────────────────────────────────────────
  Step 2/4 — Listing audio input devices
────────────────────────────────────────────────────────────
  [0] HDA Intel PCH: ALC3246 Analog (hw:0,0)  (max 2 channels, 44100 Hz)
  ✓ 1 input device(s) detected

────────────────────────────────────────────────────────────
  Step 3/4 — Calibrating microphone
────────────────────────────────────────────────────────────
  ✓ Calibrated. Energy threshold = 412

────────────────────────────────────────────────────────────
  Step 4/4 — Voice capture test (3 attempts)
────────────────────────────────────────────────────────────
[JARVIS] Listening...
  ✓ [JARVIS] You said: hello jarvis

  ✅ JARVIS voice input is working correctly!
  You can now run the full assistant with:  python main.py
```

### 7. Run the full JARVIS assistant

```bash
python main.py
```

- **With microphone:** JARVIS automatically enters voice mode, shows `[JARVIS] Listening...`, and prints what it hears.
- **Without microphone / missing library:** JARVIS gracefully falls back to keyboard input mode.

Type or say `help` to list available commands. Type or say `exit` to quit.

---

## 💬 Available Commands (Foundation)

| What you type | What JARVIS does |
|---|---|
| `hello` / `hi` | Greets you |
| `time` / `what time` | Tells the current time |
| `date` / `today` | Tells today's date |
| `help` / `commands` | Lists available commands |
| `exit` / `quit` / `bye` | Shuts down gracefully |
| *anything else* | Passes to AI brain (stub reply for now) |

---

## 🗺 Development Roadmap

| Step | Feature | Status |
|------|---------|--------|
| 1 | **Foundation** — project structure, modules, routing | ✅ Done |
| 2 | **Voice I/O** — microphone input + TTS output | 🔜 Next |
| 3 | **AI Brain** — free LLM (Hugging Face / DialoGPT) | 📋 Planned |
| 4 | **Web Search** — DuckDuckGo / Wikipedia integration | 📋 Planned |
| 5 | **App Control** — launch/close apps, system info | 📋 Planned |
| 6 | **File Operations** — search, read, write files | 📋 Planned |
| 7 | **Automation** — keyboard/mouse, scheduled tasks | 📋 Planned |
| 8 | **Wake Word** — always-on "Hey JARVIS" detection | 📋 Planned |

---

## 🔑 Environment Variables

Copy `.env.example` to `.env` and fill in only the keys you need:

| Variable | Default | Description |
|---|---|---|
| `ASSISTANT_NAME` | `JARVIS` | Name displayed in UI and spoken |
| `WAKE_WORD` | `jarvis` | Trigger phrase for always-on mode |
| `OPENAI_API_KEY` | *(empty)* | Optional — needed for GPT models |
| `OPENAI_MODEL` | `gpt-4o-mini` | OpenAI model to use |
| `HUGGINGFACE_MODEL` | `microsoft/DialoGPT-medium` | Free offline model |
| `SPEECH_LANGUAGE` | `en-US` | BCP-47 language for speech recognition |
| `TTS_RATE` | `180` | Words per minute for TTS |
| `TTS_VOLUME` | `1.0` | Volume 0.0 – 1.0 |
| `LOG_LEVEL` | `INFO` | `DEBUG` / `INFO` / `WARNING` / `ERROR` |
| `LOG_FILE` | `jarvis.log` | Path for log output |

---

## 🛠 Extending the Project

### Adding a new command

1. Open [`commands/router.py`](commands/router.py).
2. Add a keyword tuple and handler method to `_commands`:

```python
("weather", "forecast"): self._handle_weather,
```

3. Implement the handler:

```python
def _handle_weather(self, _text: str) -> bool:
    reply = "Weather module coming soon!"
    self.speaker.speak(reply)
    return False
```

### Adding a new module

1. Create a new folder (e.g., `web/`).
2. Add `__init__.py` and your implementation file.
3. Import and initialise it in `main.py`.

---

## 📄 License

MIT — free to use, modify, and distribute.
