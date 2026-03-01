from fastapi import APIRouter

from app.posts.schemas import PostCreate, PostResponse

router = APIRouter()


@router.get("/", response_model=dict)
def get_posts():
    return {"data": "This is your posts"}


@router.post("/", response_model=PostResponse)
def create_post(payload: PostCreate):
    return PostResponse(
        title=payload.title, content=payload.content, published=payload.published, rating=payload.rating
    )
