
import streamlit as st

from src import memory
from src.graph import build_graph

st.set_page_config(
    page_title="Electronics Retail Assistant",
    page_icon="🛒",
    layout="centered",
)

ROUTE_COLOURS = {
    "weather": "#4A90D9",
    "search":  "#E67E22",
    "rag":     "#27AE60",
    "sql":     "#8E44AD",
    "general": "#7F8C8D",
}
ROUTE_LABELS = {
    "weather": "🌤 Weather",
    "search":  "🔍 Web Search",
    "rag":     "📄 Policy Docs",
    "sql":     "🗄 Sales Data",
    "general": "💬 General",
}


def route_badge(route: str) -> str:
    colour = ROUTE_COLOURS.get(route, "#7F8C8D")
    label  = ROUTE_LABELS.get(route, route)
    return (
        f'<span style="background:{colour};color:white;padding:2px 10px;'
        f'border-radius:12px;font-size:0.75rem;font-weight:600;">{label}</span>'
    )


if "graph" not in st.session_state:
    memory.init_db()
    st.session_state.graph = build_graph()

if "conversation_id" not in st.session_state:
    st.session_state.conversation_id = memory.new_conversation()

if "messages" not in st.session_state:
    st.session_state.messages = []   # list of {role, content, route}

with st.sidebar:
    st.title("🛒 Electronics Assistant")
    st.caption("Powered by LangGraph + Groq")
    st.divider()

    st.markdown("**Conversation ID**")
    st.code(st.session_state.conversation_id, language=None)

    st.divider()
    st.markdown("**Resume a conversation**")
    resume_id = st.text_input("Paste a conversation ID:", key="resume_input")
    if st.button("Resume", use_container_width=True):
        if resume_id and memory.conversation_exists(resume_id):
            st.session_state.conversation_id = resume_id
            history = memory.get_full_history(resume_id)
            st.session_state.messages = [
                {"role": m["role"], "content": m["content"], "route": "general"}
                for m in history
            ]
            st.success(f"Resumed conversation {resume_id}")
            st.rerun()
        else:
            st.error("Conversation ID not found.")

    if st.button("🗑 New conversation", use_container_width=True):
        st.session_state.conversation_id = memory.new_conversation()
        st.session_state.messages = []
        st.rerun()

    st.divider()
    st.markdown("**Route legend**")
    for route, label in ROUTE_LABELS.items():
        colour = ROUTE_COLOURS[route]
        st.markdown(
            f'<span style="background:{colour};color:white;padding:2px 8px;'
            f'border-radius:10px;font-size:0.75rem;">{label}</span>',
            unsafe_allow_html=True,
        )

    st.divider()
    st.markdown("**Example questions**")
    examples = [
        "What is the weather in Athens?",
        "What is the return policy?",
        "Which category had the highest revenue?",
        "What are the latest laptop deals?",
        "What is LangGraph?",
    ]
    for ex in examples:
        if st.button(ex, use_container_width=True, key=f"ex_{ex}"):
            st.session_state["prefill"] = ex
            st.rerun()


st.markdown("## 🛒 Electronics Retail Assistant")
st.caption(
    "Ask about store policies, sales data, current market news, or the weather."
)


for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        if msg["role"] == "assistant" and msg.get("route"):
            st.markdown(route_badge(msg["route"]), unsafe_allow_html=True)
        st.markdown(msg["content"])


prefill = st.session_state.pop("prefill", None)

user_input = st.chat_input("Ask me anything…") or prefill

if user_input:

    st.session_state.messages.append({"role": "user", "content": user_input, "route": None})
    with st.chat_message("user"):
        st.markdown(user_input)


    history = memory.get_recent_history(st.session_state.conversation_id)
    memory.store_message(st.session_state.conversation_id, "user", user_input)


    with st.chat_message("assistant"):
        with st.spinner("Thinking…"):
            state = {
                "conversation_id": st.session_state.conversation_id,
                "message": user_input,
                "history": history,
            }
            result = st.session_state.graph.invoke(state)

        route    = result.get("route", "general")
        response = result["response"]

        st.markdown(route_badge(route), unsafe_allow_html=True)
        st.markdown(response)

    memory.store_message(st.session_state.conversation_id, "assistant", response)
    st.session_state.messages.append(
        {"role": "assistant", "content": response, "route": route}
    )
