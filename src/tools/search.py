"""
Feature 1 - Web search tool wrapper around Tavily.
Returns a normalised list of results: title, url, snippet, date (when available).
"""
import os

from dotenv import load_dotenv
from tavily import TavilyClient

load_dotenv()

_API_KEY = os.getenv("TAVILY_API_KEY")
_client = TavilyClient(api_key=_API_KEY) if _API_KEY else None


def web_search(query: str, max_results: int = 5) -> list[dict]:
    """
    Returns a list of dicts: {"title", "url", "snippet", "date"}.
    Returns [] (not an exception) when there's no key, no connectivity,
    or no relevant results - callers must handle the empty case gracefully.
    """
    if _client is None:
        return []

    try:
        raw = _client.search(
            query=query,
            max_results=max_results,
            include_answer=False,
        )
    except Exception:
        return []

    results = []
    for item in raw.get("results", []):
        snippet = (item.get("content") or "").strip()
        if not snippet:
            continue
        results.append(
            {
                "title": item.get("title", "Untitled"),
                "url": item.get("url", ""),
                "snippet": snippet[:600],
                "date": item.get("published_date", ""),
            }
        )
    return results
