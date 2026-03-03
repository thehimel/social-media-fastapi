# Commands

## Management

```shell
uvicorn app.main:app --reload
```

## Docker Compose (PostgreSQL)

```shell
# Start PostgreSQL in the background
docker compose up -d

# Check service status
docker compose ps

# Stop PostgreSQL
docker compose down

# Stop and remove the database volume (deletes data)
docker compose down -v

# Create database if missing (e.g. after changing POSTGRES_DB in .env)
docker compose exec postgres psql -U postgres -c "CREATE DATABASE \"kodekloud-fastapi\";"

# Verify connection from host (replace DB name if different)
docker compose exec postgres psql -U postgres -d kodekloud-fastapi -c "SELECT 1;"

# Inspect PostgreSQL logs
docker compose logs postgres
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
