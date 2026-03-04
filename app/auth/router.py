from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth import schemas
from app.auth.jwt import create_access_token
from app.auth.service import authenticate_user as service_authenticate_user
from app.config import settings
from app.database import get_db
from app.users import schemas as user_schemas

router = APIRouter(tags=["Authentication"])


@router.post("/login", response_model=schemas.Token)
def login(user_credentials: user_schemas.UserLogin, db: Session = Depends(get_db)):
    user = service_authenticate_user(db, user_credentials)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid Credentials",
        )
    access_token = create_access_token(data={"user_id": user.id})
    return schemas.Token(access_token=access_token, token_type=settings.jwt_token_type)
