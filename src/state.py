"""
Shared state passed between every node in the LangGraph graph.
Every agent node reads `message` + `history` and writes `response` + `route`.
"""
from typing import List, Optional, TypedDict


class HistoryTurn(TypedDict):
    role: str       # "user" or "assistant"
    content: str


class AgentState(TypedDict, total=False):
    conversation_id: str
    message: str                  # current user input
    history: List[HistoryTurn]    # last N turns, injected before the node runs (Feature 5a)
    route: str                    # "weather" | "search" | "rag" | "sql" | "general"
    response: str                 # final answer to return to the user
    sources: List[str]            # optional citations, used by search/rag nodes
