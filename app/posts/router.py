from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.auth.schemas import TokenData
from app.database import get_db
from app.posts import schemas
from app.posts.service import create_post as service_create_post
from app.posts.service import delete_post as service_delete_post
from app.posts.service import get_post as service_get_post
from app.posts.service import get_posts as service_get_posts
from app.posts.service import update_post as service_update_post

router = APIRouter()


@router.get("", response_model=list[schemas.Post])
@router.get("/", response_model=list[schemas.Post])
def get_posts(db: Session = Depends(get_db)):  # Depends() injects a fresh session per request and closes it after.
    return service_get_posts(db)


@router.get("/{post_id}", response_model=schemas.Post)
def get_post(
    post_id: int, db: Session = Depends(get_db)
):  # Depends() injects a fresh session per request and closes it after.
    post = service_get_post(db, post_id)
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id: {post_id} was not found")
    return post


@router.post("", response_model=schemas.Post, status_code=status.HTTP_201_CREATED)
@router.post("/", response_model=schemas.Post, status_code=status.HTTP_201_CREATED)
def create_post(
    payload: schemas.PostCreate,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user),
):
    return service_create_post(db, payload)


@router.put("/{post_id}", response_model=schemas.Post)
def update_post(
    post_id: int, payload: schemas.PostCreate, db: Session = Depends(get_db)
):  # Depends() injects a fresh session per request and closes it after.
    post = service_update_post(db, post_id, payload)
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id: {post_id} was not found")
    return post


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(
    post_id: int, db: Session = Depends(get_db)
):  # Depends() injects a fresh session per request and closes it after.
    is_deleted = service_delete_post(db, post_id)
    if not is_deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id: {post_id} was not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
