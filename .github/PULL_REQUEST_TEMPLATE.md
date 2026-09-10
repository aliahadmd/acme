## What

<!-- One paragraph: what changed and why. Link issues. -->

## Checklist

- [ ] `make check` passes locally (lint · typecheck · tests)
- [ ] API changed? `make client` re-ran → `packages/api-client` diff included; `operation_id`s stable
- [ ] Env vars changed? `.env.example` + `docs/environments.md` updated
- [ ] Schema changed? Alembic migration added (`make migration m="..."`) and reviewed
- [ ] Generated code untouched by hand (`packages/api-client/src/client/**`, `routeTree.gen.ts`)
