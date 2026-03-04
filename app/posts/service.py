from sqlalchemy.orm import Session

from app.posts import models
from app.posts import schemas


def get_posts(db: Session, owner_id: int | None = None) -> list[models.Post]:
    query = db.query(models.Post)
    if owner_id is not None:
        query = query.filter(models.Post.owner_id == owner_id)
    return query.all()  # type: ignore[return-value]


def get_post(db: Session, post_id: int) -> models.Post | None:
    post = db.get(models.Post, post_id)  # Fetch by primary key to return the post.
    return post


def create_post(db: Session, payload: schemas.PostCreate, owner_id: int) -> models.Post:
    post = models.Post(
        title=payload.title,
        content=payload.content,
        published=payload.published,
        rating=payload.rating,
        owner_id=owner_id,
    )
    db.add(post)  # Stage for insert so commit can persist it.
    db.commit()  # Persist so the post is stored and visible.
    db.refresh(post)  # Load id and created_at so we can return them.
    return post


def update_post(db: Session, post_id: int, payload: schemas.PostCreate) -> models.Post | None:
    post = db.get(models.Post, post_id)  # Fetch by primary key to update.
    if post is None:
        return None
    post.title = payload.title
    post.content = payload.content
    post.published = payload.published
    post.rating = payload.rating
    db.commit()  # Persist changes to the database.
    db.refresh(post)  # Reload to ensure we return the latest state.
    return post  # type: ignore[return-value]


def delete_post(db: Session, post_id: int) -> bool:
    post = db.get(models.Post, post_id)  # Fetch by primary key to delete.
    if post is None:
        return False
    db.delete(post)  # Mark for deletion so commit removes it.
    db.commit()  # Persist the deletion to the database.
    return True
