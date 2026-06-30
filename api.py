
from typing import Optional

from fastapi import FastAPI
from pydantic import BaseModel

from src import memory
from src.graph import build_graph

app = FastAPI(title="Electronics Retail Agentic AI")
_graph = None


@app.on_event("startup")
def startup():
    global _graph
    memory.init_db()
    _graph = build_graph()


class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None


class ChatResponse(BaseModel):
    response: str
    conversation_id: str
    route: str


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    if req.conversation_id and memory.conversation_exists(req.conversation_id):
        conversation_id = req.conversation_id
    else:
        conversation_id = memory.new_conversation()

    history = memory.get_recent_history(conversation_id)
    memory.store_message(conversation_id, "user", req.message)

    state = {"conversation_id": conversation_id, "message": req.message, "history": history}
    result = _graph.invoke(state)

    memory.store_message(conversation_id, "assistant", result["response"])

    return ChatResponse(
        response=result["response"],
        conversation_id=conversation_id,
        route=result.get("route", "general"),
    )


@app.get("/conversations/{conversation_id}/history")
def history(conversation_id: str):
    return {"conversation_id": conversation_id, "messages": memory.get_full_history(conversation_id)}
