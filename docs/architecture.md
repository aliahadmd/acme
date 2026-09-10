# Architecture

```
┌─────────────── your computer (dev) ───────────────┐
│  make dev                                          │
│  ┌──────────────┐        ┌──────────────────────┐ │
│  │ apps/web     │ CORS / │ apps/api             │ │
│  │ TanStack     │───────▶│ FastAPI (uv)         │ │
│  │ Start :3000  │  HTTP  │ :8000                │ │
│  └──────────────┘        └──────────┬───────────┘ │
│                          ┌──────────▼───────────┐ │
│  compose.yaml (infra)    │ postgres · redis ·   │ │
│  docker compose up -d ──▶│ mailpit              │ │
│                          └──────────────────────┘ │
└────────────────────────────────────────────────────┘

┌────────────── production (Dokploy VPS) ──────────────────────┐
│                    Traefik (TLS via Let's Encrypt)            │
│   you.com ──▶ web container (Node SSR, :3000)                 │
│   api.you.com ─▶ api container (FastAPI, :8000)               │
│                      │ internal network                       │
│              ┌───────▼──────────┐                             │
│              │ API_BASE_URL=    │   web SSR fetches the API  │
│              │ http://api:8000  │   over the docker network   │
│              └──────────────────┘                             │
│   Postgres + Redis run as Dokploy database resources          │
└───────────────────────────────────────────────────────────────┘

GitHub Actions (on main): build images ──▶ GHCR ──▶ trigger Dokploy deploy
```

## Layers

| Package               | Role                                                              |
| --------------------- | ----------------------------------------------------------------- |
| `apps/api`            | HTTP layer (routers) → business logic (services) → data (models)  |
| `apps/web`            | Routes (file-based) → loaders (SSR prefetch) → components (hooks) |
| `packages/api-client` | Generated, committed TS SDK + query options — never hand-edited   |

## The contract pipeline

`apps/api` FastAPI app → `openapi.json` (committed at
`packages/api-client/openapi.json`) → `@hey-api/openapi-ts` → typed SDK **and**
TanStack Query options/hooks in `packages/api-client/src/client`.

- Endpoints declare stable camelCase `operation_id`s; they become the generated
  function names (`listUsers` → `listUsersOptions()`).
- `packages/api-client/openapi.json` is committed so every PR diff shows contract
  changes; CI regenerates and fails on drift.

## Request flow (SSR)

1. Browser hits a route → Start runs the loader **on the Node server**.
2. Loader calls `context.queryClient.ensureQueryData(listUsersOptions())` → the
   generated client fetches `API_BASE_URL` (internal docker URL in prod).
3. HTML streams out with data already rendered; the query cache dehydrates into
   the page and rehydrates in the browser (no client refetch).
4. Subsequent client interactions hit `VITE_API_BASE_URL` (public API domain)
   directly, with CORS configured on the API via `CORS_ORIGINS`.

## Deliberate boundaries

- Web never hand-writes fetch calls or API types — always the generated client.
- API routers never contain business logic — always services.
- Env vars are read in exactly one place per app (`app/core/config.py`,
  `src/lib/env.ts`).
- `compose.yaml` is dev-infra only; production topology lives in Dokploy
  (`docs/deployment.md`), not in compose files.
