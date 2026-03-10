# Codebase Structure

**Analysis Date:** 2025-03-10

## Directory Layout

```
superset/
├── .github/workflows/       # CI/CD (Docker publish)
├── .planning/codebase/      # GSD codebase docs (this file)
├── .vscode/                 # Editor config
├── docker/                  # B216 Superset docker image configuration (active)
│   ├── entrypoints/        # Custom entrypoint scripts
│   ├── nginx/              # Nginx config (base + templates)
│   ├── pythonpath_dev/     # Superset config mounted as PYTHONPATH
│   └── superset-websocket/ # WebSocket server config
├── superset-origin/        # Upstream Apache Superset docker reference (read-only)
├── Dockerfile              # Custom image build
├── compose.yml             # Docker Compose for local run
├── AGENTS.md               # Project guidelines
├── ReadMe.md               # User-facing README
├── todos.md                # Task list
└── LICENSE                 # License
```

## Directory Purposes

**`docker/`:** Active configuration and scripts for the B216 Superset image. Mounted at `/app/docker` in containers. Contains bootstrap, init, config, nginx, and WebSocket config.

**`superset-origin/`:** Reference copy of Apache Superset docker setup. Used for comparing changes, porting upstream updates. Do not edit for runtime behavior.

**`.github/workflows/`:** GitHub Actions for linting the Dockerfile (hadolint) and building/pushing images to ghcr.io on tag push (`v*`).

**`.planning/codebase/`:** GSD architecture and structure docs consumed by planning/execution.

## Key File Locations

**Entry points:**
- `Dockerfile`: Base image extension; installs psycopg2-binary, Authlib, openpyxl, Pillow; CMD `run-server.sh`
- `docker/docker-bootstrap.sh`: Routes to app / worker / beat; installs local requirements
- `docker/docker-init.sh`: DB migrations, admin user, roles, optional examples
- `docker/entrypoints/run-server.sh`: Gunicorn launcher for standalone runs

**Configuration:**
- `compose.yml`: Services, volumes, depends_on, env_file
- `docker/.env.example`: Env template (DB, Redis, Superset, Mapbox, etc.)
- `docker/pythonpath_dev/superset_config.py`: Superset config from env
- `docker/superset-websocket/config.json`: WebSocket server config

**Nginx:**
- `docker/nginx/nginx.conf`: Base nginx config (gzip, mime, include superset.conf)
- `docker/nginx/templates/superset.conf.template`: Upstreams and location blocks (app, websocket, static)

**CI/CD:**
- `.github/workflows/publish-docker.yml`: hadolint, ghcr.io login, metadata, build-push

**Supporting:**
- `docker/docker-healthcheck.sh`: Health probe
- `docker/pip-install.sh`, `docker/apt-install.sh`: Package install helpers (used by upstream patterns)
- `docker/docker-frontend.sh`, `docker/frontend-mem-nag.sh`: Frontend helpers

## Naming Conventions

**Files:**
- Shell: `docker-*.sh` for top-level scripts, `run-server.sh` for entrypoints
- Config: `superset_config*.py`, `.env.example`, `config.json`
- Compose: `compose.yml` (no `docker-compose` prefix)

**Directories:**
- `docker/`: Active runtime config
- `superset-origin/`: Upstream reference
- `pythonpath_dev/`: Dev-oriented Python path config

## Where to Add New Code

**New Python packages for Superset:**
- Add to `Dockerfile` `uv pip install` list, or
- Add `docker/requirements-local.txt` and rebuild

**New Superset config overrides:**
- Create `docker/pythonpath_dev/superset_config_docker.py` (git-ignored) from `superset-origin/docker/pythonpath_dev/superset_config_local.example`, or extend `superset_config.py` if project-wide

**New env vars:**
- Document in `docker/.env.example`; add to `docker/.env` or `docker/.env-local`

**New services (e.g. nginx, websocket):**
- Extend `compose.yml`; add config under `docker/` as needed

**New scripts:**
- Top-level ops: `docker/*.sh`
- Entrypoints: `docker/entrypoints/*.sh`

## Special Directories

**`docker/pythonpath_dev/`:**
- Purpose: Superset config files mounted into container
- Generated: No
- Committed: `superset_config.py`, `.gitignore`; `superset_config_docker.py` is git-ignored

**`superset-origin/`:**
- Purpose: Upstream reference
- Generated: No (cloned/copied)
- Committed: Yes (as reference)

**`.planning/codebase/`:**
- Purpose: GSD architecture and structure docs
- Generated: By codebase mapper
- Committed: Yes

---

*Structure analysis: 2025-03-10*
