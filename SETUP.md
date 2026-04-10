# Setup Guide

This document covers everything you need to get the tool running from scratch on any OS.

---

## Requirements

- Python 3.9 or higher
- A working microphone
- Internet connection on first run only (models are downloaded once and cached)

---

## Step 1 — Create a virtual environment

Using a venv keeps dependencies isolated from your system Python. Recommended but not mandatory.

**Windows**
```bat
python -m venv venv
venv\Scripts\activate
```

**macOS / Linux**
```bash
python3 -m venv venv
source venv/bin/activate
```

You should see `(venv)` at the start of your terminal prompt once activated.

---

## Step 2 — Install dependencies

```bash
pip install -r requirements.txt
```

### PortAudio (Linux only)

`sounddevice` requires PortAudio on Linux. Install it before running `pip install`:

```bash
# Debian / Ubuntu
sudo apt install portaudio19-dev

# Fedora
sudo dnf install portaudio-devel

# Arch
sudo pacman -S portaudio
```

On Windows and macOS, PortAudio is bundled with the `sounddevice` wheel — no extra step needed.

---

## Step 3 — Run

```bash
python app.py
```

On first run, the tool will:

1. Download any missing Whisper models (tiny through medium, ~2.2 GB total)
2. Create a platform-specific launcher file for future use
3. Start the server and open `http://localhost:8000` in your browser automatically

---

## Using the launcher next time

After the first run, a launcher file is created in the project folder. Use it instead of opening a terminal every time.

| OS | File | How to use |
|----|------|------------|
| Windows | `run.bat` | Double-click, or drag to Desktop / taskbar |
| macOS | `run.command` | Double-click from Finder, or drag to Dock |
| Linux | `run.sh` | Double-click from file manager, or `./run.sh` in terminal |

The launcher activates the venv automatically if one is present.

---

## Pre-downloading models manually

Models are downloaded automatically on first run. If you want to pre-download them while on a good connection (e.g. before going offline), run this once:

```python
from faster_whisper import WhisperModel
for size in ["base", "small", "medium"]:
    WhisperModel(size, device="cpu", compute_type="int8")
    print(f"{size} cached")
```

Models are stored in `~/.cache/huggingface/hub/` and never re-downloaded.

---

## Model reference

| Model | Download size | RAM usage | Speed on i3/i5 CPU | Best for |
|-------|-------------|-----------|---------------------|----------|
| base | ~145 MB | ~300 MB | ~4x real-time | Everyday use (default) |
| small | ~460 MB | ~700 MB | ~1.5x real-time | Better accuracy, mixed languages |
| medium | ~1.5 GB | ~2.5 GB | ~0.6x real-time | Short clips where accuracy matters |

**Recommendation:** start with `base`. Switch to `small` if you find it missing words, especially for Hindi/Gujarati/English mixed speech.

---

## Language detection

The tool uses **auto-detect** by default. Whisper identifies the language in the first few seconds of audio with ~95% accuracy and adds under 0.1s of overhead. This is the recommended setting for most use cases, especially if you mix languages mid-sentence (e.g. Hinglish or Gujarati-English).

Manual language selection is useful when:
- Recording very short clips under 3 seconds
- The detector is consistently picking the wrong language for a specific accent

---

## Troubleshooting

**Microphone not detected**
Make sure your browser has microphone permission for `localhost`. Check your OS audio input settings to confirm the correct mic is set as default.

**`sounddevice` install fails on Linux**
Install PortAudio first (see Step 2), then re-run `pip install -r requirements.txt`.

**Server starts but browser does not open**
Navigate manually to `http://localhost:8000`. This can happen if your default browser takes too long to launch before the auto-open timeout.

**Model download is slow or fails**
The HuggingFace CDN can be slow in some regions. Try again or use a VPN. Downloaded portions are cached so a failed download will resume from where it left off on the next run.

**Port 8000 already in use**
Another process is using the port. Either stop it, or edit the last line of `app.py` and change `port=8000` to any free port such as `8001`.

---

## Uninstalling

To remove everything cleanly:

1. Delete the project folder
2. Delete the model cache at `~/.cache/huggingface/hub/models--Systran--faster-whisper-*`
3. Delete the venv folder if you created one inside the project
