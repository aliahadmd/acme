# 0002: TanStack Start (SSR) instead of a Vite SPA

Date: 2026-09-11
Status: accepted

## Context

The web app uses TanStack Router + Query. TanStack Start adds SSR, streaming
and server functions on top of the same primitives; it was RC (API-stable) at
scaffold time. A plain Vite SPA would deploy as static files and could even be
served by FastAPI, but loses server-side data loading and SEO.

## Decision

Use TanStack Start with its default Node/server build (`dist/server/server.js`
served by srvx) as a dedicated container.

## Consequences

- +1 container in prod (Node SSR server); static assets served by srvx.
- Loaders run on the server: `API_BASE_URL` (internal) vs `VITE_API_BASE_URL`
  (public) split in `src/lib/env.ts`.
- If Start reaches v1 with breaking changes, upgrade cost is limited to
  `apps/web`; the contract layer is unaffected.
