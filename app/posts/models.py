from sqlalchemy import Boolean, Column, Integer, String
from sqlalchemy.sql.expression import text
from sqlalchemy.sql.sqltypes import TIMESTAMP

from app.database import Base


class Post(Base):
    """ORM model for the posts table."""

    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, nullable=False)
    title = Column(String, nullable=False)
    content = Column(String, nullable=False)
    published = Column(Boolean, server_default="TRUE", nullable=False)
    rating = Column(Integer, nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text("now()"))
