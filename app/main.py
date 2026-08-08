import asyncio
import json
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from app.rag import stream_answer, warm_up

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Fire-and-forget: don't block server startup on model loading / indexing,
    # or the port never opens in time on constrained hosting (see app/rag.py).
    asyncio.create_task(warm_up())
    yield


app = FastAPI(title="Agent RAG sur documents", lifespan=lifespan)


class ChatRequest(BaseModel):
    question: str


@app.get("/")
async def index():
    return FileResponse(STATIC_DIR / "index.html")


@app.post("/api/chat")
async def chat(payload: ChatRequest):
    async def event_stream():
        async for event in stream_answer(payload.question):
            yield f"data: {json.dumps(event, ensure_ascii=False)}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")


app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
