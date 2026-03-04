from sqlalchemy.orm import Session

from app.posts.models import Post, Vote
from app.votes.types import AddVoteResult, RemoveVoteResult


def add_vote(db: Session, post_id: int, user_id: int) -> AddVoteResult:
    """Add a vote. Returns status for the router to map to HTTP responses."""
    post = db.query(Post).filter(Post.id == post_id).first()
    if post is None:
        return AddVoteResult.NOT_FOUND
    existing = db.query(Vote).filter(Vote.post_id == post_id, Vote.user_id == user_id).first()
    if existing:
        return AddVoteResult.CONFLICT
    vote = Vote(post_id=post_id, user_id=user_id)
    db.add(vote)
    db.commit()
    return AddVoteResult.OK


def remove_vote(db: Session, post_id: int, user_id: int) -> RemoveVoteResult:
    """Remove a vote. Returns status for the router to map to HTTP responses."""
    vote = db.query(Vote).filter(Vote.post_id == post_id, Vote.user_id == user_id).first()
    if vote is None:
        return RemoveVoteResult.NOT_FOUND
    db.delete(vote)
    db.commit()
    return RemoveVoteResult.OK
