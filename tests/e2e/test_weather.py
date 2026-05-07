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


# --- POST /weather/invoke ---


async def test_invoke_no_auth_returns_401(client: AsyncClient) -> None:
    response = await client.post(
        "/weather/invoke",
        json={"message": "hello", "thread_id": TEST_THREAD_ID},
    )
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid or missing API key"}


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


async def test_invoke_missing_thread_id_returns_422(auth_client: AsyncClient) -> None:
    response = await auth_client.post(
        "/weather/invoke",
        json={"message": "What's the weather in SF?"},
    )
    assert response.status_code == 422
