from collections.abc import Awaitable, Callable

from fastapi import FastAPI, Request, Response, status
from fastapi.responses import JSONResponse

import app.routers.weather as weather
from app.core.lifespan import lifespan
from app.settings.api import get_settings

app = FastAPI(lifespan=lifespan)

PUBLIC_PATHS = {"/health"}


@app.middleware("http")
async def api_key_middleware(
    request: Request,
    call_next: Callable[[Request], Awaitable[Response]],
) -> Response:
    if request.url.path not in PUBLIC_PATHS:
        api_key = request.headers.get("X-AGENTS-API-KEY")
        settings = get_settings(request.app)
        if not api_key or api_key != settings.agents_api_key:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Invalid or missing API key"},
            )
    return await call_next(request)


@app.get("/")
async def root() -> dict[str, str]:
    return {"message": "Hello World"}


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "UP"}


app.include_router(weather.router)
