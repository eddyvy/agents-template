from fastapi import FastAPI

import app.routers.weather as weather
from app.core.auth import auth_api_key_middleware
from app.core.lifespan import lifespan

app = FastAPI(lifespan=lifespan)

PUBLIC_PATHS = {"/health"}


# Middleware for API key authentication
app.middleware("http")(auth_api_key_middleware)


@app.get("/")
async def root() -> dict[str, str]:
    return {"message": "Hello World"}


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "UP"}


app.include_router(weather.router)
