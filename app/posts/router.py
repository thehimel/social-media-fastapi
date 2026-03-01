from uuid import UUID

from fastapi import APIRouter, HTTPException

from app.posts.schemas import PostCreate, PostResponse
from app.posts.service import create_post as service_create_post
from app.posts.service import get_post as service_get_post
from app.posts.service import get_posts as service_get_posts

router = APIRouter()


@router.get("/", response_model=list[PostResponse])
def get_posts():
    return service_get_posts()


@router.get("/{post_id}", response_model=PostResponse)
def get_post(post_id: UUID):
    post = service_get_post(post_id)
    if post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    return post


@router.post("/", response_model=PostResponse)
def create_post(payload: PostCreate):
    return service_create_post(payload)
