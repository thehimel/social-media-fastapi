# REST vs GraphQL

## What is REST?

**REST** (Representational State Transfer) is an architectural style for APIs. Resources are identified by URLs; HTTP methods define actions. One endpoint per resource (or resource collection). The client gets a fixed response shape per endpoint.

**Characteristics:**

- **Resource-oriented** — URLs represent resources (`/posts`, `/posts/1`, `/users`)
- **HTTP methods** — GET (read), POST (create), PUT/PATCH (update), DELETE (delete)
- **Fixed responses** — Each endpoint returns a predefined structure
- **Multiple requests** — Fetching related data often needs several calls

**Example:** `GET /api/posts/1` returns a post. To get the author, `GET /api/users/1`. Two requests.

## What is GraphQL?

**GraphQL** is a query language and runtime. The client sends a **query** describing exactly what data it needs. One endpoint; the response shape matches the query.

**Characteristics:**

- **Query-driven** — Client specifies fields and nested data in one request
- **Single endpoint** — Typically `POST /graphql` for all operations
- **Flexible responses** — Response shape follows the query
- **Over-fetching / under-fetching** — Avoided by design

**Example:** One query fetches a post and its author:

```graphql
query {
  post(id: 1) {
    title
    content
    author {
      email
    }
  }
}
```

## REST vs GraphQL — comparison

| Aspect | REST | GraphQL |
|--------|------|---------|
| **Endpoints** | Many (one per resource/action) | One (or few) |
| **Request** | HTTP method + URL | Query/mutation in body |
| **Response shape** | Fixed per endpoint | Defined by client query |
| **Over-fetching** | Possible (full resource returned) | Avoided (client picks fields) |
| **Under-fetching** | Possible (multiple round-trips) | Avoided (nested queries) |
| **Caching** | HTTP caching (GET, status codes) | More complex (POST by default) |
| **Learning curve** | Simpler (HTTP, URLs) | Steeper (schema, queries) |
| **Tooling** | OpenAPI, Swagger | GraphiQL, schema introspection |

## How is REST implemented in FastAPI?

FastAPI is **REST-first**. You define routes with decorators; each route maps to an HTTP method and path.

```python
from fastapi import APIRouter

router = APIRouter()

@router.get("/posts")
def get_posts():
    return [{"id": 1, "title": "First"}]

@router.get("/posts/{post_id}")
def get_post(post_id: int):
    return {"id": post_id, "title": "First"}

@router.post("/posts")
def create_post(payload: PostCreate):
    return {"id": 1, **payload.dict()}
```

- **Routing** — `@router.get`, `@router.post`, etc.
- **Path params** — `{post_id}` in the path
- **Body** — Pydantic models for request/response validation
- **Docs** — OpenAPI/Swagger at `/docs` (automatic)

## How is GraphQL implemented in FastAPI?

FastAPI does **not** include GraphQL. You add it via a library and mount it on the app.

**Common libraries:**

- **Strawberry** — Modern, type hints, async support
- **Ariadne** — Schema-first, flexible
- **Graphene** — Mature, widely used

**Example with Strawberry:**

```python
import strawberry
from fastapi import FastAPI
from strawberry.fastapi import GraphQLRouter

@strawberry.type
class Post:
    id: int
    title: str
    content: str

@strawberry.type
class Query:
    @strawberry.field
    def post(self, id: int) -> Post:
        return Post(id=id, title="First", content="Hello")

schema = strawberry.Schema(query=Query)
graphql_app = GraphQLRouter(schema)

app = FastAPI()
app.include_router(graphql_app, prefix="/graphql")
```

- **Single endpoint** — `POST /graphql` (or GET for introspection)
- **Schema** — Types and resolvers define the API
- **Queries** — Client sends `{"query": "..."}` in the body

## When to use REST vs GraphQL?

**Use REST** when:

- Simple CRUD, resource-oriented API
- You want HTTP caching, standard tooling
- Team is familiar with REST
- Mobile/web need similar data shapes

**Use GraphQL** when:

- Clients need varied, nested data (e.g. dashboards, mobile vs web)
- You want to avoid over-fetching and under-fetching
- Many clients with different requirements
- You need strong typing and schema introspection

**Hybrid** — FastAPI can serve both: REST routes for most endpoints, GraphQL router for complex queries.
