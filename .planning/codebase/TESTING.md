# Testing Patterns

**Analysis Date:** 2025-03-10

## Overview

This project customizes the Apache Superset Docker image. **No test files exist in this repository.** Tests run against the base Superset application inside the built image; test infrastructure is inherited from superset-origin and the upstream Apache Superset image.

## Test Framework

**Runner:** pytest
**Config:** Inherited from Apache Superset base image

**Run commands (from superset-origin):**

```bash
# Integration tests (superset-origin/scripts/python_tests.sh)
pytest --durations-min=2 --cov-report= --cov=superset ./tests/integration_tests "$@"

# Module-specific (superset-origin/scripts/tests/run.sh)
pytest -vv --durations=0 "${TEST_MODULE}"
```

Tests live in `./tests/integration_tests` inside the Apache Superset container—not in this repo.

## Test Setup

**Prerequisites (from superset-origin scripts):**

1. `superset db upgrade`
2. `superset init`
3. `superset load-test-users`

**Config:** `SUPERSET_CONFIG=tests.integration_tests.superset_test_config`

**Database:** PostgreSQL; `SUPERSET__SQLALCHEMY_DATABASE_URI` for test DB (e.g. `postgresql+psycopg2://superset:superset@localhost/test`).

## Test File Organization

**Location:** Tests are in the upstream Superset image, not in this repo.

**superset-origin test runners:**
- `superset-origin/scripts/python_tests.sh` — runs integration tests with coverage (no report)
- `superset-origin/scripts/tests/run.sh` — docker-based runner with DB reset, init, and module selection

## Docker-Based Test Execution

`superset-origin/scripts/tests/run.sh`:

- Resets test DB (drops and recreates)
- Runs `superset db upgrade`, `superset init`, `superset load-test-users`
- Executes pytest with `-vv --durations=0`

**Flags:**
- `--no-init` — skip reset and init
- `--no-reset-db` — skip DB reset
- `--no-tests` — run init only
- `--reset-db` — reset DB only
- `--module <path>` — run specific module (e.g. `tests/charts/api_tests.py`)

## CI Testing

**This project (`.github/workflows/publish-docker.yml`):**
- Hadolint on `Dockerfile` — no pytest
- Build and push on version tags (`v*`)

**superset-origin:**
- Uses `docker-pytest-entrypoint.sh` for CI
- Waits for PostgreSQL, optionally resets DB with `FORCE_RELOAD=true`
- Uses `superset_test_config` for Cypress/CI config

## Coverage

**Current state:** Coverage is disabled (`--cov-report= `) in `python_tests.sh`. No coverage targets are enforced in this project.

## Test Types

**Unit tests:** Not used in this repo; upstream Superset has its own.

**Integration tests:** Run via superset-origin scripts against `./tests/integration_tests` inside the container.

**E2E:** Cypress used in superset-origin; this project does not run it.

**Dockerfile linting:** Hadolint in `.github/workflows/publish-docker.yml`.

## Mocking

Not applicable; this repo has no test code. Upstream Superset uses standard pytest mocking patterns.

## Planned Testing (from todos.md)

- Pre-commit configuration including ruff and ty checks
- No explicit test additions for this project yet

## Key Files

| File | Purpose |
|------|---------|
| `superset-origin/scripts/python_tests.sh` | Run integration tests with coverage (disabled report) |
| `superset-origin/scripts/tests/run.sh` | Docker-based test runner with DB reset |
| `superset-origin/docker/docker-pytest-entrypoint.sh` | CI pytest entrypoint |
| `.github/workflows/publish-docker.yml` | Hadolint on Dockerfile |

---

*Testing analysis: 2025-03-10*
