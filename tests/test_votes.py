"""Tests for vote (like) endpoints."""


def test_vote_on_post(authorized_client, test_posts, routes):
    """Verify authorized user can vote on a post."""
    res = authorized_client.post(routes.posts_add_vote(test_posts[3].id))
    assert res.status_code == 201


def test_vote_twice_post(authorized_client, test_posts, test_vote, routes):
    """Verify duplicate vote returns 409."""
    res = authorized_client.post(routes.posts_add_vote(test_posts[3].id))
    assert res.status_code == 409


def test_delete_vote(authorized_client, test_posts, test_vote, routes):
    """Verify authorized user can remove their vote."""
    res = authorized_client.delete(routes.posts_remove_vote(test_posts[3].id))
    assert res.status_code == 204


def test_delete_vote_non_exist(authorized_client, test_posts, routes):
    """Verify 404 when removing a non-existent vote."""
    res = authorized_client.delete(routes.posts_remove_vote(test_posts[3].id))
    assert res.status_code == 404


def test_vote_post_non_exist(authorized_client, test_posts, routes):
    """Verify 404 when voting on a non-existent post."""
    res = authorized_client.post(routes.posts_add_vote(80000))
    assert res.status_code == 404


def test_vote_unauthorized_user(client, test_posts, routes):
    """Verify unauthorized user cannot vote."""
    res = client.post(routes.posts_add_vote(test_posts[3].id))
    assert res.status_code == 401
