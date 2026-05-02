from app.main import root


async def test_root_returns_message() -> None:
    result = await root()
    assert result == {"message": "Hello World"}


async def test_root_return_type() -> None:
    result = await root()
    assert isinstance(result, dict)
    assert all(isinstance(k, str) and isinstance(v, str) for k, v in result.items())
