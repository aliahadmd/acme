# Environment matrix

Three stages, three sources of truth. **Rule:** every env var appears in an
`.env.example` (committed contract) and in this matrix. Real values are never
committed.

| Variable            | App | Local dev                              | CI                    | Prod (Dokploy)                          |
| ------------------- | --- | -------------------------------------- | --------------------- | --------------------------------------- |
| `DATABASE_URL`      | api | `apps/api/.env` (→ compose postgres)   | not needed            | Postgres (pgvector) Application URL     |
| `CORS_ORIGINS`      | api | `apps/api/.env` (`http://localhost:3000`) | not needed          | Public web domain(s), comma-separated   |
| `ENVIRONMENT`       | api | `apps/api/.env` = `local`              | not needed            | `production` (switches logging to JSON) |
| `LOG_LEVEL`         | api | `apps/api/.env` = `INFO`               | not needed            | `INFO`                                  |
| `REDIS_URL`         | api | `apps/api/.env` (optional)             | not needed            | Dokploy Redis resource URL              |
| `S3_ENDPOINT`       | api | `apps/api/.env` = `http://localhost:8333` | not needed          | `http://s3:8333` (internal) or `https://s3.<domain>` |
| `S3_ACCESS_KEY`     | api | `apps/api/.env` (dev: `acme`)          | not needed            | Real key from your S3 service           |
| `S3_SECRET_KEY`     | api | `apps/api/.env` (dev only)             | not needed            | Real secret (Dokploy env)               |
| `S3_BUCKET`         | api | `apps/api/.env` = `acme-dev`           | not needed            | e.g. `acme-prod`                        |
| `SMTP_HOST`         | api | `apps/api/.env` = `localhost` (Mailpit) | not needed           | Your MTA / relay host                   |
| `SMTP_PORT`         | api | `apps/api/.env` = `1025`               | not needed            | `587` (submission) typically            |
| `SMTP_USER` / `SMTP_PASSWORD` | api | unset                        | not needed            | Relay credentials (Dokploy env)         |
| `SMTP_FROM`         | api | `apps/api/.env` = `dev@acme.local`     | not needed            | A domain you own (SPF-aligned!)         |
| `SMTP_USE_TLS`      | api | `false`                                | not needed            | `true`                                  |
| `VITE_API_BASE_URL` | web | `apps/web/.env` = `http://localhost:8000` | not needed          | `https://api.<your-domain>` (inlined at BUILD time) |
| `API_BASE_URL`      | web | `apps/web/.env` = `http://localhost:8000` | not needed          | `http://api:8000` (internal, runtime)   |
| `POSTGRES_*`        | compose | root `.env` (dev infra passwords/ports) | not needed        | — (Postgres runs as an Application, see deployment) |
| `DOKPLOY_URL`       | CI  | —                                      | GitHub secret         | Dokploy API base URL                    |
| `DOKPLOY_TOKEN`     | CI  | —                                      | GitHub secret         | Dokploy API token                       |
| `DOKPLOY_API_APP_ID` / `DOKPLOY_WEB_APP_ID` | CI | — | GitHub secrets | Application ids from Dokploy            |

## Security rules

1. `.env` files are gitignored; only `.env.example` files are committed. They
   contain comments and safe defaults, never real secrets.
2. `VITE_*` vars are **inlined into the public JS bundle at build time** — treat
   them as public. Server-only values use no prefix and are read at runtime
   (`API_BASE_URL`).
3. Prod secrets are set per service in Dokploy's **Environment** tab. Rotate
   them there; nothing needs to change in the repo.
4. gitleaks runs in CI to catch accidental secret commits.
5. In prod, the web SSR server talks to the API over the internal docker
   network (`http://api:8000`) — the public API URL is only for browsers.
6. `S3_ACCESS_KEY`/`S3_SECRET_KEY` and `SMTP_PASSWORD` are credentials —
   generate fresh values for prod; the dev defaults in `.env.example` are for
   the local, non-exposed containers only.

## Adding a variable (checklist)

1. Add it to the app's settings module (`app/core/config.py` or `src/lib/env.ts`).
2. Add it — with a comment — to the app's `.env.example`.
3. Add a row to this matrix.
4. Set the real value in Dokploy (prod) and locally in `.env`.
