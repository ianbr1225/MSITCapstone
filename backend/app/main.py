"""
RetainIQ — Week 4 Backend
FastAPI server computing student risk levels from engagement scores.
"""

import sys
import time
import logging
from pathlib import Path
from typing import Literal

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Allow importing sibling modules (risk_engine.py lives next to app/)
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from risk_engine import compute_risk_level  # noqa: E402

logger = logging.getLogger("retainiq")
logging.basicConfig(level=logging.INFO)

app = FastAPI(title="RetainIQ API", version="0.2.0")

# Allow the Vite dev server to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["GET"],
    allow_headers=["*"],
)


# ── Request-timing middleware ────────────────────────────────────────
@app.middleware("http")
async def log_request_time(request: Request, call_next):
    """Log wall-clock duration for every request (for latency visibility)."""
    start = time.perf_counter()
    response = await call_next(request)
    duration_ms = (time.perf_counter() - start) * 1000
    logger.info(f"{request.method} {request.url.path} - {duration_ms:.1f}ms")
    return response


# ── Pydantic response model ─────────────────────────────────────────
class StudentRisk(BaseModel):
    """Schema for a single student risk record returned by the API."""
    name: str
    risk_level: Literal["High", "Medium", "Low"]
    engagement_score: int = Field(ge=0, le=100)


# ── Raw mock data (no DB — engagement scores only, risk is computed) ─
RAW_STUDENT_DATA = [
    {"name": "Alice Johnson",   "engagement_score": 23},
    {"name": "Brian Lee",       "engagement_score": 87},
    {"name": "Carmen Rivera",   "engagement_score": 54},
    {"name": "David Okonkwo",   "engagement_score": 18},
    {"name": "Elena Martinez",  "engagement_score": 91},
]


@app.get("/api/risk-list", response_model=list[StudentRisk])
def get_risk_list():
    """Return student risk data with levels computed from engagement scores."""
    return [
        {
            "name": s["name"],
            "engagement_score": s["engagement_score"],
            "risk_level": compute_risk_level(s["engagement_score"]),
        }
        for s in RAW_STUDENT_DATA
    ]
