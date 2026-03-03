from sqlalchemy.orm import Session

from app.posts.models import Post
from app.posts.schemas import PostCreate, PostResponse


def get_posts(db: Session) -> list[PostResponse]:
    posts = db.query(Post).all()  # Fetch all posts from the database.
    return [
        PostResponse(
            id=int(p.id),
            title=str(p.title),
            content=str(p.content),
            published=bool(p.published),
            rating=p.rating
            if p.rating is None
            else int(p.rating),  # int() satisfies type checker; SQLAlchemy reports InstrumentedAttribute.
            created_at=p.created_at,
        )
        for p in posts
    ]


def get_post(db: Session, post_id: int) -> PostResponse | None:
    post = db.get(Post, post_id)  # Fetch by primary key to return the post.
    if post is None:
        return None
    return PostResponse(
        id=int(post.id),
        title=str(post.title),
        content=str(post.content),
        published=bool(post.published),
        rating=post.rating
        if post.rating is None
        else int(post.rating),  # int() satisfies type checker; SQLAlchemy reports InstrumentedAttribute.
        created_at=post.created_at,
    )


def create_post(db: Session, payload: PostCreate) -> PostResponse:
    post = Post(
        title=payload.title,
        content=payload.content,
        published=payload.published,
        rating=payload.rating,
    )
    db.add(post)  # Stage for insert so commit can persist it.
    db.commit()  # Persist so the post is stored and visible.
    db.refresh(post)  # Load id and created_at so we can return them.
    return PostResponse(
        id=int(post.id),
        title=str(post.title),
        content=str(post.content),
        published=bool(post.published),
        rating=post.rating
        if post.rating is None
        else int(post.rating),  # int() satisfies type checker; SQLAlchemy reports InstrumentedAttribute.
        created_at=post.created_at,
    )


def update_post(db: Session, post_id: int, payload: PostCreate) -> PostResponse | None:
    post = db.get(Post, post_id)  # Fetch by primary key to update.
    if post is None:
        return None
    post.title = payload.title
    post.content = payload.content
    post.published = payload.published
    post.rating = payload.rating
    db.commit()  # Persist changes to the database.
    db.refresh(post)  # Reload to ensure we return the latest state.
    return PostResponse(
        id=int(post.id),
        title=str(post.title),
        content=str(post.content),
        published=bool(post.published),
        rating=post.rating
        if post.rating is None
        else int(post.rating),  # int() satisfies type checker; SQLAlchemy reports InstrumentedAttribute.
        created_at=post.created_at,
    )


def delete_post(db: Session, post_id: int) -> bool:
    post = db.get(Post, post_id)  # Fetch by primary key to delete.
    if post is None:
        return False
    db.delete(post)  # Mark for deletion so commit removes it.
    db.commit()  # Persist the deletion to the database.
    return True
