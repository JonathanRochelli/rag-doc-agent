"""Retrieval-augmented generation: retrieve relevant chunks, then stream a cited answer from Claude."""
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
_embedder = SentenceTransformer(EMBEDDING_MODEL)
_anthropic = AsyncAnthropic(api_key=ANTHROPIC_API_KEY or None)

SYSTEM_PROMPT = """Tu es un assistant qui répond aux questions UNIQUEMENT à partir des documents fournis dans le message de l'utilisateur.

Règles :
- Base chaque réponse exclusivement sur le contenu des documents fournis, jamais sur des connaissances externes.
- Cite systématiquement la source de chaque information avec la notation [source: nom_du_fichier].
- Si l'information demandée n'est pas présente dans les documents, dis-le clairement plutôt que d'inventer une réponse.
- Réponds de façon concise et directe."""


def retrieve(query: str, top_k: int = TOP_K) -> list[dict]:
    query_embedding = _embedder.encode([query]).tolist()
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


def ensure_index() -> None:
    """Index the demo corpus on first boot if the collection is empty.

    Hosting platforms with an ephemeral disk (Render/Fly free tiers) wipe
    data/chroma on every deploy or restart, so ingestion must be able to
    run automatically at startup rather than only via the CLI.
    """
    if _collection.count() == 0:
        from app.ingest import ingest_into

        ingest_into(_collection, _embedder)


async def stream_answer(question: str) -> AsyncIterator[dict]:
    chunks = retrieve(question)
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
