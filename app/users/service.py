from sqlalchemy.orm import Session

from app.users import schemas, models


def create_user(db: Session, payload: schemas.UserCreate):
    user = models.User(email=str(payload.email), password=payload.password)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
