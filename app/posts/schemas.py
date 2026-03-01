from typing import Optional

from pydantic import BaseModel


class PostCreate(BaseModel):
    title: str
    content: str
    published: bool = True
    rating: Optional[int] = None


class PostResponse(BaseModel):
    title: str
    content: str
    published: bool
    rating: Optional[int]
