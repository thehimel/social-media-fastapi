# Server Basics

## When we access FastAPI at `http://127.0.0.1:8000/`, the log shows ports like `62304`, `62354`, etc. Why?

The port in the log is the **client port**, not the server port. The server listens on 8000. When a client connects, the OS assigns an ephemeral port to the client side of the connection. So `127.0.0.1:62304` means the request came from a client at that IP using client port 62304. Each connection has two endpoints: server (8000) and client (random high port).

## What is Uvicorn and what does `uvicorn main:app --reload` do?

**Uvicorn** is the server — the process that listens for HTTP requests and runs your app. FastAPI is a framework; it needs a server like Uvicorn to handle the actual HTTP traffic. Uvicorn implements the ASGI interface. The command `uvicorn main:app --reload` means: load the `app` object from the `main` module, and use `--reload` to restart on code changes (dev only).
