from sqlalchemy.orm import Session

from app.config import settings
from app.users import models
from app.users import schemas
from app.users.service import get_user_by_email as service_get_user_by_email
from app.users.utils import hash_password, verify_password

_DUMMY_HASH = hash_password(settings.auth_dummy_password)


def authenticate_user(db: Session, credentials: schemas.UserLogin) -> models.User | None:
    """Verify credentials and return the user if valid; None if invalid."""
    user = service_get_user_by_email(db, str(credentials.email))

    # Use dummy hash when user is missing so verify_password always runs; avoids timing side-channel that would reveal whether the email exists.
    stored_hash = user.password if user else _DUMMY_HASH
    if verify_password(plain_password=credentials.password, hashed_password=stored_hash):
        return user

    return None
