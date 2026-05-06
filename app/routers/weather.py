from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel

from app.security import verify_api_key
from app.weather_agent.api import get_weather_agent

router = APIRouter(
    prefix="/weather",
    tags=["weather"],
    dependencies=[Depends(verify_api_key)],
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
