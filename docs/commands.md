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

## Alembic

Run from the project root. See [Alembic Setup](steps/config/alembic-setup.md) for full guide.

| Alembic | Purpose | Django equivalent |
|---------|---------|-------------------|
| `alembic revision --autogenerate -m "message"` | Create migration from model changes | `python manage.py makemigrations` |
| `alembic revision -m "message"` | Create manual migration (no autogenerate) | `python manage.py makemigrations` |
| `alembic upgrade head` | Apply all pending migrations | `python manage.py migrate` |
| `alembic upgrade <revision>` | Upgrade to a specific revision | `python manage.py migrate <app> <revision>` |
| `alembic downgrade -1` | Roll back one revision | `python manage.py migrate <app> <prev_rev>` |
| `alembic downgrade <revision>` | Roll back to a specific revision | `python manage.py migrate <app> <revision>` |
| `alembic current` | Show current revision | `python manage.py showmigrations` |
| `alembic heads` | Show latest (head) migration | `python manage.py showmigrations` |
| `alembic history` | List migration history | `python manage.py showmigrations` |

**Note:** `alembic downgrade -N` works for any negative N (e.g. `-2`, `-3`) to roll back multiple revisions. For branched migrations, prefer `alembic downgrade <revision>` with a specific revision ID.

Verify applied migrations in PostgreSQL:

```shell
docker compose exec postgres psql -U postgres -d kodekloud-fastapi -c "SELECT * FROM public.alembic_version ORDER BY version_num ASC;"
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
