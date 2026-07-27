# RetainIQ — Deployment & Setup Guide

Procedural reference for setting up and running the RetainIQ system.
Covers prerequisites, environment configuration, and step-by-step commands
for both local development and the Docker-based deployment.

---

## System prerequisites

| Requirement | Version used in development |
|---|---|
| Python | 3.14.2 |
| Node.js / npm | (check `node --version` / `npm --version` locally) |
| Docker Desktop | Required for the containerized stack (Steps 5–6 of Week 5) |
| Git | Any recent version |

---

## Required environment variables

A single environment variable is required for the backend:

| Variable | Description | Example value |
|---|---|---|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://retainiq_user:retainiq_pass@localhost:5432/retainiq` |

The reference file is [`backend/.env.example`](../backend/.env.example).
For local development, copy it to `backend/.env` and edit as needed.
For the Docker stack, `DATABASE_URL` is set automatically in
`docker-compose.yml` — no `.env` file needed inside the container.

---

## Local development setup (without Docker)

### 1. Backend

```bash
cd backend

# Create a local .env from the example
cp .env.example .env
# Edit DATABASE_URL if your local Postgres uses different credentials

# Install Python dependencies
python -m pip install -r requirements.txt

# Create the database schema and seed initial data
# (Requires a running PostgreSQL instance at the URL in .env)
python seed.py

# Start the API server
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

The API will be available at `http://localhost:8000`.
Swagger UI is at `http://localhost:8000/docs`.

> **Note:** `seed.py` is a required first step for any fresh environment.
> It is the single place where schema creation (`create_all()`) happens —
> `main.py` intentionally does not create tables on startup.

### 2. Frontend

```bash
cd frontend

# Install Node dependencies
npm install

# Start the Vite dev server
npm run dev
```

The dashboard will be available at `http://localhost:5173`.
It fetches data from `http://localhost:8000/api/risk-list`.

---

## Docker-based setup

### 1. Start the stack

```bash
# From the repository root
docker compose up
```

This starts two services:
- **`db`** — PostgreSQL 16, with a healthcheck and a named volume (`pgdata`)
  for data persistence.
- **`backend`** — Python 3.14, runs `seed.py` (idempotent) then starts
  `uvicorn` on port 8000.

The backend waits for the database healthcheck to pass before starting.

### 2. Start the frontend (separately)

```bash
cd frontend
npm run dev
```

The frontend is **not** containerized — it runs via the standard Vite dev
server and connects to the backend at `http://localhost:8000`.

### 3. Verify the stack

- Swagger UI: `http://localhost:8000/docs`
- Risk list endpoint: `http://localhost:8000/api/risk-list`
- Dashboard: `http://localhost:5173`

### 4. Tear down

```bash
docker compose down           # stops containers, preserves volume
docker compose down -v        # stops containers AND deletes the pgdata volume
```

---

## Running the seed script

```bash
cd backend
python seed.py
```

Behavior:
- Creates the `students` table if it does not exist.
- Checks whether the table already has rows. If it does, prints a message
  and exits without inserting anything.
- If the table is empty, inserts 6 students (including Farida Hassan at
  score 65, a boundary case on the Medium/Low threshold).

**Idempotency:** Running `seed.py` twice results in exactly 6 rows, not 12.
This is safe to call on every Docker container start.

---

## Running tests

```bash
cd backend
python -m pytest tests/ --cov=risk_engine --cov=app.main --cov-report=term-missing -v
```

Tests do **not** require a running PostgreSQL instance or a `DATABASE_URL`
to be set. Integration tests use an in-memory SQLite database via FastAPI
dependency override — see `tests/integration/conftest.py` for the isolation
strategy.

Current suite: 36 tests (8 integration + 28 unit), 100% coverage on
`risk_engine.py` and `app/main.py`.

---

## Running the benchmark script

```bash
python scripts/benchmark.py [--url URL] [--n N]
```

| Flag | Default | Description |
|---|---|---|
| `--url` | `http://localhost:8000` | Base URL of the running API |
| `--n` | `100` | Number of requests to fire |

Output (console only):
- Average latency (ms)
- p95 latency (ms)
- Throughput (requests/second)

Run this against the Docker stack or a locally running uvicorn instance.
The API must be running before the benchmark script is started.

---

## Build / production notes

<!-- REFLECTION NEEDED: discuss production deployment strategy, hosting
     platform choices, and any additional configuration needed for a
     production environment vs. the current local/Docker dev setup -->

The current setup is oriented toward local development and demonstration.
No production deployment target (cloud platform, managed hosting, etc.)
has been configured as of Week 5 — this is deliberate scope deferral,
not an oversight.
