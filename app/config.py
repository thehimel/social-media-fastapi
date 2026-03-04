import os
import signal
import sys

from pydantic import ValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Database
    postgres_user: str
    postgres_password: str
    postgres_host: str = "localhost"
    postgres_port: str = "5432"
    postgres_db: str = "kodekloud-fastapi"
    sql_echo: bool = False

    # Auth: password hashed at runtime for login timing-attack mitigation when user is not found.
    auth_dummy_password: str = ""


try:
    settings = Settings()
except ValidationError as e:
    missing = [str(err["loc"][0]).upper() for err in e.errors() if err["type"] == "missing"]
    print(f"Missing: {', '.join(missing)}. Set in .env. See .env.example.", file=sys.stderr)
    try:
        os.kill(os.getppid(), signal.SIGTERM)
    except OSError:
        pass
    sys.exit(1)
