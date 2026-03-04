# Architectural Patterns

## Which architectural pattern have you used for API design in this project?

**Modular monolith** with **REST resource-oriented** API and a central **API aggregator**. Features are grouped as modules (`posts`); each module owns its router, service, schemas, and models. The `api/router` aggregates sub-routers with prefixes and tags.

**File tree:**

```
app/
├── main.py                 # FastAPI app; includes api_router with prefix /api
├── api/
│   ├── __init__.py
│   └── router.py           # Central aggregator; includes posts_router with prefix /posts
├── posts/
│   ├── __init__.py
│   ├── router.py           # GET /, POST / for posts
│   ├── service.py
│   ├── schemas.py
│   └── models.py
└── __init__.py
```

**Routes:** `GET /`, `GET /api/posts`, `POST /api/posts`.

| Term        | Description                                                        |
|-------------|--------------------------------------------------------------------|
| **router**  | HTTP routes; defines endpoints; calls service; thin layer          |
| **service** | Business logic; orchestrates; may call repository or external APIs |
| **schemas** | Pydantic models; request/response validation; API contract         |
| **models**  | DB/ORM entities; table definitions; used for persistence           |

---

## What are common architectural patterns used for API design?

Common patterns for API design, with social media app examples, pros/cons, and file structure.

---

## Layered (N-tier)

**Metaphor:** Like a **building with floors** — reception on top, offices in the middle, storage in the basement. Requests flow down; data flows up. Each floor has a single job.

Split by technical responsibility: **API** → **business logic** → **data access** → **DB**. Each layer depends only on the layer below.

**Pros:** Clear separation, easy to onboard, testable layers.

**Cons:** Changes often span multiple layers; can become a "big ball of mud" if layers grow too thick.

**File tree (social media):**

```
app/
├── api/                    # Presentation layer
│   └── routes/
│       ├── posts.py
│       ├── users.py
│       └── feed.py
├── services/               # Business logic layer
│   ├── post_service.py
│   ├── user_service.py
│   └── feed_service.py
├── repositories/           # Data access layer — CRUD, queries, DB calls only
│   ├── post_repository.py
│   ├── user_repository.py
│   └── feed_repository.py
└── models/                 # Domain/DB models
    ├── post.py
    └── user.py
```

| Term             | Description                                                          |
|------------------|----------------------------------------------------------------------|
| **api/routes**   | HTTP entry point; receives requests, calls service, returns response |
| **services**     | Business logic; orchestrates repositories; no DB or HTTP details     |
| **repositories** | Data access; CRUD, queries, DB session; no business logic            |
| **models**       | Domain/DB entities; ORM or plain classes; shape of data in DB        |

**Repository** — CRUD operations, raw queries, and DB session handling. No business logic. Example: `get_by_id()`, `create()`, `update()`, `delete()`, `list_by_user()`. The service layer calls the repository; the repository talks to the DB.

---

## Modular monolith

**Metaphor:** Like a **department store** — one building, many sections (clothing, electronics, groceries). Each section runs its own area; they share the same roof and checkout (app) but stay organized by department.

One deployable app; features grouped as **modules**. Each module owns its routes, logic, and data access.

**Pros:** Simple deployment, clear boundaries, can evolve into microservices later.

**Cons:** Shared DB; modules can still couple if not disciplined.

**File tree (social media):**

```
app/
├── main.py
├── api/
│   └── router.py           # Aggregates all modules
├── posts/
│   ├── router.py
│   ├── service.py
│   ├── repository.py
│   ├── models.py           # DB/ORM models for posts
│   └── schemas.py
├── users/
│   ├── router.py
│   ├── service.py
│   ├── repository.py
│   ├── models.py           # DB/ORM models for users
│   └── schemas.py
├── feed/
│   ├── router.py
│   ├── service.py
│   └── schemas.py          # Feed often reads from posts/users; may not have its own models
└── comments/
    ├── router.py
    ├── service.py
    ├── repository.py
    ├── models.py           # DB/ORM models for comments
    └── schemas.py
```

| Term           | Description                                                  |
|----------------|--------------------------------------------------------------|
| **router**     | HTTP routes; defines endpoints; calls service; thin layer    |
| **service**    | Business logic; calls repository; validates and orchestrates |
| **repository** | Data access; CRUD and queries; talks to DB                   |
| **models**     | DB/ORM entities; table definitions; used by repository       |
| **schemas**    | Pydantic models; request/response validation; API contract   |

---

## Vertical slice

**Metaphor:** Like a **pizza slice** — each slice goes from crust to tip (top to bottom). One slice = one use case, end to end. Cut the pizza by feature, not by ingredient.

Organize by **use case**, not layer. Each slice has its own handler, logic, and data access.

**Pros:** Changes stay in one slice; no cross-layer edits; good for DDD.

**Cons:** Some duplication; slices can diverge in style.

**File tree (social media):**

```
app/
├── slices/
│   ├── create_post/
│   │   ├── handler.py
│   │   ├── service.py
│   │   └── schemas.py
│   ├── get_feed/
│   │   ├── handler.py
│   │   ├── service.py
│   │   └── schemas.py
│   ├── like_post/
│   │   ├── handler.py
│   │   └── service.py
│   └── add_comment/
│       ├── handler.py
│       ├── service.py
│       └── schemas.py
└── shared/
    └── models.py
```

| Term        | Description                                                                      |
|-------------|----------------------------------------------------------------------------------|
| **handler** | HTTP entry point for the slice; validates input, calls service, returns response |
| **service** | Use-case logic; may include DB access; slice-specific                            |
| **schemas** | Pydantic models; request/response validation for the slice                       |
| **models**  | Shared DB entities; used across slices                                           |

**Handler** — HTTP entry point for the slice. Receives the request, validates input (via schemas), calls the service, and returns the response. Thin: no business logic. Example: `create_post` handler parses JSON → validates with `PostCreate` schema → calls `post_service.create()` → returns `Post`.

---

## Hexagonal (Ports and Adapters)

**Metaphor:** Like a **plug socket** — the core (domain) defines the shape of the plug (port). You can plug in different devices (adapters): a lamp, a charger, a different brand. Swap adapters without changing the socket.

**Domain** at the center; **ports** (interfaces) define what the domain needs; **adapters** implement those interfaces. Domain has no dependency on HTTP, DB, or external services. Inbound adapters (HTTP, CLI) drive the app; outbound adapters (DB, email) are driven by the domain.

**Pros:** Domain isolated from frameworks; easy to test (mock adapters); swap DB or API without touching core logic.

**Cons:** More abstraction; can feel like overkill for simple CRUD.

**File tree (social media):**

```
app/
├── domain/                 # Core — pure business logic, no I/O
│   ├── post.py
│   ├── user.py
│   └── entities.py
├── ports/                  # Interfaces (what the domain needs)
│   ├── post_repository.py  # Abstract: save, get_by_id, list
│   └── notifier.py         # Abstract: notify_followers
├── adapters/
│   ├── inbound/            # Entry points — drive the domain
│   │   └── http/
│   │       └── fastapi_routes.py
│   └── outbound/           # Implementations — driven by domain
│       ├── postgres_post_repository.py
│       └── email_notifier.py
└── main.py                 # Wires adapters to domain
```

| Term                  | Description                                                              |
|-----------------------|--------------------------------------------------------------------------|
| **domain**            | Core business logic; pure Python; no I/O, no frameworks                  |
| **ports**             | Interfaces (abstract); define what domain needs; implemented by adapters |
| **adapters/inbound**  | Entry points; HTTP, CLI; receive input, call domain                      |
| **adapters/outbound** | Implementations; DB, email; domain calls these via ports                 |

**Port** — Interface the domain defines. Example: `PostRepository` with `save(post)`, `get_by_id(id)`. The domain calls the port; an adapter implements it.

---

## CQRS (Command Query Responsibility Segregation)

**Metaphor:** Like a **restaurant** — the kitchen (write) and the menu (read) are separate. The kitchen handles orders; the menu is a pre-made, optimized view. Different flows for different purposes.

Separate **read** and **write** paths. Write path for commands; read path optimized for queries (denormalized, cached).

**Pros:** Optimize reads and writes independently; flexible read models; scales well.

**Cons:** More complexity; eventual consistency; two models to maintain.

**File tree (social media):**

```
app/
├── commands/               # Write path
│   ├── create_post/
│   │   ├── handler.py
│   │   └── model.py
│   ├── update_post/
│   └── delete_post/
├── queries/                # Read path
│   ├── get_feed/
│   │   ├── handler.py
│   │   └── read_model.py   # Denormalized, cached
│   ├── get_post/
│   └── get_user_posts/
└── shared/
    └── event_bus.py        # Optional: sync read models
```

| Term           | Description                                                          |
|----------------|----------------------------------------------------------------------|
| **commands**   | Write path; handlers that create/update/delete; change state         |
| **queries**    | Read path; handlers that fetch data; optimized, denormalized, cached |
| **handler**    | Entry point for command or query; thin; delegates to logic           |
| **model**      | Write model; normalized; used by commands                            |
| **read_model** | Read model; denormalized; optimized for queries; may be cached       |

---

## Event-driven

**Metaphor:** Like a **bulletin board** — someone pins a note (event); whoever cares reacts. No one talks directly; the board is the middleman. Add new readers without changing the poster.

Components emit **events**; others react asynchronously. Loose coupling via message bus or queue.

**Pros:** Loose coupling; scalable; async processing; easy to add new consumers.

**Cons:** Harder to trace; eventual consistency; operational complexity.

**File tree (social media):**

```
app/
├── api/
│   ├── posts.py
│   ├── users.py
│   └── feed.py
├── events/
│   ├── post_created.py
│   ├── comment_added.py
│   └── user_followed.py
├── handlers/               # Event consumers
│   ├── update_feed_on_post.py
│   ├── notify_followers.py
│   └── update_comment_count.py
├── event_bus.py            # Kafka, RabbitMQ, etc.
└── services/
    ├── post_service.py
    └── feed_service.py
```

| Term          | Description                                                             |
|---------------|-------------------------------------------------------------------------|
| **api**       | HTTP routes; receives requests; may emit events; calls services         |
| **events**    | Event definitions; payloads emitted when something happens              |
| **handlers**  | Event consumers; react to events; update feed, send notifications, etc. |
| **event_bus** | Message queue or broker; delivers events to handlers                    |
| **services**  | Business logic; may be called by api or triggered by events             |

---

## Microservices

**Metaphor:** Like a **mall** — each store is independent: its own staff, inventory, and hours. They share the building (network) but run separately. One store can close without affecting others.

Separate **services** per domain. Each has its own API, DB, and deployment.

**Pros:** Independent scaling and deployment; team ownership; technology flexibility.

**Cons:** Distributed complexity; network latency; eventual consistency; ops overhead.

**File tree (social media):**

```
services/
├── posts-service/
│   ├── app/
│   │   ├── main.py
│   │   ├── router.py
│   │   └── models.py
│   └── Dockerfile
├── users-service/
│   ├── app/
│   └── Dockerfile
├── feed-service/
│   ├── app/
│   └── Dockerfile
├── notifications-service/
│   ├── app/
│   └── Dockerfile
└── api-gateway/            # Single entry point
    └── ...
```

| Term          | Description                                                                 |
|---------------|-----------------------------------------------------------------------------|
| **router**    | HTTP routes within the service; defines endpoints                           |
| **models**    | DB/ORM entities; service-specific; each service has its own DB              |
| **main**      | Service entry point; wires routes and dependencies                          |

---

## API Gateway

**Metaphor:** Like a **hotel concierge** — you talk to one person who checks you in, directs you to the right place, and handles requests. They don't do the work; they route and coordinate.

**Single entry point** for all client requests. Handles auth, rate limiting, routing to backend services.

**Pros:** Centralized auth, rate limiting, routing; hides internal topology.

**Cons:** Single point of failure; extra network hop; can become a bottleneck.

**File tree (social media):**

```
gateway/
├── config/
│   └── routes.yml         # /posts → posts-service, /feed → feed-service
├── middleware/
│   ├── auth.py
│   └── rate_limit.py
└── main.py

services/
├── posts-service/
├── users-service/
└── feed-service/
```

| Term              | Description                                                 |
|-------------------|-------------------------------------------------------------|
| **config/routes** | Route mapping; which path forwards to which backend service |
| **middleware**    | Auth, rate limiting, logging; runs before routing           |
| **main**          | Gateway entry point; loads config and middleware            |

---

## REST resource-oriented

**Metaphor:** Like a **library** — books (resources) are organized by category. You browse (GET), borrow (POST), return (PUT), or remove (DELETE). Standard actions on standard things.

Design around **resources** and **HTTP verbs**. URLs represent resources; methods define actions.

**Pros:** Standard, cacheable, easy to understand; works well with CDNs and caches.

**Cons:** Can be awkward for complex workflows; over-fetching/under-fetching.

**File tree (social media):**

```
app/
├── api/
│   ├── posts.py           # GET/POST /posts, GET/PUT/DELETE /posts/{id}
│   ├── users.py           # GET/POST /users, GET/PUT /users/{id}
│   ├── feed.py            # GET /users/{id}/feed
│   └── comments.py        # GET/POST /posts/{id}/comments
├── schemas/
│   ├── post.py
│   └── user.py
└── services/
    ├── post_service.py
    └── feed_service.py
```

| Term         | Description                                                     |
|--------------|-----------------------------------------------------------------|
| **api**      | HTTP routes; one file per resource; GET/POST/PUT/DELETE on URLs |
| **schemas**  | Pydantic models; request/response shapes; validation            |
| **services** | Business logic; called by api; may call DB or other services    |

---

## Summary

Most social media APIs use **modular monolith** or **microservices** with **REST** for the API surface. **Hexagonal** suits domains with rich business logic and a need to swap infrastructure. **CQRS** and **event-driven** are common for feeds and notifications at scale.
