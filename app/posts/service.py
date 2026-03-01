from uuid import uuid4 as uuid

from app.posts.schemas import PostCreate, PostResponse

posts: list[PostResponse] = [
    PostResponse(id=uuid(), title="Post 1", content="Content 1", published=False, rating=5),
    PostResponse(id=uuid(), title="Post 2", content="Content 2", published=True, rating=4),
    PostResponse(id=uuid(), title="Post 3", content="Content 3", published=True, rating=3),
    PostResponse(id=uuid(), title="Post 4", content="Content 4", published=False, rating=2),
]


def get_posts() -> list[PostResponse]:
    return posts


def create_post(payload: PostCreate) -> PostResponse:
    post = PostResponse(
        id=uuid(),
        title=payload.title,
        content=payload.content,
        published=payload.published,
        rating=payload.rating,
    )
    posts.append(post)
    return post
