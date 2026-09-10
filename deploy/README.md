# Deploying to the Dokploy VPS — first-time setup

Step-by-step runbook. Topology and env-var reference: `docs/deployment.md`.
Do this once; after that, pushing to `main` deploys automatically.

## 0. Prerequisites

- A VPS with Dokploy installed (https://dokploy.com/docs).
- A DNS zone you control: `api.<domain>` and `<domain>` A/AAAA records → VPS IP.
- A GitHub repo for this project (CI workflows live in `.github/workflows/`).

## 1. Databases (Dokploy → Databases → Create)

1. **Postgres** — create it, note the internal connection string, and convert it
   to SQLAlchemy format:
   `postgresql+psycopg://<user>:<password>@<host>:5432/<db>`
   (host is the database's service name inside Dokploy's network).
2. **Redis** (optional) — create it; note the internal URL.

## 2. GHCR registry access (Dokploy → Docker Registries)

CI pushes private images to `ghcr.io/<org>/<repo>`. Add a registry entry in
Dokploy with a GitHub username + a PAT (classic) that has `read:packages`.

## 3. Applications (Dokploy → Applications → Create)

Create two applications of type **Docker Image** (source: the GHCR images):

### api
- Image: `ghcr.io/<org>/<repo>/api:main`
- Deploy URL (if asked): `https://api.<domain>`
- **Domains**: add `api.<domain>`, port `8000`, enable HTTPS (Let's Encrypt).
- **Environment**:
  - `DATABASE_URL=postgresql+psycopg://…` (from step 1)
  - `CORS_ORIGINS=https://<domain>`
  - `ENVIRONMENT=production`
  - `LOG_LEVEL=INFO`
- **Advanced → Pre-deploy command**: `/app/.venv/bin/alembic upgrade head`
- Health check path: `/health`

### web
- Image: `ghcr.io/<org>/<repo>/web:main`
- **Domains**: add `<domain>`, port `3000`, enable HTTPS.
- **Environment**:
  - `API_BASE_URL=http://api:8000` (internal! browsers never use this)
  - `VITE_API_BASE_URL=https://api.<domain>`
- Health check path: `/`

> `VITE_API_BASE_URL` is inlined at **build** time. It lives in
> `.github/workflows/deploy.yml` as a build arg — change it there if the API
> domain changes, then re-deploy.

Note both **application IDs** (visible in the UI/API) for step 4.

## 4. GitHub secrets & variables (repo → Settings → Secrets and variables → Actions)

Secrets:

| Secret               | Value                                    |
| -------------------- | ---------------------------------------- |
| `DOKPLOY_URL`        | `https://<dokploy-host>` (no slash)      |
| `DOKPLOY_TOKEN`      | Dokploy → Profile → API token            |
| `DOKPLOY_API_APP_ID` | api application id                       |
| `DOKPLOY_WEB_APP_ID` | web application id                       |

Variables (the public API URL inlined into the web bundle at build time):

| Variable           | Value                       |
| ------------------ | --------------------------- |
| `PUBLIC_API_URL`   | `https://api.<domain>`      |

## 5. First deploy

```
git remote add origin git@github.com:<org>/<repo>.git
git push -u origin main
```

`Deploy` workflow: builds both images → pushes to GHCR → calls Dokploy's deploy
API for each application. Watch progress in GitHub Actions and Dokploy's
deployment logs.

## 6. Verify

- `curl https://api.<domain>/health` → `{"status":"ok","environment":"production"}`
- Open `https://<domain>` → home page lists users (server-rendered).
- `https://<domain>/health` → shows API status from inside the page.

## Fallback: build on the VPS (no CI)

If you'd rather have Dokploy build from the repo: create each application as
**Dockerfile** source with **build context = repository root** and
**Dockerfile path** `apps/api/Dockerfile` / `apps/web/Dockerfile`, connect the
GitHub provider with watch paths (`apps/api/**` / `apps/web/**` +
`packages/**`), and skip step 4. Trade-offs in `docs/decisions/0003-ghcr-dokploy.md`.
