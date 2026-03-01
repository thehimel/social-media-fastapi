# Commands

## Management

```shell
uvicorn app.main:app --reload
```

## Ruff

```shell
# Lint
ruff check .

# Format
ruff format .

# Lint with auto-fix
ruff check . --fix

# Lint and format specific path
ruff check app/
ruff format app/
```

## Pre-commit

```shell
# Install pre-commit hooks (run once)
pre-commit install

# Run pre-commit on all files
pre-commit run --all-files

# Run pre-commit on staged files only (default when run on commit)
pre-commit run
```

## Install Dependencies

```shell
# Install FastAPI with all optional dependencies; Note quotes to avoid shell issues with brackets
pip install "fastapi[all]"
```
