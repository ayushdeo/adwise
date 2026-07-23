#!/usr/bin/env python3
"""
plot.py — Draw the revenue-vs-trust Pareto figure AND compute the pre-registered
go/no-go verdict.

Reads results/pareto.csv (from evaluate.py), writes:
  - results/pareto.png     the figure (one curve per policy + oracle ceiling)
  - results/go_no_go.md    the automated verdict against the pre-registered criteria

Pre-registered GO criteria (from docs/derisk-harness-spec.md):
  1. Pareto dominance: OURS (best of P4/P5) beats baselines (best of P2/P3) by
     >= 15% relative revenue at matched trust, across most of the overlapping range.
  2. Oracle gap: OURS reaches >= 70% of the ORACLE revenue at matched trust.
  3. (Robustness across judge = checked separately with the calibration subset.)

Run
---
  python src/plot.py                          # uses results/pareto.csv
"""

from __future__ import annotations

import argparse
import csv
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Tuple

import matplotlib
matplotlib.use("Agg")  # headless-safe (works over the VS Code extension / no display)
import matplotlib.pyplot as plt

OURS = {"P4_receptivity", "P5_value"}
BASELINES = {"P2_random", "P3_static"}

# ------------------------------------------------------------------ io

def load_pareto(path: Path) -> Dict[str, List[Tuple[float, float]]]:
    """policy -> sorted list of (trust, revenue) points."""
    by_policy: Dict[str, List[Tuple[float, float]]] = defaultdict(list)
    with path.open("r", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            by_policy[row["policy"]].append(
                (float(row["mean_trust"]), float(row["mean_revenue"])))
    for p in by_policy:
        by_policy[p] = sorted(by_policy[p])
    return by_policy

def interp_revenue(points: List[Tuple[float, float]], trust: float) -> float:
    """Piecewise-linear revenue at a given trust; None-safe outside range."""
    xs = [t for t, _ in points]
    ys = [r for _, r in points]
    if trust < xs[0] or trust > xs[-1]:
        return float("nan")
    for i in range(1, len(xs)):
        if xs[i] >= trust:
            x0, x1, y0, y1 = xs[i - 1], xs[i], ys[i - 1], ys[i]
            if x1 == x0:
                return max(y0, y1)
            return y0 + (y1 - y0) * (trust - x0) / (x1 - x0)
    return ys[-1]

def upper_envelope(by_policy, names) -> List[Tuple[float, float]]:
    """Merge several policies into one monotone upper-envelope curve."""
    pts = []
    for n in names:
        pts += by_policy.get(n, [])
    pts = sorted(pts)
    env, best = [], -1.0
    for t, r in pts:
        best = max(best, r)
        env.append((t, best))
    return env

# ------------------------------------------------------------------ figure

STYLE = {
    "P0_never": ("#999999", "o", "P0 never"),
    "P1_always": ("#d62728", "s", "P1 always"),
    "P2_random": ("#ff7f0e", "^", "P2 random"),
    "P3_static": ("#8c564b", "D", "P3 static-coherence"),
    "P4_receptivity": ("#1f77b4", "o", "P4 receptivity-gated (ours)"),
    "P5_value": ("#2ca02c", "P", "P5 value-greedy (ours)"),
    "ORACLE": ("#000000", None, "Oracle (upper bound)"),
}

def draw(by_policy, out_png: Path) -> None:
    plt.figure(figsize=(7.5, 5.5))
    for pol, (color, marker, label) in STYLE.items():
        if pol not in by_policy:
            continue
        pts = by_policy[pol]
        xs = [t for t, _ in pts]; ys = [r for _, r in pts]
        if pol == "ORACLE":
            plt.plot(xs, ys, "--", color=color, label=label, linewidth=2, zorder=5)
        elif pol in ("P0_never", "P1_always"):
            plt.scatter(xs, ys, color=color, marker=marker, s=70, label=label, zorder=4)
        else:
            lw = 2.5 if pol in OURS else 1.5
            plt.plot(xs, ys, color=color, marker=marker, label=label,
                     linewidth=lw, markersize=5, alpha=0.9)
    plt.xlabel("Mean cumulative trust cost per session")
    plt.ylabel("Mean revenue per session (proxy)")
    plt.title("Revenue vs. trust: when to insert a sponsored suggestion")
    plt.legend(loc="lower right", fontsize=8)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    out_png.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(out_png, dpi=150)
    print(f"Wrote figure -> {out_png}")

# ------------------------------------------------------------------ verdict

def verdict(by_policy, out_md: Path,
            gain_threshold: float = 0.15, oracle_threshold: float = 0.70) -> None:
    ours = upper_envelope(by_policy, OURS)
    base = upper_envelope(by_policy, BASELINES)
    orac = by_policy.get("ORACLE", [])
    if not ours or not base:
        out_md.write_text("Insufficient data for verdict.\n", encoding="utf-8")
        return

    # overlapping trust range
    lo = max(ours[0][0], base[0][0])
    hi = min(ours[-1][0], base[-1][0])
    if hi <= lo:
        out_md.write_text("No overlapping trust range between ours and baselines.\n",
                          encoding="utf-8")
        return

    grid = [lo + (hi - lo) * i / 20 for i in range(21)]
    gains, oracle_ratios, rowlines = [], [], []
    wins = 0
    for t in grid:
        ro = interp_revenue(ours, t)
        rb = interp_revenue(base, t)
        rr = interp_revenue(orac, t) if orac else float("nan")
        if rb and rb > 0 and ro == ro and rb == rb:
            gain = (ro - rb) / rb
            gains.append(gain)
            if gain >= gain_threshold:
                wins += 1
            ratio = (ro / rr) if (rr == rr and rr > 0) else float("nan")
            if ratio == ratio:
                oracle_ratios.append(ratio)
            rowlines.append(f"| {t:.3f} | {rb:.3f} | {ro:.3f} | {gain*100:+.1f}% | "
                            f"{('%.0f%%'%(ratio*100)) if ratio==ratio else 'n/a'} |")

    med_gain = sorted(gains)[len(gains)//2] if gains else float("nan")
    frac_win = wins / len(gains) if gains else 0.0
    med_oracle = sorted(oracle_ratios)[len(oracle_ratios)//2] if oracle_ratios else float("nan")

    crit1 = frac_win >= 0.6 and med_gain >= gain_threshold
    crit2 = med_oracle >= oracle_threshold if med_oracle == med_oracle else False
    go = crit1 and crit2

    lines = [
        "# De-risk go/no-go verdict (auto-generated)\n",
        f"**Overall: {'✅ GO' if go else '⚠️ NO-GO / investigate'}**\n",
        "## Pre-registered criteria",
        f"- **C1 Pareto dominance** (ours beats baselines by ≥{gain_threshold*100:.0f}% "
        f"across ≥60% of range): **{'PASS' if crit1 else 'FAIL'}** — "
        f"median gain {med_gain*100:+.1f}%, won at {frac_win*100:.0f}% of trust levels.",
        f"- **C2 Oracle gap** (ours reaches ≥{oracle_threshold*100:.0f}% of oracle): "
        f"**{'PASS' if crit2 else 'FAIL'}** — median {med_oracle*100:.0f}% of oracle."
        if med_oracle == med_oracle else
        f"- **C2 Oracle gap**: n/a (no overlapping oracle range).",
        "- **C3 Robustness across judges**: run the calibration subset "
        "(`label.py` against a hosted model) and re-run this script; compare verdicts.\n",
        "## Revenue at matched trust (ours = best of P4/P5, baseline = best of P2/P3)",
        "| trust | baseline rev | ours rev | rel. gain | % of oracle |",
        "|---|---|---|---|---|",
        *rowlines,
        "\n*Note:* on synthetic data this only validates the harness. The real verdict "
        "requires `cache/features.parquet` from a labeling run on real conversations.",
    ]
    out_md.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote verdict -> {out_md}")
    print(f"  C1 dominance: {'PASS' if crit1 else 'FAIL'} (median gain {med_gain*100:+.1f}%, "
          f"{frac_win*100:.0f}% of range) | C2 oracle: "
          f"{'PASS' if crit2 else 'FAIL'} ({med_oracle*100:.0f}%)" if med_oracle==med_oracle
          else f"  C1 {'PASS' if crit1 else 'FAIL'} | C2 n/a")
    print(f"  ==> {'GO' if go else 'NO-GO / investigate'}")

# ------------------------------------------------------------------ main

def main() -> None:
    ap = argparse.ArgumentParser(description="Plot Pareto + compute go/no-go verdict")
    ap.add_argument("--pareto", type=str, default="results/pareto.csv")
    ap.add_argument("--png", type=str, default="results/pareto.png")
    ap.add_argument("--verdict", type=str, default="results/go_no_go.md")
    args = ap.parse_args()

    path = Path(args.pareto)
    if not path.exists():
        raise SystemExit(f"{path} not found. Run: python src/evaluate.py")
    by_policy = load_pareto(path)
    draw(by_policy, Path(args.png))
    verdict(by_policy, Path(args.verdict))


if __name__ == "__main__":
    main()
