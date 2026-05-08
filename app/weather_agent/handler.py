from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
from langchain_core.messages import BaseMessage
from pydantic import BaseModel

from app.weather_agent.api import get_weather_agent

router = APIRouter(
    prefix="/weather-agent",
    tags=["weather-agent"],
)


class InvokeRequest(BaseModel):
    message: str
    thread_id: str


class InvokeResponse(BaseModel):
    response: str


@router.post("/invoke")
async def invoke_weather_agent(body: InvokeRequest, request: Request) -> InvokeResponse:
    agent = get_weather_agent(request.app)
    result = await agent.ainvoke(body.message, body.thread_id)
    return InvokeResponse(response=result)


@router.post("/stream")
async def stream_weather_agent(
    body: InvokeRequest, request: Request
) -> StreamingResponse:
    agent = get_weather_agent(request.app)

    return StreamingResponse(
        agent.astream(body.message, body.thread_id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


@router.get("/threads/{thread_id}")
async def get_thread_history(
    thread_id: str, request: Request
) -> dict[str, list[BaseMessage]]:
    agent = get_weather_agent(request.app)
    messages = await agent.get_messages(thread_id)

    return {"messages": messages}
