"""Ingestion pipeline: read documents, chunk them, embed them, store them in ChromaDB.

Usage:
    python -m app.ingest
"""
from pathlib import Path

import chromadb
from sentence_transformers import SentenceTransformer

from app.chunking import chunk_text
from app.config import (
    CHROMA_COLLECTION,
    CHROMA_DIR,
    CHUNK_OVERLAP,
    CHUNK_SIZE,
    DOCUMENTS_DIR,
    EMBEDDING_MODEL,
)

SUPPORTED_EXTENSIONS = {".md", ".txt"}


def load_documents(documents_dir: Path):
    for path in sorted(documents_dir.rglob("*")):
        if path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS:
            yield path


def ingest_into(collection, model, documents_dir: Path = DOCUMENTS_DIR) -> int:
    """Embed every document under documents_dir and add the chunks to an (empty) collection."""
    ids, texts, metadatas = [], [], []
    for path in load_documents(documents_dir):
        content = path.read_text(encoding="utf-8")
        for chunk in chunk_text(content, CHUNK_SIZE, CHUNK_OVERLAP):
            ids.append(f"{path.stem}-{chunk.index}")
            texts.append(chunk.text)
            metadatas.append({"source": path.name})

    if not texts:
        print(f"No documents found in {documents_dir}")
        return 0

    embeddings = model.encode(texts, show_progress_bar=True).tolist()
    collection.add(ids=ids, documents=texts, metadatas=metadatas, embeddings=embeddings)
    print(f"{len(texts)} chunks indexed from {documents_dir}")
    return len(texts)


def ingest() -> int:
    """CLI entry point: rebuild the collection from scratch (python -m app.ingest)."""
    CHROMA_DIR.mkdir(parents=True, exist_ok=True)
    client = chromadb.PersistentClient(path=str(CHROMA_DIR))

    existing = {c.name for c in client.list_collections()}
    if CHROMA_COLLECTION in existing:
        client.delete_collection(CHROMA_COLLECTION)
    collection = client.create_collection(CHROMA_COLLECTION)

    model = SentenceTransformer(EMBEDDING_MODEL)
    count = ingest_into(collection, model)
    print(f"-> {CHROMA_DIR}")
    return count


if __name__ == "__main__":
    ingest()
