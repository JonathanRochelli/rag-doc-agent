# RAG Document Agent

RAG (retrieval-augmented generation) chatbot: it answers questions based **only** on an indexed document corpus, and always cites its sources. FastAPI backend + generation via the Claude API (Anthropic), local retrieval with ChromaDB.

Demo project for a freelance profile focused on AI automation / LLM agents.

## Included demo

The repo ships with a fictional product documentation corpus ("NovaTrack", an imaginary project management tool): product guide, FAQ, refund policy. This lets you try the agent right away without needing your own documents.

## Architecture

```
User question
      │
      ▼
Local embeddings (sentence-transformers, all-MiniLM-L6-v2)
      │
      ▼
Vector search (ChromaDB, local persistent storage)
      │
      ▼
Relevant chunks + question ──► Claude (Anthropic API, streamed response)
      │
      ▼
Cited answer, streamed to the browser (SSE)
```

Key point: generation (Claude) and embeddings (sentence-transformers, local) are decoupled. Only one API key is needed (Anthropic); vector search costs nothing and works offline.

## Stack

- **Backend**: FastAPI + Uvicorn
- **LLM**: Anthropic API (Claude), streamed responses (SSE)
- **Embeddings**: `sentence-transformers` (local model, free, no API key needed)
- **Vector store**: ChromaDB (persistent, local, no external service)
- **Frontend**: vanilla HTML/CSS/JS (no framework)

## Setup

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
```

Copy `.env.example` to `.env` and add your Anthropic API key:

```bash
cp .env.example .env
```

```
ANTHROPIC_API_KEY=sk-ant-...
CLAUDE_MODEL=claude-opus-5
```

Get a key at [console.anthropic.com](https://console.anthropic.com/).

### Choosing the model

The default model is `claude-opus-5` (the most capable). For a lower-cost demo, just change `CLAUDE_MODEL` in `.env`:

| Model | Recommended use |
|---|---|
| `claude-opus-5` | Maximum quality, default |
| `claude-sonnet-5` | Good quality/cost balance for most cases |
| `claude-haiku-4-5` | Cheapest, for high-volume demo traffic |

## Usage

**1. Index the documents** (redo whenever the corpus changes):

```bash
python -m app.ingest
```

**2. Start the server**:

```bash
uvicorn app.main:app --reload
```

Open [http://localhost:8000](http://localhost:8000).

## Using your own documents

1. Replace the contents of `data/documents/` with your own `.md` or `.txt` files (one file per source document; the file name is used as the source identifier in citations).
2. Re-run `python -m app.ingest`.
3. Restart the server if needed.

For PDFs or other formats, adapt `app/ingest.py` (`load_documents`) to extract text before passing it to `chunk_text`.

## Tests

```bash
pytest
```

Tests cover the chunking logic (`app/chunking.py`) — the part most likely to break silently when modified.

## Limits of this demo

- Static corpus: no document upload from the UI (deliberately out of scope, to limit cost and abuse risk on a public demo).
- No multi-user support or persistent conversation history.
- No prompt caching — only worth adding at meaningful request volume.

## Going further

- Add user document uploads (with size/type limits and per-session isolation).
- Add multi-turn conversation history.
