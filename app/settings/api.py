from fastapi import FastAPI, Request

from app.settings.settings import Settings


def setup_settings(app: FastAPI):
    settings = Settings()
    app.state.settings = settings


def get_settings(app: FastAPI) -> Settings:
    return app.state.settings


def get_settings_from_request(request: Request) -> Settings:
    return request.app.state.settings
