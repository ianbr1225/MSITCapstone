"""
RetainIQ — SQLAlchemy ORM models.

Defines the database schema. Note: risk_level is intentionally NOT stored —
it is computed at request time by compute_risk_level() to avoid data drift.
"""

from sqlalchemy import Column, Integer, String

from database import Base


class Student(Base):
    """A student record with an engagement score (risk level is derived)."""

    __tablename__ = "students"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    engagement_score = Column(Integer, nullable=False)

    def __repr__(self):
        return f"<Student(id={self.id}, name={self.name!r}, engagement_score={self.engagement_score})>"
