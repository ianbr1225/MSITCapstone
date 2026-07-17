"""
RetainIQ — Rule-Based Risk Engine
Pure Python, zero framework imports. Independently unit-testable.

<!-- REFLECTION NEEDED: describe any challenge encountered implementing the
threshold logic or Pydantic validation, and how it was resolved -->
"""


def compute_risk_level(engagement_score: int) -> str:
    """Classify a student's attrition risk from their engagement score.

    Thresholds (deterministic, no ML):
        engagement_score < 30       → High   (scores 0–29)
        30 <= engagement_score < 65 → Medium (scores 30–64)
        engagement_score >= 65      → Low    (scores 65–100)

    Parameters
    ----------
    engagement_score : int
        An integer in the closed range [0, 100].

    Returns
    -------
    str
        One of ``"High"``, ``"Medium"``, or ``"Low"``.

    Raises
    ------
    ValueError
        If *engagement_score* is not an ``int`` (``bool`` is rejected) or
        falls outside the [0, 100] range.
    """
    # ── Type check (bool is a subclass of int, so reject it explicitly) ──
    if isinstance(engagement_score, bool) or not isinstance(engagement_score, int):
        raise ValueError(
            f"engagement_score must be an int, got {type(engagement_score).__name__}"
        )

    # ── Range check ──────────────────────────────────────────────────────
    if engagement_score < 0 or engagement_score > 100:
        raise ValueError(
            f"engagement_score must be between 0 and 100 inclusive, got {engagement_score}"
        )

    # ── Threshold classification ─────────────────────────────────────────
    if engagement_score < 30:
        return "High"
    if engagement_score < 65:
        return "Medium"
    return "Low"
