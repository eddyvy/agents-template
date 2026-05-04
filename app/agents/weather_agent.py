# pip install -qU deepagents langchain-deepseek
from functools import lru_cache

from deepagents import create_deep_agent
from langchain_core.runnables import Runnable
from langchain_deepseek import ChatDeepSeek

from app.config import get_settings


def get_weather(city: str) -> str:
    """Get weather for a given city."""
    return f"It's always sunny in {city}!"


@lru_cache
def get_weather_agent() -> Runnable:  # type: ignore[type-arg]
    settings = get_settings()
    model = ChatDeepSeek(model="deepseek-chat", api_key=settings.deepseek_api_key)  # type: ignore[arg-type]
    return create_deep_agent(
        model=model,
        tools=[get_weather],
        system_prompt="You are a helpful assistant",
    )
