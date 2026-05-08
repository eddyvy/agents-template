from unittest.mock import AsyncMock, MagicMock, patch

from fastapi import FastAPI
from langchain_core.messages import AIMessage, HumanMessage
from langgraph.types import GraphOutput

from app.settings.settings import Settings
from app.weather_agent.api import get_weather_agent, setup_weather_agent
from app.weather_agent.weather_agent import WeatherAgent, get_weather


def test_get_weather_returns_expected_text() -> None:
    result = get_weather("Bogota")
    assert result == "It's always sunny in Bogota!"


async def test_weather_agent_ainvoke_uses_expected_payload() -> None:
    internal_agent = MagicMock()
    internal_agent.ainvoke = AsyncMock(
        return_value=GraphOutput(
            value={"messages": [AIMessage(content="It's sunny today")]}
        )  # noqa: S106
    )

    settings = Settings.model_construct(
        agents_api_key="agents-test-key",
        deepseek_api_key="deepseek-test-key",
        database_url="postgresql://postgres:postgres@localhost:5432/test",
    )
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
        model_name="deepseek-v4-pro",
        api_key="deepseek-test-key",
    )
    create_deep_agent_mock.assert_called_once()

    result = await agent.ainvoke("How is the weather?", "thread-123")

    internal_agent.ainvoke.assert_awaited_once()
    call_args = internal_agent.ainvoke.await_args
    assert call_args.args == ()
    payload = call_args.kwargs["input"]
    assert isinstance(payload, dict)
    assert "messages" in payload
    messages = payload["messages"]
    assert isinstance(messages, list)
    assert len(messages) == 1
    assert isinstance(messages[0], HumanMessage)
    assert messages[0].content == "How is the weather?"
    assert call_args.kwargs["config"] == {"configurable": {"thread_id": "thread-123"}}
    assert call_args.kwargs["version"] == "v2"
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


async def test_weather_agent_astream_uses_expected_payload() -> None:
    captured: dict = {}

    async def fake_astream(*args, **kwargs):
        captured.update(kwargs)
        yield "chunk1"
        yield "chunk2"

    internal_agent = MagicMock()
    internal_agent.astream = fake_astream

    settings = Settings.model_construct(
        agents_api_key="agents-test-key",
        deepseek_api_key="deepseek-test-key",
        database_url="postgresql://postgres:postgres@localhost:5432/test",
    )
    checkpointer = MagicMock()

    with (
        patch("app.weather_agent.weather_agent.ChatDeepSeek"),
        patch(
            "app.weather_agent.weather_agent.create_deep_agent",
            return_value=internal_agent,
        ),
    ):
        agent = WeatherAgent(settings, checkpointer)
        _ = [
            event async for event in agent.astream("How is the weather?", "thread-123")
        ]

    payload = captured["input"]
    assert isinstance(payload, dict)
    assert "messages" in payload
    messages = payload["messages"]
    assert len(messages) == 1
    assert isinstance(messages[0], HumanMessage)
    assert messages[0].content == "How is the weather?"
    assert captured["config"] == {"configurable": {"thread_id": "thread-123"}}
    assert captured["version"] == "v2"
    assert captured["stream_mode"] == "messages"


async def test_weather_agent_astream_formats_events_as_sse() -> None:
    async def fake_astream(*args, **kwargs):
        yield "event_a"
        yield "event_b"

    internal_agent = MagicMock()
    internal_agent.astream = fake_astream

    settings = Settings.model_construct(
        agents_api_key="agents-test-key",
        deepseek_api_key="deepseek-test-key",
        database_url="postgresql://postgres:postgres@localhost:5432/test",
    )
    checkpointer = MagicMock()

    with (
        patch("app.weather_agent.weather_agent.ChatDeepSeek"),
        patch(
            "app.weather_agent.weather_agent.create_deep_agent",
            return_value=internal_agent,
        ),
    ):
        agent = WeatherAgent(settings, checkpointer)
        events = [
            event async for event in agent.astream("How is the weather?", "thread-123")
        ]

    assert events == ["data: event_a\n\n", "data: event_b\n\n"]


async def test_weather_agent_astream_yields_nothing_when_no_events() -> None:
    async def fake_astream(*args, **kwargs):
        return
        yield  # make it an async generator

    internal_agent = MagicMock()
    internal_agent.astream = fake_astream

    settings = Settings.model_construct(
        agents_api_key="agents-test-key",
        deepseek_api_key="deepseek-test-key",
        database_url="postgresql://postgres:postgres@localhost:5432/test",
    )
    checkpointer = MagicMock()

    with (
        patch("app.weather_agent.weather_agent.ChatDeepSeek"),
        patch(
            "app.weather_agent.weather_agent.create_deep_agent",
            return_value=internal_agent,
        ),
    ):
        agent = WeatherAgent(settings, checkpointer)
        events = [
            event async for event in agent.astream("How is the weather?", "thread-123")
        ]

    assert events == []
