from sqlalchemy.orm import Session

from app.users import models
from app.users import schemas
from app.users.utils import hash_password


def create_user(db: Session, payload: schemas.UserCreate):
    hashed_password = hash_password(payload.password)
    user = models.User(email=str(payload.email), password=hashed_password)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
