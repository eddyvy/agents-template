from unittest.mock import AsyncMock, MagicMock, patch

from fastapi import FastAPI

from app.checkpointer.api import (
    close_checkpointer,
    get_checkpointer,
    setup_checkpointer,
)


class FakeCheckpointerContext:
    def __init__(self) -> None:
        self.checkpointer = MagicMock()
        self.checkpointer.setup = AsyncMock()
        self.entered = False
        self.exited = False

    async def __aenter__(self) -> MagicMock:
        self.entered = True
        return self.checkpointer

    async def __aexit__(self, exc_type: object, exc: object, tb: object) -> None:
        self.exited = True


async def test_setup_checkpointer_initializes_and_stores_on_app_state() -> None:
    app = FastAPI()
    context = FakeCheckpointerContext()

    with (
        patch(
            "app.checkpointer.api.get_settings",
            return_value=MagicMock(database_url="postgresql://example"),
        ),
        patch(
            "app.checkpointer.api.AsyncPostgresSaver.from_conn_string",
            return_value=context,
        ),
    ):
        await setup_checkpointer(app)

    assert context.entered is True
    context.checkpointer.setup.assert_awaited_once()
    assert app.state.checkpointer is context.checkpointer
    assert app.state._checkpointer_cm is context


async def test_close_checkpointer_closes_open_context_manager() -> None:
    app = FastAPI()
    context = FakeCheckpointerContext()
    app.state._checkpointer_cm = context

    await close_checkpointer(app)

    assert context.exited is True


async def test_close_checkpointer_without_context_manager_is_noop() -> None:
    app = FastAPI()

    await close_checkpointer(app)

    assert hasattr(app.state, "_checkpointer_cm") is False


def test_get_checkpointer_returns_stored_instance() -> None:
    app = FastAPI()
    checkpointer = MagicMock()
    app.state.checkpointer = checkpointer

    assert get_checkpointer(app) is checkpointer
