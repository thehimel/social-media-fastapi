from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class PostBase(BaseModel):
    title: str
    content: str
    published: bool = True
    rating: Optional[int] = None


class PostCreate(PostBase):
    pass


class Post(PostBase):
    id: int
    owner_id: int
    created_at: datetime

    # Allow Pydantic to read from ORM attributes (e.g. post.id, post.title) so we can return SQLAlchemy model
    # instances directly from endpoints; without this, passing an ORM object raises ValidationError.
    model_config = ConfigDict(from_attributes=True)
