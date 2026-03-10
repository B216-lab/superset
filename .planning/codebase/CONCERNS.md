# Codebase Concerns

**Analysis Date:** 2025-03-10

## Tech Debt

**superset-origin vs docker divergence:**

- Issue: `superset-origin/` is a reference copy from Apache Superset upstream. The project's active config lives in `docker/`. `docker/README.md` references `superset_config_local.example` and `docker-compose-non-dev.yml`, but both exist only in `superset-origin/`; `docker/pythonpath_dev/` has no `superset_config_local.example`.
- Files: `docker/README.md`, `docker/pythonpath_dev/`, `superset-origin/docker/`
- Impact: Developers following docker/README.md cannot complete the local-override flow; production compose guidance points to a non-existent file.
- Fix approach: Add `docker/pythonpath_dev/superset_config_local.example` and either add a `docker-compose-non-dev.yml` at project root or fix README references.

**AGENTS.md mismatch:**

- Issue: AGENTS.md references `uv sync`, `ya-parser`, `ruff`, `pytest`, `src/`, `tests/` as if this were a Python application project. The repo is a Docker image build with no `src/`, `tests/`, or `pyproject.toml`.
- Files: `AGENTS.md`
- Impact: Agents and contributors receive incorrect development workflow instructions.
- Fix approach: Align AGENTS.md with the actual project (Docker-based Superset image) or remove non-applicable sections.

**Spec-driven workflow without specs:**

- Issue: AGENTS.md mandates spec-driven development and a `specs/` directory. `specs/` does not exist; `todos.md` lists items meant to become specs.
- Files: `AGENTS.md`, `todos.md`
- Impact: Workflow rules cannot be followed; ambiguity about whether specs are required before implementation.
- Fix approach: Create `specs/` and migrate todos into specs, or relax AGENTS.md to match current practice.

**Unused CI build-args:**

- Issue: `.github/workflows/publish-docker.yml` passes `VITE_DADATA_KEY` and `VITE_DADATA_API` as build-args. The project Dockerfile has no `ARG` declarations; the base image `apache/superset:5.0.0` may or may not use them.
- Files: `.github/workflows/publish-docker.yml`, `Dockerfile`
- Impact: Build-args are passed but may have no effect; configuration intent is unclear.
- Fix approach: Declare and use ARGs in the Dockerfile if needed, or remove build-args from the workflow.

**TODOs in superset-origin:**

- Issue: `superset-origin/docker/entrypoints/docker-ci.sh` contains TODOs for "copy config overrides from ENV vars" and "run celery in detached state". This file is reference only; `compose.yml` does not use it.
- Files: `superset-origin/docker/entrypoints/docker-ci.sh`
- Impact: Low; file is not part of the active stack.
- Fix approach: Ignore or remove if superset-origin is strictly reference.

## Known Bugs

**None explicitly documented.** Known issues appear as security/misconfig rather than reproducible bugs.

## Security Considerations

**Running as root:**

- Risk: `compose.yml` sets `user: "root"` for superset, superset-init, superset-worker, and superset-worker-beat. The Dockerfile switches to `superset` for CMD, but compose overrides with root.
- Files: `compose.yml` (lines 36, 61, 81, 106)
- Current mitigation: None; containers run with full root privileges.
- Recommendations: Use `user: "superset"` or a non-root UID/GID; ensure volume permissions allow the chosen user.

**Default credentials in .env.example:**

- Risk: `docker/.env.example` ships with `DATABASE_PASSWORD=superset`, `POSTGRES_PASSWORD=superset`, `ADMIN_PASSWORD` defaulting to `admin` in `docker-init.sh`, and `SUPERSET_SECRET_KEY` as a fixed value. Comments warn about production, but the file is copy-paste friendly.
- Files: `docker/.env.example`, `docker/docker-init.sh` (line 23)
- Current mitigation: Comments stating "Make sure you set this to a unique secure random value on production".
- Recommendations: Use placeholder values (e.g. `CHANGE_ME_IN_PRODUCTION`) instead of usable defaults; require explicit override for production.

**Exposed API keys in .env.example:**

- Risk: `MAPBOX_API_KEY` in `docker/.env.example` is a real public key (pk.eyJ...).
- Files: `docker/.env.example` (line 40)
- Current mitigation: None.
- Recommendations: Replace with a placeholder or remove; document that users must supply their own key.

**Talisman disabled:**

- Risk: `docker/pythonpath_dev/superset_config.py` sets `TALISMAN_ENABLED = False`, disabling Flask-Talisman security headers (e.g. CSP, X-Content-Type-Options).
- Files: `docker/pythonpath_dev/superset_config.py` (line 16)
- Current mitigation: None.
- Recommendations: Enable Talisman for production or document why it must stay disabled.

**WebSocket JWT secret:**

- Risk: `docker/superset-websocket/config.json` contains `jwtSecret: "CHANGE-ME-IN-PRODUCTION-GOTTA-BE-LONG-AND-SECRET"`.
- Files: `docker/superset-websocket/config.json` (line 19)
- Current mitigation: Placeholder value.
- Recommendations: Load from environment; fail startup if not overridden in production.

## Performance Bottlenecks

**SQL Lab results not persisted:**

- Problem: `RESULTS_BACKEND` uses `FileSystemCache("/app/superset_home/sqllab")`. `compose.yml` does not mount `superset_home`; only `./docker:/app/docker` is mounted.
- Files: `docker/pythonpath_dev/superset_config.py` (line 33), `compose.yml`
- Cause: Cache directory is ephemeral; data is lost on container restart.
- Improvement path: Add a `superset_home` volume (as in `superset-origin/docker-compose-non-dev.yml`) if SQL Lab result persistence is desired.

**Single gunicorn worker default:**

- Problem: `run-server.sh` uses `SERVER_WORKER_AMOUNT:-1`, so one worker by default.
- Files: `docker/entrypoints/run-server.sh` (line 9)
- Cause: Default favors simplicity over throughput.
- Improvement path: Document and tune via env for production; consider higher default for multi-core hosts.

## Fragile Areas

**Healthcheck URL construction:**

- Files: `docker/docker-healthcheck.sh` (line 3)
- Why fragile: Uses `${SUPERSET_APP_ROOT/\//}` to strip leading slash. Edge cases (e.g. `SUPERSET_APP_ROOT="/superset/"`) can yield incorrect paths like `/superset//health`. Superset app service in `compose.yml` does not use this healthcheck.
- Safe modification: Add explicit handling for root vs non-root paths; consider `/health` and `${SUPERSET_APP_ROOT}health` variants.
- Test coverage: None.

**docker-init.sh SUPERSET_LOAD_EXAMPLES value:**

- Files: `docker/docker-init.sh` (lines 10–11, 49)
- Why fragile: Script checks `SUPERSET_LOAD_EXAMPLES = "yes"`; `.env.example` uses `SUPERSET_LOAD_EXAMPLES=no`. Behavior depends on exact string match; `true`/`false` would not work.
- Safe modification: Support both `yes`/`no` and `true`/`false` or document the expected value.
- Test coverage: None.

**Nginx template host.docker.internal:**

- Files: `docker/nginx/templates/superset.conf.template`
- Why fragile: Uses `host.docker.internal` for app, websocket, and webpack proxy. This works on Docker Desktop (Mac/Windows) but not on Linux by default.
- Safe modification: Use configurable host or service names for Linux compatibility.
- Test coverage: None.

## Scaling Limits

**Redis and Postgres:**

- Current capacity: Single Redis and Postgres containers with default settings.
- Limit: No replication, failover, or resource limits defined in compose.
- Scaling path: Add Redis/Postgres clusters, resource limits, and production-grade config for higher load.

## Dependencies at Risk

**Pinned base image:**

- Package: `apache/superset:5.0.0` (Dockerfile line 1)
- Risk: Hardcoded version; no automatic updates.
- Impact: Security and feature updates depend on manual base image bumps.
- Migration plan: Add Dependabot or Renovate for Docker base image; consider multi-stage builds if customizations grow.

## Missing Critical Features

**SSO configuration:**

- Problem: `todos.md` lists "Prepare SSO support configuration". Dockerfile installs Authlib but no OAuth2/SSO wiring exists in config.
- Blocks: SSO cannot be used without manual setup.
- Files: `todos.md`, `docker/pythonpath_dev/superset_config.py`, `Dockerfile`

**Pre-commit and lint tooling:**

- Problem: AGENTS.md says "Run pre-commit hooks" but no pre-commit config is present. `todos.md` requests pre-commit for yaml, hadolint, shellcheck, ruff, ty.
- Blocks: No automated checks before commit.
- Files: `AGENTS.md`, `todos.md`

**Production compose template:**

- Problem: `todos.md` requests a compose template with variables (e.g. Jinja) for production with secrets passed externally.
- Blocks: Production deployment requires manual env management.
- Files: `todos.md`

## Test Coverage Gaps

**Untested area: Docker stack and config**

- What's not tested: No automated tests for Docker build, compose startup, config loading, or entrypoint scripts.
- Files: `Dockerfile`, `compose.yml`, `docker/docker-init.sh`, `docker/docker-bootstrap.sh`, `docker/entrypoints/run-server.sh`, `docker/pythonpath_dev/superset_config.py`
- Risk: Regressions in image or config go unnoticed.
- Priority: Medium (manual validation only).

---

*Concerns audit: 2025-03-10*
