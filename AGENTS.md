# AGENTS.md - Superset docker image

## Project identity

This document describes the project structure for the Superset docker image.

## Project structure

```
superset/
├── AGENTS.md                  # This file — project guidelines
├── superset-origin/           # Original Apache Superset docker configuration taken from superset github repository for reference
├── docker/                    # B216 Superset docker image configuration
├── compose.yml                # Docker compose file for the project to run Superset locally
└── Dockerfile                 # Superset image with PostgreSQL driver and SSO on top
```

## Guiding principles

1. Spec-driven development. Specifications should be stored in the `specs/` directory. Every feature is specified in `specs/` before implementation begins. Code follows specs, not the other way around. Specs are living documents updated when requirements change.


### Specification Workflow

1. **Read the spec** in `specs/` before implementing any feature.
2. **Implement** according to the spec's completion criteria.
3. **Update the spec** if implementation reveals the spec was incomplete or incorrect.
4. **Mark spec items as done** by checking their completion criteria checkboxes.
5. **Never implement features that lack a spec.** Write the spec first.


## Python Coding standards

- **Formatter**: `ruff format` — no manual formatting debates.
- **Linter**: `ruff check` — fix all auto-fixable issues; remaining issues require manual resolution.
- **Line length**: 99 characters.
- **Quotes**: Double quotes (`"`).
- **Imports**: Sorted by `ruff`.

### Type-annotations

- All public functions must have full type annotations (parameters and return types).
- Use `from __future__ import annotations` in every module.
- Private/internal helpers should have annotations where non-obvious.
- Prefer `str | None` over `Optional[str]`.


### Naming Conventions

- **Modules**: `snake_case.py`
- **Classes**: `PascalCase`
- **Functions/methods**: `snake_case`
- **Constants**: `UPPER_SNAKE_CASE`
- **Private**: Prefix with single underscore `_`


### Error Handling

- Never swallow exceptions silently.
- Use custom exception classes defined in a `exceptions.py` module.
- Log errors with full context (URL, retry count, selector attempted) before re-raising or handling.

### Logging

- Log levels: `DEBUG` for DOM details, `INFO` for progress, `WARNING` for retries, `ERROR` for failures.
- Never log sensitive data (full cookies, tokens).

### Comments and Docstrings

- Do NOT write comments that merely narrate what code does.
- Write docstrings for public classes and functions explaining *why* and *what* (not *how*).
- Use Google-style docstrings.


## Development Workflow

### Setup

```bash
# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create virtual environment and install dependencies
uv sync
```

### Before committing

* Run pre-commit hooks


### Git Conventions

- Conventional commit messages: imperative mood, concise (`Add attendance extraction logic`, not `Added some stuff`).
- Conventional branch naming: `feat/<short-description>`, `fix/<short-description>`, `spec/<short-description>`.
- No force-pushes to `main`.
- Specs changes and code changes may share a commit if they are tightly coupled.


### Common Commands

```bash
# Run the parser
uv run ya-parser --config config.yaml

# Lint
uv run ruff check src/ tests/

# Format
uv run ruff format src/ tests/

# Type check
uv run ty check

# Test
uv run pytest

# Test with visible browser (debugging)
uv run pytest --headed
```
