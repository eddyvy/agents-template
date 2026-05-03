from typing import Annotated

from fastapi import Depends, HTTPException, Security, status
from fastapi.security import APIKeyHeader

from app.config import Settings, get_settings

_api_key_header = APIKeyHeader(name="X-AGENTS-API-KEY", auto_error=False)


def verify_api_key(
    api_key: Annotated[str | None, Security(_api_key_header)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> None:
    if not api_key or api_key != settings.agents_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key",
        )
