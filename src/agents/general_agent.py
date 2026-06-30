from src.llm import call_llm, format_history
from src.state import AgentState


def run(state: AgentState) -> AgentState:
    message = state["message"]
    history_text = format_history(state.get("history", []))

    answer = call_llm(
        f"Conversation so far:\n{history_text}\n\nUser: {message}",
        system_prompt="You are a helpful general-purpose assistant for an electronics "
        "retail company. Answer in the same language the user used. If the user refers "
        "to something said earlier in the conversation, use the conversation history "
        "above to resolve the reference correctly.",
    )
    state["response"] = answer
    return state
