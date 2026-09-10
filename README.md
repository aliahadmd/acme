# acme

Full-stack monorepo: **FastAPI (uv)** API + **TanStack Start (React, SSR)** web,
type-safe end to end via a generated API client. Deploys to a Dokploy VPS via
GitHub Actions.

```text
apps/api            FastAPI + SQLModel + Alembic (uv, ruff, ty, pytest)
apps/web            TanStack Start + Router + Query (Vite, biome, vitest)
packages/api-client Generated TS SDK + TanStack Query options (from OpenAPI)
packages/config     Shared tsconfig
docs/               Architecture · environment matrix · deployment · ADRs
deploy/README.md    First-time Dokploy setup
```

## Quickstart

```bash
make install   # deps + local .env files (from committed examples)
make dev       # postgres/redis (docker) + api :8000 + web :3000
```

- Web: http://localhost:3000 — home page server-renders the users list.
- API docs: http://localhost:8000/docs

```bash
make check     # lint + typecheck + tests (what CI runs)
make client    # regenerate the TS client after changing the API
make migrate   # apply DB migrations (make migration m="..." to create one)
```

Read [`AGENTS.md`](./AGENTS.md) first if you're an AI agent (or a human in a
hurry): it maps the repo, the commands, and the contract pipeline.

## Dev → prod

| Stage | Where things live                                                             |
| ----- | ----------------------------------------------------------------------------- |
| Local | `.env` per app (gitignored) · infra via `compose.yaml`                        |
| CI    | lint/typecheck/test + client-drift + secret-scan on every PR                  |
| Prod  | GHCR images → Dokploy (Traefik TLS, Postgres/Redis resources) — `deploy/README.md` |
