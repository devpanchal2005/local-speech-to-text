# Speech to Text - Local Tool

Offline, OS-independent speech-to-text using Faster-Whisper + FastAPI + a browser UI.

---

## Requirements
- Python 3.9+
- A working microphone
- No internet required after setup (models download once on first use)

---

## Setup

### 1. Create a virtual environment (recommended)
```bash
python -m venv venv

# macOS / Linux
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

> On some Linux systems you may need PortAudio for sounddevice:
> ```bash
> sudo apt install portaudio19-dev   # Debian/Ubuntu
> sudo dnf install portaudio-devel   # Fedora
> brew install portaudio             # macOS (if needed)
> ```

---

## Run

```bash
python app.py
```

Then open your browser at: **http://localhost:8000**

---

## How it works

1. Click the mic button in the browser to start recording.
2. Click again to stop. Audio is sent over a WebSocket to the local server.
3. Faster-Whisper transcribes it and sends the text back.
4. Transcript appears in the text box. You can copy, download, or edit it.

---

## Model sizes

| Model | Size | Speed | Best for |
|-------|------|-------|----------|
| base | ~145 MB | Fast | Everyday use (default) |
| small | ~460 MB | Medium | Better accuracy |
| medium | ~1.5 GB | Slower | High accuracy |

Models are downloaded automatically on first use from HuggingFace and cached locally.

---

## Supported languages

The tool auto-detects language by default. You can also manually select: English, Hindi, Gujarati, French, German, Spanish, Chinese, Japanese, Arabic, Portuguese, Russian, and many more (Whisper supports 99 languages).

---

## Project structure

```
stt_tool/
  app.py           # FastAPI backend + WebSocket transcription
  index.html       # Frontend UI (served by FastAPI)
  requirements.txt
  README.md
```
"# local-speech-to-text" 
