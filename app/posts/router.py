from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.database import get_db
from app.users import models as user_models
from app.posts import schemas
from app.posts.service import create_post as service_create_post
from app.posts.service import delete_post as service_delete_post
from app.posts.service import get_post as service_get_post
from app.posts.service import get_post_with_votes as service_get_post_with_votes
from app.posts.service import get_posts as service_get_posts
from app.posts.service import update_post as service_update_post
from app.votes.types import AddVoteResult, RemoveVoteResult
from app.votes.service import add_vote as service_add_vote
from app.votes.service import remove_vote as service_remove_vote

router = APIRouter()


@router.get("", response_model=list[schemas.PostOut], name="posts_list")
@router.get("/", response_model=list[schemas.PostOut], name="posts_list")
def get_posts(
    db: Session = Depends(get_db),
    current_user: user_models.User = Depends(get_current_user),
    limit: int = 10,
    skip: int = 0,
    search: Optional[str] = "",
):
    try:
        return service_get_posts(
            db,
            owner_id=current_user.id,
            limit=limit,
            skip=skip,
            search=search or "",
        )
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database error occurred",
        ) from e


@router.get("/{post_id}", response_model=schemas.PostOut)
def get_post(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: user_models.User = Depends(get_current_user),
):
    result = service_get_post_with_votes(db, post_id)
    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id: {post_id} was not found")
    if result.post.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to perform requested action",
        )
    return result


@router.post("", response_model=schemas.Post, status_code=status.HTTP_201_CREATED, name="posts_create")
@router.post("/", response_model=schemas.Post, status_code=status.HTTP_201_CREATED, name="posts_create")
def create_post(
    payload: schemas.PostCreate,
    db: Session = Depends(get_db),
    current_user: user_models.User = Depends(get_current_user),
):
    return service_create_post(db, payload, owner_id=current_user.id)


@router.put("/{post_id}", response_model=schemas.Post, name="posts_update")
def update_post(
    post_id: int,
    payload: schemas.PostCreate,
    db: Session = Depends(get_db),
    current_user: user_models.User = Depends(get_current_user),
):
    post = service_get_post(db, post_id)
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id: {post_id} was not found")
    if post.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to perform requested action",
        )
    return service_update_post(db, post_id, payload)


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT, name="posts_delete")
def delete_post(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: user_models.User = Depends(get_current_user),
):
    post = service_get_post(db, post_id)
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id: {post_id} was not found")
    if post.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to perform requested action",
        )
    service_delete_post(db, post_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/{post_id}/vote", status_code=status.HTTP_201_CREATED, name="posts_add_vote")
def add_vote(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: user_models.User = Depends(get_current_user),
):
    result = service_add_vote(db, post_id, current_user.id)
    if result is AddVoteResult.NOT_FOUND:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    if result is AddVoteResult.CONFLICT:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"user {current_user.id} has already voted on post {post_id}",
        )
    return {"message": "successfully added vote"}


@router.delete("/{post_id}/vote", status_code=status.HTTP_204_NO_CONTENT, name="posts_remove_vote")
def remove_vote(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: user_models.User = Depends(get_current_user),
):
    result = service_remove_vote(db, post_id, current_user.id)
    if result is RemoveVoteResult.NOT_FOUND:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vote does not exist")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
