# apps/api — FastAPI backend

## Stack & conventions

- **uv only** (`uv add`, `uv run`). Python 3.13. Deps + ruff/pytest config live in
  `pyproject.toml`.
- Endpoints: sync `def` unless you know the code is async-safe; `Annotated` DI
  (`SessionDep`); router-level `prefix`/`tags`; `response_model` + return type on every
  endpoint; **explicit camelCase `operation_id=`** — it becomes the generated client's
  function name (e.g. `listUsers` → `listUsersOptions()`).
- Layering: `routers/` (thin HTTP only) → `services/` (business logic) → `models/`
  (SQLModel tables, which double as API schemas).
- Config **only** through `app/core/config.py` (pydantic-settings). Adding a setting
  means updating `.env.example` and `docs/environments.md` in the same PR.

## Workflows

- Dev: `make dev` (or `cd apps/api && uv run fastapi dev`). Tests: `uv run pytest`
  (TestClient + in-memory sqlite — no postgres needed).
- Migration: change `app/models/` → `make migration m="description"` → **review the
  generated file** → `make migrate`.
- After any endpoint change run `make client` and keep operation_ids stable.

## File map

- `app/main.py` — app factory (CORS from settings); `app/core/config.py` — settings;
  `app/core/logging.py` — text locally, JSON when `ENVIRONMENT=production`.
- `app/db/session.py` — engine/session; `app/deps.py` — shared dependency annotations.
- `scripts/export_openapi.py` — writes the OpenAPI contract for `packages/api-client`.
- `Dockerfile` — uv multi-stage, runs `.venv/bin/fastapi run`, HEALTHCHECK `/health`.
