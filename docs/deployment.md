# Deployment (production topology)

Runtime: a VPS running [Dokploy](https://dokploy.com). Dokploy gives you
Traefik (routing + automatic TLS), per-service env management, and database
resources. This repo deploys **two applications**, a **Postgres+pgvector
database**, an **S3-compatible object store**, and optionally **Redis**:

| Service    | Source                        | Port | Domain        | Notes                                                                        |
| ---------- | ----------------------------- | ---- | ------------- | ---------------------------------------------------------------------------- |
| `api`      | GHCR image (built by CI)      | 8000 | `api.<domain>` | Runs `fastapi run`; HEALTHCHECK `/health`                                   |
| `web`      | GHCR image (built by CI)      | 3000 | `<domain>`    | Node SSR server (srvx); HEALTHCHECK `/`                                      |
| `postgres` | `pgvector/pgvector:pg17` image | 5432 | internal only | Application + volume — NOT Dokploy's stock Postgres (no pgvector extension) |
| `s3`       | `chrislusf/seaweedfs:4.46`    | 8333 | `s3.<domain>` | Application + volume; S3 API. MinIO is archived/unmaintained — avoid         |
| `redis`    | Dokploy Redis resource        | —    | —             | Optional (reserved for caching/queues)                                       |

**Why CI-built images?** Builds run on GitHub's machines (VPS stays light), the
deployed image is always exactly what CI tested, and the git SHA is the deploy
unit (clean rollbacks). A build-on-VPS fallback exists — see
`deploy/README.md`.

## Data flow in prod

- Browser → `https://<domain>` (web) and `https://api.<domain>` (API, CORS
  allowed).
- Web SSR → API via the **internal** docker network: `API_BASE_URL=http://api:8000`.
- API → Postgres via the pgvector Application's internal connection string.
- API → S3 via `S3_ENDPOINT=http://s3:8333` (internal); presigned URLs handed
  to browsers use the public `https://s3.<domain>`.
- API → SMTP relay/MTA via `SMTP_*` (see Email below).

## Email

The API sends via plain SMTP (`app/services/email_service.py`) — the mail
server is a deployment choice, not code. Options, in order of practicality:

1. **SMTP relay with API credentials** (recommended): Resend, Postmark, Amazon
   SES — point `SMTP_*` at their SMTP endpoints. No deliverability burden.
2. **Self-hosted MTA on a separate VPS**: [Stalwart](https://stalw.art/)
   (modern, all-in-one) or [Postal](https://github.com/postalserver/postal)
   (transactional-focused). Requires a dedicated IP, rDNS/PTR, SPF + DKIM +
   DMARC records, and a provider that doesn't block port 25 (Hetzner blocks it
   by default — request an unblock).
3. **Never** run the MTA on the app VPS next to Dokploy — mail servers and app
   servers have opposite IP-reputation requirements.

## Environment variables

See `docs/environments.md` for the complete matrix. In short: set
`DATABASE_URL`, `CORS_ORIGINS`, `ENVIRONMENT=production`, `LOG_LEVEL`,
`S3_*`, and `SMTP_*` on the api; `API_BASE_URL=http://api:8000` and
`VITE_API_BASE_URL` on the web app.
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
