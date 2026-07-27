# RetainIQ — Agent Handoff Guide

Technical reference for an AI coding agent picking up this codebase.
Covers project structure, conventions, key files, and how to run everything.

---

## Project purpose

RetainIQ is a decision-support web app for university lecturers to identify
at-risk students. A lecturer sees a risk-sorted table of students, color-coded
by risk level (High / Medium / Low), computed from engagement scores.

The system is explicitly a **decision support tool** — it surfaces
information, it does not take action on its own.

---

## Repository layout

```
retainiq/
├── backend/
│   ├── app/
│   │   └── main.py              ← FastAPI app, /api/risk-list endpoint
│   ├── tests/
│   │   ├── integration/
│   │   │   ├── conftest.py      ← SQLite in-memory test fixtures (StaticPool)
│   │   │   └── test_api.py      ← Black-box endpoint tests
│   │   └── unit/
│   │       └── test_risk_engine.py  ← White-box pure-function tests
│   ├── database.py              ← SQLAlchemy engine, SessionLocal, get_db dependency
│   ├── models.py                ← Student ORM model (no risk_level column)
│   ├── risk_engine.py           ← compute_risk_level() — pure function, no deps
│   ├── seed.py                  ← Idempotent seed + schema creation (the ONLY create_all)
│   ├── requirements.txt
│   ├── Dockerfile
│   ├── .dockerignore
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   └── LecturerDashboard.jsx  ← Main dashboard component
│   │   └── utils/
│   │       └── sortStudents.js        ← Pure sorting function (tested)
│   ├── package.json
│   └── vite.config.js
├── scripts/
│   └── benchmark.py             ← Latency/throughput benchmark (httpx)
├── docs/                        ← Architecture, version control, handoff docs
├── docker-compose.yml           ← Backend + Postgres orchestration
└── .gitignore
```

---

## Critical design decisions to respect

1. **`risk_engine.py` is frozen.** The scoring function's logic and
   thresholds are complete and tested. Do not change its signature or
   behavior. Only the data source feeding it changes between weeks.

2. **No `create_all()` in `main.py`.** Schema creation is the exclusive
   responsibility of `seed.py`. Putting `create_all()` at module level in
   `main.py` would fire at import time and break pytest's SQLite-based test
   isolation (the `get_db` override only intercepts route-level calls, not
   module-level engine operations).

3. **`risk_level` is never stored.** It is derived at request time by
   `compute_risk_level()`. Storing it would create a value that can drift
   out of sync with its source data.

4. **`database.py` engine is lazily constructed.** `engine` and
   `SessionLocal` are `None` when `DATABASE_URL` is unset. This allows
   `from database import Base, get_db` to succeed at import time without
   requiring a live database — tests override `get_db` entirely.

5. **Tests use SQLite in-memory, not Postgres.** The `conftest.py` creates
   an in-memory SQLite engine with `StaticPool` (pinning all sessions to one
   connection so tables are visible across sessions). Known tradeoff: SQLite
   dialect differs from Postgres, but the schema is simple enough that this
   is negligible.

---

## How to run

### Local development (no Docker)

```bash
# Backend
cd backend
cp .env.example .env          # edit DATABASE_URL if needed
pip install -r requirements.txt
python seed.py                # creates schema + seeds data (idempotent)
uvicorn app.main:app --reload

# Frontend
cd frontend
npm install
npm run dev                   # runs on http://localhost:5173
```

### Docker stack

```bash
docker compose up             # starts backend + postgres
# Frontend still runs separately:
cd frontend && npm run dev
```

### Tests

```bash
cd backend
python -m pytest tests/ --cov=risk_engine --cov=app.main --cov-report=term-missing -v
```

No `DATABASE_URL` needed — tests use SQLite in-memory via dependency override.

### Benchmark

```bash
python scripts/benchmark.py --url http://localhost:8000 --n 100
```

---

## Branch and commit conventions

- **Branches:** `main` (stable) ← `development` (integration) ← `feature/<name>` (work).
- **Commits:** Conventional style (`feat:`, `test:`, `refactor:`, `chore:`, `docs:`).
- **Merges:** Non-squash (preserve incremental history). Feature → development via PR.
- **Tags:** Annotated, `v0.X-<name>` pattern. Each has a GitHub Release.

---

## Current tags

| Tag | What shipped |
|---|---|
| `v0.1-architecture` | Architecture + design phase |
| `v0.2-scaffold` | Repository scaffolding |
| `v0.3-mock-mvp` | Mock-data MVP (dashboard + simulated API) |
| `v0.4-core-logic-tests` | Rule-based risk engine, testing, output validation |
| `v0.5-integration` | PostgreSQL, Docker, benchmarking |

---

## Seeded data (6 students)

| Name | Engagement Score | Risk Level |
|---|---|---|
| Alice Johnson | 23 | High |
| Brian Lee | 87 | Low |
| Carmen Rivera | 54 | Medium |
| David Okonkwo | 18 | High |
| Elena Martinez | 91 | Low |
| Farida Hassan | 65 | Low (boundary) |

Farida Hassan sits exactly on the Medium/Low threshold (`>= 65 → Low`),
providing a real boundary case in the seeded dataset.

---

## Explicit non-goals (as of Week 5)

Do not build these unless the user explicitly asks:
- Authentication / authorization
- Alembic or any migration tooling
- Frontend containerization
- Metrics dashboard or persistent metrics storage
- ML-based risk scoring (current logic is rule-based by design)
