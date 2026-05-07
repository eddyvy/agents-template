from unittest.mock import AsyncMock, patch

from fastapi import FastAPI

from app.core.lifespan import lifespan


async def test_lifespan_runs_startup_then_shutdown_steps() -> None:
    app = FastAPI()
    events: list[str] = []

    def setup_settings_side_effect(_app: FastAPI) -> None:
        events.append("settings")

    async def setup_checkpointer_side_effect(_app: FastAPI) -> None:
        events.append("checkpointer")

    def setup_weather_agent_side_effect(_app: FastAPI) -> None:
        events.append("weather-agent")

    async def close_checkpointer_side_effect(_app: FastAPI) -> None:
        events.append("close-checkpointer")

    with (
        patch(
            "app.core.lifespan.setup_settings",
            side_effect=setup_settings_side_effect,
        ) as setup_settings_mock,
        patch(
            "app.core.lifespan.setup_checkpointer",
            new=AsyncMock(side_effect=setup_checkpointer_side_effect),
        ) as setup_checkpointer_mock,
        patch(
            "app.core.lifespan.setup_weather_agent",
            side_effect=setup_weather_agent_side_effect,
        ) as setup_weather_agent_mock,
        patch(
            "app.core.lifespan.close_checkpointer",
            new=AsyncMock(side_effect=close_checkpointer_side_effect),
        ) as close_checkpointer_mock,
    ):
        async with lifespan(app):
            assert events == ["settings", "checkpointer", "weather-agent"]

    assert events == ["settings", "checkpointer", "weather-agent", "close-checkpointer"]
    setup_settings_mock.assert_called_once_with(app)
    setup_checkpointer_mock.assert_awaited_once_with(app)
    setup_weather_agent_mock.assert_called_once_with(app)
    close_checkpointer_mock.assert_awaited_once_with(app)
