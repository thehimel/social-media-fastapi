# Async and Concurrency

## What is ASGI? Is it a server?

**ASGI** (Asynchronous Server Gateway Interface) is *not* a server — it's an interface/specification that defines how apps and servers talk to each other. Uvicorn is the server; ASGI is the contract it implements. ASGI is the async successor to **WSGI** (Web Server Gateway Interface), adds WebSockets and HTTP/2, and is used by FastAPI, Starlette, and Django async.

## Which async library(s) does FastAPI use?

**Starlette** — FastAPI is built on Starlette, an ASGI framework. Starlette provides routing, middleware, WebSockets, and the request/response cycle. **asyncio** — Python's built-in async library; Starlette (and thus FastAPI) runs on asyncio's event loop. **anyio** — Used by Starlette to run sync endpoints in a thread pool.

- **Async:** FastAPI → Starlette → asyncio (event loop)
- **Sync:** FastAPI → Starlette → anyio → thread pool

## What is a process, thread, event, and coroutine?

**Process** — A running program with its own memory. Like a **factory**: separate building, own resources. Processes don't share memory; they're isolated.

*FastAPI:* Running `uvicorn app.main:app` starts one process. Each Gunicorn worker is a separate process.

**Thread** — A unit of execution inside a process. Like a **worker in the factory**: multiple workers share the same space and resources. Same process, same memory.

*FastAPI:* Sync endpoints (`def get_orders()`) run in threads from the thread pool. Multiple concurrent sync requests use multiple threads from the pool.

**Event** — A signal that something happened. Like a **doorbell**: when it rings, you react. Event-driven code waits for events and responds instead of polling.

*FastAPI:* An HTTP request is an event. WebSocket messages are events. `@app.on_event("startup")` and `@app.on_event("shutdown")` hook into lifecycle events.

**Coroutine** — A task that can pause and resume. Like a **bookmark in a book**: you pause at `await`, do other work, then resume where you left off. Used in async Python.

*FastAPI:* Every `async def` endpoint is a coroutine, e.g. `async def get_user(id: int): ...`. When it hits `await session.execute(...)`, it pauses and lets other requests run.

## What is the event loop and thread pool?

**Event loop** — The core of async Python. It runs in a single thread and schedules coroutines: when one hits `await` (e.g. waiting for a DB or HTTP response), it pauses that coroutine and runs others. No blocking I/O in the loop means many requests can be handled concurrently.

**Thread pool** — A fixed set of worker threads for running sync (blocking) code. When a sync FastAPI endpoint runs, it's offloaded to a thread from the pool so the event loop stays free. The event loop handles async work; the thread pool handles sync work.

## Is the thread pool size a hard limit? What happens if all threads are busy?

**No fixed limit** — The pool has a max size (default: often `min(32, cpu_count + 4)` in Python). It's configurable. **If all threads are busy**, new sync requests wait in a queue until a thread is free. They don't fail; they just block until a worker is available. Too many concurrent sync requests can cause latency. Prefer async for I/O-bound endpoints to avoid saturating the pool.

## What is `async` and `await` in FastAPI? Python is single-threaded — how is concurrency achieved? Is Python multithreaded here?

**`async def`** — Marks a function as a coroutine. It can pause and resume. FastAPI treats it as async and runs it in the event loop.

**`await`** — Used inside `async def` to wait for an async operation (DB, HTTP, etc.). It yields control to the event loop so other coroutines can run while waiting. The coroutine resumes when the awaited operation completes. Without `await`, the call would block.

**Single-threaded concurrency** — The event loop runs in one thread. It achieves concurrency through cooperative multitasking: when a coroutine awaits I/O, the loop pauses it and runs others. No parallelism — just switching between tasks while I/O is in progress. One thread, many concurrent requests.

**Is Python multithreaded here?** — **Yes.** FastAPI uses multiple threads: one for the event loop (async work) and a thread pool for sync endpoints. So the process is multithreaded. Async endpoints run in the single event-loop thread; sync endpoints run in separate threads from the pool.

## When do we need `async def` in FastAPI?

Use **`async def`** when the work inside is **I/O-bound and uses async libraries**. The event loop can run other requests while waiting. Use **`def`** (sync) when the work is **CPU-bound** or uses **sync-only libraries** — FastAPI runs sync endpoints in a thread pool so they don't block the event loop.

**Use async** — external APIs, DB, cache, file I/O with async clients:

```python
# External API with httpx (async)
@router.get("/quote")
async def get_quote():
    async with httpx.AsyncClient() as client:
        r = await client.get("https://api.example.com/quote")
    return r.json()

# DB with asyncpg or SQLAlchemy 2.0 async
@router.get("/user/{id}")
async def get_user(id: int):
    async with async_session() as session:
        result = await session.execute(select(User).where(User.id == id))
    return result.scalar_one()
```

**Use sync** — sync DB drivers, `requests`, CPU-heavy work:

```python
# Sync DB (psycopg2, SQLAlchemy sync) — FastAPI runs in thread pool
@router.get("/orders")
def get_orders():
    with Session() as session:
        return session.query(Order).all()

# CPU-bound — must be sync so it runs in thread pool
@router.post("/process")
def heavy_compute(data: Payload):
    return expensive_calculation(data)
```

**Avoid** — `async def` that does sync (blocking) I/O. It blocks the event loop and hurts concurrency. For DB: use async def only with async drivers (asyncpg, SQLAlchemy async); use sync `def` with sync drivers (psycopg2, SQLAlchemy `Session`). Mixing `async def` + sync driver blocks the loop.

```python
# ❌ BAD — requests is sync; blocks the event loop
@router.get("/bad")
async def bad_external():
    r = requests.get("https://api.example.com/data")  # blocks!
    return r.json()

# ❌ BAD — time.sleep blocks
async def bad_delay():
    await asyncio.sleep(1)   # ✅ OK
    time.sleep(1)            # ❌ blocks event loop

# ❌ BAD — sync DB driver (Session, psycopg2) inside async def blocks
# Use async def + async driver (asyncpg, SQLAlchemy async) OR def + sync driver
async def bad_db():
    with Session() as session:           # sync driver
        return session.query(User).all()  # blocks!

# ❌ BAD — sync file I/O
async def bad_file():
    with open("data.json") as f:         # blocks!
        return json.load(f)
```

**Fix** — Use `def` (sync) so FastAPI runs it in the thread pool, or switch to async libraries (`httpx`, `aiofiles`, `asyncpg`, etc.).
