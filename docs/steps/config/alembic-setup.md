# Alembic Setup

[Source](https://notes.kodekloud.com/docs/Python-API-Development-with-FastAPI/Database-Migration/Alembic-Setup/page) |
[Video](https://learn.kodekloud.com/user/courses/python-api-development-with-fastapi/module/a6a7b30d-5ca7-4d69-a323-c508340e9931/lesson/3ad8ae82-a1b2-4e6c-b89a-b2bae924f121)

This guide walks through setting up **Alembic** for migration management with SQLAlchemy in this FastAPI project. It is adapted from the KodeKloud course to match the project structure.

## Project Structure

After setup, migration scripts live in `alembic/versions/`:

```text
kodekloud-fastapi/
    alembic/
        versions/
            abc123_initial_schema_posts_and_users.py
            def456_add_phone_number.py
        env.py
    alembic.ini
    app/
```

## Commands

| Alembic | Purpose | Django Equivalent |
|---------|---------|-------------------|
| `alembic revision --autogenerate -m "message"` | Create migration from model changes | `python manage.py makemigrations` |
| `alembic upgrade head` | Apply all pending migrations | `python manage.py migrate` |
| `alembic downgrade -1` | Roll back one revision | `python manage.py migrate <app> <prev_rev>` |
| `alembic current` | Show current revision | `python manage.py showmigrations` |
| `alembic history` | List migration history | `python manage.py showmigrations` |

---

## Prerequisites

- PostgreSQL running (e.g. via `docker compose up -d`)
- `.env` configured with `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_HOST`, `POSTGRES_PORT`, `POSTGRES_DB`
- Application uses [app/database.py](../../app/database.py) and [app/config.py](../../app/config.py)
- SQLAlchemy models (Post, User) already defined in [app/posts/models.py](../../app/posts/models.py) and [app/users/models.py](../../app/users/models.py)

---

## Step 1: Stop the Application and Reset the Database

Stop the FastAPI server before running migrations to avoid conflicts.

To start with a clean slate (required when switching from `create_all` to Alembic), remove the existing database volume:

```bash
docker compose down -v
docker compose up -d
```

This deletes all data. Omit `-v` if you want to preserve existing data.

To inspect current data before resetting:

```sql
SELECT * FROM public.posts ORDER BY id ASC;
```

---

## Step 2: Install Alembic

```bash
pip install alembic
```

Add `alembic` to [requirements.txt](../../requirements.txt), then verify:

```bash
alembic --help
```

---

## Step 3: Initialize Alembic

From the **project root** (the directory containing `app/`, `docker-compose.yml`, etc.):

```bash
alembic init alembic
```

This creates:

- `alembic/` — migration scripts directory
- `alembic/versions/` — revision files
- `alembic.ini` — main config file
- `alembic/env.py` — environment and metadata config

---

## Step 4: Configure env.py

Edit `alembic/env.py` to use this project’s settings and models.

**4.1** Add the project root to `sys.path` at the top (after existing imports):

```python
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
```

**4.2** After `config = context.config`, import `Base` and settings, and override the database URL (avoids hardcoding credentials in `alembic.ini`):

```python
from app.database import Base
from app.config import settings

config.set_main_option(
    "sqlalchemy.url",
    f"postgresql+psycopg2://{settings.postgres_user}:{settings.postgres_password}"
    f"@{settings.postgres_host}:{settings.postgres_port}/{settings.postgres_db}",
)
```

**4.3** Set `target_metadata` so Alembic can detect schema changes:

```python
target_metadata = Base.metadata
```

**4.4** Import all models so they are registered with `Base.metadata`:

```python
from app.posts.models import Post  # noqa: F401
from app.users.models import User  # noqa: F401
```

**Example `env.py` snippet** (merge with your existing `env.py` structure):

```python
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context

from app.database import Base
from app.config import settings
from app.posts.models import Post  # noqa: F401
from app.users.models import User  # noqa: F401

config = context.config
config.set_main_option(
    "sqlalchemy.url",
    f"postgresql+psycopg2://{settings.postgres_user}:{settings.postgres_password}"
    f"@{settings.postgres_host}:{settings.postgres_port}/{settings.postgres_db}",
)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)
target_metadata = Base.metadata
```

---

## Step 5: Configure alembic.ini

The URL is overridden in `env.py` from `.env`, so you can leave the placeholder in `alembic.ini` or set a dummy value:

```ini
sqlalchemy.url = postgresql+psycopg2://user:pass@localhost/dbname
```

`env.py` will override this at runtime. Avoid hardcoding credentials in `alembic.ini`; use environment variables via `env.py` in production.

---

## Step 6: Remove create_all

Remove the old table-creation code from [app/main.py](../../app/main.py) so Alembic is the single source of truth:

- Remove `Base.metadata.create_all(bind=engine)` and its comment
- Remove imports: `Base`, `engine`, `Post`, `User` (keep only `get_db` from `app.database`)

---

## Step 7: Create and Run the First Migration

**7.1** Generate the initial revision (captures current schema):

```bash
alembic revision --autogenerate -m "Initial schema: posts and users"
```

**7.2** Inspect the generated file in `alembic/versions/` and fix any issues.

**7.3** Apply the migration:

```bash
alembic upgrade head
```

**7.4** Confirm the database state:

```bash
alembic current
```

**7.5** Start the FastAPI server again.

---

## Schema Changes

When you add or remove columns (e.g. remove `phone_number` from `User`), create a new migration:

```bash
alembic revision --autogenerate -m "Remove phone_number from users"
alembic upgrade head
```

Inspect the generated file in `alembic/versions/` before applying.

---

## Troubleshooting

- **Import errors**: Ensure the project root is in `sys.path` in `env.py`.
- **No changes detected**: Confirm all models are imported in `env.py` and inherit from `Base`.
- **Connection refused**: Check PostgreSQL is running and `.env` matches your setup.
