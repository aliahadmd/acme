# CLAUDE.md

@AGENTS.md

## Claude Code specifics

- Prefer `make` targets for workflows; use `pnpm --filter @acme/web …` for targeted JS
  commands and `cd apps/api && uv run …` for targeted Python commands.
- When you change FastAPI endpoints, always finish with `make client` so the generated
  TypeScript client and query hooks are regenerated in the same change.
- After changing any env var: update the app's `.env.example` AND `docs/environments.md`
  in the same edit.
