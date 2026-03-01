from fastapi import APIRouter

from app.posts.router import router as posts_router

router = APIRouter()

router.include_router(posts_router, prefix="/posts", tags=["Posts"])
