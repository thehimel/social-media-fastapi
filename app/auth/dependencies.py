from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.auth.jwt import verify_access_token
from app.database import get_db
from app.users import models
from app.users.service import get_user as service_get_user

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> models.User:
    """Verify the JWT, fetch the user from the database, and return the full user object."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    token_data = verify_access_token(token, credentials_exception)
    if token_data.user_id is None:
        raise credentials_exception
    user = service_get_user(db, token_data.user_id)
    if user is None:
        raise credentials_exception
    return user
