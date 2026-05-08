from collections.abc import AsyncGenerator
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from app.app import app
from app.core.auth import API_KEY_HEADER
from app.settings.settings import Settings

TEST_API_KEY = "test-secret-key"
TEST_THREAD_ID = "test-thread-123"


@pytest.fixture
def mock_settings() -> MagicMock:
    settings = MagicMock(spec=Settings)
    settings.agents_api_key = TEST_API_KEY
    return settings


@pytest.fixture
def inject_settings(mock_settings: MagicMock):
    app.state.settings = mock_settings
    yield
    if hasattr(app.state, "settings"):
        delattr(app.state, "settings")


@pytest.fixture
async def client(inject_settings: None) -> AsyncGenerator[AsyncClient]:
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac


@pytest.fixture
async def auth_client(client: AsyncClient) -> AsyncClient:
    client.headers.update({API_KEY_HEADER: TEST_API_KEY})
    return client


def make_mock_agent(response_content: str) -> MagicMock:
    mock_agent = MagicMock()
    mock_agent.ainvoke = AsyncMock(return_value=response_content)
    return mock_agent


def make_mock_streaming_agent(events: list[str]) -> MagicMock:
    async def _astream(message: str, thread_id: str):
        for event in events:
            yield event

    mock_agent = MagicMock()
    mock_agent.astream = _astream
    return mock_agent


# --- POST /weather-agent/invoke ---


async def test_invoke_no_auth_returns_401(client: AsyncClient) -> None:
    response = await client.post(
        "/weather-agent/invoke",
        json={"message": "hello", "thread_id": TEST_THREAD_ID},
    )
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid or missing API key"}


async def test_invoke_returns_200(auth_client: AsyncClient) -> None:
    mock_agent = make_mock_agent("It's always sunny in SF!")

    with patch("app.weather_agent.handler.get_weather_agent", return_value=mock_agent):
        response = await auth_client.post(
            "/weather-agent/invoke",
            json={"message": "What's the weather in SF?", "thread_id": TEST_THREAD_ID},
        )

    assert response.status_code == 200


async def test_invoke_returns_agent_response(auth_client: AsyncClient) -> None:
    mock_agent = make_mock_agent("It's always sunny in SF!")

    with patch("app.weather_agent.handler.get_weather_agent", return_value=mock_agent):
        response = await auth_client.post(
            "/weather-agent/invoke",
            json={"message": "What's the weather in SF?", "thread_id": TEST_THREAD_ID},
        )

    assert response.json() == {"response": "It's always sunny in SF!"}


async def test_invoke_missing_message_returns_422(auth_client: AsyncClient) -> None:
    response = await auth_client.post("/weather-agent/invoke", json={})
    assert response.status_code == 422


async def test_invoke_missing_thread_id_returns_422(auth_client: AsyncClient) -> None:
    response = await auth_client.post(
        "/weather-agent/invoke",
        json={"message": "What's the weather in SF?"},
    )
    assert response.status_code == 422


# --- POST /weather-agent/stream ---


async def test_stream_no_auth_returns_401(client: AsyncClient) -> None:
    response = await client.post(
        "/weather-agent/stream",
        json={"message": "hello", "thread_id": TEST_THREAD_ID},
    )
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid or missing API key"}


async def test_stream_missing_message_returns_422(auth_client: AsyncClient) -> None:
    response = await auth_client.post("/weather-agent/stream", json={})
    assert response.status_code == 422


async def test_stream_missing_thread_id_returns_422(auth_client: AsyncClient) -> None:
    response = await auth_client.post(
        "/weather-agent/stream",
        json={"message": "What's the weather in SF?"},
    )
    assert response.status_code == 422


async def test_stream_returns_200(auth_client: AsyncClient) -> None:
    mock_agent = make_mock_streaming_agent(["data: chunk\n\n"])

    with patch("app.weather_agent.handler.get_weather_agent", return_value=mock_agent):
        response = await auth_client.post(
            "/weather-agent/stream",
            json={"message": "What's the weather in SF?", "thread_id": TEST_THREAD_ID},
        )

    assert response.status_code == 200


async def test_stream_returns_event_stream_content_type(
    auth_client: AsyncClient,
) -> None:
    mock_agent = make_mock_streaming_agent([])

    with patch("app.weather_agent.handler.get_weather_agent", return_value=mock_agent):
        response = await auth_client.post(
            "/weather-agent/stream",
            json={"message": "What's the weather in SF?", "thread_id": TEST_THREAD_ID},
        )

    assert "text/event-stream" in response.headers["content-type"]


async def test_stream_yields_sse_formatted_events(auth_client: AsyncClient) -> None:
    mock_agent = make_mock_streaming_agent(["data: event1\n\n", "data: event2\n\n"])

    with patch("app.weather_agent.handler.get_weather_agent", return_value=mock_agent):
        response = await auth_client.post(
            "/weather-agent/stream",
            json={"message": "What's the weather in SF?", "thread_id": TEST_THREAD_ID},
        )

    assert response.text == "data: event1\n\ndata: event2\n\n"


async def test_stream_empty_response_when_no_events(auth_client: AsyncClient) -> None:
    mock_agent = make_mock_streaming_agent([])

    with patch("app.weather_agent.handler.get_weather_agent", return_value=mock_agent):
        response = await auth_client.post(
            "/weather-agent/stream",
            json={"message": "What's the weather in SF?", "thread_id": TEST_THREAD_ID},
        )

    assert response.text == ""


# --- GET /weather-agent/threads/{thread_id} ---


async def test_get_thread_history_no_auth_returns_401(client: AsyncClient) -> None:
    response = await client.get(f"/weather-agent/threads/{TEST_THREAD_ID}")
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid or missing API key"}


async def test_get_thread_history_returns_200(auth_client: AsyncClient) -> None:
    mock_agent = MagicMock()
    mock_agent.get_messages = AsyncMock(return_value=[])

    with patch("app.weather_agent.handler.get_weather_agent", return_value=mock_agent):
        response = await auth_client.get(f"/weather-agent/threads/{TEST_THREAD_ID}")

    assert response.status_code == 200


async def test_get_thread_history_calls_agent_with_thread_id(
    auth_client: AsyncClient,
) -> None:
    mock_agent = MagicMock()
    mock_agent.get_messages = AsyncMock(return_value=[])

    with patch("app.weather_agent.handler.get_weather_agent", return_value=mock_agent):
        await auth_client.get(f"/weather-agent/threads/{TEST_THREAD_ID}")

    mock_agent.get_messages.assert_awaited_once_with(TEST_THREAD_ID)


async def test_get_thread_history_returns_messages(auth_client: AsyncClient) -> None:
    from langchain_core.messages import AIMessage, HumanMessage

    messages = [
        HumanMessage(content="What's the weather in SF?"),
        AIMessage(content="It's always sunny in SF!"),
    ]
    mock_agent = MagicMock()
    mock_agent.get_messages = AsyncMock(return_value=messages)

    with patch("app.weather_agent.handler.get_weather_agent", return_value=mock_agent):
        response = await auth_client.get(f"/weather-agent/threads/{TEST_THREAD_ID}")

    body = response.json()
    assert "messages" in body
    assert len(body["messages"]) == 2


async def test_get_thread_history_returns_empty_messages_for_unknown_thread(
    auth_client: AsyncClient,
) -> None:
    mock_agent = MagicMock()
    mock_agent.get_messages = AsyncMock(return_value=[])

    with patch("app.weather_agent.handler.get_weather_agent", return_value=mock_agent):
        response = await auth_client.get("/weather-agent/threads/unknown-thread")

    assert response.json() == {"messages": []}
