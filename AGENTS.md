# AGENTS.md — acme

Full-stack monorepo: **FastAPI (uv) API** + **TanStack Start (React, SSR) web**, kept
type-safe by a generated API client. Deploys to a Dokploy VPS via GitHub Actions.

## Golden rules

1. **Never hand-edit generated code**: `packages/api-client/src/client/**` and
   `apps/web/src/routeTree.gen.ts`. Regenerate instead (commands below).
2. **Never commit real secrets.** `.env` files are gitignored; `.env.example` files are
   the committed contract. Prod secrets live only in Dokploy's Environment tab.
3. **Every PR keeps `make check` green** (lint + typecheck + test) **and the generated
   client fresh** — CI fails on a stale client.
4. `Makefile` is the single command surface. If a command isn't there, add it rather
   than improvising.

## Map

| Path                | What                                                                   |
| ------------------- | ---------------------------------------------------------------------- |
| `apps/api`          | FastAPI + uv backend — conventions: `apps/api/AGENTS.md`               |
| `apps/web`          | TanStack Start (SSR) frontend — conventions: `apps/web/AGENTS.md`      |
| `packages/api-client` | TS SDK + TanStack Query options, GENERATED from the API's OpenAPI    |
| `packages/config`   | Shared tsconfig                                                        |
| `docs/`             | architecture, environment matrix, deployment, ADRs                     |
| `deploy/README.md`  | Step-by-step Dokploy production setup                                  |
| `compose.yaml`      | LOCAL DEV infra only (postgres, redis, mailpit) — no app code          |

## Commands (`make help` lists all)

| Do                        | Run                                                       |
| ------------------------- | --------------------------------------------------------- |
| Install everything        | `make install` (creates `.env` from examples, pnpm + uv)  |
| Dev servers + infra       | `make dev` → api :8000 · web :3000 · postgres :5432       |
| All tests                 | `make test` (api: pytest · web: vitest)                   |
| Lint / format / typecheck | `make lint` / `make format` / `make typecheck`            |
| Everything CI runs        | `make check`                                              |
| Regenerate API client     | `make client` (exports OpenAPI → TS client + query hooks) |
| DB migrations             | `make migrate` · new: `make migration m="description"`    |
| Build Docker images       | `make docker-build-api` / `make docker-build-web`         |

## The contract pipeline (how API changes reach the web)

1. Change `apps/api` (router → service → model). Set a stable camelCase
   `operation_id=` on every endpoint — it becomes the generated function name.
2. Run `make client`: `scripts/export_openapi.py` writes
   `packages/api-client/openapi.json` (committed — PR diffs show the contract),
   then hey-api regenerates the typed SDK **and TanStack Query options**.
3. Consume in web: `useQuery(listUsersOptions())`,
   `context.queryClient.ensureQueryData(...)` in loaders.
4. CI regenerates and fails if `packages/api-client` was left stale.

## Environments (dev → CI → prod)

- **Local**: `.env` files (gitignored, copied from `.env.example` by `make install`)
  per app; infra via `compose.yaml` + root `.env`.
- **CI**: secrets from GitHub Environments; client-drift and gitleaks checks run on
  every PR.
- **Prod**: secrets only in Dokploy Environment tabs (per service).
  The full variable matrix — which var comes from where at each stage — is
  `docs/environments.md`. Update it whenever you add or change a variable.

## Deploy

`main` → GitHub Actions builds both images → GHCR → triggers Dokploy deploy → Traefik
routes + TLS. Runbooks: `deploy/README.md` (first-time setup) and `docs/deployment.md`
(topology, env vars, rollback).
