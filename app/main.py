from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session

from app.api.router import router as api_router
from app.config import settings
from app.database import get_db

app = FastAPI()

origins = [o.strip() for o in settings.cors_origins.split(",") if o.strip()] if settings.cors_origins != "*" else ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api", tags=["API"])


@app.get("/")
def root():
    return {"message": "Hello World"}


@app.get("/health/db")
def health_db(db: Session = Depends(get_db)):  # Depends() injects a fresh session per request and closes it after.
    """Verify database connection for health checks."""
    try:
        db.execute(text("SELECT 1"))  # Verify the connection is alive for health checks.
    except OperationalError as e:
        raise HTTPException(status_code=503, detail="Database unavailable") from e
    return {"status": "success"}
