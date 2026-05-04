from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.agents.weather_agent import get_weather_agent
from app.security import verify_api_key

router = APIRouter(
    prefix="/weather",
    tags=["weather"],
    dependencies=[Depends(verify_api_key)],
)


class InvokeRequest(BaseModel):
    message: str


class InvokeResponse(BaseModel):
    response: str


@router.post("/invoke")
async def invoke_weather_agent(body: InvokeRequest) -> InvokeResponse:
    agent = get_weather_agent()
    result = await agent.ainvoke(
        {"messages": [{"role": "user", "content": body.message}]}
    )
    return InvokeResponse(response=result["messages"][-1].content)
