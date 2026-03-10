# Architecture

**Analysis Date:** 2025-03-10

## Pattern Overview

**Overall:** Custom Docker image layered on upstream Apache Superset with composition-based customization. The project extends `apache/superset:5.0.0` by adding Python packages (PostgreSQL driver, Authlib for SSO) and mounting project-specific configuration and scripts at runtime.

**Key Characteristics:**
- Base image inheritance—no fork of Superset core; all customization via layers and mounts
- Volume-mounted `docker/` provides config and scripts; base image provides application code
- Multi-container orchestration: init runs once, app/worker/beat run continuously
- Environment-driven configuration with optional local overrides

## Layers

**Build layer (`Dockerfile`):**
- Purpose: Extend base image with additional Python packages
- Location: `Dockerfile`
- Contains: `FROM`, `RUN uv pip install` for psycopg2-binary, Authlib, openpyxl, Pillow; `USER` transitions; `CMD`
- Depends on: `apache/superset:5.0.0`
- Used by: `compose.yml` build context, GitHub Actions publish workflow

**Runtime configuration layer (`docker/`):**
- Purpose: Supply Superset config, bootstrap scripts, and optional overrides
- Location: `docker/`
- Contains: `docker-bootstrap.sh`, `docker-init.sh`, `pythonpath_dev/superset_config.py`, nginx configs, entrypoints
- Depends on: Base image structure (paths like `/app/docker`, `/app/pythonpath`)
- Used by: All containers via volume mount `./docker:/app/docker`; `PYTHONPATH` includes `/app/docker/pythonpath_dev`

**Orchestration layer (`compose.yml`):**
- Purpose: Define services, dependencies, env files, and startup order
- Location: `compose.yml`
- Contains: redis, db (PostgreSQL), superset, superset-init, superset-worker, superset-worker-beat
- Depends on: Built image, `docker/.env`, optional `docker/.env-local`
- Used by: `docker compose up`, local development

**Reference layer (`superset-origin/`):**
- Purpose: Upstream Apache Superset docker configuration for reference; not used at runtime
- Location: `superset-origin/`
- Contains: Original scripts, configs, nginx; separate git submodule/history
- Depends on: None (read-only reference)
- Used by: Developers comparing or porting changes from upstream

## Data Flow

**Startup flow:**

1. `docker compose up` builds image from `Dockerfile` (if needed), starts redis and db
2. `superset-init` runs `docker/docker-init.sh` once: installs local deps via `docker-bootstrap.sh`, `superset db upgrade`, creates admin user, `superset init`, optionally loads examples
3. `superset` runs `docker-bootstrap.sh app-gunicorn` → `/usr/bin/run-server.sh` (gunicorn), bound to 8088
4. `superset-worker` runs `docker-bootstrap.sh worker` → Celery worker
5. `superset-worker-beat` runs `docker-bootstrap.sh beat` → Celery beat scheduler

**Configuration flow:**

1. Env loaded: `docker/.env` (required), `docker/.env-local` (optional override)
2. Python config: `PYTHONPATH` includes `/app/docker/pythonpath_dev`; Superset loads `superset_config.py`
3. Optional: `superset_config_docker.py` (git-ignored) overrides settings when present

**State management:**
- Database: PostgreSQL (db service), persisted in `db_home` volume
- Cache / broker: Redis (redis service), persisted in `redis` volume
- Config / scripts: Volume `./docker:/app/docker`; changes apply on container restart

## Key Abstractions

**docker-bootstrap.sh:**
- Purpose: Single entry script for app, worker, beat; installs local requirements, routes to correct process
- Examples: `docker/docker-bootstrap.sh`
- Pattern: `case "${1}" in worker|beat|app|app-gunicorn) ... esac`; calls `uv pip install` for postgres/requirements-local

**docker-init.sh:**
- Purpose: One-time initialization (migrations, admin user, roles, optional examples)
- Examples: `docker/docker-init.sh`
- Pattern: Sequential steps with `echo_step`; depends on `docker-bootstrap.sh` for env setup

**superset_config.py:**
- Purpose: Central Superset config from env (DB, Redis, Celery, feature flags)
- Examples: `docker/pythonpath_dev/superset_config.py`
- Pattern: `SQLALCHEMY_DATABASE_URI`, `CACHE_CONFIG`, `CeleryConfig` built from `os.getenv`; optional `superset_config_docker` import

**run-server.sh:**
- Purpose: Launch gunicorn with Superset; used when image is run directly (e.g. `docker run`) or as alternative to base `/usr/bin/run-server.sh`
- Examples: `docker/entrypoints/run-server.sh`
- Pattern: Gunicorn invocation with bind, workers, timeout; respects env vars like `SUPERSET_BIND_ADDRESS`, `SERVER_WORKER_AMOUNT`

## Entry Points

**Compose services (primary):**
- `superset-init`: `["/app/docker/docker-init.sh"]` — runs once on startup
- `superset`: `["/app/docker/docker-bootstrap.sh", "app-gunicorn"]` — web app
- `superset-worker`: `["/app/docker/docker-bootstrap.sh", "worker"]` — Celery worker
- `superset-worker-beat`: `["/app/docker/docker-bootstrap.sh", "beat"]` — Celery beat

**Standalone image:**
- `Dockerfile` CMD: `["/app/docker/entrypoints/run-server.sh"]` — gunicorn (requires `docker/` mounted)

**Supporting scripts:**
- `docker/docker-healthcheck.sh`: HTTP health check for `/health`
- `docker/docker-frontend.sh`, `docker/frontend-mem-nag.sh`: Frontend/build helpers (from upstream pattern)

## Error Handling

**Strategy:** Fail-fast in scripts (`set -e` / `set -eo pipefail`); errors surface via container exit.

**Patterns:**
- `docker-init.sh`: `set -e`; each step runs sequentially; Cypress mode branches for test data
- `docker-bootstrap.sh`: `set -eo pipefail`; unknown operation echoes "Unknown Operation!!!" and exits
- Health check: `curl -f ... || exit 1` in `docker-healthcheck.sh`

## Cross-Cutting Concerns

**Logging:** Configured via `SUPERSET_LOG_LEVEL` in `superset_config.py`; gunicorn log level via `GUNICORN_LOGLEVEL`.

**Validation:** DB/Redis connection strings built from env; missing vars yield runtime failures.

**Authentication:** Authlib installed for OAuth2/SSO; actual SSO config done in `superset_config_docker.py` or similar overrides.

---

*Architecture analysis: 2025-03-10*
