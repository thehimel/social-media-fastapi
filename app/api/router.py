from fastapi import APIRouter

from app.posts.router import router as posts_router
from app.users.router import router as users_router

router = APIRouter()

router.include_router(posts_router, prefix="/posts", tags=["Posts"])
router.include_router(users_router, prefix="/users", tags=["Users"])
