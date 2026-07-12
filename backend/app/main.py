"""
RetainIQ — Week 4 MVP Backend
Single-file FastAPI server returning hardcoded student risk data.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="RetainIQ API", version="0.1.0")

# Allow the Vite dev server to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["GET"],
    allow_headers=["*"],
)

# ── Hardcoded mock data (no DB, no ML) ──────────────────────────────
MOCK_STUDENTS = [
    {"name": "Alice Johnson",   "risk_level": "High",   "engagement_score": 23},
    {"name": "Brian Lee",       "risk_level": "Low",    "engagement_score": 87},
    {"name": "Carmen Rivera",   "risk_level": "Medium", "engagement_score": 54},
    {"name": "David Okonkwo",   "risk_level": "High",   "engagement_score": 18},
    {"name": "Elena Martinez",  "risk_level": "Low",    "engagement_score": 91},
]


@app.get("/api/risk-list")
def get_risk_list():
    """Return the mock student risk list."""
    return MOCK_STUDENTS
