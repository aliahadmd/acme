# Architecture

```
┌─────────────── your computer (dev) ───────────────┐
│  make dev                                          │
│  ┌──────────────┐        ┌──────────────────────┐ │
│  │ apps/web     │ CORS / │ apps/api             │ │
│  │ TanStack     │───────▶│ FastAPI (uv)         │ │
│  │ Start :3000  │  HTTP  │ :8000                │ │
│  └──────────────┘        └──────────┬───────────┘ │
│        │  SMTP (email)   ┌──────────▼───────────┐ │
│  ┌─────▼─────┐          │ postgres (pgvector)  │ │
│  │ mailpit   │          │ seaweedfs (S3 :8333) │ │
│  │ :1025/:8025          │ redis                │ │
│  └───────────┘          └──────────────────────┘ │
│        all via compose.yaml (`make up`)           │
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

## Platform services (dev / prod)

| Concern        | Dev (compose.yaml)              | Prod (Dokploy)                          | App access                          |
| -------------- | ------------------------------- | --------------------------------------- | ----------------------------------- |
| Database       | `pgvector/pgvector:pg17`        | pgvector image as Application + volume  | `DATABASE_URL`                      |
| Vectors        | pgvector extension in the same DB | same                                  | `pgvector` python pkg, `CREATE EXTENSION vector` (migration 0002) |
| Object storage | SeaweedFS (S3 API :8333)        | SeaweedFS Application + volume          | `S3_*` via `app/services/storage.py` (provider-neutral S3) |
| Email          | Mailpit catch-all (:1025/:8025) | Your SMTP relay/MTA (see deployment.md) | `SMTP_*` via `app/services/email_service.py` |
| Cache/queues   | Redis :6379                     | Dokploy Redis resource                  | `REDIS_URL` (reserved)              |

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
