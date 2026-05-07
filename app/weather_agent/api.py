from typing import cast

from fastapi import FastAPI

from app.checkpointer.api import get_checkpointer
from app.settings.api import get_settings
from app.weather_agent.weather_agent import WeatherAgent


def setup_weather_agent(app: FastAPI) -> None:
    weather_agent = WeatherAgent(get_settings(app), get_checkpointer(app))
    app.state.weather_agent = weather_agent


def get_weather_agent(app: FastAPI) -> WeatherAgent:
    return cast(WeatherAgent, app.state.weather_agent)
