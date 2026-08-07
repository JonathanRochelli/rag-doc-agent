from dataclasses import dataclass


@dataclass
class Chunk:
    text: str
    index: int


def chunk_text(text: str, chunk_size: int = 800, overlap: int = 150) -> list[Chunk]:
    """Split text into paragraph-aware chunks with a trailing overlap for context continuity."""
    text = text.strip()
    if not text:
        return []

    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]

    raw_chunks: list[str] = []
    current = ""
    for para in paragraphs:
        candidate = f"{current}\n\n{para}" if current else para
        if len(candidate) <= chunk_size:
            current = candidate
            continue
        if current:
            raw_chunks.append(current)
        if len(para) <= chunk_size:
            current = para
        else:
            step = max(chunk_size - overlap, 1)
            for start in range(0, len(para), step):
                raw_chunks.append(para[start:start + chunk_size])
            current = ""
    if current:
        raw_chunks.append(current)

    chunks = []
    for i, chunk_body in enumerate(raw_chunks):
        if i > 0 and overlap > 0:
            prefix = raw_chunks[i - 1][-overlap:]
            chunk_body = f"{prefix}\n{chunk_body}"
        chunks.append(Chunk(text=chunk_body, index=i))
    return chunks
