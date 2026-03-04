"""Shared pytest fixtures for the test suite. Pytest auto-discovers conftest.py."""

from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.config import settings
from app.database import Base, get_db
from app.main import app

# Use a separate test database to avoid affecting development data.
SQLALCHEMY_DATABASE_URL = (
    f"postgresql://{settings.postgres_user}:{settings.postgres_password}"
    f"@{settings.postgres_host}:{settings.postgres_port}/{settings.postgres_db}_test"
)

engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture
def session():
    """Create a fresh database for each test: drop all tables, recreate, yield a session."""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def client(session):
    """Override get_db to use the test session; yield a TestClient."""

    def override_get_db():
        try:
            yield session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.clear()


@pytest.fixture
def routes():
    """URL paths from the app via url_path_for (app as source of truth)."""
    return SimpleNamespace(
        root=app.url_path_for("root"),
        auth_login=app.url_path_for("auth_login"),
        users_create=app.url_path_for("users_create"),
        posts_list=app.url_path_for("posts_list"),
        posts_create=app.url_path_for("posts_create"),
        posts_detail=lambda post_id: app.url_path_for("get_post", post_id=post_id),
        posts_update=lambda post_id: app.url_path_for("posts_update", post_id=post_id),
        posts_delete=lambda post_id: app.url_path_for("posts_delete", post_id=post_id),
        posts_add_vote=lambda post_id: app.url_path_for("posts_add_vote", post_id=post_id),
        posts_remove_vote=lambda post_id: app.url_path_for("posts_remove_vote", post_id=post_id),
    )


@pytest.fixture
def test_user(client, routes):
    """Create a test user via the API and return user data including password."""
    user_data = {"email": "testuser@example.com", "password": "password123"}
    res = client.post(routes.users_create, json=user_data)
    assert res.status_code == 201
    new_user = res.json()
    new_user["password"] = user_data["password"]
    return new_user


@pytest.fixture
def test_user2(client, routes):
    """Create a second test user for ownership tests (e.g. delete/update another user's post)."""
    user_data = {"email": "testuser2@example.com", "password": "password123"}
    res = client.post(routes.users_create, json=user_data)
    assert res.status_code == 201
    new_user = res.json()
    new_user["password"] = user_data["password"]
    return new_user


@pytest.fixture
def token(test_user):
    """Create an access token for the test user."""
    from app.auth.jwt import create_access_token

    return create_access_token(data={"user_id": test_user["id"]})


@pytest.fixture
def authorized_client(client, token):
    """TestClient with Authorization header set for authenticated requests."""
    client.headers = {
        **client.headers,
        "Authorization": f"Bearer {token}",
    }
    return client


@pytest.fixture
def test_posts(test_user, test_user2, session):
    """Create test posts: first three owned by test_user, fourth by test_user2."""
    from app.posts.models import Post

    posts_data = [
        {"title": "first title", "content": "first content", "owner_id": test_user["id"]},
        {"title": "2nd title", "content": "2nd content", "owner_id": test_user["id"]},
        {"title": "3rd title", "content": "3rd content", "owner_id": test_user["id"]},
        {"title": "other user post", "content": "owned by user2", "owner_id": test_user2["id"]},
    ]
    posts = [Post(**p) for p in posts_data]
    session.add_all(posts)
    session.commit()
    return session.query(Post).order_by(Post.id).all()


@pytest.fixture
def test_vote(test_posts, session, test_user):
    """Create a vote for test_user on the fourth post (owned by test_user2)."""
    from app.posts.models import Vote

    new_vote = Vote(post_id=test_posts[3].id, user_id=test_user["id"])
    session.add(new_vote)
    session.commit()
    return new_vote
