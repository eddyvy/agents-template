# app/core/auth.py
from collections.abc import Awaitable, Callable

from fastapi import Request, Response, status
from fastapi.responses import JSONResponse

from app.settings.api import get_settings

API_KEY_HEADER = "X-AGENTS-API-KEY"
PUBLIC_PATHS = frozenset({"/health"})


async def auth_api_key_middleware(
    request: Request,
    call_next: Callable[[Request], Awaitable[Response]],
) -> Response:
    if request.url.path not in PUBLIC_PATHS:
        api_key = request.headers.get(API_KEY_HEADER)
        settings = get_settings(request.app)
        if not api_key or api_key != settings.agents_api_key:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Invalid or missing API key"},
            )
    return await call_next(request)
