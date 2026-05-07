import json
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

from fastapi import FastAPI, Request, Response

from app.core.auth import API_KEY_HEADER, auth_api_key_middleware


def make_request(
    *,
    app: FastAPI,
    path: str,
    headers: dict[str, str] | None = None,
) -> Request:
    raw_headers = [
        (key.lower().encode("latin-1"), value.encode("latin-1"))
        for key, value in (headers or {}).items()
    ]
    scope = {
        "type": "http",
        "method": "GET",
        "path": path,
        "headers": raw_headers,
        "query_string": b"",
        "server": ("testserver", 80),
        "client": ("127.0.0.1", 12345),
        "scheme": "http",
        "http_version": "1.1",
        "app": app,
    }
    return Request(scope)


async def test_public_path_skips_authentication() -> None:
    app = FastAPI()
    request = make_request(app=app, path="/health")
    expected_response = Response(status_code=204)
    call_next = AsyncMock(return_value=expected_response)

    with patch("app.core.auth.get_settings") as get_settings_mock:
        response = await auth_api_key_middleware(request, call_next)

    assert response is expected_response
    call_next.assert_awaited_once_with(request)
    get_settings_mock.assert_not_called()


async def test_private_path_without_api_key_returns_401() -> None:
    app = FastAPI()
    request = make_request(app=app, path="/")
    call_next = AsyncMock(return_value=Response(status_code=204))
    settings = SimpleNamespace(agents_api_key="test-secret")

    with patch(
        "app.core.auth.get_settings", return_value=settings
    ) as get_settings_mock:
        response = await auth_api_key_middleware(request, call_next)

    assert response.status_code == 401
    assert json.loads(response.body.decode("utf-8")) == {
        "detail": "Invalid or missing API key"
    }
    call_next.assert_not_awaited()
    get_settings_mock.assert_called_once_with(app)


async def test_private_path_with_wrong_api_key_returns_401() -> None:
    app = FastAPI()
    request = make_request(
        app=app,
        path="/",
        headers={API_KEY_HEADER: "wrong-secret"},
    )
    call_next = AsyncMock(return_value=Response(status_code=204))
    settings = SimpleNamespace(agents_api_key="test-secret")

    with patch("app.core.auth.get_settings", return_value=settings):
        response = await auth_api_key_middleware(request, call_next)

    assert response.status_code == 401
    assert json.loads(response.body.decode("utf-8")) == {
        "detail": "Invalid or missing API key"
    }
    call_next.assert_not_awaited()


async def test_private_path_with_valid_api_key_calls_next() -> None:
    app = FastAPI()
    request = make_request(
        app=app,
        path="/",
        headers={API_KEY_HEADER: "test-secret"},
    )
    expected_response = Response(status_code=204)
    call_next = AsyncMock(return_value=expected_response)
    settings = SimpleNamespace(agents_api_key="test-secret")

    with patch("app.core.auth.get_settings", return_value=settings):
        response = await auth_api_key_middleware(request, call_next)

    assert response is expected_response
    call_next.assert_awaited_once_with(request)
