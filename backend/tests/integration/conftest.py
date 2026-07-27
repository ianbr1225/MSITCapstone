"""
Integration test fixtures for the /api/risk-list endpoint.

Isolation strategy: SQLite in-memory database with dependency override
-----------------------------------------------------------------------
We override the FastAPI `get_db` dependency to point at an in-memory SQLite
engine instead of the production Postgres database. This means:

  1. Tests run without requiring a live Postgres instance (no docker compose
     up needed to run the test suite).
  2. Each test function gets a fresh session seeded with known data; the
     session is rolled back after the test so tests are fully independent.
  3. The get_db override only intercepts route-level dependency calls.
     This is why main.py has NO module-level create_all() — if it did, that
     would fire at import time against the production engine, bypassing our
     SQLite override entirely and failing whenever Postgres isn't running.

SQLite connection pinning
--------------------------
Plain `sqlite://` (in-memory) creates a brand-new, empty database for every
new connection. Since FastAPI's TestClient opens connections independently of
the fixture session, all sessions must be pinned to the SAME underlying
connection so they share the same in-memory state. We achieve this by creating
the engine with a static pool (StaticPool) that always returns the same
connection object.

Known trade-off: SQLite and Postgres have dialect differences (e.g. JSON
columns, RETURNING clauses, case-sensitivity of LIKE). For this schema
(id/name/engagement_score only, no Postgres-specific types or queries) the
risk is negligible — all existing assertions remain valid across both dialects.
"""

import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Make backend/ importable from within the tests/integration/ subdirectory
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from app.main import app           # noqa: E402
from database import Base, get_db  # noqa: E402
from models import Student         # noqa: E402

# ── In-memory SQLite engine for tests ───────────────────────────────────
# StaticPool pins all sessions to a single connection so that tables created
# in the fixture are visible to the route handler's session during the test.
TEST_DATABASE_URL = "sqlite://"
test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


# Known test data — mirrors the production seed but is defined here so tests
# are independent of seed.py's behaviour (running seed.py is not a prerequisite
# for running the test suite).
TEST_STUDENTS = [
    {"name": "Alice Johnson",  "engagement_score": 23},   # → High
    {"name": "Brian Lee",      "engagement_score": 87},   # → Low
    {"name": "Carmen Rivera",  "engagement_score": 54},   # → Medium
    {"name": "David Okonkwo",  "engagement_score": 18},   # → High
    {"name": "Elena Martinez", "engagement_score": 91},   # → Low
    {"name": "Farida Hassan",  "engagement_score": 65},   # → Low (boundary: exactly 65, the first Low score)
]


@pytest.fixture(scope="function")
def db_session():
    """Create all tables in SQLite, seed test data, yield session, rollback."""
    Base.metadata.create_all(bind=test_engine)
    session = TestingSessionLocal()
    try:
        session.add_all([Student(**s) for s in TEST_STUDENTS])
        session.commit()
        yield session
    finally:
        session.rollback()
        session.close()
        Base.metadata.drop_all(bind=test_engine)


@pytest.fixture(scope="function")
def client(db_session):
    """
    TestClient with the get_db dependency overridden to use the test SQLite
    session, ensuring no real Postgres connection is attempted during tests.
    """
    def override_get_db():
        try:
            yield db_session
        finally:
            pass  # rollback/close handled by db_session fixture

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
