# Async Routes in This App

## We don't have any async route. Is there any route where we can use async?

**Short answer:** No. Not with the current setup. All routes that use the database should stay as sync `def`. Using `async def` with sync DB calls would block the event loop and hurt concurrency.

## Why do we use sync routes?

The app uses **sync SQLAlchemy**:

- `create_engine` (not `create_async_engine`)
- `Session` (sync session, not `AsyncSession`)
- `psycopg2` driver (sync)

See [app/database.py](../../app/database.py). The `get_db` dependency yields a sync `Session`; all services use sync DB access.

**Rule:** Use `async def` only when the work inside uses **async I/O libraries**. Use `def` when the work uses **sync-only libraries** — FastAPI runs sync endpoints in a thread pool so they don't block the event loop.

## Which routes could be async?

Only routes that do **no** database or other blocking I/O could safely be `async def`. In this app:

- **`root()`** — `/` has no I/O. Making it `async def` would be harmless but not useful.
- **All other routes** — `health_db`, posts, users, auth — use the DB via `get_db`. They must stay sync `def`.

**Avoid:** `async def` with sync DB calls. That blocks the event loop and hurts concurrency:

```python
# ❌ BAD — sync DB inside async def blocks the event loop
@router.get("/posts")
async def get_posts(db: Session = Depends(get_db)):
    return db.query(Post).all()  # blocks!
```

**Correct:** Keep sync `def` with sync DB:

```python
# ✅ OK — FastAPI runs sync endpoints in a thread pool
@router.get("/posts")
def get_posts(db: Session = Depends(get_db)):
    return db.query(Post).all()
```

## What would we need to use async effectively?

To use `async def` for DB routes, you would need:

1. **Async SQLAlchemy** — `create_async_engine`, `AsyncSession`, `async_sessionmaker`
2. **Async driver** — `asyncpg` instead of `psycopg2`
3. **Async `get_db`** — yield `AsyncSession` instead of `Session`
4. **`await` in services** — all DB calls use `await session.execute(...)`, etc.

Until that migration is done, keep all DB routes as sync `def`. See [async-concurrency.md](./async-concurrency.md) for the general async vs sync rules in FastAPI.
