from contextlib import AbstractAsyncContextManager
from typing import cast

from fastapi import FastAPI
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver

from app.settings.api import get_settings


async def setup_checkpointer(app: FastAPI) -> None:
    context_manager: AbstractAsyncContextManager[AsyncPostgresSaver] = (
        AsyncPostgresSaver.from_conn_string(get_settings(app).database_url)
    )

    saver = await context_manager.__aenter__()
    await saver.setup()

    app.state.checkpointer = saver
    app.state._checkpointer_cm = context_manager


async def close_checkpointer(app: FastAPI) -> None:
    if hasattr(app.state, "_checkpointer_cm"):
        context_manager = cast(
            AbstractAsyncContextManager[AsyncPostgresSaver],
            app.state._checkpointer_cm,
        )
        await context_manager.__aexit__(None, None, None)


def get_checkpointer(app: FastAPI) -> AsyncPostgresSaver:
    return cast(AsyncPostgresSaver, app.state.checkpointer)
