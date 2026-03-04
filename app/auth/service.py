from sqlalchemy.orm import Session

from app.auth import schemas
from app.auth.jwt import create_access_token
from app.config import settings
from app.users import models
from app.users.service import get_user_by_email as service_get_user_by_email
from app.users.utils import hash_password, verify_password

_DUMMY_HASH = hash_password(settings.auth_dummy_password)


def authenticate_user(db: Session, email: str, password: str) -> models.User | None:
    """Verify credentials and return the user if valid; None if invalid."""
    user = service_get_user_by_email(db, email)

    # Use dummy hash when user is missing so verify_password always runs; avoids timing side-channel that would reveal whether the email exists.
    stored_hash = user.password if user else _DUMMY_HASH
    if verify_password(plain_password=password, hashed_password=stored_hash):
        return user

    return None


def login(db: Session, email: str, password: str) -> schemas.Token | None:
    """Authenticate and return a token if valid; None if invalid."""
    user = authenticate_user(db, email=email, password=password)
    if user is None:
        return None
    access_token = create_access_token(data={"user_id": user.id})
    return schemas.Token(access_token=access_token, token_type=settings.jwt_token_type)
