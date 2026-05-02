from collections.abc import AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.fixture
async def client() -> AsyncGenerator[AsyncClient]:
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac


async def test_root_status_ok(client: AsyncClient) -> None:
    response = await client.get("/")
    assert response.status_code == 200


async def test_root_response_body(client: AsyncClient) -> None:
    response = await client.get("/")
    assert response.json() == {"message": "Hello World"}


async def test_root_content_type(client: AsyncClient) -> None:
    response = await client.get("/")
    assert response.headers["content-type"] == "application/json"
