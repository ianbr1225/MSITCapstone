"""
RetainIQ — Latency and throughput benchmark script.

Usage:
    python scripts/benchmark.py [--url URL] [--n N]

    --url   Base URL of the API (default: http://localhost:8000)
    --n     Number of requests to fire (default: 100)

Output (console only — no dashboard, no persistence):
    - Per-request latency (ms)
    - Average latency (ms)
    - p95 latency (ms)
    - Throughput (requests/second)

Run this against the Dockerized stack:
    docker compose up -d
    python scripts/benchmark.py

Or against a locally running uvicorn:
    uvicorn app.main:app --app-dir backend
    python scripts/benchmark.py
"""

import argparse
import statistics
import time

import httpx


def run_benchmark(base_url: str, n: int) -> None:
    endpoint = f"{base_url}/api/risk-list"
    print(f"\nRetainIQ Benchmark")
    print(f"  Endpoint : {endpoint}")
    print(f"  Requests : {n}")
    print("-" * 45)

    latencies_ms: list[float] = []

    # Warm-up: one request not counted in results
    try:
        httpx.get(endpoint, timeout=10.0)
    except Exception as exc:
        print(f"[ERROR] Could not reach {endpoint}: {exc}")
        print("  Make sure the backend is running (docker compose up or uvicorn).")
        return

    wall_start = time.perf_counter()

    for i in range(n):
        t0 = time.perf_counter()
        response = httpx.get(endpoint, timeout=10.0)
        t1 = time.perf_counter()

        if response.status_code != 200:
            print(f"  [WARN] Request {i + 1} returned HTTP {response.status_code}")

        latencies_ms.append((t1 - t0) * 1000)

    wall_elapsed = time.perf_counter() - wall_start

    avg_ms   = statistics.mean(latencies_ms)
    p95_ms   = sorted(latencies_ms)[int(len(latencies_ms) * 0.95)]
    rps      = n / wall_elapsed

    print(f"  Average latency : {avg_ms:.2f} ms")
    print(f"  p95 latency     : {p95_ms:.2f} ms")
    print(f"  Throughput      : {rps:.2f} req/s")
    print("-" * 45)


def main() -> None:
    parser = argparse.ArgumentParser(description="RetainIQ API benchmark")
    parser.add_argument(
        "--url",
        default="http://localhost:8000",
        help="Base URL of the API (default: http://localhost:8000)",
    )
    parser.add_argument(
        "--n",
        type=int,
        default=100,
        help="Number of requests to fire (default: 100)",
    )
    args = parser.parse_args()
    run_benchmark(base_url=args.url, n=args.n)


if __name__ == "__main__":
    main()
