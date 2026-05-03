from app.main import health, root


async def test_root_returns_message() -> None:
    result = await root()
    assert result == {"message": "Hello World"}


async def test_root_return_type() -> None:
    result = await root()
    assert isinstance(result, dict)
    assert all(isinstance(k, str) and isinstance(v, str) for k, v in result.items())


async def test_health_returns_status() -> None:
    result = await health()
    assert result == {"status": "UP"}


async def test_health_return_type() -> None:
    result = await health()
    assert isinstance(result, dict)
    assert all(isinstance(k, str) and isinstance(v, str) for k, v in result.items())
