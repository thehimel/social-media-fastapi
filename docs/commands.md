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

## Install Dependencies

```shell
# Install FastAPI with all optional dependencies; Note quotes to avoid shell issues with brackets
pip install "fastapi[all]"
```
