from sqlalchemy.orm import Session

from app.users import models
from app.users import schemas
from app.users.utils import hash_password


def get_user(db: Session, user_id: int) -> models.User | None:
    return db.get(models.User, user_id)


def create_user(db: Session, payload: schemas.UserCreate):
    hashed_password = hash_password(payload.password)
    user = models.User(email=str(payload.email), password=hashed_password)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
