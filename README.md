# 🎥 Video Agent

An end-to-end AI application that converts YouTube videos and local audio files into searchable knowledge using speech recognition, summarization, vector search, and Retrieval-Augmented Generation (RAG).

The application downloads/extracts audio, transcribes speech using Whisper (or Sarvam AI for Hinglish), generates summaries, stores the content in a ChromaDB vector database, and enables question answering using Retrieval-Augmented Generation (RAG).

---

## Features

- Download audio from YouTube videos
- Process local audio files
- Automatic audio chunking
- Speech-to-text using OpenAI Whisper
- Hinglish transcription using Sarvam AI
- AI-powered summarization
- ChromaDB vector database for semantic search
- RAG-based Question Answering
- Streamlit web interface

---

## Tech Stack

- Python
- Whisper
- LangChain
- ChromaDB
- Sentence Transformers
- Mistral AI
- Streamlit
- yt-dlp
- FFmpeg

---

## Project Structure

```
video-agent/
│
├── core/
│   ├── extractor.py
│   ├── transcriber.py
│   ├── summarizer.py
│   ├── rag_engine.py
│   └── vector_store.py
│
├── utils/
│   └── audio_processor.py
│
├── app.py
├── main.py
├── requirements.txt
└── .env
```

---

## Installation

### Clone the repository

```bash
git clone <your-repository-url>
cd video-agent
```

### Create a virtual environment

```bash
python -m venv venv
```

### Activate the environment

Windows

```bash
venv\Scripts\activate
```

### Install dependencies

```bash
pip install -r requirements.txt
```

---

## Environment Variables

Create a `.env` file in the project root.

```env
MISTRAL_API_KEY=your_api_key
SARVAM_API_KEY=your_api_key
```

---

## Run the Application

```bash
streamlit run app.py
```

or

```bash
python main.py
```

---

## Requirements

- Python 3.12+
- FFmpeg installed and added to PATH

---

## Future Improvements

- Speaker diarization
- Multi-language support
- PDF export
- Better retrieval and citations
- Cloud deployment

---
