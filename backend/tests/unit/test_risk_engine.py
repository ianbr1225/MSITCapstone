"""
White-box unit tests for risk_engine.compute_risk_level().
Tests the function directly in isolation — no FastAPI, no HTTP.
"""

import pytest
from risk_engine import compute_risk_level


# ── Valid inputs — High risk (engagement_score < 30) ─────────────────

@pytest.mark.parametrize("score", [0, 1, 18, 23, 29])
def test_high_risk(score):
    assert compute_risk_level(score) == "High"


# ── Valid inputs — Medium risk (30 <= engagement_score < 65) ─────────

@pytest.mark.parametrize("score", [30, 31, 54, 64])
def test_medium_risk(score):
    assert compute_risk_level(score) == "Medium"


# ── Valid inputs — Low risk (engagement_score >= 65) ─────────────────

@pytest.mark.parametrize("score", [65, 66, 87, 91, 100])
def test_low_risk(score):
    assert compute_risk_level(score) == "Low"


# ── Boundary values ──────────────────────────────────────────────────

def test_boundary_29_is_high():
    """29 is the last High score (< 30)."""
    assert compute_risk_level(29) == "High"


def test_boundary_30_is_medium():
    """30 is the first Medium score (>= 30)."""
    assert compute_risk_level(30) == "Medium"


def test_boundary_64_is_medium():
    """64 is the last Medium score (< 65)."""
    assert compute_risk_level(64) == "Medium"


def test_boundary_65_is_low():
    """65 is the first Low score (>= 65)."""
    assert compute_risk_level(65) == "Low"


# ── Invalid inputs — out of range ────────────────────────────────────

@pytest.mark.parametrize("score", [-1, -100, 101, 200])
def test_out_of_range_raises_value_error(score):
    with pytest.raises(ValueError, match="must be between 0 and 100"):
        compute_risk_level(score)


# ── Invalid inputs — wrong type ──────────────────────────────────────

@pytest.mark.parametrize("score", ["50", 50.5, None, True, False, [50]])
def test_wrong_type_raises_value_error(score):
    with pytest.raises(ValueError, match="must be an int"):
        compute_risk_level(score)
