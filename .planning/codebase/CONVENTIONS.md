# Coding Conventions

**Analysis Date:** 2025-03-10

## Source of Truth

Conventions are defined in `AGENTS.md`. This project builds a custom Apache Superset Docker image; custom code lives in `docker/` (shell scripts, Python config). The `superset-origin/` directory holds reference Apache Superset docker configuration.

## Naming Patterns

**Python modules and files:**
- `snake_case.py` — modules use snake_case
- Example: `superset_config.py` in `docker/pythonpath_dev/`

**Classes:**
- `PascalCase`
- Example: `CeleryConfig` in `docker/pythonpath_dev/superset_config.py`

**Functions and methods:**
- `snake_case`
- Example: `echo_step`, `reset_db`, `test_init` in shell scripts

**Constants:**
- `UPPER_SNAKE_CASE`
- Example: `DATABASE_DIALECT`, `REDIS_HOST`, `TALISMAN_ENABLED` in `docker/pythonpath_dev/superset_config.py`

**Private identifiers:**
- Prefix with single underscore `_` (e.g. `_helper`)

**Shell functions:**
- `snake_case`
- Example: `echo_step`, `reset_db`, `echo_mem_warn`

## Code Style

### Python

**Formatter:** `ruff format`
**Linter:** `ruff check`
**Line length:** 99 characters
**Quotes:** Double quotes (`"`)

Commands (from `AGENTS.md`):

```bash
uv run ruff check src/ tests/
uv run ruff format src/ tests/
```

Imports are sorted by ruff; use `ruff` for all formatting.

### Shell

**Shebang:** `#!/usr/bin/env bash` (preferred) or `#!/bin/bash`

**Error handling:** Use strict mode:
- `set -e` — exit on error (common in `docker/` scripts)
- `set -eo pipefail` — also fail on pipe errors (`docker/docker-init.sh`)
- `set -euo pipefail` — also fail on undefined vars (`docker/pip-install.sh`, `docker/apt-install.sh`)

**Variable expansion:**
- Use `${VAR:-default}` for optional env vars (`docker/entrypoints/run-server.sh`)
- Quote expansions in conditionals: `[ "$VAR" = "value" ]`

### YAML

- Use `true` and `false` (not `yes`/`no`) for boolean values
- Example: `compose.yml` uses `required: true` / `required: false`

## Import Organization

**Python:**
- Imports sorted by ruff (stdlib, third-party, local)
- Wildcard imports use `# noqa: F403` when intentional: `from superset_config_docker import *  # noqa: F403`
- Long lines may use `# noqa: E501` for line-length exemptions

**Common noqa codes in codebase:**
- `F403` — star import
- `E501` — line too long
- `S602`, `S607` — subprocess/shell (intentional)
- `C901` — function too complex (temporary)
- `N806` — lowercase var in global (e.g. `Base`)

## Type Annotations

- All public functions must have full type annotations (parameters and return types)
- Use `from __future__ import annotations` in every module
- Prefer `str | None` over `Optional[str]`
- Private helpers should have annotations where non-obvious

Example from `superset-origin/scripts/check-env.py`:

```python
def main(docker: bool, frontend: bool, backend: bool) -> None:  # noqa: C901
```

```python
def get_version(self) -> Optional[str]:
```

## Error Handling

- Never swallow exceptions silently
- Use custom exception classes defined in an `exceptions.py` module
- Log errors with full context (URL, retry count, selector attempted) before re-raising or handling

**Shell:**
- Use `set -e` (or `-eo pipefail`) so scripts exit on failure
- Emit errors to stderr: `echo "Error message" >&2`
- Use `exit 1` for failure

## Logging

**Framework:** Python `logging` module

**Levels (from AGENTS.md):**
- `DEBUG` — DOM details
- `INFO` — progress
- `WARNING` — retries
- `ERROR` — failures

Never log sensitive data (full cookies, tokens).

Example in `docker/pythonpath_dev/superset_config.py`:

```python
logger.info(
    "Loaded your Docker configuration at [%s]", superset_config_docker.__file__
)
```

## Comments and Docstrings

- Do NOT write comments that merely narrate what code does
- Write docstrings for public classes and functions explaining *why* and *what* (not *how*)
- Use Google-style docstrings

## Function Design

**Size:** Avoid overly complex functions; use `# noqa: C901` sparingly when refactoring is deferred
**Parameters:** Use type hints on public functions
**Return values:** Explicit return type annotations

## Module Design

**Config imports:** Optional override pattern with try/except:
- In `docker/pythonpath_dev/superset_config.py`, try `import superset_config_docker` and log success; on `ImportError`, use default config

## Docker and Compose

**Dockerfile:**
- Base image: `apache/superset:5.0.0`
- Use `uv pip install` for Python packages when available
- Run Hadolint in CI (`.github/workflows/publish-docker.yml`)

**Compose:**
- Use `path:` and `required:` for env_file entries
- Use `condition: service_completed_successfully` for init dependencies

## Planned Tooling (from todos.md)

- Pre-commit configuration for: yaml lint, hadolint, shellcheck, ruff, ty

---

*Convention analysis: 2025-03-10*
