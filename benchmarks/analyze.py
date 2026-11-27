import argparse
import csv
import statistics
from collections import defaultdict

import matplotlib.pyplot as plt


def percentile(data, p):
    data = sorted(data)
    k = (len(data) - 1) * p / 100
    lo, hi = int(k), min(int(k) + 1, len(data) - 1)
    return data[lo] + (data[hi] - data[lo]) * (k - lo)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", default="benchmarks/knative_results.csv")
    ap.add_argument("--chart", default="benchmarks/knative_chart.png")
    ap.add_argument("--title", default="Knative on Minikube: cold vs warm latency")
    args = ap.parse_args()

    groups = defaultdict(list)
    with open(args.csv) as f:
        for row in csv.DictReader(f):
            if row["status"] == "200":
                groups[row["type"]].append(float(row["latency_ms"]))

    print(f"{'type':<6} {'n':>4} {'min':>8} {'p50':>8} {'p95':>8} {'max':>8} {'mean':>8}")
    stats = {}
    for t in ("cold", "warm"):
        d = groups.get(t, [])
        if not d:
            continue
        stats[t] = {
            "p50": percentile(d, 50),
            "p95": percentile(d, 95),
        }
        print(
            f"{t:<6} {len(d):>4} {min(d):>8.1f} {stats[t]['p50']:>8.1f} "
            f"{stats[t]['p95']:>8.1f} {max(d):>8.1f} {statistics.mean(d):>8.1f}"
        )

    labels = list(stats.keys())
    x = range(len(labels))
    w = 0.35
    fig, ax = plt.subplots(figsize=(6, 4))
    b1 = ax.bar([i - w / 2 for i in x], [stats[l]["p50"] for l in labels], w, label="p50")
    b2 = ax.bar([i + w / 2 for i in x], [stats[l]["p95"] for l in labels], w, label="p95")
    ax.bar_label(b1, fmt="%.0f")
    ax.bar_label(b2, fmt="%.0f")
    ax.set_xticks(list(x))
    ax.set_xticklabels(labels)
    ax.set_ylabel("Latency (ms)")
    ax.set_title(args.title)
    ax.legend()
    fig.tight_layout()
    fig.savefig(args.chart, dpi=150)
    print(f"Chart saved to {args.chart}")


if __name__ == "__main__":
    main()