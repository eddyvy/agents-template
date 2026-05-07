from collections.abc import AsyncGenerator
from unittest.mock import MagicMock

import pytest
from httpx import ASGITransport, AsyncClient

from app.app import app
from app.settings.settings import Settings

TEST_API_KEY = "test-secret-key"


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
    client.headers.update({"X-AGENTS-API-KEY": TEST_API_KEY})
    return client


# --- /health ---


async def test_health_no_auth_returns_200(client: AsyncClient) -> None:
    response = await client.get("/health")
    assert response.status_code == 200


async def test_health_response_body(client: AsyncClient) -> None:
    response = await client.get("/health")
    assert response.json() == {"status": "UP"}


async def test_health_with_auth_returns_200(auth_client: AsyncClient) -> None:
    response = await auth_client.get("/health")
    assert response.status_code == 200


# --- auth middleware ---


async def test_root_no_auth_returns_401(client: AsyncClient) -> None:
    response = await client.get("/")
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid or missing API key"}


async def test_root_wrong_key_returns_401(client: AsyncClient) -> None:
    response = await client.get("/", headers={"X-AGENTS-API-KEY": "wrong-key"})
    assert response.status_code == 401


async def test_root_correct_key_returns_200(auth_client: AsyncClient) -> None:
    response = await auth_client.get("/")
    assert response.status_code == 200


# --- / ---


async def test_root_response_body(auth_client: AsyncClient) -> None:
    response = await auth_client.get("/")
    assert response.json() == {"message": "Hello World"}


async def test_root_content_type(auth_client: AsyncClient) -> None:
    response = await auth_client.get("/")
    assert response.headers["content-type"] == "application/json"
