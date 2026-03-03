from sqlalchemy import Boolean, Column, Integer, String

from app.database import Base


class Post(Base):
    """ORM model for the posts table."""

    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, nullable=False)
    title = Column(String, nullable=False)
    content = Column(String, nullable=False)
    published = Column(Boolean, default=True)
