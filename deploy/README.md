# Deploying to the Dokploy VPS — first-time setup

Step-by-step runbook. Topology and env-var reference: `docs/deployment.md`.
Do this once; after that, pushing to `main` deploys automatically.

## 0. Prerequisites

- A VPS with Dokploy installed (https://dokploy.com/docs).
- A DNS zone you control: `api.<domain>` and `<domain>` A/AAAA records → VPS IP.
- A GitHub repo for this project (CI workflows live in `.github/workflows/`).

## 1. Postgres + pgvector (Dokploy → Applications → Create)

⚠️ Dokploy's stock **Database** resource is plain Postgres — **no pgvector**.
Run the pgvector image as an Application instead:

- Source: Docker image `pgvector/pgvector:pg17` (pin the tag)
- **Volumes**: add a volume → mount path `/var/lib/postgresql/data`
- **Environment**: `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`
  (generate strong values; note them for step 4)
- No domain — internal network only. The internal connection string for the
  api is:
  `postgresql+psycopg://<user>:<password>@<service-name>:5432/<db>`
  (`<service-name>` is the application's name inside Dokploy's network).

### Optional: Redis

Dokploy → Databases → Redis (stock resource is fine — no extensions needed).

## 2. Object storage: SeaweedFS (Dokploy → Applications → Create)

MinIO is archived/unmaintained — use SeaweedFS (Apache-2.0, active):

- Source: Docker image `chrislusf/seaweedfs:4.46` (pin the tag)
- **Command**:
  `server -dir=/data -volume.max=0 -master.volumeSizeLimitMB=10240 -filer -s3 -s3.port=8333`
- **Volumes**: volume → `/data` (this holds all objects — size it well)
- **Domains**: `s3.<domain>` → port `8333`, HTTPS on
- **Authentication**: mount an `s3.json` identities file (Dokploy → Advanced →
  File mounts) and add `-s3.config=/etc/seaweedfs/s3.json` to the command —
  see `docker/seaweedfs/s3.json` in the repo for the format. Generate a strong
  access/secret key; note them for step 4.
- Internal endpoint for the api: `http://<service-name>:8333`

## 3. GHCR registry access (Dokploy → Docker Registries)

CI pushes private images to `ghcr.io/<org>/<repo>`. Add a registry entry in
Dokploy with a GitHub username + a PAT (classic) that has `read:packages`.

## 4. Applications (Dokploy → Applications → Create)

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
  - `S3_ENDPOINT=http://<seaweedfs-service>:8333`
  - `S3_ACCESS_KEY` / `S3_SECRET_KEY` / `S3_BUCKET` (from step 2 — generate fresh strong keys)
  - `SMTP_HOST` / `SMTP_PORT` / `SMTP_USER` / `SMTP_PASSWORD` / `SMTP_FROM` /
    `SMTP_USE_TLS=true` (from your mail relay — see docs/deployment.md § Email)
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

Note both **application IDs** (visible in the UI/API) for step 5.

## 5. GitHub secrets & variables (repo → Settings → Secrets and variables → Actions)

The deploy-trigger job stays **skipped** until you create the repo variable
`DOKPLOY_DEPLOY_ENABLED=true` — so `main` stays green before Dokploy is set up.

Secrets:

| Secret               | Value                                    |
| -------------------- | ---------------------------------------- |
| `DOKPLOY_URL`        | `https://<dokploy-host>` (no slash)      |
| `DOKPLOY_TOKEN`      | Dokploy → Profile → API token            |
| `DOKPLOY_API_APP_ID` | api application id                       |
| `DOKPLOY_WEB_APP_ID` | web application id                       |

Variables:

| Variable                 | Value                       |
| ------------------------ | --------------------------- |
| `PUBLIC_API_URL`         | `https://api.<domain>`      |
| `DOKPLOY_DEPLOY_ENABLED` | `true` (when step 4 is done)|

## 6. First deploy

```
git remote add origin git@github.com:<org>/<repo>.git
git push -u origin main
```

`Deploy` workflow: builds both images → pushes to GHCR → calls Dokploy's deploy
API for each application. Watch progress in GitHub Actions and Dokploy's
deployment logs.

## 7. Verify

- `curl https://api.<domain>/health` → `{"status":"ok","environment":"production"}`
- Open `https://<domain>` → home page lists users (server-rendered).
- `https://<domain>/health` → shows API status from inside the page.

## Fallback: build on the VPS (no CI)

If you'd rather have Dokploy build from the repo: create each application as
**Dockerfile** source with **build context = repository root** and
**Dockerfile path** `apps/api/Dockerfile` / `apps/web/Dockerfile`, connect the
GitHub provider with watch paths (`apps/api/**` / `apps/web/**` +
`packages/**`), and skip step 5. Trade-offs in `docs/decisions/0003-ghcr-dokploy.md`.
