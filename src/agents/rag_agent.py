from src.llm import call_llm, format_history
from src.state import AgentState
from src.tools.rag import retrieve


def run(state: AgentState) -> AgentState:
    message = state["message"]
    history_text = format_history(state.get("history", []))

    chunks = retrieve(message, top_k=4)

    if not chunks:
        answer = call_llm(
            f"The user asked: {message}\n\n"
            f"No relevant passages were found in the internal knowledge base. "
            f"Tell the user honestly that this isn't covered in the available policy "
            f"documents, and do NOT invent an answer. "
            f"Answer in the same language as the user's message.\n\n"
            f"Conversation so far:\n{history_text}",
        )
        state["response"] = answer
        state["sources"] = []
        return state

    context = "\n\n".join(
        f"[{i + 1}] (source: {c['source']}, chunk {c['chunk_index']})\n{c['text']}"
        for i, c in enumerate(chunks)
    )

    answer = call_llm(
        f"Conversation so far:\n{history_text}\n\n"
        f"User asked: {message}\n\n"
        f"Here are the retrieved internal policy passages:\n{context}\n\n"
        f"Answer the user's question using ONLY information found in these passages. "
        f"Do not state anything that isn't supported by them. Cite passages inline "
        f"using [1], [2], etc. If the passages don't fully answer the question, say so. "
        f"Answer in the same language the user used.",
        system_prompt="You are a policy assistant for an electronics retail company, "
        "answering questions strictly from internal documents (returns, warranty, "
        "shipping, loyalty program).",
    )

    sources = [f"[{i + 1}] {c['source']} (chunk {c['chunk_index']})" for i, c in enumerate(chunks)]
    state["response"] = answer + "\n\nSources:\n" + "\n".join(sources)
    state["sources"] = sources
    return state
