# local-speech-to-text

Offline, OS-independent speech-to-text tool using Faster-Whisper + FastAPI + a browser UI.

No cloud, no API keys, no subscriptions. Everything runs locally on your machine.

---

## What it does

- Record audio directly from your browser
- Transcribes using Faster-Whisper (runs fully on CPU)
- Supports 99 languages with auto-detection
- Persistent history with search across all past recordings
- Copy, edit, and download transcripts

---

## Quick start

```bash
# 1. Clone or download the project
# 2. Install dependencies
pip install -r requirements.txt

# 3. Run
python app.py
```

The browser opens automatically at `http://localhost:8000`.
A platform-specific launcher (`run.bat` / `run.sh` / `run.command`) is created on first run — use that next time instead.

For full setup instructions including virtual environments, PortAudio, and model pre-downloading, see [SETUP.md](SETUP.md).

---

## Project structure

```
stt_tool/
  app.py            # FastAPI backend + WebSocket transcription
  index.html        # Frontend UI (served by FastAPI)
  requirements.txt  # Python dependencies
  README.md         # This file
  SETUP.md          # Detailed setup guide
  run.bat           # Windows launcher (auto-generated)
  run.sh            # Linux launcher (auto-generated)
  run.command       # macOS launcher (auto-generated)
```

---

## Tech stack

- [Faster-Whisper](https://github.com/SYSTRAN/faster-whisper) — CTranslate2-based Whisper inference, 4x faster than original
- [FastAPI](https://fastapi.tiangolo.com/) — backend and WebSocket server
- [Uvicorn](https://www.uvicorn.org/) — ASGI server
- Vanilla JS frontend, no frameworks
