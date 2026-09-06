import os
import uuid

from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel

from .llm_client import get_agent_reply
from .analytics import generate_analytics

app = FastAPI(title="Northstar Homes AI Agent")

# session_id -> list[{"role": "user"|"assistant", "content": str}]
SESSIONS: dict[str, list] = {}

STATIC_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static")


class ChatRequest(BaseModel):
    session_id: str | None = None
    message: str


class ChatResponse(BaseModel):
    session_id: str
    reply: str


class EndRequest(BaseModel):
    session_id: str


@app.post("/api/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    session_id = req.session_id or str(uuid.uuid4())
    history = SESSIONS.setdefault(session_id, [])

    if not req.message or not req.message.strip():
        raise HTTPException(status_code=400, detail="message cannot be empty")

    history.append({"role": "user", "content": req.message})
    reply = get_agent_reply(history, session_id)
    history.append({"role": "assistant", "content": reply})

    return ChatResponse(session_id=session_id, reply=reply)


@app.post("/api/end")
def end_conversation(req: EndRequest):
    history = SESSIONS.get(req.session_id)
    if history is None:
        raise HTTPException(status_code=404, detail="unknown session_id")
    if not history:
        raise HTTPException(status_code=400, detail="conversation is empty")

    analytics = generate_analytics(history)
    return {"session_id": req.session_id, "analytics": analytics}


@app.get("/api/health")
def health():
    return {"status": "ok"}


# Serve the simple chat frontend
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/")
def root():
    return FileResponse(os.path.join(STATIC_DIR, "index.html"))
