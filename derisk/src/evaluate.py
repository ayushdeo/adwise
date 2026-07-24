#!/usr/bin/env python3
"""
evaluate.py — Sweep each policy's knob to trace a revenue-vs-trust curve.

For every policy family we vary the knob that controls how aggressively it
inserts ads, producing a set of (mean_trust, mean_revenue) points. The ORACLE
frontier is traced by sweeping the budget B (its true Pareto ceiling for the
data). Output: results/pareto.csv, consumed by plot.py.

Budget note: by default B is generous (--budget 999) so the *policy knob* traces
the full frontier rather than the budget clipping it. Lower --budget to study the
session-trust-budget mechanic itself.

Run
---
  python src/evaluate.py                      # uses cache/features.parquet, else synthetic
  python src/evaluate.py --synthetic          # force synthetic
  python src/evaluate.py --budget 1.5         # exercise a binding trust budget
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path
from typing import Dict, List, Tuple

import policies as P

# ------------------------------------------------------------------ knob grids

def linspace(a: float, b: float, n: int) -> List[float]:
    if n == 1:
        return [a]
    step = (b - a) / (n - 1)
    return [round(a + i * step, 4) for i in range(n)]

def sweep_points(convs, budget: float, seeds: int = 5) -> List[Dict]:
    """Return list of {policy, knob, mean_trust, mean_revenue} rows."""
    rows: List[Dict] = []

    def add(policy_name, knob, pol, n_seeds=1):
        # average over seeds for stochastic policies
        rev = trust = 0.0
        for s in range(n_seeds):
            m = P.evaluate(convs, pol, budget, seed=s)
            rev += m["mean_revenue"]; trust += m["mean_trust"]
        rows.append({"policy": policy_name, "knob": knob,
                     "mean_trust": trust / n_seeds, "mean_revenue": rev / n_seeds})

    # corner references
    add("P0_never", 0.0, P.p_never())
    add("P1_always", 1.0, P.p_always())

    # P2 random: p in [0,1], stochastic -> average seeds
    for p in linspace(0.0, 1.0, 11):
        add("P2_random", p, P.p_random(p), n_seeds=seeds)

    # P3 static-coherence: theta over the 1..5 fit scale (lower theta -> more ads)
    for theta in [5, 4, 3, 2, 1]:
        add("P3_static", float(theta), P.p_static_coherence(theta))

    # P4 receptivity-gated: tau in [0,1] (higher tau -> fewer ads)  [OURS v1]
    for tau in linspace(0.0, 1.0, 11):
        add("P4_receptivity", tau, P.p_receptivity_gated(tau))

    # P5 value-greedy: lambda grid (higher lambda -> fewer ads)     [OURS v2 stand-in]
    for lam in [0.0, 0.25, 0.5, 1.0, 1.5, 2.0, 3.0, 5.0, 8.0, 12.0, 20.0, 50.0]:
        add("P5_value", lam, P.p_value_greedy(lam))

    # P6 learned controller: threshold sweep (only if scores were merged into slots)
    if any(s.score is not None for c in convs for s in c.slots):
        for thr in linspace(0.0, 1.0, 21):
            add("P6_learned", thr, P.p_learned(thr))

    return rows

def oracle_frontier(convs, b_grid: List[float]) -> List[Dict]:
    rows = []
    for b in b_grid:
        m = P.evaluate_oracle(convs, b)
        # plot the oracle at its REALIZED trust (it often spends < budget cap),
        # so it is a true upper bound for every policy at matched trust.
        rows.append({"policy": "ORACLE", "knob": b,
                     "mean_trust": m["mean_trust"], "mean_revenue": m["mean_revenue"]})
    return rows

# ------------------------------------------------------------------ main

def main() -> None:
    ap = argparse.ArgumentParser(description="Policy knob sweep -> results/pareto.csv")
    ap.add_argument("--features", type=str, default="cache/features.parquet")
    ap.add_argument("--scores", type=str, default="cache/controller_scores.parquet",
                    help="learned-controller scores; if present, adds the P6_learned curve")
    ap.add_argument("--out", type=str, default="results/pareto.csv")
    ap.add_argument("--budget", type=float, default=999.0,
                    help="trust budget; large => knob traces full frontier")
    ap.add_argument("--seeds", type=int, default=5, help="seeds for stochastic policies")
    ap.add_argument("--synthetic", action="store_true")
    args = ap.parse_args()

    path = Path(args.features)
    if args.synthetic or not path.exists():
        if not args.synthetic:
            print(f"[info] {path} not found -> synthetic data.")
        convs = P.make_synthetic()
        source = "synthetic"
    else:
        scores = Path(args.scores)
        convs = P.load_features(path, scores if scores.exists() else None)
        source = str(path) + (f" + {scores}" if scores.exists() else "")
    print(f"Evaluating {len(convs)} conversations from {source}, budget={args.budget}")

    rows = sweep_points(convs, args.budget, seeds=args.seeds)

    # oracle frontier over a trust grid spanning the data
    max_trust = max((r["mean_trust"] for r in rows if r["policy"] == "P1_always"), default=1.0)
    b_grid = linspace(0.02, max(0.1, max_trust * 1.1), 40)  # dense => tight concave frontier
    rows += oracle_frontier(convs, b_grid)

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["policy", "knob", "mean_trust", "mean_revenue"])
        w.writeheader()
        for r in rows:
            w.writerow(r)
    print(f"Wrote {len(rows)} rows -> {out}")
    print(f"  next: python src/plot.py --pareto {out}")


if __name__ == "__main__":
    main()
