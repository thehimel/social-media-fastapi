from sqlalchemy import func
from sqlalchemy.orm import Session

from app.posts import models
from app.posts import schemas


def get_posts(
    db: Session,
    owner_id: int | None = None,
    limit: int = 10,
    skip: int = 0,
    search: str | None = "",
) -> list[schemas.PostOut]:
    """
    Fetch posts with vote counts using a join query.

    Join reasoning:
    - LEFT OUTER JOIN (isouter=True) on votes: Include every post even when it has zero votes.
      An INNER JOIN would exclude posts with no votes.
    - GROUP BY Post.id: Aggregate vote rows per post so we get one row per post with a count.
    - func.count(Vote.post_id): Count votes per post. Using post_id ensures we count rows from
      the votes table; counting Post.id would always be 1 per group.
    """
    query = (
        db.query(models.Post, func.count(models.Vote.post_id).label("votes"))
        .join(models.Vote, models.Vote.post_id == models.Post.id, isouter=True)
        .group_by(models.Post.id)
    )
    if owner_id is not None:
        query = query.filter(models.Post.owner_id == owner_id)
    if search:
        query = query.filter(models.Post.title.contains(search))
    rows = query.limit(limit).offset(skip).all()
    return [schemas.PostOut(post=row.Post, votes=row.votes) for row in rows]


def get_post(db: Session, post_id: int) -> models.Post | None:
    post = db.get(models.Post, post_id)  # Fetch by primary key to return the post.
    return post


def get_post_with_votes(db: Session, post_id: int) -> schemas.PostOut | None:
    """
    Fetch a single post with its vote count using a join query.

    Uses the same join pattern as get_posts for consistency:
    - LEFT OUTER JOIN on votes so posts with zero votes still return (votes=0).
    - GROUP BY Post.id to aggregate and count votes per post.
    - filter(Post.id == post_id) to restrict to the requested post.
    """
    row = (
        db.query(models.Post, func.count(models.Vote.post_id).label("votes"))
        .join(models.Vote, models.Vote.post_id == models.Post.id, isouter=True)
        .group_by(models.Post.id)
        .filter(models.Post.id == post_id)
        .first()
    )
    if row is None:
        return None
    return schemas.PostOut(post=row.Post, votes=row.votes)


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
