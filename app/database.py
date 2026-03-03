from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker

from app.config import settings

# For SQLite: DATABASE_URL = "sqlite:///sql_app.db"
# For PostgreSQL: DATABASE_URL = "postgresql://<username>:<password>@<ip-address>/<database_name>"
DATABASE_URL = (
    f"postgresql://{settings.postgres_user}:{settings.postgres_password}"
    f"@{settings.postgres_host}:{settings.postgres_port}/{settings.postgres_db}"
)

# Base class for our models
Base = declarative_base()

engine = create_engine(
    DATABASE_URL,
    # connect_args={"check_same_thread": False},  # Only required for SQLite.
    pool_pre_ping=True,  # Optional: Test connections before use to avoid stale.
    echo=settings.sql_echo,  # Optional: log SQL when SQL_ECHO env is true.
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """Provide a DB session for FastAPI dependency injection."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
