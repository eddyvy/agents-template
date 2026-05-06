from contextlib import suppress
from unittest.mock import AsyncMock, MagicMock, patch

from app import database as database_module


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


async def test_init_db_keeps_checkpointer_open_until_close() -> None:
    context = FakeCheckpointerContext()
    database_module._db._checkpointer = None
    database_module._db._checkpointer_cm = None

    try:
        with (
            patch(
                "app.database.get_settings",
                return_value=MagicMock(database_url="postgresql://example"),
            ),
            patch(
                "app.database.AsyncPostgresSaver.from_conn_string",
                return_value=context,
            ),
        ):
            await database_module.init_db()

            assert context.entered is True
            assert context.exited is False
            assert database_module.get_checkpointer() is context.checkpointer

            await database_module.close_db()

        assert context.exited is True
        assert database_module._db._checkpointer is None
        assert database_module._db._checkpointer_cm is None
    finally:
        with suppress(Exception):
            await database_module.close_db()
        database_module._db._checkpointer = None
        database_module._db._checkpointer_cm = None
