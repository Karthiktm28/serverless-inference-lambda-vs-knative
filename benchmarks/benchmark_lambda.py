import argparse
import csv
import subprocess
import time
import uuid

import requests

PAYLOAD = {"text": "this is a great product"}
FUNCTION = "inference-api"


def call(url):
    start = time.perf_counter()
    r = requests.post(f"{url}/predict", json=PAYLOAD, timeout=30)
    ms = (time.perf_counter() - start) * 1000
    return r.status_code, ms


def force_cold_start():
    """Changing an environment variable makes AWS discard the warm
    execution environments, so the next call is a cold start."""
    value = uuid.uuid4().hex[:8]
    update = subprocess.run(
        ["aws", "lambda", "update-function-configuration",
         "--function-name", FUNCTION,
         "--environment", f"Variables={{BENCH_RUN={value}}}"],
        capture_output=True, text=True,
    )
    if update.returncode != 0:
        raise RuntimeError(update.stderr)
    wait = subprocess.run(
        ["aws", "lambda", "wait", "function-updated",
         "--function-name", FUNCTION],
        capture_output=True, text=True,
    )
    if wait.returncode != 0:
        raise RuntimeError(wait.stderr)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--url", required=True)
    p.add_argument("--cold-runs", type=int, default=20)
    p.add_argument("--warm-runs", type=int, default=100)
    p.add_argument("--out", default="benchmarks/lambda_results.csv")
    args = p.parse_args()

    rows = []

    for i in range(args.cold_runs):
        print(f"Cold run {i + 1}/{args.cold_runs}: forcing a new environment...")
        force_cold_start()
        status, ms = call(args.url)
        print(f"  status={status} latency={ms:.0f} ms")
        rows.append(["lambda", "cold", i + 1, status, round(ms, 2)])

    print("Warming up...")
    call(args.url)
    for i in range(args.warm_runs):
        status, ms = call(args.url)
        rows.append(["lambda", "warm", i + 1, status, round(ms, 2)])
    print(f"Done {args.warm_runs} warm requests.")

    with open(args.out, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["platform", "type", "run", "status", "latency_ms"])
        w.writerows(rows)
    print(f"Saved to {args.out}")


if __name__ == "__main__":
    main()