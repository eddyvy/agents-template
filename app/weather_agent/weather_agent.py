from deepagents import create_deep_agent
from langchain_deepseek import ChatDeepSeek
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver

from app.settings.settings import Settings


def get_weather(city: str) -> str:
    """Get weather for a given city."""
    return f"It's always sunny in {city}!"


class WeatherAgent:
    def __init__(self, settings: Settings, checkpointer: AsyncPostgresSaver):
        model = ChatDeepSeek(model="deepseek-chat", api_key=settings.deepseek_api_key)
        self.agent = create_deep_agent(
            model=model,
            tools=[get_weather],
            system_prompt="You are a helpful assistant",
            checkpointer=checkpointer,
        )

    async def ainvoke(self, message: str, thread_id: str) -> str:
        result = await self.agent.ainvoke(
            {"messages": [{"role": "user", "content": message}]},
            config={"configurable": {"thread_id": thread_id}},
        )
        return result["messages"][-1].content
