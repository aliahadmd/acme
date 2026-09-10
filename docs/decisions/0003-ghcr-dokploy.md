# 0003: CI-built images to GHCR, Dokploy pulls and routes

Date: 2026-09-11
Status: accepted

## Context

Dokploy can build images on the VPS from the repo, or run prebuilt images.
Building on a small VPS is slow and competes with production workloads; monorepo
build contexts also need careful configuration there.

## Decision

GitHub Actions builds both images on `main`, pushes to GHCR tagged with the
git SHA and `main`, then triggers Dokploy's deploy API (token in GitHub
secrets). Dokploy applications reference the GHCR images.

## Consequences

- VPS stays light; deploys are pulls + restarts (seconds).
- GHCR images are private by default → Dokploy needs registry credentials
  (see `deploy/README.md`).
- CI is the only build path — keep `make docker-build-*` working for local
  parity.
