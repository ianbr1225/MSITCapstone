"""
RetainIQ — Database connection and session management.

Reads DATABASE_URL from environment (loaded via python-dotenv for local dev).
Provides a SQLAlchemy engine, session factory, and a FastAPI dependency
generator for injecting DB sessions into route functions.
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

# Guard: fail fast if DATABASE_URL isn't set at all (catches misconfigured
# environments before the first query).
if DATABASE_URL is None:
    raise RuntimeError(
        "DATABASE_URL environment variable is not set. "
        "Copy backend/.env.example to backend/.env and fill in credentials."
    )

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """FastAPI dependency: yield a DB session, close it when the request ends."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
