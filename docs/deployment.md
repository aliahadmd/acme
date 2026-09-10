# Deployment (production topology)

Runtime: a VPS running [Dokploy](https://dokploy.com). Dokploy gives you
Traefik (routing + automatic TLS), per-service env management, and database
resources. This repo deploys **two applications** plus **databases**:

| Service  | Source                     | Port | Domain           | Notes                                |
| -------- | -------------------------- | ---- | ---------------- | ------------------------------------ |
| `api`    | GHCR image (built by CI)   | 8000 | `api.<domain>`   | Runs `fastapi run`; HEALTHCHECK `/health` |
| `web`    | GHCR image (built by CI)   | 3000 | `<domain>`       | Node SSR server (srvx); HEALTHCHECK `/`   |
| Postgres | Dokploy database resource  | —    | —                | Backup schedules configured in Dokploy |
| Redis    | Dokploy database resource  | —    | —                | Optional (reserved for caching/queues)  |

**Why CI-built images?** Builds run on GitHub's machines (VPS stays light), the
deployed image is always exactly what CI tested, and the git SHA is the deploy
unit (clean rollbacks). A build-on-VPS fallback exists — see
`deploy/README.md`.

## Data flow in prod

- Browser → `https://<domain>` (web) and `https://api.<domain>` (API, CORS
  allowed).
- Web SSR → API via the **internal** docker network: `API_BASE_URL=http://api:8000`.
- API → Postgres via the Dokploy-provided internal connection string.

## Environment variables

See `docs/environments.md` for the complete matrix. In short: set
`DATABASE_URL`, `CORS_ORIGINS`, `ENVIRONMENT=production`, `LOG_LEVEL` on the
api; `API_BASE_URL=http://api:8000` and `VITE_API_BASE_URL` on the web app.
`VITE_API_BASE_URL` is inlined at image build time — if it changes, redeploy
(the CI build receives it as a build arg; keep it stable or rebuild).

## Migrations

Add a **pre-deploy command** on the api application:

```
/app/.venv/bin/alembic upgrade head
```

Migrations run before the new container starts serving traffic.

## Rollback

Redeploy a previous commit: re-run the deploy workflow with the desired SHA
(`gh workflow run deploy` after `git checkout <sha> && git push -f` is **not**
recommended — instead run the build job against the old tag in CI, or use
`docker build-push-action` inputs). Dokploy also keeps previous application
versions in its UI; prefer fixing forward, rollbacks via SHA-tagged images.

## Monitoring

- api: `https://api.<domain>/health` (also used by the container HEALTHCHECK).
- web: `https://<domain>/` (HEALTHCHECK) and `/health` (shows API status).
- Logs: Dokploy deployment + container logs views.
