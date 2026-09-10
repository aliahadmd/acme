# 0001: pnpm monorepo with apps/ and packages/

Date: 2026-09-11
Status: accepted

## Context

One backend (FastAPI) and one frontend (TanStack Start) evolve together. The
frontend depends on the backend's API shape; two repos would need versioned
client packages or manual syncing, and AI agents would lose cross-cutting
context.

## Decision

Single repository: `apps/api`, `apps/web`, `packages/api-client`,
`packages/config`; pnpm workspaces + Turborepo orchestrate JS, turbo tasks wrap
the uv-based API. The OpenAPI contract is generated into a committed package
(`packages/api-client/openapi.json` + generated client).

## Consequences

- One PR changes API + client + UI atomically; CI enforces the client is fresh.
- Docker builds for `web` need the repo root as build context (workspace deps).
- Repo clone is slightly heavier; acceptable for a two-app product.
