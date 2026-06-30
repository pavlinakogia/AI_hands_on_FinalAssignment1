import re

from src.llm import call_llm, format_history
from src.state import AgentState
from src.tools.weather import get_weather


def run(state: AgentState) -> AgentState:
    message = state["message"]
    history_text = format_history(state.get("history", []))

    # naive city extraction: ask the LLM for just the city name
    city = call_llm(
        f"Extract only the city name mentioned in this message. "
        f"Reply with the city name only, nothing else.\n\nMessage: {message}",
        temperature=0,
    )
    city = re.sub(r"[^\w\sΑ-Ωα-ωάέίόύήώϊΐϋΰ-]", "", city).strip()

    weather = get_weather(city) if city else None

    if weather is None:
        answer = call_llm(
            f"The user asked about weather but no valid city could be resolved "
            f"(city extracted: '{city}'). Politely ask them to specify a city. "
            f"Answer in the same language as the user's message.\n\n"
            f"Conversation so far:\n{history_text}\n\nUser: {message}"
        )
        state["response"] = answer
        return state

    answer = call_llm(
        f"Conversation so far:\n{history_text}\n\n"
        f"User asked: {message}\n\n"
        f"Weather data for {weather['city']}: current temp {weather['current_temp']}°C, "
        f"wind {weather['wind_speed']} km/h, today's range "
        f"{weather['temp_min']}-{weather['temp_max']}°C, "
        f"rain probability {weather['rain_probability']}%.\n\n"
        f"Answer the user's question using this data. Since this is a retail/electronics "
        f"store assistant, briefly note if the weather might affect store footfall or "
        f"deliveries (e.g. heavy rain -> lower footfall, online orders up). "
        f"Answer in the same language the user used.",
        system_prompt="You are a helpful assistant for an electronics retail company.",
    )
    state["response"] = answer
    return state
