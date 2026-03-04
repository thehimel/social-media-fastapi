from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt

from app.auth import schemas
from app.config import settings


def create_access_token(data: dict) -> str:
    """Create a JWT access token with the given payload and expiration."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.jwt_access_token_expire_minutes)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def verify_access_token(token: str, credentials_exception: Exception) -> schemas.TokenData:
    """Decode and verify the JWT; return TokenData or raise credentials_exception."""
    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
        user_id = payload.get("user_id")
        if user_id is None:
            raise credentials_exception
        return schemas.TokenData(user_id=user_id)
    except JWTError:
        raise credentials_exception
