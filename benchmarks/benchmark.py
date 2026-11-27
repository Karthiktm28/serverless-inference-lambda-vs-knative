import argparse
import csv
import subprocess
import time
from datetime import datetime

import requests

URL = "http://127.0.0.1/predict"
HOST = "inference-api.default.127.0.0.1.sslip.io"
PAYLOAD = {"text": "this is a great product"}


def call():
    start = time.perf_counter()
    r = requests.post(URL, json=PAYLOAD, headers={"Host": HOST}, timeout=60)
    ms = (time.perf_counter() - start) * 1000
    return r.status_code, ms


def wait_for_scale_to_zero(timeout=180):
    """Poll until no inference-api pods are running."""
    end = time.time() + timeout
    while time.time() < end:
        out = subprocess.run(
            ["kubectl", "get", "pods", "-l",
             "serving.knative.dev/service=inference-api", "--no-headers"],
            capture_output=True, text=True,
        ).stdout.strip()
        if not out:
            return True
        time.sleep(5)
    return False


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--cold-runs", type=int, default=10)
    p.add_argument("--warm-runs", type=int, default=100)
    p.add_argument("--out", default="benchmarks/knative_results.csv")
    args = p.parse_args()

    rows = []

    for i in range(args.cold_runs):
        print(f"Cold run {i + 1}/{args.cold_runs}: waiting for scale-to-zero...")
        if not wait_for_scale_to_zero():
            print("  Pod did not scale to zero in time, skipping.")
            continue
        status, ms = call()
        print(f"  status={status} latency={ms:.0f} ms")
        rows.append(["knative", "cold", i + 1, status, round(ms, 2)])

    print("Warming up...")
    call()
    for i in range(args.warm_runs):
        status, ms = call()
        rows.append(["knative", "warm", i + 1, status, round(ms, 2)])
    print(f"Done {args.warm_runs} warm requests.")

    with open(args.out, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["platform", "type", "run", "status", "latency_ms"])
        w.writerows(rows)
    print(f"Saved to {args.out} at {datetime.now():%H:%M:%S}")


if __name__ == "__main__":
    main()