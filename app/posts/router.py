from fastapi import APIRouter

from app.posts.schemas import PostCreate, PostResponse
from app.posts.service import get_posts as service_get_posts
from app.posts.service import create_post as service_create_post


router = APIRouter()


@router.get("/", response_model=list[PostResponse])
def get_posts():
    return service_get_posts()


@router.post("/", response_model=PostResponse)
def create_post(payload: PostCreate):
    return service_create_post(payload)
