from fastapi import FastAPI

from app.core.auth import auth_api_key_middleware
from app.core.lifespan import lifespan
from app.weather_agent.handler import router as weather_agent_router

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


app.include_router(weather_agent_router)
