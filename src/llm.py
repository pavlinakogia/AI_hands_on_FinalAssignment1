import os

from groq import Groq
from dotenv import load_dotenv

load_dotenv()

_API_KEY = os.getenv("GROQ_API_KEY")
if not _API_KEY:
    raise RuntimeError(
        "GROQ_API_KEY is not set. Add it to your .env file."
    )

_client = Groq(api_key=_API_KEY)
MODEL_NAME = "llama-3.1-8b-instant"


def call_llm(prompt: str, system_prompt: str = "", temperature: float = 0.4) -> str:
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})

    response = _client.chat.completions.create(
        model=MODEL_NAME,
        messages=messages,
        temperature=temperature,
        max_tokens=1024,
    )
    return (response.choices[0].message.content or "").strip()


def format_history(history: list) -> str:
    if not history:
        return ""
    lines = []
    for turn in history:
        speaker = "User" if turn["role"] == "user" else "Assistant"
        lines.append(f"{speaker}: {turn['content']}")
    return "\n".join(lines)