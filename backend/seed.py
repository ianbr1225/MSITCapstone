"""
RetainIQ — Idempotent seed script.

Usage:
    python seed.py

Behavior:
- Creates the `students` table if it doesn't exist (schema creation lives
  here and ONLY here — main.py intentionally does NOT call create_all()).
- If the table already has rows, prints a message and exits without inserting
  anything. Running this script twice is safe — it will not duplicate rows.
- If the table is empty, inserts the 5 canonical mock students.

This script is called automatically by the Docker container CMD before
uvicorn starts, and can also be run manually for local environment setup.
"""

import sys
from pathlib import Path

# Ensure the backend directory is on the path so database/models resolve
# whether this is run as `python seed.py` from backend/ or from Docker.
sys.path.insert(0, str(Path(__file__).resolve().parent))

from database import Base, SessionLocal, engine  # noqa: E402
from models import Student  # noqa: E402

# ── The one authoritative place where the schema is created ─────────────
if engine is None:
    raise RuntimeError(
        "DATABASE_URL is not set — cannot seed. "
        "Copy backend/.env.example to backend/.env and fill in credentials, "
        "or ensure the DATABASE_URL environment variable is exported."
    )
Base.metadata.create_all(bind=engine)

SEED_DATA = [
    {"name": "Alice Johnson",  "engagement_score": 23},
    {"name": "Brian Lee",      "engagement_score": 87},
    {"name": "Carmen Rivera",  "engagement_score": 54},
    {"name": "David Okonkwo",  "engagement_score": 18},
    {"name": "Elena Martinez", "engagement_score": 91},
]


def seed():
    db = SessionLocal()
    try:
        count = db.query(Student).count()
        if count > 0:
            print(f"[seed] Table already has {count} row(s) — skipping insert.")
            return

        students = [Student(**row) for row in SEED_DATA]
        db.add_all(students)
        db.commit()
        print(f"[seed] Inserted {len(students)} student(s) successfully.")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
