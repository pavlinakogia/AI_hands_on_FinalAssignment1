"""
Baseline weather tool, using the free Open-Meteo API (no key required).
Framed for the retail domain: weather can affect footfall/deliveries for
an electronics store, so we also surface a short "retail impact" note.
"""
import requests

_GEOCODE_URL = "https://geocoding-api.open-meteo.com/v1/search"
_FORECAST_URL = "https://api.open-meteo.com/v1/forecast"


def get_weather(city: str) -> dict | None:
    """Returns current + today's forecast for a city, or None if not found."""
    geo = requests.get(_GEOCODE_URL, params={"name": city, "count": 1}, timeout=10).json()
    if not geo.get("results"):
        return None

    loc = geo["results"][0]
    lat, lon = loc["latitude"], loc["longitude"]

    forecast = requests.get(
        _FORECAST_URL,
        params={
            "latitude": lat,
            "longitude": lon,
            "current": "temperature_2m,weather_code,wind_speed_10m",
            "daily": "temperature_2m_max,temperature_2m_min,precipitation_probability_max",
            "timezone": "auto",
        },
        timeout=10,
    ).json()

    return {
        "city": loc.get("name", city),
        "country": loc.get("country", ""),
        "current_temp": forecast["current"]["temperature_2m"],
        "wind_speed": forecast["current"]["wind_speed_10m"],
        "temp_max": forecast["daily"]["temperature_2m_max"][0],
        "temp_min": forecast["daily"]["temperature_2m_min"][0],
        "rain_probability": forecast["daily"]["precipitation_probability_max"][0],
    }
