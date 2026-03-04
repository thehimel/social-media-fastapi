# Test Suite Setup

This guide documents the **test suite** for the FastAPI application: structure, fixtures, and how to run tests. The design follows the KodeKloud course patterns for FastAPI testing.

## Prerequisites

1. **PostgreSQL running** (e.g. via `docker compose up -d` or `docker compose -f docker-compose.dev.yml up -d`).
2. **Test database created** — use a separate database so tests do not affect development data:

   ```sql
   CREATE DATABASE "kodekloud-fastapi_test";
   ```

   Or via Docker:

   ```shell
   docker compose exec postgres psql -U postgres -c 'CREATE DATABASE "kodekloud-fastapi_test";'
   ```

   The test database name is `{POSTGRES_DB}_test` (from your `.env`).

3. **`.env` configured** with `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_HOST`, `POSTGRES_PORT`, `POSTGRES_DB`, and `JWT_SECRET_KEY`.

## Test Structure

```
tests/
├── __init__.py
├── conftest.py      # Shared fixtures (session, client, routes, test_user, authorized_client, etc.)
├── test_users.py    # User creation, login, failed login
├── test_posts.py    # Post CRUD, authorization, ownership
└── test_votes.py    # Vote add, remove, duplicate, unauthorized
```

The **routes** fixture uses `app.url_path_for()` so URLs come from the app (single source of truth). Route names are set on decorators (e.g. `name="auth_login"`, `name="posts_list"`).

## Fixtures (conftest.py)

| Fixture | Purpose |
|---------|---------|
| **session** | Fresh DB per test: drop all tables, recreate, yield a SQLAlchemy session. |
| **client** | `TestClient` with `get_db` overridden to use the test session. |
| **routes** | URL paths from the app via `app.url_path_for()` (app as source of truth). |
| **test_user** | Creates a user via POST `/api/users/`; returns `{id, email, password, ...}`. |
| **test_user2** | Second user for ownership tests (e.g. delete/update another user's post). |
| **token** | JWT for `test_user` via `create_access_token`. |
| **authorized_client** | `client` with `Authorization: Bearer <token>` header. |
| **test_posts** | Four posts: three owned by `test_user`, one by `test_user2`. |
| **test_vote** | A vote by `test_user` on the fourth post (owned by `test_user2`). |

## Test Database Override

Tests use a **separate database** (`{postgres_db}_test`) and override `get_db` so routes use the test session. This keeps development data untouched and ensures each test runs against a clean schema (drop/create per test).

## Trailing Slashes

FastAPI treats `/users` and `/users/` differently. If a route is defined with a trailing slash (e.g. `/api/users/`), requests **must** include it. Omitting it can cause a 307 redirect and unexpected status codes in tests. The test suite uses `/api/users/`, `/api/posts/`, etc., consistently.

## Test Coverage

### Users (`test_users.py`)

- **test_root** — Root endpoint returns `{"message": "Hello World"}`.
- **test_create_user** — User creation returns 201 and valid `UserResponse`.
- **test_login_user** — Login returns 200 and a bearer token.
- **test_incorrect_login** — Invalid credentials return 404 with `"Invalid Credentials"`.

### Posts (`test_posts.py`)

- **test_get_all_posts** — Authorized user retrieves their posts (owner-filtered).
- **test_unauthorized_user_get_all_posts** — Unauthorized request returns 401.
- **test_unauthorized_user_get_one_post** — Unauthorized single-post request returns 401.
- **test_get_one_post** — Authorized user retrieves their own post.
- **test_get_one_post_not_exist** — Non-existent post returns 404.
- **test_create_post** — Parametrized: create posts with various payloads.
- **test_create_post_default_published_true** — Omitted `published` defaults to `True`.
- **test_unauthorized_user_create_post** — Unauthorized create returns 401.
- **test_unauthorized_user_delete_post** — Unauthorized delete returns 401.
- **test_delete_post_success** — Authorized user deletes their own post (204).
- **test_delete_post_non_exist** — Delete non-existent post returns 404.
- **test_delete_other_user_post** — Cannot delete another user's post (403).
- **test_update_post** — Authorized user updates their own post.
- **test_update_other_user_post** — Cannot update another user's post (403).
- **test_unauthorized_user_update_post** — Unauthorized update returns 401.
- **test_update_post_non_exist** — Update non-existent post returns 404.

### Votes (`test_votes.py`)

- **test_vote_on_post** — Authorized user can vote (201).
- **test_vote_twice_post** — Duplicate vote returns 409.
- **test_delete_vote** — Authorized user can remove their vote (204).
- **test_delete_vote_non_exist** — Remove non-existent vote returns 404.
- **test_vote_post_non_exist** — Vote on non-existent post returns 404.
- **test_vote_unauthorized_user** — Unauthorized vote returns 401.

## Running Tests

See [Commands](../../commands.md#pytest) for the full list. Quick reference:

```shell
pytest                    # Run all tests
pytest -v                 # Verbose
pytest -v -s              # Verbose + show print output
pytest -x                 # Stop on first failure
pytest tests/test_users.py # Run a single file
```

## Schema Validation

Tests use Pydantic schemas (`UserResponse`, `Post`, `PostOut`, `Token`) to validate API responses. Instantiating a schema with `**res.json()` ensures the response structure matches the expected model and surfaces schema mismatches as test failures.
