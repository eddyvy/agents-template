from fastapi import FastAPI
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver

from app.settings.api import get_settings


async def setup_checkpointer(app: FastAPI):
    context_manager = AsyncPostgresSaver.from_conn_string(
        get_settings(app).database_url
    )

    saver = await context_manager.__aenter__()
    await saver.setup()

    app.state.checkpointer = saver
    app.state._checkpointer_cm = context_manager


async def close_checkpointer(app: FastAPI):
    if hasattr(app.state, "_checkpointer_cm"):
        await app.state._checkpointer_cm.__aexit__(None, None, None)


def get_checkpointer(app: FastAPI) -> AsyncPostgresSaver:
    return app.state.checkpointer
