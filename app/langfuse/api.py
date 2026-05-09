from typing import cast

from fastapi import FastAPI
from langfuse import Langfuse
from langfuse.langchain import CallbackHandler

from app.settings.api import get_settings


def setup_langfuse(app: FastAPI) -> None:
    settings = get_settings(app)

    langfuse = Langfuse(
        public_key=settings.langfuse_public_key,
        secret_key=settings.langfuse_secret_key,
        host=settings.langfuse_base_url,
    )

    if langfuse.auth_check():
        print("Langfuse client is authenticated and ready!")
    else:
        print("Authentication failed. Please check your credentials and host.")

    langfuse_handler = CallbackHandler()

    app.state.langfuse_client = langfuse
    app.state.langfuse_handler = langfuse_handler


def get_langfuse_client(app: FastAPI) -> Langfuse:
    return cast(Langfuse, app.state.langfuse_client)


def get_langfuse_handler(app: FastAPI) -> CallbackHandler:
    return cast(CallbackHandler, app.state.langfuse_handler)
