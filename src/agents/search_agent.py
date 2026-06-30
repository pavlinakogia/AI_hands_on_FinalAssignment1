from src.llm import call_llm, format_history
from src.state import AgentState
from src.tools.search import web_search


def run(state: AgentState) -> AgentState:
    message = state["message"]
    history_text = format_history(state.get("history", []))

    results = web_search(message, max_results=5)

    if not results:
        answer = call_llm(
            f"The user asked: {message}\n\n"
            f"A web search was attempted but returned no useful results. "
            f"Tell the user honestly that you couldn't find current information on this, "
            f"and do NOT make up facts. Answer in the same language as the user's message.\n\n"
            f"Conversation so far:\n{history_text}",
        )
        state["response"] = answer
        state["sources"] = []
        return state

    context = "\n\n".join(
        f"[{i + 1}] {r['title']} ({r.get('date', 'n/a')})\n{r['snippet']}\nURL: {r['url']}"
        for i, r in enumerate(results)
    )

    answer = call_llm(
        f"Conversation so far:\n{history_text}\n\n"
        f"User asked: {message}\n\n"
        f"Here are web search results:\n{context}\n\n"
        f"Answer the user's question grounded ONLY in these results. "
        f"Use inline citation markers like [1], [2] matching the numbered sources above. "
        f"If the results don't actually answer the question, say so honestly. "
        f"Answer in the same language the user used.",
        system_prompt="You are a research assistant for an electronics retail company, "
        "answering questions about current market info, prices, and news.",
    )

    sources = [f"[{i + 1}] {r['title']} - {r['url']}" for i, r in enumerate(results)]
    state["response"] = answer + "\n\nSources:\n" + "\n".join(sources)
    state["sources"] = sources
    return state
