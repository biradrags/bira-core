.PHONY: help install test lint typecheck check docker-up
help:
	@grep -E '^[a-z-]+:' Makefile | sed 's/:.*//'
install:
	uv sync --all-extras
docker-up:
	docker compose up -d
test:
	uv run pytest -q
lint:
	uv run ruff check src tests && uv run ruff format --check src tests
typecheck:
	uv run mypy
check: lint typecheck test
