from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy import text
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session

from app.api.router import router as api_router
from app.database import Base, engine, get_db
from app.posts.models import Post  # noqa: F401 - register with metadata
from app.users.models import User  # noqa: F401 - register with metadata

# Automatically create tables on application startup.
Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(api_router, prefix="/api", tags=["API"])


@app.get("/")
def root():
    return {"message": "Hello World"}


@app.get("/health/db")
def health_db(db: Session = Depends(get_db)):  # Depends() injects a fresh session per request and closes it after.
    """Verify database connection for health checks."""
    try:
        db.execute(text("SELECT 1"))  # Verify connection is alive for health checks.
    except OperationalError as e:
        raise HTTPException(status_code=503, detail="Database unavailable") from e
    return {"status": "success"}
