🤖 AI Chatbot Backend (Python + Ollama + TTS)
--
This project uses a fully open-source AI stack to provide:

💬 Streaming AI chat replies

🎤 Voice output (Text-to-Speech)

🧠 Local LLM via Ollama

🌐 FastAPI backend

📦 Requirements
--


Ollama (Local LLM Server)
--
Install Ollama:

- 👉 https://ollama.com

After installing, pull a model:

  - ollama pull llama3


Start Ollama server:

  - ollama serve

  - (Default runs on http://localhost:11434)



 Python Dependencies
--
Python (Recommended)
Python 3.11.x -> (Required for TTS compatibility)

Install required packages:

- pip install fastapi uvicorn requests TTS

🚀 Running the Backend

Start FastAPI server:

- python -m uvicorn main:app --reload

Backend will run on:

- http://127.0.0.1:8000

🔁 Chat Streaming Endpoint
- POST /chat-stream


- Streams AI response from Ollama in real-time.

🔊 Voice (Text-to-Speech)

- This project uses Coqui TTS (open-source) for natural AI voice.

Example model:

- tts_models/en/ljspeech/glow-tts


Voice is generated after full AI message is received.

- 🌍 Web Support (CORS Enabled)

- FastAPI is configured with CORS to support.

🧠 Stack Overview
--
- FastAPI	-> Backend server
- Ollama	-> Local LLM (AI brain)
- Coqui TTS ->	Voice generation
- Flutter	 -> Frontend UI (https://github.com/darttechwala/ChatBot)

✅ Features
--
- Fully offline capable (local AI)

- Streaming chat responses

- Voice replies

- Multi-platform (Android, iOS, Web, macOS, Windows)

- Open-source stack

⚠ Notes
--

Ollama must be running before starting backend
