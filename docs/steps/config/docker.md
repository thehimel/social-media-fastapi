# Docker Setup

This guide explains the **Docker** configuration for the FastAPI application: why each file exists, how they relate, and notable concepts such as `build`, **volumes**, and **bind mounts**.

## Why These Files Exist

| File | Purpose |
|------|---------|
| [Dockerfile](../../../Dockerfile) | Defines how to build the **API image** (base image, dependencies, startup command). Used by both dev and prod. |
| [docker-compose.dev.yml](../../../docker-compose.dev.yml) | Orchestrates **development**: API + PostgreSQL with bind mount and `--reload` for fast iteration. |
| [docker-compose.prod.yml](../../../docker-compose.prod.yml) | Orchestrates **production**: API + PostgreSQL without bind mount, port 80, optimized for stability. |

## Relationship Between the Files

```
Dockerfile ─────────────────────────────────────────────────────────────┐
     │                                                                  │
     │  build: .                                                        │
     ▼                                                                  │
docker-compose.dev.yml  ──►  API container (port 8000, bind mount, --reload)
docker-compose.prod.yml ──►  API container (port 80, no bind mount)
     │
     └──► postgres service (shared in both)
```

- **Dockerfile** is the blueprint for the API image. Both compose files reference it via `build: .`.
- **docker-compose.dev.yml** and **docker-compose.prod.yml** define the same services (API + PostgreSQL) but with different settings for each environment.
- The **PostgreSQL** service is nearly identical in both; the main differences are in the **API** service.

## Notable Concepts

### `api: build: .`

The `build: .` directive tells Docker Compose to:

1. Look for a [Dockerfile](../../../Dockerfile) in the current directory (`.`)
2. Build an image from that Dockerfile
3. Use that image to run the API container

Without `build: .`, you would need to run `docker build` manually and then reference the image by name (e.g. `image: my-fastapi-app`). With `build: .`, Compose builds the image automatically when you run `docker compose up` or `docker compose up --build`.

### Volumes

**Volumes** persist data and can share files between the host and the container. There are two types used here:

| Type | Syntax | Purpose |
|------|--------|---------|
| **Named volume** | `postgres_data:/var/lib/postgresql/data` | Persists PostgreSQL data. Survives container restarts and removals. |
| **Bind mount** | `.:/usr/src/app` | Mounts the host project directory into the container. Used only in dev. |

**Where is `postgres_data` stored?** Docker stores named volumes in its internal storage. On Linux: `/var/lib/docker/volumes/<project_name>_postgres_data/_data`. On Mac/Windows with Docker Desktop, it lives inside the Docker VM. Run `docker volume ls` to list volumes (Compose prefixes the name with the project, e.g. `kodekloud-fastapi_postgres_data`), then `docker volume inspect <volume_name>` to see the exact path.

### Bind Mount (Development Only)

In [docker-compose.dev.yml](../../../docker-compose.dev.yml):

```yaml
volumes:
  - .:/usr/src/app
```

This **bind mount** maps the host project directory (`.`) to `/usr/src/app` inside the container. It does **not** copy the codebase—it creates a **live link**. The container sees the host directory directly, so when you edit a file on the host, the container sees the change immediately (same files, no sync or copy). As a result:

- **Edits on the host** (e.g. in your IDE) are **immediately visible** inside the container.
- Combined with `--reload`, Uvicorn restarts when you change code, so you get a fast feedback loop without rebuilding the image.

**Why not `:ro` (read-only)?** Some guides use `./:/usr/src/app:ro` to prevent the container from modifying host files. We use read-write because Python writes `__pycache__` when importing, and tools like Alembic (if run inside the container) need to write migration files. With `:ro`, those writes would fail. Read-write is the default and matches typical Python development workflows.

**Production** ([docker-compose.prod.yml](../../../docker-compose.prod.yml)) does **not** use a bind mount. The container runs the code baked into the image at build time, which is more stable and predictable.

### `depends_on` and `condition: service_healthy`

```yaml
depends_on:
  postgres:
    condition: service_healthy
```

This ensures the API container starts only after PostgreSQL is **ready to accept connections**. The `healthcheck` on the postgres service runs `pg_isready`; once it passes, the API can start. Without this, the API might start before PostgreSQL is ready and fail to connect.

### Port Mapping

| Environment | Mapping | Access |
|-------------|---------|--------|
| **Dev** | `8000:8000` | `http://localhost:8000` |
| **Prod** | `80:8000` | `http://localhost` (port 80 is the default HTTP port) |

### `--reload` (Development Only)

In dev, the API runs with:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

The `--reload` flag makes Uvicorn watch for file changes and restart the app automatically. This is useful in development but should be **disabled in production** because it adds overhead and is not suitable for multi-worker setups.

## Quick Reference

| Action | Dev | Prod |
|--------|-----|------|
| Start | `docker compose -f docker-compose.dev.yml up -d` | `docker compose -f docker-compose.prod.yml up -d` |
| Rebuild | `docker compose -f docker-compose.dev.yml up --build -d` | `docker compose -f docker-compose.prod.yml up --build -d` |
| Stop | `docker compose -f docker-compose.dev.yml down` | `docker compose -f docker-compose.prod.yml down` |

See [Commands](../../commands.md#docker) for the full list of Docker-related commands.
