# Technology Stack

**Analysis Date:** 2025-03-10

## Languages

**Primary:**
- Python (version from base image) - Backend application (Apache Superset), configuration in `docker/pythonpath_dev/superset_config.py`, bootstrap scripts in `docker/`

**Secondary:**
- Shell (bash) - Entrypoints and bootstrap scripts: `docker/docker-bootstrap.sh`, `docker/docker-init.sh`, `docker/entrypoints/run-server.sh`, `docker/pip-install.sh`

## Runtime

**Environment:**
- Docker containers built from `apache/superset:5.0.0` base image
- Python virtual environment at `/app/.venv` (created by base image)
- Gunicorn for production: `docker/entrypoints/run-server.sh`

**Package Manager:**
- uv (Astral) - Used in `Dockerfile` and `docker/docker-bootstrap.sh` for Python package installation
- Lockfile: Not present at project root (base image manages deps)

## Frameworks

**Core:**
- Apache Superset 5.0.0 - BI/analytics platform (Flask, Flask-AppBuilder, SQLAlchemy)
- Flask - Web framework (via Superset)
- Gunicorn - WSGI server for production (`gthread` worker class, configurable via env vars)

**Build/Dev:**
- Docker - Image builds and local deployment
- Docker Compose - Multi-container orchestration in `compose.yml`

## Key Dependencies

**Critical (installed in Dockerfile):**
- `psycopg2-binary` - PostgreSQL metadata store and datasource connections
- `Authlib` - OAuth2/SSO authentication support
- `openpyxl` - Excel file upload support
- `Pillow` - PDF generation for Alerts & Reports dashboards

**Infrastructure (from base image):**
- Flask, Flask-AppBuilder, Flask-Caching, Flask-Migrate
- SQLAlchemy
- Celery (worker + beat for async tasks)
- Redis client (caching, Celery broker)
- Gunicorn

## Configuration

**Environment:**
- `docker/.env` (required) + `docker/.env-local` (optional override) - Both used by compose services
- Example: `docker/.env.example`
- Key vars: `DATABASE_*`, `REDIS_*`, `SUPERSET_SECRET_KEY`, `MAPBOX_API_KEY`, `SUPERSET_PORT`, etc.

**Build:**
- `Dockerfile` - Extends `apache/superset:5.0.0`, adds packages via `uv pip install`
- `.dockerignore` - Excludes `.git`, `.github`, `**/.env.*`, `*.md`
- Python config: `docker/pythonpath_dev/superset_config.py` (base) + optional `superset_config_docker.py` (git-ignored overrides)
- `PYTHONPATH=/app/pythonpath:/app/docker/pythonpath_dev` (from `docker/.env.example`)

## Platform Requirements

**Development:**
- Docker and Docker Compose
- Sufficient memory for build (macOS: avoid exit code 137 by increasing Docker resources)
- `docker compose up` from project root

**Production:**
- Deployment target: Container registry (ghcr.io), pre-prod via SSH to host
- PostgreSQL 16, Redis 7
- Port 8088 (Superset), 8080 (websocket when nginx used)

---

*Stack analysis: 2025-03-10*
