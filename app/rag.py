"""Retrieval-augmented generation: retrieve relevant chunks, then stream a cited answer from Claude."""
import asyncio
from typing import AsyncIterator

import anthropic
import chromadb
from anthropic import AsyncAnthropic
from sentence_transformers import SentenceTransformer

from app.config import (
    ANTHROPIC_API_KEY,
    CHROMA_COLLECTION,
    CHROMA_DIR,
    CLAUDE_MODEL,
    EMBEDDING_MODEL,
    TOP_K,
)

_chroma_client = chromadb.PersistentClient(path=str(CHROMA_DIR))
_collection = _chroma_client.get_or_create_collection(CHROMA_COLLECTION)
_anthropic = AsyncAnthropic(api_key=ANTHROPIC_API_KEY or None)

# The embedding model (torch + a HF download on first boot) and the demo-corpus
# indexing are deferred until first use instead of running at import/startup time,
# so the web server can start accepting connections immediately.
_embedder: SentenceTransformer | None = None
_ready_lock = asyncio.Lock()
_index_ready = False

SYSTEM_PROMPT = """Tu es un assistant qui répond aux questions UNIQUEMENT à partir des documents fournis dans le message de l'utilisateur.

Règles :
- Base chaque réponse exclusivement sur le contenu des documents fournis, jamais sur des connaissances externes.
- Cite systématiquement la source de chaque information avec la notation [source: nom_du_fichier].
- Si l'information demandée n'est pas présente dans les documents, dis-le clairement plutôt que d'inventer une réponse.
- Réponds de façon concise et directe."""


async def _ensure_ready() -> SentenceTransformer:
    """Load the embedding model and index the demo corpus, once, on first use."""
    global _embedder, _index_ready

    async with _ready_lock:
        if _embedder is None:
            _embedder = await asyncio.to_thread(SentenceTransformer, EMBEDDING_MODEL)
        if not _index_ready:
            if _collection.count() == 0:
                from app.ingest import ingest_into

                await asyncio.to_thread(ingest_into, _collection, _embedder)
            _index_ready = True

    return _embedder


async def warm_up() -> None:
    """Fire-and-forget startup hook: pre-load the model/index in the background
    so the web server can bind its port immediately (see module docstring note)."""
    try:
        await _ensure_ready()
    except Exception:
        # A failed warm-up isn't fatal — the first real request will retry
        # via _ensure_ready() and surface the error there instead.
        pass


async def retrieve(query: str, top_k: int = TOP_K) -> list[dict]:
    embedder = await _ensure_ready()
    query_embedding = await asyncio.to_thread(lambda: embedder.encode([query]).tolist())
    results = _collection.query(query_embeddings=query_embedding, n_results=top_k)
    documents = results.get("documents") or [[]]
    metadatas = results.get("metadatas") or [[]]
    return [
        {"text": text, "source": meta.get("source", "inconnu")}
        for text, meta in zip(documents[0], metadatas[0])
    ]


def build_context_block(chunks: list[dict]) -> str:
    if not chunks:
        return "(aucun document pertinent trouvé)"
    return "\n\n".join(
        f'<document source="{c["source"]}">\n{c["text"]}\n</document>' for c in chunks
    )


async def stream_answer(question: str) -> AsyncIterator[dict]:
    chunks = await retrieve(question)
    context_block = build_context_block(chunks)
    user_message = f"<documents>\n{context_block}\n</documents>\n\nQuestion : {question}"

    sources = sorted({c["source"] for c in chunks})
    yield {"type": "sources", "sources": sources}

    if not ANTHROPIC_API_KEY:
        yield {
            "type": "error",
            "message": "Aucune clé API Anthropic configurée. Renseigne ANTHROPIC_API_KEY dans le fichier .env.",
        }
        return

    try:
        async with _anthropic.messages.stream(
            model=CLAUDE_MODEL,
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            output_config={"effort": "low"},
            messages=[{"role": "user", "content": user_message}],
        ) as stream:
            async for text in stream.text_stream:
                yield {"type": "text", "text": text}
    except anthropic.AuthenticationError:
        yield {
            "type": "error",
            "message": "Clé API Anthropic invalide. Vérifie la variable ANTHROPIC_API_KEY.",
        }
    except anthropic.APIConnectionError:
        yield {"type": "error", "message": "Impossible de contacter l'API Anthropic."}
    except anthropic.APIStatusError as exc:
        yield {"type": "error", "message": f"Erreur API Claude ({exc.status_code})."}
    except Exception:
        yield {
            "type": "error",
            "message": "Erreur inattendue lors de la génération de la réponse.",
        }
