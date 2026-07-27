# RetainIQ — System Architecture

## Overview

RetainIQ is a decision-support web application that helps university lecturers
identify at-risk students based on engagement and performance signals. The
system follows a three-tier architecture: a React frontend, a FastAPI backend
exposing a REST API, and a PostgreSQL database for persistence.

This document reflects the architecture as actually implemented through
Week 5 (System Integration). Where scope was deliberately deferred to later
project phases, that is noted explicitly rather than described as complete.

> **Note:** This document was reconstructed from project records and current
> implementation. If the original Week 3 design doc used different module
> names or groupings, reconcile them against this version before treating it
> as final.

---

## Component Diagram (logical)

```
┌─────────────────────┐       HTTP (JSON)       ┌──────────────────────┐
│   React Frontend     │ ──────────────────────► │   FastAPI Backend    │
│   (Vite)              │ ◄────────────────────── │                       │
└─────────────────────┘                          └──────────┬───────────┘
                                                              │
                                                              │ SQLAlchemy
                                                              ▼
                                                   ┌──────────────────────┐
                                                   │   PostgreSQL          │
                                                   │   (students table)    │
                                                   └──────────────────────┘

Deployment: Docker Compose orchestrates the backend and database as
containerized services. The frontend runs independently (npm run dev / build)
and is pointed at the backend's exposed port.
```

---

## Modules

### 1. Frontend — Dashboard UI
- **Tech:** React (Vite), CSS Modules.
- **Responsibility:** Renders the lecturer-facing dashboard: a risk-sorted,
  sortable table of students with hover states, loading states, and a
  fade-in transition on data load.
- **Key file:** `LecturerDashboard.jsx` (+ `LecturerDashboard.module.css`).
- **Data flow:** Fetches from `/api/risk-list` on mount; client-side sorting
  handled by a pure, independently-tested `sortStudents` function.

### 2. Backend — API Layer
- **Tech:** FastAPI.
- **Responsibility:** Exposes `/api/risk-list`, orchestrates the request
  lifecycle (DB query → risk computation → response validation), and applies
  CORS policy for the frontend origin.
- **Key file:** `app/main.py`.

### 3. Backend — Risk Engine (core logic)
- **Tech:** Pure Python, no framework dependencies.
- **Responsibility:** Deterministic, threshold-based risk classification.
  Takes an `engagement_score` (0–100) and returns `High`, `Medium`, or `Low`.
  No machine learning is used at this stage of the project — this is
  explicit, documented scope, not an oversight. The function is structured
  to accept additional named signals later, so it is forward-compatible with
  a future feature-engineering/ML phase without requiring a rewrite.
- **Key file:** `risk_engine.py`.
- **Validation:** Out-of-range or malformed input raises `ValueError` rather
  than silently producing incorrect output.

### 4. Backend — Data Models & Persistence
- **Tech:** SQLAlchemy ORM, PostgreSQL.
- **Responsibility:** Defines the `Student` table (`id`, `name`,
  `engagement_score`). Risk level is intentionally **not** stored — it is
  derived at request time by the Risk Engine, avoiding a stored value that
  could drift out of sync with its source data.
- **Key files:** `database.py` (engine/session/dependency), `models.py`
  (ORM model).

### 5. Backend — Data Seeding
- **Tech:** Python script using the same SQLAlchemy session setup.
- **Responsibility:** Idempotently seeds baseline student records on first
  run (schema creation + insert-if-empty check). Safe to run repeatedly
  without duplicating data. This is the single place schema creation
  happens in the system.
- **Key file:** `seed.py`.

### 6. Backend — Output Validation
- **Tech:** Pydantic.
- **Responsibility:** Defines the `StudentRisk` response schema
  (`name`, `risk_level`, `engagement_score` with range constraints) and
  enforces it on every API response via FastAPI's `response_model`, so
  malformed data cannot silently leave the system.

### 7. Backend — Observability (timing middleware)
- **Tech:** FastAPI middleware.
- **Responsibility:** Logs per-request latency (method, path, duration in
  ms) to the console. Basis for the quantitative performance metrics
  produced by the benchmarking module below.

### 8. Tooling — Performance Benchmarking
- **Tech:** Python script using `httpx`.
- **Responsibility:** Fires a configurable number of requests against
  `/api/risk-list` and reports average latency, p95 latency, and
  requests-per-second throughput to the console. No dashboard or persistent
  metrics storage — output is consumed manually for reporting.
- **Key file:** `scripts/benchmark.py`.

### 9. Deployment — Containerization
- **Tech:** Docker, Docker Compose.
- **Responsibility:** Packages the backend and database as two orchestrated
  services (`backend`, `db`) with environment-variable-driven configuration,
  a healthcheck-gated startup order, and a named volume for database
  persistence. The frontend is deliberately excluded from containerization
  at this stage — it runs via the standard Vite dev/build workflow and is
  pointed at the backend's exposed port.

---

## Deliberately deferred (out of current scope)

The following were identified in early planning but are **not** implemented,
by design, as of Week 5:

- Authentication / authorization
- Machine learning-based risk scoring (current logic is rule-based and
  explainable by design)
- Scheduled/automated data ingestion pipeline
- Student-level detail drill-down view
- Database migration tooling (schema is created via a single
  `create_all()` call, appropriate at the current single-table scale)

This is intentional scope discipline, not an oversight — each item is
deferred to keep every implemented piece honest, working, and testable
rather than partially built.

---

## Data Flow (single request)

1. Frontend requests `GET /api/risk-list` on dashboard load.
2. FastAPI route handler receives the request, obtains a DB session via
   dependency injection (`get_db`).
3. SQLAlchemy queries all rows from the `students` table.
4. Each row's `engagement_score` is passed to `compute_risk_level()` in the
   Risk Engine, producing a `risk_level`.
5. Results are assembled into `StudentRisk` objects and validated against
   the Pydantic response model before being serialized to JSON.
6. Frontend receives the response, sorts it client-side via `sortStudents`,
   and renders the dashboard table.

Timing middleware logs the duration of this entire cycle at step 2–5.
