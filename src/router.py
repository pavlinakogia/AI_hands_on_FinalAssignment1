"""
Feature 4 - Intent classification. Single temperature=0 LLM call with
few-shot examples per route. Falls back to 'general' on anything
ambiguous or unparseable.
"""
from src.llm import call_llm

_VALID_ROUTES = {"weather", "search", "rag", "sql", "general"}

_PROMPT = """Classify the user's message into exactly one of these routes:

- weather: questions about current weather, temperature, rain, forecast for a city.
- search: questions needing current/up-to-date external info (news, current prices, recent events, market trends).
- rag: questions about internal company policy (returns, warranty, shipping, loyalty program, internal documents).
- sql: questions about sales data, product data, store data, numbers that would need a database query.
- general: anything else (general knowledge, definitions, casual conversation, follow-ups about earlier conversation).

Examples:
"What is the weather in Athens tomorrow?" -> weather
"Θα έχει ηλιοφάνεια στη Θεσσαλονίκη;" -> weather
"What are the latest smartphone price trends?" -> search
"Υπάρχουν νέα για τις τιμές των laptop αυτή την εβδομάδα;" -> search
"What is the warranty period for laptops?" -> rag
"Ποια είναι η πολιτική επιστροφών σας;" -> rag
"What were total sales last month?" -> sql
"Ποιο κατάστημα είχε τα περισσότερα έσοδα;" -> sql
"Explain what LangGraph is." -> general
"What city did I tell you I like?" -> general

Now classify this message. Reply with ONLY the route label, nothing else.

Message: {message}
"""


def classify(message: str) -> str:
    raw = call_llm(_PROMPT.format(message=message), temperature=0).strip().lower()
    # be defensive: strip punctuation/quotes the model might add
    cleaned = "".join(ch for ch in raw if ch.isalpha())
    return cleaned if cleaned in _VALID_ROUTES else "general"
