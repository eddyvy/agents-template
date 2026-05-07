from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

from fastapi import FastAPI

from app.weather_agent.api import get_weather_agent, setup_weather_agent
from app.weather_agent.weather_agent import WeatherAgent, get_weather


def test_get_weather_returns_expected_text() -> None:
    result = get_weather("Bogota")
    assert result == "It's always sunny in Bogota!"


async def test_weather_agent_ainvoke_uses_expected_payload() -> None:
    internal_agent = MagicMock()
    internal_agent.ainvoke = AsyncMock(
        return_value={"messages": [MagicMock(content="It's sunny today")]}  # noqa: S106
    )

    settings = SimpleNamespace(deepseek_api_key="deepseek-test-key")
    checkpointer = MagicMock()

    with (
        patch("app.weather_agent.weather_agent.ChatDeepSeek") as chat_model_mock,
        patch(
            "app.weather_agent.weather_agent.create_deep_agent",
            return_value=internal_agent,
        ) as create_deep_agent_mock,
    ):
        agent = WeatherAgent(settings, checkpointer)

    chat_model_mock.assert_called_once_with(
        model_name="deepseek-chat",
        api_key="deepseek-test-key",
    )
    create_deep_agent_mock.assert_called_once()

    result = await agent.ainvoke("How is the weather?", "thread-123")

    internal_agent.ainvoke.assert_awaited_once_with(
        {"messages": [{"role": "user", "content": "How is the weather?"}]},
        config={"configurable": {"thread_id": "thread-123"}},
    )
    assert result == "It's sunny today"


def test_setup_weather_agent_stores_instance_in_app_state() -> None:
    app = FastAPI()
    settings = MagicMock()
    checkpointer = MagicMock()
    weather_agent = MagicMock()

    with (
        patch("app.weather_agent.api.get_settings", return_value=settings),
        patch("app.weather_agent.api.get_checkpointer", return_value=checkpointer),
        patch(
            "app.weather_agent.api.WeatherAgent",
            return_value=weather_agent,
        ) as weather_agent_mock,
    ):
        setup_weather_agent(app)

    weather_agent_mock.assert_called_once_with(settings, checkpointer)
    assert app.state.weather_agent is weather_agent


def test_get_weather_agent_reads_instance_from_app_state() -> None:
    app = FastAPI()
    weather_agent = MagicMock()
    app.state.weather_agent = weather_agent

    assert get_weather_agent(app) is weather_agent
