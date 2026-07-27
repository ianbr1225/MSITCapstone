"""
Black-box / integration tests for the /api/risk-list endpoint.
Uses FastAPI TestClient — exercises the full request/response cycle.

Test data and DB isolation are provided by conftest.py (SQLite in-memory,
get_db dependency override). These tests do NOT depend on seed.py or a
running Postgres instance.
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app, StudentRisk
from risk_engine import compute_risk_level

# NOTE: `client` fixture is defined in conftest.py — it wires a TestClient
# to an in-memory SQLite DB seeded with the same 5 students as production.
# RAW_STUDENT_DATA is no longer imported; the source of truth is now the DB.

EXPECTED_COUNT = 5  # matches TEST_STUDENTS in conftest.py


# ── Basic endpoint contract ──────────────────────────────────────────

def test_risk_list_returns_200(client):
    response = client.get("/api/risk-list")
    assert response.status_code == 200


def test_risk_list_returns_correct_count(client):
    response = client.get("/api/risk-list")
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == EXPECTED_COUNT


def test_risk_list_has_correct_keys(client):
    response = client.get("/api/risk-list")
    data = response.json()
    expected_keys = {"name", "risk_level", "engagement_score"}
    for record in data:
        assert set(record.keys()) == expected_keys


# ── Schema validation ────────────────────────────────────────────────

def test_risk_list_conforms_to_pydantic_model(client):
    """Every record in the response must parse into StudentRisk."""
    response = client.get("/api/risk-list")
    data = response.json()
    for record in data:
        parsed = StudentRisk(**record)
        assert parsed.risk_level in ("High", "Medium", "Low")
        assert 0 <= parsed.engagement_score <= 100


# ── Risk level correctness ──────────────────────────────────────────

def test_risk_levels_match_engine(client):
    """Every returned risk_level must agree with compute_risk_level()."""
    response = client.get("/api/risk-list")
    for record in response.json():
        expected = compute_risk_level(record["engagement_score"])
        assert record["risk_level"] == expected, (
            f"{record['name']}: expected {expected}, got {record['risk_level']}"
        )


def test_alice_johnson_is_high_risk(client):
    """Spot-check: Alice Johnson (engagement=23) → High."""
    response = client.get("/api/risk-list")
    alice = next(r for r in response.json() if r["name"] == "Alice Johnson")
    assert alice["risk_level"] == "High"
    assert alice["engagement_score"] == 23


def test_brian_lee_is_low_risk(client):
    """Spot-check: Brian Lee (engagement=87) → Low."""
    response = client.get("/api/risk-list")
    brian = next(r for r in response.json() if r["name"] == "Brian Lee")
    assert brian["risk_level"] == "Low"
    assert brian["engagement_score"] == 87


# ── CORS ─────────────────────────────────────────────────────────────

def test_cors_header_for_allowed_origin(client):
    """CORS should reflect http://localhost:5173 as an allowed origin."""
    response = client.get(
        "/api/risk-list",
        headers={"Origin": "http://localhost:5173"},
    )
    assert response.headers.get("access-control-allow-origin") == "http://localhost:5173"
