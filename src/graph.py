from langgraph.graph import END, StateGraph

from src.agents import general_agent, rag_agent, search_agent, sql_agent, weather_agent
from src.router import classify
from src.state import AgentState


def router_node(state: AgentState) -> AgentState:
    state["route"] = classify(state["message"])
    return state


def route_decision(state: AgentState) -> str:
    return state["route"]


def build_graph():
    graph = StateGraph(AgentState)

    graph.add_node("router", router_node)
    graph.add_node("weather", weather_agent.run)
    graph.add_node("search", search_agent.run)
    graph.add_node("rag", rag_agent.run)
    graph.add_node("sql", sql_agent.run)
    graph.add_node("general", general_agent.run)

    graph.set_entry_point("router")

    graph.add_conditional_edges(
        "router",
        route_decision,
        {
            "weather": "weather",
            "search": "search",
            "rag": "rag",
            "sql": "sql",
            "general": "general",
        },
    )

    for node in ["weather", "search", "rag", "sql", "general"]:
        graph.add_edge(node, END)

    return graph.compile()
