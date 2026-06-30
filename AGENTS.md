# AGENTS.md - Superset docker image

## Project identity

Describe project structure for Superset docker image.

## Project structure

```
superset/
├── AGENTS.md                  # This file — project guidelines
├── superset-origin/           # Original Apache Superset docker configuration taken from superset github repository for reference
├── docker/                    # B216 Superset docker image configuration
├── compose.yml                # Docker compose file for the project to run Superset locally
└── Dockerfile                 # Superset image with PostgreSQL driver and SSO on top
```

## Other

### RTK

- Use `~/.codex/RTK.md`: prefix shell commands with `rtk` when compatible.
- Prefer `rtk read`, `rtk git`, `rtk test`, `rtk pnpm/npm/npx`, `rtk tsc/lint`, `rtk docker/go/python` wrappers.
- Use `rtk proxy <cmd>` for unsupported commands when possible.
- Use native command only if RTK hides needed output or changes behavior; state why briefly.

### Caveman

- Always use `caveman` skill for talk, use ultra level
- Prefer caveman-family skills when task matches: `caveman-commit` for commits or commit messages, `caveman-review` for normal code review, `caveman-compress` for skill or memory summaries

---

- Use heavier review skills only when user asks for deep, security, performance, or framework-specific review
- Use global skill definitions as source of truth for when skills apply; do not treat this file as skill index
- Use only minimal relevant skill set. Do not load broad skills just in case
- After reading any skill, retain only a `caveman-compress` ultra-style summary for current turn; avoid re-reading full skill body unless task needs exact detail
- When you do something, don't spam with some new readme, additional documentation or anything like that until I ask for it


### Specification Workflow

1. **Read spec** in `specs/` before implementing feature.
2. **Implement** by spec completion criteria.
3. **Update spec** if implementation show spec incomplete or wrong.
4. **Mark spec items done** by checking completion criteria checkboxes.
5. **Never implement feature without spec.** Write spec first.


## Python Coding standards

- **Formatter**: `ruff format` - no manual formatting debate.
- **Linter**: `ruff check` - fix all auto-fixable issues; manual fix rest.
- **Line length**: 99 characters.
- **Quotes**: Double quotes (`"`).
- **Imports**: Sorted by `ruff`.

### Type-annotations

- All public functions need full type annotations: params + return types.
- Use `from __future__ import annotations` in every module.
- Private/internal helpers need annotations when non-obvious.
- Prefer `str | None` over `Optional[str]`.


### Naming Conventions

- **Modules**: `snake_case.py`
- **Classes**: `PascalCase`
- **Functions/methods**: `snake_case`
- **Constants**: `UPPER_SNAKE_CASE`
- **Private**: Prefix with single underscore `_`


### Error Handling

- Never swallow exceptions silently.
- Use custom exception classes from `exceptions.py`.
- Log errors with full context: URL, retry count, selector attempted, then re-raise or handle.

### Logging

- Log levels: `DEBUG` for DOM details, `INFO` for progress, `WARNING` for retries, `ERROR` for failures.
- Never log sensitive data (full cookies, tokens).

### Comments and Docstrings

- Do NOT write comments that only narrate code.
- Write docstrings for public classes and functions explaining *why* + *what*, not *how*.
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

- Run pre-commit hooks


### Git Conventions

- Conventional commit messages: imperative mood, concise (`Add attendance extraction logic`, not `Added some stuff`).
- Conventional branch naming: `feat/<short-description>`, `fix/<short-description>`, `spec/<short-description>`.
- No force-pushes to `main`.
- Specs changes + code changes may share commit if tightly coupled.


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
