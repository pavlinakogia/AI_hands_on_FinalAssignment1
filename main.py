
import argparse

from src import memory
from src.graph import build_graph


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--conversation-id", default=None)
    parser.add_argument("--history-turns", type=int, default=memory.DEFAULT_HISTORY_TURNS)
    args = parser.parse_args()

    memory.init_db()
    graph = build_graph()

    if args.conversation_id and memory.conversation_exists(args.conversation_id):
        conversation_id = args.conversation_id
        print(f"Resuming conversation {conversation_id}")
    else:
        conversation_id = memory.new_conversation()
        print(f"Started new conversation: {conversation_id}")

    print("Type 'exit' or 'quit' to end the session.\n")

    while True:
        user_input = input("You: ").strip()
        if user_input.lower() in {"exit", "quit"}:
            break
        if not user_input:
            continue

        # Feature 5a - retrieve last N turns BEFORE adding the current message
        history = memory.get_recent_history(conversation_id, args.history_turns)

        # Feature 5b - store the user message
        memory.store_message(conversation_id, "user", user_input)

        state = {
            "conversation_id": conversation_id,
            "message": user_input,
            "history": history,
        }
        result = graph.invoke(state)
        response = result["response"]

        print(f"\nAgent [{result.get('route', '?')}]: {response}\n")

        # Feature 5b - store the agent response
        memory.store_message(conversation_id, "assistant", response)


if __name__ == "__main__":
    main()
