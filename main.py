from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, FileResponse
from pydantic import BaseModel

import requests
import json
import uuid
import threading
from queue import Queue
import os
import wave

from TTS.api import TTS


# -----------------------------
# App + AI Init
# -----------------------------

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

OLLAMA_URL = "http://localhost:11434/api/generate"

tts = TTS(
    model_name="tts_models/en/ljspeech/tacotron2-DDC",
    progress_bar=False,
    gpu=False
)


# -----------------------------
# Voice Queue System
# -----------------------------

voice_queue = Queue()
voice_results = {}
voice_lock = threading.Lock()


# -----------------------------
# Helpers (split + merge wav)
# -----------------------------

def split_text(text, max_len=300):
    parts = []
    text = text.strip()

    while len(text) > max_len:
        cut = text.rfind(" ", 0, max_len)
        if cut == -1:
            cut = max_len

        parts.append(text[:cut])
        text = text[cut:].strip()

    if text:
        parts.append(text)

    return parts


def merge_wavs(files, output):
    with wave.open(files[0], 'rb') as first:
        params = first.getparams()

    with wave.open(output, 'wb') as out:
        out.setparams(params)

        for f in files:
            with wave.open(f, 'rb') as w:
                out.writeframes(w.readframes(w.getnframes()))


# -----------------------------
# Voice Worker (SAFE)
# -----------------------------

def voice_worker():
    while True:
        text, req_id = voice_queue.get()

        try:
            chunks = split_text(text)

            temp_files = []

            for i, chunk in enumerate(chunks):
                temp = f"tmp_{req_id}_{i}.wav"

                tts.tts_to_file(
                    text=chunk,
                    file_path=temp,
                    split_sentences=False
                )

                temp_files.append(temp)

            final_file = f"audio_{req_id}.wav"

            merge_wavs(temp_files, final_file)

            for f in temp_files:
                os.remove(f)

            with voice_lock:
                voice_results[req_id] = final_file

        except Exception as e:
            print("VOICE ERROR:", e)

        voice_queue.task_done()


# Start single worker
threading.Thread(target=voice_worker, daemon=True).start()


# -----------------------------
# Models
# -----------------------------

class ChatRequest(BaseModel):
    messages: list


# -----------------------------
# Streaming Chat Endpoint
# -----------------------------

@app.post("/chat-stream")
def chat_stream(req: ChatRequest):

    prompt = ""
    for m in req.messages:
        if m["role"] == "user":
            prompt += f"User: {m['text']}\n"
        else:
            prompt += f"AI: {m['text']}\n"

    payload = {
        "model": "llama3",
        "prompt": prompt + "AI:",
        "stream": True
    }

    r = requests.post(OLLAMA_URL, json=payload, stream=True)

    req_id = uuid.uuid4().hex

    def generate():
        full_text = ""

        for line in r.iter_lines():
            if not line:
                continue

            data = json.loads(line.decode())

            if "response" in data:
                chunk = data["response"]
                full_text += chunk

                yield json.dumps({
                    "type": "text",
                    "data": chunk
                }) + "\n"

            if data.get("done"):

                voice_queue.put((full_text, req_id))

                yield json.dumps({
                    "type": "voice_processing",
                    "id": req_id
                }) + "\n"

                break

    return StreamingResponse(generate(), media_type="application/json")


# -----------------------------
# Voice Status Endpoint
# -----------------------------

@app.get("/voice-status/{req_id}")
def voice_status(req_id: str):
    with voice_lock:
        if req_id in voice_results:
            return {"ready": True, "file": voice_results[req_id]}
    return {"ready": False}


# -----------------------------
# Audio Serve Endpoint
# -----------------------------

@app.get("/audio/{file}")
def audio(file: str):
    return FileResponse(file, media_type="audio/wav")
