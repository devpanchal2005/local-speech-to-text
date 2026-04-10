import os
import io
import tempfile
import threading
import queue
import wave
import time

import numpy as np
import sounddevice as sd
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from faster_whisper import WhisperModel
import uvicorn

app = FastAPI(title="Speech-to-Text Tool")

# Models to ensure are downloaded on startup (base -> medium)
PREDOWNLOAD_MODELS = ["base", "small", "medium"]  # large-v3 excluded: too slow for CPU

def ensure_models_downloaded():
    from huggingface_hub import snapshot_download
    import huggingface_hub

    for size in PREDOWNLOAD_MODELS:
        repo_id = f"Systran/faster-whisper-{size}"
        cache_dir = os.path.join(os.path.expanduser("~"), ".cache", "huggingface", "hub")
        # Check if already cached by looking for config file
        safe_name = "models--" + repo_id.replace("/", "--")
        model_path = os.path.join(cache_dir, safe_name)
        if os.path.exists(model_path):
            print(f"[startup] '{size}' already cached, skipping.")
            continue
        print(f"[startup] Downloading '{size}' model... this may take a while.")
        try:
            snapshot_download(repo_id=repo_id, cache_dir=cache_dir)
            print(f"[startup] '{size}' downloaded.")
        except Exception as e:
            print(f"[startup] Failed to download '{size}': {e}")

ensure_models_downloaded()

def create_launcher():
    import sys, stat
    here = os.path.dirname(os.path.abspath(__file__))
    system = sys.platform

    if system == "win32":
        launcher = os.path.join(here, "run.bat")
        if not os.path.exists(launcher):
            with open(launcher, "w") as f:
                f.write(
                    "@echo off\n"
                    "title Speech to Text\n"
                    "cd /d '%~dp0'\n"
                    "if exist venv\\Scripts\\activate.bat (\n"
                    "    call venv\\Scripts\\activate.bat\n"
                    ") else (\n"
                    "    echo [warning] No venv found, using system Python.\n"
                    ")\n"
                    "python app.py\n"
                    "pause\n"
                )
            print("[launcher] Created run.bat — double-click it next time to start.")

    elif system == "darwin":
        launcher = os.path.join(here, "run.command")
        if not os.path.exists(launcher):
            with open(launcher, "w") as f:
                f.write(
                    "#!/bin/bash\n"
                    "cd \"$(dirname \"$0\")\"\n"
                    "if [ -f venv/bin/activate ]; then\n"
                    "    source venv/bin/activate\n"
                    "else\n"
                    "    echo '[warning] No venv found, using system Python.'\n"
                    "fi\n"
                    "python3 app.py\n"
                )
            os.chmod(launcher, os.stat(launcher).st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
            print("[launcher] Created run.command — double-click it from Finder next time.")

    else:
        launcher = os.path.join(here, "run.sh")
        if not os.path.exists(launcher):
            with open(launcher, "w") as f:
                f.write(
                    "#!/bin/bash\n"
                    "cd \"$(dirname \"$0\")\"\n"
                    "if [ -f venv/bin/activate ]; then\n"
                    "    source venv/bin/activate\n"
                    "else\n"
                    "    echo '[warning] No venv found, using system Python.'\n"
                    "fi\n"
                    "python3 app.py\n"
                )
            os.chmod(launcher, os.stat(launcher).st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
            print("[launcher] Created run.sh — run it with ./run.sh or double-click from your file manager next time.")

create_launcher()


# Global state
model_cache = {}
recording_queue = queue.Queue()
is_recording = False
current_model_size = "base"

SAMPLE_RATE = 16000
CHANNELS = 1

def get_model(size: str) -> WhisperModel:
    if size not in model_cache:
        print(f"Loading Whisper model: {size} ...")
        model_cache[size] = WhisperModel(size, device="cpu", compute_type="int8")
        print(f"Model '{size}' loaded.")
    return model_cache[size]

def transcribe_audio(audio_data: np.ndarray, model_size: str, language: str = None) -> dict:
    model = get_model(model_size)
    audio_float = audio_data.astype(np.float32) / 32768.0

    kwargs = {}
    if language and language != "auto":
        kwargs["language"] = language

    segments, info = model.transcribe(audio_float, beam_size=5, **kwargs)
    text = " ".join(seg.text.strip() for seg in segments).strip()
    return {
        "text": text,
        "language": info.language,
        "language_probability": round(info.language_probability, 3),
        "duration": round(info.duration, 2),
    }

@app.get("/", response_class=HTMLResponse)
async def root():
    html_path = os.path.join(os.path.dirname(__file__), "index.html")
    with open(html_path, "r") as f:
        return HTMLResponse(content=f.read())

@app.get("/api/models")
async def list_models():
    return {"models": ["base", "small", "medium", "large-v3"]}

@app.websocket("/ws/transcribe")
async def websocket_transcribe(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_json()
            action = data.get("action")

            if action == "transcribe":
                model_size = data.get("model", "base")
                language = data.get("language", "auto")

                audio_np = np.array(data["audio"], dtype=np.int16)

                await websocket.send_json({"status": "processing"})

                try:
                    result = transcribe_audio(audio_np, model_size, language)
                    await websocket.send_json({"status": "done", "result": result})
                except Exception as e:
                    await websocket.send_json({"status": "error", "message": str(e)})

            elif action == "preload":
                model_size = data.get("model", "base")
                try:
                    get_model(model_size)
                    await websocket.send_json({"status": "model_ready", "model": model_size})
                except Exception as e:
                    await websocket.send_json({"status": "error", "message": str(e)})

    except WebSocketDisconnect:
        pass

if __name__ == "__main__":
    import threading, webbrowser
    def open_browser():
        import time
        time.sleep(1.2)
        webbrowser.open("http://localhost:8000")
    threading.Thread(target=open_browser, daemon=True).start()
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=False)
