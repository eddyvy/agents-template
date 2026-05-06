from collections.abc import AsyncGenerator
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from app.app import app
from app.settings.settings import Settings, get_settings

TEST_API_KEY = "test-secret-key"
TEST_THREAD_ID = "test-thread-123"


@pytest.fixture
def mock_settings() -> MagicMock:
    settings = MagicMock(spec=Settings)
    settings.agents_api_key = TEST_API_KEY
    return settings


@pytest.fixture
async def auth_client(mock_settings: MagicMock) -> AsyncGenerator[AsyncClient]:
    app.dependency_overrides[get_settings] = lambda: mock_settings
    with (
        patch("app.app.get_settings", return_value=mock_settings),
        patch("app.database.init_db", new_callable=AsyncMock),
        patch("app.routers.weather.get_checkpointer", return_value=MagicMock()),
    ):
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as ac:
            ac.headers.update({"X-AGENTS-API-KEY": TEST_API_KEY})
            yield ac
    app.dependency_overrides.clear()


def make_mock_agent(response_content: str) -> MagicMock:
    mock_message = MagicMock()
    mock_message.content = response_content
    mock_agent = MagicMock()
    mock_agent.ainvoke = AsyncMock(return_value={"messages": [mock_message]})
    return mock_agent


# --- POST /weather/invoke ---


async def test_invoke_no_auth_returns_401() -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.post(
            "/weather/invoke",
            json={"message": "hello", "thread_id": TEST_THREAD_ID},
        )
        assert response.status_code == 401


async def test_invoke_returns_200(auth_client: AsyncClient) -> None:
    mock_agent = make_mock_agent("It's always sunny in SF!")

    with patch("app.routers.weather.get_weather_agent", return_value=mock_agent):
        response = await auth_client.post(
            "/weather/invoke",
            json={"message": "What's the weather in SF?", "thread_id": TEST_THREAD_ID},
        )

    assert response.status_code == 200


async def test_invoke_returns_agent_response(auth_client: AsyncClient) -> None:
    mock_agent = make_mock_agent("It's always sunny in SF!")

    with patch("app.routers.weather.get_weather_agent", return_value=mock_agent):
        response = await auth_client.post(
            "/weather/invoke",
            json={"message": "What's the weather in SF?", "thread_id": TEST_THREAD_ID},
        )

    assert response.json() == {"response": "It's always sunny in SF!"}


async def test_invoke_missing_message_returns_422(auth_client: AsyncClient) -> None:
    response = await auth_client.post("/weather/invoke", json={})
    assert response.status_code == 422
