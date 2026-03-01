# Server Basics

## When we access FastAPI at `http://127.0.0.1:8000/`, the log shows ports like `62304`, `62354`, etc. Why?

The port in the log is the **client port**, not the server port. The server listens on 8000. When a client connects, the OS assigns an ephemeral port to the client side of the connection. So `127.0.0.1:62304` means the request came from a client at that IP using client port 62304. Each connection has two endpoints: server (8000) and client (random high port).

## What is Uvicorn and what does `uvicorn app.main:app --reload` do?

**Uvicorn** is the server — the process that listens for HTTP requests and runs your app. FastAPI is a framework; it needs a server like Uvicorn to handle the actual HTTP traffic. Uvicorn implements the ASGI interface. The command `uvicorn app.main:app --reload` means: load the `app` object from the `app.main` module, and use `--reload` to restart on code changes (dev only).

## What are `tags` in FastAPI?

**Tags** group endpoints in the interactive docs (Swagger UI at `/docs`, ReDoc at `/redoc`). They organize related endpoints under a heading (e.g. "Posts") and make the API easier to browse. Tags are documentation-only — they don't affect routing or behavior. Set them on `include_router(tags=["Posts"])`, on each route `@router.get(..., tags=["Posts"])`, or on the `APIRouter(tags=["posts"])`.

## What is the difference between PUT and PATCH?

**PUT** — Full replacement. The client sends the entire resource. The server replaces the resource with the request body. Missing fields are typically cleared or set to defaults. Use for "replace this resource with this exact representation." Idempotent.

**PATCH** — Partial update. The client sends only the fields to change. The server merges those fields into the existing resource. Unmentioned fields stay unchanged. Use for "update only these fields." Idempotent.

**Summary:** PUT = replace whole resource; PATCH = update specific fields.

## What is idempotent?

**Idempotent** — Performing the same operation multiple times has the same effect as doing it once. Example: calling `PUT /posts/1` with the same body ten times leaves the resource in the same state as calling it once. GET, PUT, PATCH, DELETE are typically idempotent; POST is not (each call usually creates a new resource).

## Why use `next()` for finding the first match in a list?

**`next(iterator, default)`** returns the first item from an iterator, or `default` if the iterator is empty. For "find first match or None":

```python
return next((p for p in posts if p.id == id), None)
```

- `(p for p in posts if p.id == id)` — generator that yields matching items
- `next(..., None)` — first match, or `None` if no match (avoids `StopIteration` or `IndexError`)

**Why not a loop?** Same result, but `next()` is concise and idiomatic. **Why not `filter()`?** `list(filter(...))[0]` raises `IndexError` when empty; `next(..., None)` returns `None` safely.

## What is idiomatic?

**Idiomatic** — Written in the natural, conventional way for that language. Code that uses the language's built-in features and common patterns, not patterns borrowed from other languages. Example: `for item in items:` is idiomatic Python; `for i in range(len(items)):` is not. When we say "idiomatic," we mean the standard, preferred way experienced developers write it.
