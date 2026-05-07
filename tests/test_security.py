from types import SimpleNamespace

import pytest
from fastapi import HTTPException, status

from app.security import verify_api_key


def test_verify_api_key_accepts_valid_key() -> None:
    settings = SimpleNamespace(agents_api_key="valid-key")

    verify_api_key("valid-key", settings)


@pytest.mark.parametrize("api_key", [None, "wrong-key"])
def test_verify_api_key_rejects_invalid_or_missing_key(api_key: str | None) -> None:
    settings = SimpleNamespace(agents_api_key="valid-key")

    with pytest.raises(HTTPException) as exc_info:
        verify_api_key(api_key, settings)

    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert exc_info.value.detail == "Invalid or missing API key"
