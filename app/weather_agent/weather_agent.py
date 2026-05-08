from collections.abc import AsyncGenerator

from deepagents import create_deep_agent
from langchain.agents.middleware.types import (
    AgentState,
    _InputAgentState,
    _OutputAgentState,
)
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_deepseek import ChatDeepSeek
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from langgraph.graph.state import CompiledStateGraph
from langgraph.types import GraphOutput

from app.settings.settings import Settings


def get_weather(city: str) -> str:
    """Get weather for a given city."""
    return f"It's always sunny in {city}!"


class WeatherAgent:
    def __init__(self, settings: Settings, checkpointer: AsyncPostgresSaver):
        model = ChatDeepSeek(
            model_name="deepseek-v4-pro", api_key=settings.deepseek_api_key
        )
        self.model = model
        self.checkpointer = checkpointer
        self.agent: CompiledStateGraph[
            AgentState[BaseMessage],
            None,
            _InputAgentState,
            _OutputAgentState[BaseMessage],
        ] = create_deep_agent(
            model=model,
            tools=[get_weather],
            system_prompt="You are a helpful assistant",
            checkpointer=checkpointer,
        )

    async def ainvoke(self, message: str, thread_id: str) -> str:
        input_state: _InputAgentState = {
            "messages": [HumanMessage(content=message)],
        }
        result: GraphOutput[_OutputAgentState[BaseMessage]] = await self.agent.ainvoke(
            input=input_state,
            config={"configurable": {"thread_id": thread_id}},
            version="v2",
        )
        messages = result.value.get("messages", [])
        if not messages or len(messages) == 0:
            return ""

        return str(messages[-1].content)

    async def astream(self, message: str, thread_id: str) -> AsyncGenerator[str]:
        input_state: _InputAgentState = {
            "messages": [HumanMessage(content=message)],
        }
        async for event in self.agent.astream(
            input=input_state,
            config={"configurable": {"thread_id": thread_id}},
            version="v2",
            stream_mode="messages",
        ):
            yield f"data: {str(event)}\n\n"

    async def get_messages(self, thread_id: str) -> list[BaseMessage]:
        state = await self.agent.aget_state(
            config={"configurable": {"thread_id": thread_id}}
        )
        messages: list[BaseMessage] = state.values.get("messages", [])
        return messages
