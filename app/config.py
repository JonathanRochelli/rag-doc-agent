import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
CLAUDE_MODEL = os.environ.get("CLAUDE_MODEL", "claude-opus-5")
EMBEDDING_MODEL = os.environ.get("EMBEDDING_MODEL", "all-MiniLM-L6-v2")

DOCUMENTS_DIR = Path(os.environ.get("DOCUMENTS_DIR", BASE_DIR / "data" / "documents"))
CHROMA_DIR = Path(os.environ.get("CHROMA_DIR", BASE_DIR / "data" / "chroma"))
CHROMA_COLLECTION = "documents"

CHUNK_SIZE = 800
CHUNK_OVERLAP = 150
TOP_K = 4
