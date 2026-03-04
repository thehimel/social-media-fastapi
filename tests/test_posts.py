"""Tests for post CRUD and authorization."""

import pytest

from app.posts import schemas


def test_get_all_posts(authorized_client, test_posts, routes):
    """Verify authorized user can retrieve their posts (owner-filtered)."""
    res = authorized_client.get(routes.posts_list)
    assert res.status_code == 200
    assert len(res.json()) == 3  # test_user owns 3 posts (indices 0, 1, 2)
    posts_list = [schemas.PostOut(**item) for item in res.json()]
    assert len(posts_list) == 3


def test_unauthorized_user_get_all_posts(client, test_posts, routes):
    """Verify unauthorized user cannot retrieve posts."""
    res = client.get(routes.posts_list)
    assert res.status_code == 401


def test_unauthorized_user_get_one_post(client, test_posts, routes):
    """Verify unauthorized user cannot retrieve a single post."""
    res = client.get(routes.posts_detail(test_posts[0].id))
    assert res.status_code == 401


def test_get_one_post(authorized_client, test_posts, routes):
    """Verify authorized user can retrieve their own post."""
    res = authorized_client.get(routes.posts_detail(test_posts[0].id))
    assert res.status_code == 200
    post_out = schemas.PostOut(**res.json())
    assert post_out.post.id == test_posts[0].id
    assert post_out.post.content == test_posts[0].content


def test_get_one_post_not_exist(authorized_client, test_posts, routes):
    """Verify 404 when requesting a non-existent post."""
    res = authorized_client.get(routes.posts_detail(88888))
    assert res.status_code == 404


@pytest.mark.parametrize(
    "title, content, published",
    [
        ("awesome new title", "awesome new content", True),
        ("favorite pizza", "i love pepperoni", False),
        ("tallest skyscrapers", "wahoo", True),
    ],
)
def test_create_post(authorized_client, test_user, test_posts, routes, title, content, published):
    """Verify authorized user can create posts with various payloads."""
    res = authorized_client.post(
        routes.posts_create,
        json={"title": title, "content": content, "published": published},
    )
    created_post = schemas.Post(**res.json())
    assert res.status_code == 201
    assert created_post.title == title
    assert created_post.content == content
    assert created_post.published == published
    assert created_post.owner_id == test_user["id"]


def test_create_post_default_published_true(authorized_client, test_user, test_posts, routes):
    """Verify omitted published field defaults to True."""
    res = authorized_client.post(
        routes.posts_create,
        json={"title": "arbitrary title", "content": "aasdfjasdf"},
    )
    created_post = schemas.Post(**res.json())
    assert res.status_code == 201
    assert created_post.published is True
    assert created_post.owner_id == test_user["id"]


def test_unauthorized_user_create_post(client, test_posts, routes):
    """Verify unauthorized user cannot create posts."""
    res = client.post(
        routes.posts_create,
        json={"title": "arbitrary title", "content": "aasdfjasdf"},
    )
    assert res.status_code == 401


def test_unauthorized_user_delete_post(client, test_posts, routes):
    """Verify unauthorized user cannot delete posts."""
    res = client.delete(routes.posts_delete(test_posts[0].id))
    assert res.status_code == 401


def test_delete_post_success(authorized_client, test_user, test_posts, routes):
    """Verify authorized user can delete their own post."""
    res = authorized_client.delete(routes.posts_delete(test_posts[0].id))
    assert res.status_code == 204


def test_delete_post_non_exist(authorized_client, test_user, test_posts, routes):
    """Verify 404 when deleting a non-existent post."""
    res = authorized_client.delete(routes.posts_delete(800000))
    assert res.status_code == 404


def test_delete_other_user_post(authorized_client, test_user, test_posts, routes):
    """Verify user cannot delete another user's post (403)."""
    res = authorized_client.delete(routes.posts_delete(test_posts[3].id))
    assert res.status_code == 403


def test_update_post(authorized_client, test_user, test_posts, routes):
    """Verify authorized user can update their own post."""
    data = {
        "title": "updated title",
        "content": "updated content",
    }
    res = authorized_client.put(routes.posts_update(test_posts[0].id), json=data)
    updated_post = schemas.Post(**res.json())
    assert res.status_code == 200
    assert updated_post.title == data["title"]
    assert updated_post.content == data["content"]


def test_update_other_user_post(authorized_client, test_user, test_posts, routes):
    """Verify user cannot update another user's post (403)."""
    data = {
        "title": "updated title",
        "content": "updated content",
    }
    res = authorized_client.put(routes.posts_update(test_posts[3].id), json=data)
    assert res.status_code == 403


def test_unauthorized_user_update_post(client, test_posts, routes):
    """Verify unauthorized user cannot update posts."""
    res = client.put(
        routes.posts_update(test_posts[0].id),
        json={"title": "updated title", "content": "updated content"},
    )
    assert res.status_code == 401


def test_update_post_non_exist(authorized_client, test_user, test_posts, routes):
    """Verify 404 when updating a non-existent post."""
    data = {
        "title": "updated title",
        "content": "updated content",
    }
    res = authorized_client.put(routes.posts_update(8000000), json=data)
    assert res.status_code == 404
