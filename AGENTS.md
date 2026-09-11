# Agent Guide

## Setup and Commands

- Use Python `3.13.x` and `uv`; install the locked environment with `uv sync`.
- The ASGI entrypoint is `main:app`; run the development server with `uv run uvicorn main:app --reload`.
- Run tests with `uv run pytest`; integration tests require `TEST_DATABASE_URL` pointing to a dedicated PostgreSQL database whose name contains `test`. A syntax-only check is `uv run python -m compileall apps core migrations main.py`.
- There is no configured lint, formatter, or typecheck tool in `pyproject.toml`.

## Configuration

- Settings load `.env` using case-sensitive names. Development requires `ENVIRONMENT=development`, `DB__PASSWORD`, and `DB__NAME`; start from `.env.example`.
- Development uses local storage under `media/`. Production code requires `STORAGE_KEY`, `STORAGE_SECRET`, and `STORAGE_BUCKET` for Google Cloud Storage. `README.md` and `.env.example` still document `GCS_*` names, so trust `core/settings/production.py` and `core/storage/base.py` when configuring the app.
- `.env` files are ignored by git; do not commit credentials. Replace the placeholder `SECRET_KEY` before any real deployment.

## Structure

- `main.py` creates the FastAPI app and imports the users routers. Feature code is under `apps/users` and `apps/optic`; shared settings, database, auth, and storage code is under `core/`.
- Importing `core.database` calls `load_models()`, which registers both feature model modules for SQLAlchemy relationships and Alembic autogeneration.

## Database

- Alembic uses the async PostgreSQL URL assembled from application settings in `migrations/env.py`; migration scripts live in `migrations/versions/` and the script location is configured in `pyproject.toml`.
- With a reachable configured PostgreSQL database, apply migrations with `uv run alembic upgrade head`. Generate one with `uv run alembic revision --autogenerate -m "description"`, then inspect the generated revision before applying it.
