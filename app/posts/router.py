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
from app.posts.service import get_posts as service_get_posts
from app.posts.service import update_post as service_update_post

router = APIRouter()


@router.get("", response_model=list[schemas.Post])
@router.get("/", response_model=list[schemas.Post])
def get_posts(
    db: Session = Depends(get_db),
    current_user: user_models.User = Depends(get_current_user),
):
    try:
        return service_get_posts(db, owner_id=current_user.id)
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database error occurred",
        ) from e


@router.get("/{post_id}", response_model=schemas.Post)
def get_post(
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
    return post


@router.post("", response_model=schemas.Post, status_code=status.HTTP_201_CREATED)
@router.post("/", response_model=schemas.Post, status_code=status.HTTP_201_CREATED)
def create_post(
    payload: schemas.PostCreate,
    db: Session = Depends(get_db),
    current_user: user_models.User = Depends(get_current_user),
):
    return service_create_post(db, payload, owner_id=current_user.id)


@router.put("/{post_id}", response_model=schemas.Post)
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


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
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
