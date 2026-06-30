"""
Feature 5 - All database reads/writes for conversation history live here,
and only here (agent nodes never touch SQL directly for memory).

5a: get_recent_history() returns the last N turns to inject into prompts.
5b: every message (user + assistant) is persisted to SQLite so a
    conversation can be resumed after a full restart via conversation_id.
"""
import os
import sqlite3
import uuid
from datetime import datetime, timezone

_BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_DB_PATH = os.path.join(_BASE_DIR, "data", "conversations.db")

DEFAULT_HISTORY_TURNS = 6


def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(_DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    os.makedirs(os.path.dirname(_DB_PATH), exist_ok=True)
    conn = _connect()
    try:
        conn.execute(
            """CREATE TABLE IF NOT EXISTS conversations (
                conversation_id TEXT PRIMARY KEY,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )"""
        )
        conn.execute(
            """CREATE TABLE IF NOT EXISTS messages (
                message_id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                FOREIGN KEY (conversation_id) REFERENCES conversations (conversation_id)
            )"""
        )
        conn.commit()
    finally:
        conn.close()


def new_conversation() -> str:
    conversation_id = str(uuid.uuid4())[:8]
    now = datetime.now(timezone.utc).isoformat()
    conn = _connect()
    try:
        conn.execute(
            "INSERT INTO conversations (conversation_id, created_at, updated_at) VALUES (?, ?, ?)",
            (conversation_id, now, now),
        )
        conn.commit()
    finally:
        conn.close()
    return conversation_id


def conversation_exists(conversation_id: str) -> bool:
    conn = _connect()
    try:
        row = conn.execute(
            "SELECT 1 FROM conversations WHERE conversation_id = ?", (conversation_id,)
        ).fetchone()
        return row is not None
    finally:
        conn.close()


def store_message(conversation_id: str, role: str, content: str) -> None:
    now = datetime.now(timezone.utc).isoformat()
    conn = _connect()
    try:
        conn.execute(
            "INSERT INTO messages (conversation_id, role, content, timestamp) VALUES (?, ?, ?, ?)",
            (conversation_id, role, content, now),
        )
        conn.execute(
            "UPDATE conversations SET updated_at = ? WHERE conversation_id = ?",
            (now, conversation_id),
        )
        conn.commit()
    finally:
        conn.close()


def get_full_history(conversation_id: str) -> list[dict]:
    """All messages for a conversation, oldest first. Used to resume after restart (5b)."""
    conn = _connect()
    try:
        rows = conn.execute(
            "SELECT role, content FROM messages WHERE conversation_id = ? "
            "ORDER BY message_id ASC",
            (conversation_id,),
        ).fetchall()
        return [{"role": r["role"], "content": r["content"]} for r in rows]
    finally:
        conn.close()


def get_recent_history(conversation_id: str, n: int = DEFAULT_HISTORY_TURNS) -> list[dict]:
    """Last n messages (not n 'turns' of 2 - n raw messages), oldest first (5a)."""
    full = get_full_history(conversation_id)
    return full[-n:] if n > 0 else []
