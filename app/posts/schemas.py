from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class PostCreate(BaseModel):
    title: str
    content: str
    published: bool = True
    rating: Optional[int] = None


class PostResponse(BaseModel):
    id: int
    title: str
    content: str
    published: bool
    rating: Optional[int]
    created_at: datetime
