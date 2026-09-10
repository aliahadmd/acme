# syntax=docker/dockerfile:1
# Build context: REPO ROOT (workspace deps needed):
#   docker build -t acme-web -f apps/web/Dockerfile .

FROM node:24-alpine AS build
WORKDIR /repo
RUN corepack enable
# Be patient with slow registry connections (CI and constrained networks)
ENV npm_config_fetch_retries=5 \
    npm_config_fetch_retry_mintimeout=20000 \
    npm_config_fetch_retry_maxtimeout=120000 \
    npm_config_fetch_timeout=600000

# Public API URL, inlined into the client bundle at build time (public — no secrets in VITE_*).
ARG VITE_API_BASE_URL=https://api.example.com
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL

# Install workspace deps first — layer only changes when the lockfile changes
COPY package.json pnpm-workspace.yaml pnpm-lock.yaml ./
COPY packages/config/package.json packages/config/
COPY packages/api-client/package.json packages/api-client/
COPY apps/web/package.json apps/web/
RUN pnpm install --frozen-lockfile

COPY packages ./packages
COPY apps/web ./apps/web
RUN pnpm --filter @acme/web build

# Runtime: only the SSR build output + the srvx server binary
FROM node:24-alpine
WORKDIR /app
RUN addgroup -S app && adduser -S app -G app
COPY --from=build --chown=app:app /repo/apps/web/dist ./dist
COPY --from=build --chown=app:app /repo/node_modules/.pnpm/srvx*/node_modules/srvx ./node_modules/srvx
USER app
ENV NODE_ENV=production \
    HOST=0.0.0.0 \
    PORT=3000
EXPOSE 3000
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD wget -qO- http://127.0.0.1:3000/health >/dev/null 2>&1 || exit 1
CMD ["node", "node_modules/srvx/bin.js", "--prod", "-s", "dist/client", "dist/server/server.js"]
