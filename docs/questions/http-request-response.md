# HTTP Request and Response

## What is an HTTP request?

An **HTTP request** is a message a client sends to a server to ask for an action. It has:

- **Request line** — Method (GET, POST, PUT, DELETE, etc.) + path + HTTP version
- **Headers** — Metadata (e.g. `Content-Type`, `Authorization`, `Accept`)
- **Body** — Optional payload (e.g. JSON for POST/PUT)

**Note:** The request line is the first line and is **not** part of the headers. Headers are the `Name: Value` pairs that follow. Order: request line → headers → blank line → body.

```mermaid
flowchart TD
    subgraph Request["HTTP Request"]
        A["Request line: METHOD + path + HTTP version"]
        B["Headers: Content-Type, Authorization, Accept, ..."]
        C["Body (optional): JSON, form data, etc."]
    end
    A --> B --> C
```

**Example:** `GET /api/posts/1 HTTP/1.1` with `Authorization: Bearer <token>` asks the server to return post 1 for the authenticated user.

## What is an HTTP response?

An **HTTP response** is the server’s reply to a request. It has:

- **Status line** — HTTP version + status code (e.g. 200 OK, 404 Not Found)
- **Headers** — Metadata (e.g. `Content-Type`, `Cache-Control`)
- **Body** — Optional payload (e.g. JSON with the resource)

**Note:** The status line is the first line and is **not** part of the headers. Headers are the `Name: Value` pairs that follow. Order: status line → headers → blank line → body.

```mermaid
flowchart TD
    subgraph Response["HTTP Response"]
        D["Status line: HTTP version + status code + reason"]
        E["Headers: Content-Type, Cache-Control, ..."]
        F["Body (optional): JSON, HTML, etc."]
    end
    D --> E --> F
```

**Example:** `HTTP/1.1 200 OK` with `Content-Type: application/json` and a JSON body returns the requested data.

## What are common HTTP status codes?

| Series | Range | Meaning |
|--------|-------|---------|
| **1xx** | 100–199 | Informational — request received, processing continues |
| **2xx** | 200–299 | Success — request succeeded |
| **3xx** | 300–399 | Redirection — client must take further action |
| **4xx** | 400–499 | Client error — request invalid or unauthorized |
| **5xx** | 500–599 | Server error — server failed to fulfill the request |

| Code | Meaning | Typical use |
|------|---------|-------------|
| **200** | OK | Successful GET, PUT, PATCH |
| **201** | Created | Successful POST that creates a resource |
| **204** | No Content | Successful DELETE or update with no body |
| **400** | Bad Request | Invalid input or malformed request |
| **401** | Unauthorized | Missing or invalid auth (e.g. token) |
| **403** | Forbidden | Authenticated but not allowed |
| **404** | Not Found | Resource does not exist |
| **409** | Conflict | Duplicate or conflicting state (e.g. duplicate vote) |
| **422** | Unprocessable Entity | Validation error (e.g. Pydantic schema) |
| **500** | Internal Server Error | Unexpected server error |

**Example (422):** `POST /api/users/` with `{"email": "not-an-email", "password": "secret"}` returns 422 because `email` must be a valid `EmailStr`. Or `{"email": "user@example.com"}` (missing `password`) returns 422 because `password` is required.

## How does FastAPI handle request and response?

**Request** — FastAPI parses the request using **dependency injection** and **Pydantic**:

- Path params: `@router.get("/posts/{post_id}")` → `post_id: int`
- Query params: `limit: int = 10`, `search: Optional[str] = ""`
- Body: `payload: schemas.PostCreate` (JSON → Pydantic)
- Headers: `Authorization: str = Header(...)` or `Depends(oauth2_scheme)`
- Form data: `OAuth2PasswordRequestForm` for login

**Response** — FastAPI serializes the return value using `response_model`:

- `response_model=schemas.Post` — Pydantic model → JSON
- `status_code=201` — Override default 200
- `Response(status_code=204)` — No body (e.g. DELETE)

**Flow:** Request → validation (Pydantic) → route handler → response serialization → HTTP response.

## What is the request–response cycle?

**Client** → **Request** → **Server** → **Response** → **Client**

1. Client sends HTTP request (method, path, headers, body)
2. Server receives it, routes to handler, validates input
3. Handler runs business logic, returns data
4. Server serializes response, sends HTTP response
5. Client receives status, headers, and body

In FastAPI: **Uvicorn** receives the request → **Starlette** routes it → **FastAPI** validates and runs the handler → response is serialized and sent back.

## Complete blueprint: request and response

**Request** — `POST /api/posts/` to create a post:

```http
POST /api/posts/ HTTP/1.1
Host: localhost:8000
Content-Type: application/json
Accept: application/json
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Length: 52

{"title": "My first post", "content": "Hello world", "published": true}
```

| Part | Value |
|------|-------|
| **Request line** | `POST /api/posts/ HTTP/1.1` |
| **Host** | Server and port |
| **Content-Type** | Format of the body (JSON) |
| **Accept** | Preferred response format |
| **Authorization** | Bearer token for auth |
| **Body** | JSON payload |

**Response** — `201 Created`:

```http
HTTP/1.1 201 Created
content-type: application/json
content-length: 156

{"id":1,"title":"My first post","content":"Hello world","published":true,"owner_id":1,"created_at":"2025-03-03T12:00:00Z","owner":{"id":1,"email":"user@example.com","created_at":"2025-03-03T11:00:00Z"}}
```

| Part | Value |
|------|-------|
| **Status line** | `HTTP/1.1 201 Created` |
| **content-type** | Response body format |
| **content-length** | Body size in bytes |
| **Body** | JSON resource |
