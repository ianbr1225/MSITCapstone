"""
RetainIQ — Database connection and session management.

Reads DATABASE_URL from environment (loaded via python-dotenv for local dev).
Provides a SQLAlchemy engine, session factory, and a FastAPI dependency
generator for injecting DB sessions into route functions.

Design note on lazy construction
---------------------------------
`engine` and `SessionLocal` are built only when DATABASE_URL is present in the
environment. This allows `from database import Base, get_db` to succeed at
import time (needed by both main.py and test conftest.py) without requiring a
live DATABASE_URL in every environment. Tests override get_db entirely via
FastAPI dependency_overrides, so they never reach the guard in get_db().
"""

import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Load .env from the backend directory (no-op if the file doesn't exist,
# e.g. inside Docker where env vars are set via docker-compose).
load_dotenv(Path(__file__).resolve().parent / ".env")

DATABASE_URL = os.getenv("DATABASE_URL")

# Base is always importable — models.py and conftest.py both need it at
# import time, regardless of whether DATABASE_URL is set.
Base = declarative_base()

# engine and SessionLocal are only constructed when DATABASE_URL is available.
# In test environments, get_db is overridden before any route runs, so these
# are never called.
if DATABASE_URL is not None:
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
else:
    engine = None        # type: ignore[assignment]
    SessionLocal = None  # type: ignore[assignment]


def get_db():
    """FastAPI dependency: yield a DB session, close it when the request ends."""
    if SessionLocal is None:
        raise RuntimeError(
            "DATABASE_URL environment variable is not set. "
            "Copy backend/.env.example to backend/.env and fill in credentials."
        )
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
