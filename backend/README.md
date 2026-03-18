# CPPM Backend

Centralized Professional Profile Manager - Backend API.

## Quality checks

Install dev dependencies (includes ruff, pyright, bandit):

```bash
uv sync --all-extras
```

| Tool     | Purpose              | Command |
|----------|----------------------|--------|
| **Ruff** | Lint + format        | `uv run ruff check app tests` / `uv run ruff format app tests` |
| **Pyright** | Static type checking | `uv run pyright app` |
| **Bandit**  | Security lint        | `uv run bandit -r app -c pyproject.toml` |

Run all checks (from `backend`):

```bash
uv run ruff check app tests && uv run ruff format --check app tests && uv run pyright app && uv run bandit -r app -c pyproject.toml
```

Fix auto-fixable issues (format + safe lint fixes):

```bash
uv run ruff format app tests && uv run ruff check app tests --fix
```

CI (GitHub Actions) runs these checks plus pytest on push/PR to `main`/`master` (see `.github/workflows/quality.yml`).

## Testing

Tests use **pytest** with **pytest-cov** for coverage.

### Run tests

From the `backend` directory:

```bash
uv sync --all-extras   # install dev dependencies (pytest, pytest-cov, etc.)
uv run pytest tests/
```

### Run tests with coverage

```bash
uv run pytest tests/ --cov=app --cov-report=term-missing --cov-report=html
```

- `--cov-report=term-missing` prints missing line numbers in the terminal.
- `--cov-report=html` writes an HTML report to `htmlcov/` (open `htmlcov/index.html` in a browser).

### Database requirement

Most tests need a **PostgreSQL** database. Set either:

- `TEST_DATABASE_URL` (e.g. `postgresql://user:pass@localhost:5432/cppm_test`), or  
- `DATABASE_URL`

to a running PostgreSQL instance. If the database is not available, tests that depend on it are **skipped**; tests that do not need the DB (e.g. config, dependencies, parsers, OAuth with mocks) still run.

### Coverage target

Aim for high line coverage of `app/` (e.g. 80%+). With a test DB, run the full suite and check the report; adjust `[tool.coverage.run]` and `[tool.coverage.report]` in `pyproject.toml` as needed.
