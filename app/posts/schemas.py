from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class PostCreate(BaseModel):
    title: str
    content: str
    published: bool = True
    rating: Optional[int] = None


class PostResponse(BaseModel):
    id: UUID
    title: str
    content: str
    published: bool
    rating: Optional[int]
