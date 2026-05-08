.PHONY: dev lint format types test check

dev:
	uv run fastapi dev

lint:
	uv run ruff check .

format:
	uv run ruff format .

types:
	uv run mypy app/

test:
	uv run pytest

check: lint format types test
