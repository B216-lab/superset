# External Integrations

**Analysis Date:** 2025-03-10

## APIs & External Services

**Maps:**
- Mapbox - Geospatial visualizations
  - Config: `MAPBOX_API_KEY` in `docker/.env.example`
  - Superset uses this for map chart types when key is set

**Build-time (optional):**
- DaData (referenced in CI) - `VITE_DADATA_KEY`, `VITE_DADATA_API` in `publish-docker.yml` build-args (optional, not used in base compose)

## Data Storage

**Databases:**
- PostgreSQL 16 - Metadata store and primary supported dialect
  - Image: `postgres:16` in `compose.yml`
  - Connection: `DATABASE_DIALECT`, `DATABASE_USER`, `DATABASE_PASSWORD`, `DATABASE_HOST`, `DATABASE_PORT`, `DATABASE_DB`
  - Driver: `psycopg2-binary` (installed in `Dockerfile`)
  - URI built in `docker/pythonpath_dev/superset_config.py`

**Caching:**
- Redis 7 - Celery broker, result backend, application cache
  - Image: `redis:7` in `compose.yml`
  - Config: `REDIS_HOST`, `REDIS_PORT`, `REDIS_CELERY_DB`, `REDIS_RESULTS_DB` (from `docker/.env.example`)
  - Used by: `CACHE_CONFIG`, `DATA_CACHE_CONFIG`, `THUMBNAIL_CACHE_CONFIG`, `CeleryConfig` in `docker/pythonpath_dev/superset_config.py`
  - SQL Lab results: `FileSystemCache` at `/app/superset_home/sqllab` (not Redis)

## Authentication & Identity

**Auth Provider:**
- Custom OAuth2/SSO via Authlib - Installed in `Dockerfile`, configuration not committed (override in `superset_config_docker.py`)
- Superset docs: [Custom OAuth2 configuration](https://superset.apache.org/docs/configuration/configuring-superset/#custom-oauth2-configuration)
- Requires: `CUSTOM_SECURITY_MANAGER`, OAuth2 client config in superset config override
- Local fallback: Built-in admin user (admin / `ADMIN_PASSWORD`) created by `docker/docker-init.sh`

## Monitoring & Observability

**Error Tracking:**
- None detected

**Logs:**
- Gunicorn: `ACCESS_LOG_FILE`, `ERROR_LOG_FILE` (default: stdout/stderr)
- Superset: `SUPERSET_LOG_LEVEL` (e.g. `info`)
- `docker/superset-websocket/config.json`: `logLevel`, `logToFile`, `logFilename`
- StatsD in websocket config (host 127.0.0.1:8125) - optional, typically disabled

## CI/CD & Deployment

**Hosting:**
- GitHub Container Registry (ghcr.io) - `publish-docker.yml`, `publish-preprod.yml`
- Pre-prod: SSH deploy to host via `appleboy/ssh-action` (secrets: `HOST`, `USERNAME`, `KEY`, `PORT`)

**CI Pipeline:**
- GitHub Actions - `publish-docker.yml` (hadolint, build-push), `publish-preprod.yml` (SSH pull/restart)
- Triggers: Push tags `v*`, workflow_dispatch
- Images: `ghcr.io/${{ github.repository_owner }}/${{ github.event.repository.name }}`

## Environment Configuration

**Required env vars (from `docker/.env.example`):**
- `DATABASE_DIALECT`, `DATABASE_USER`, `DATABASE_PASSWORD`, `DATABASE_HOST`, `DATABASE_PORT`, `DATABASE_DB`
- `SUPERSET_SECRET_KEY`
- `PYTHONPATH` (for config loading)
- `REDIS_HOST`, `REDIS_PORT` (defaults: redis, 6379)

**Secrets location:**
- `docker/.env` (git-ignored via `**/.env.*` in `.dockerignore`)
- `docker/.env-local` (optional override)
- GitHub secrets: `GITHUB_TOKEN`, `VITE_DADATA_KEY`; `HOST`, `USERNAME`, `KEY`, `PORT` for pre-prod

## Webhooks & Callbacks

**Incoming:**
- None detected

**Outgoing:**
- None (application-level)

## Additional Integrations

**Superset websocket:**
- Port 8080 - Async events (e.g. SQL Lab progress)
- Config: `docker/superset-websocket/config.json` - Redis, JWT (`jwtSecret`, `jwtAlgorithms`, `jwtCookieName`), StatsD
- Nginx template: `docker/nginx/templates/superset.conf.template` proxies `/ws` to websocket service

**Nginx (optional/reference):**
- `docker/nginx/nginx.conf` - Gzip, MIME types, includes `superset.conf`
- Template proxies to `host.docker.internal` (8088 app, 8080 websocket, 9000 static) - dev setup

---

*Integration audit: 2025-03-10*
