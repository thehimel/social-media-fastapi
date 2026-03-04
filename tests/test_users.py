"""Tests for user creation and authentication endpoints."""

import pytest

from app.users import schemas


def test_root(client, routes):
    """Verify the root endpoint returns the expected message."""
    res = client.get(routes.root)
    assert res.status_code == 200
    assert res.json().get("message") == "Hello World"


def test_create_user(client, routes):
    """Verify user creation returns 201 and valid UserResponse schema."""
    res = client.post(
        routes.users_create,
        json={"email": "newuser@example.com", "password": "password123"},
    )
    new_user = schemas.UserResponse(**res.json())
    assert new_user.email == "newuser@example.com"
    assert res.status_code == 201


def test_login_user(test_user, client, routes):
    """Verify login returns 200 and a valid token."""
    res = client.post(
        routes.auth_login,
        data={"username": test_user["email"], "password": test_user["password"]},
    )
    assert res.status_code == 200
    login_res = res.json()
    assert "access_token" in login_res
    assert login_res.get("token_type", "").lower() == "bearer"


@pytest.mark.parametrize(
    "email, password, status_code",
    [
        ("wrong@example.com", "password123", 404),
        ("testuser@example.com", "wrongpassword", 404),
        ("wrong@example.com", "wrongpassword", 404),
    ],
)
def test_incorrect_login(test_user, client, routes, email, password, status_code):
    """Verify invalid credentials return 404 with Invalid Credentials detail."""
    res = client.post(
        routes.auth_login,
        data={"username": email, "password": password},
    )
    assert res.status_code == status_code
    if status_code == 404:
        assert res.json().get("detail") == "Invalid Credentials"
