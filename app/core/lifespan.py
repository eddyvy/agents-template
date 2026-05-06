from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.checkpointer.api import close_checkpointer, setup_checkpointer
from app.settings.api import setup_settings
from app.weather_agent.api import setup_weather_agent


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_settings(app)

    await setup_checkpointer(app)

    setup_weather_agent(app)

    yield

    await close_checkpointer(app)
