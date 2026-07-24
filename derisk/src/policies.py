#!/usr/bin/env python3
"""
policies.py — Ad-insertion policies + exact oracle for the de-risk harness.

A conversation is an ordered list of candidate ad slots. At each slot a policy
decides whether to insert one sponsored suggestion (always the highest-revenue
genre for that slot). Inserting yields `best_rev` revenue and spends `trust_hit`
from a per-session **trust budget** B; once B is exhausted, no more ads.

Policies
--------
  P0 never                 : never insert            (revenue floor / trust ceiling)
  P1 always                : insert every slot (budget-limited, in order)
  P2 random(p)             : insert w.p. p           (budget-limited)
  P3 static_coherence(theta): insert if max genre_fit >= theta  (ignores receptivity/budget-shape)
  P4 receptivity_gated(tau): insert if receptivity >= tau       (OURS v1)
  P5 value_greedy(lambda)  : insert if best_rev - lambda*trust_hit > 0  (OURS v2 stand-in;
                             controller.py will replace with a trained policy)
  ORACLE(B)                : exact knapsack upper bound: max revenue s.t. sum(trust_hit) <= B

Run
---
  python src/policies.py                       # demo on cache/features.parquet if present,
                                               # else on a synthetic dataset
"""

from __future__ import annotations

import argparse
import random
from dataclasses import dataclass, field
from itertools import combinations
from pathlib import Path
from typing import Callable, Dict, List, Optional, Tuple

# ------------------------------------------------------------------ data model

@dataclass
class Slot:
    receptivity: float
    trust_hit: float
    best_rev: float
    max_fit: int                       # max genre_fit over genres (for static-coherence)
    score: Optional[float] = None      # learned controller score (set by controller.py)

@dataclass
class Conversation:
    conv_id: str
    slots: List[Slot] = field(default_factory=list)

# A policy maps (slot, remaining_budget, rng) -> insert? (bool)
Policy = Callable[[Slot, float, random.Random], bool]

# ------------------------------------------------------------------ policies

def p_never() -> Policy:
    return lambda s, b, rng: False

def p_always() -> Policy:
    return lambda s, b, rng: True

def p_random(p: float) -> Policy:
    return lambda s, b, rng: rng.random() < p

def p_static_coherence(theta: float) -> Policy:
    # theta on the 1..5 fit scale
    return lambda s, b, rng: s.max_fit >= theta

def p_receptivity_gated(tau: float) -> Policy:
    return lambda s, b, rng: s.receptivity >= tau

def p_value_greedy(lam: float) -> Policy:
    # insert when the revenue outweighs the (lambda-scaled) trust cost
    return lambda s, b, rng: (s.best_rev - lam * s.trust_hit) > 0.0

def p_learned(threshold: float) -> Policy:
    # insert when the trained controller's score clears the threshold (OURS v2, trained)
    return lambda s, b, rng: (s.score is not None) and (s.score >= threshold)

# ------------------------------------------------------------------ simulation

def simulate_conv(conv: Conversation, policy: Policy, budget: float,
                  rng: random.Random) -> Tuple[float, float]:
    """Walk slots in order; insert when the policy says yes AND the trust_hit
    still fits the remaining budget. Returns (revenue, trust_spent)."""
    remaining = budget
    revenue = 0.0
    spent = 0.0
    for s in conv.slots:
        if policy(s, remaining, rng) and s.trust_hit <= remaining + 1e-9:
            revenue += s.best_rev
            spent += s.trust_hit
            remaining -= s.trust_hit
    return revenue, spent

def oracle_conv(conv: Conversation, budget: float) -> Tuple[float, float]:
    """Exact max revenue subject to sum(trust_hit) <= budget.
    Brute force for small slot counts; DP (discretized) otherwise."""
    slots = conv.slots
    n = len(slots)
    if n == 0:
        return 0.0, 0.0
    if n <= 18:
        best_rev, best_cost = 0.0, 0.0
        # iterate subsets by size; keep best feasible revenue
        idx = range(n)
        for k in range(n + 1):
            for combo in combinations(idx, k):
                cost = sum(slots[i].trust_hit for i in combo)
                if cost <= budget + 1e-9:
                    rev = sum(slots[i].best_rev for i in combo)
                    if rev > best_rev:
                        best_rev, best_cost = rev, cost
        return best_rev, best_cost
    # DP: discretize trust to integer "milli-trust" units
    scale = 100
    cap = int(round(budget * scale))
    dp = [0.0] * (cap + 1)
    for s in slots:
        w = int(round(s.trust_hit * scale))
        v = s.best_rev
        if w > cap:
            continue
        for c in range(cap, w - 1, -1):
            cand = dp[c - w] + v
            if cand > dp[c]:
                dp[c] = cand
    return max(dp), 0.0  # cost not tracked in DP branch

def oracle_select(conv: Conversation, budget: float) -> Tuple[set, float, float]:
    """Like oracle_conv but returns the CHOSEN slot indices (for behavior cloning).
    Exact brute force for small slot counts; greedy value-density fallback otherwise."""
    slots = conv.slots
    n = len(slots)
    if n == 0:
        return set(), 0.0, 0.0
    if n <= 18:
        best_rev, best_combo, best_cost = 0.0, (), 0.0
        for k in range(n + 1):
            for combo in combinations(range(n), k):
                cost = sum(slots[i].trust_hit for i in combo)
                if cost <= budget + 1e-9:
                    rev = sum(slots[i].best_rev for i in combo)
                    if rev > best_rev:
                        best_rev, best_combo, best_cost = rev, combo, cost
        return set(best_combo), best_rev, best_cost
    # greedy by value density (approx) for large n
    order = sorted(range(n), key=lambda i: slots[i].best_rev / max(slots[i].trust_hit, 1e-6),
                   reverse=True)
    chosen, spent, rev = set(), 0.0, 0.0
    for i in order:
        if spent + slots[i].trust_hit <= budget + 1e-9:
            chosen.add(i); spent += slots[i].trust_hit; rev += slots[i].best_rev
    return chosen, rev, spent

def evaluate(convs: List[Conversation], policy: Policy, budget: float,
             seed: int = 0) -> Dict[str, float]:
    rng = random.Random(seed)
    revs, costs = [], []
    for c in convs:
        r, t = simulate_conv(c, policy, budget, rng)
        revs.append(r)
        costs.append(t)
    return {
        "mean_revenue": sum(revs) / len(revs),
        "mean_trust": sum(costs) / len(costs),
    }

def evaluate_oracle(convs: List[Conversation], budget: float) -> Dict[str, float]:
    revs, costs = [], []
    for c in convs:
        r, t = oracle_conv(c, budget)
        revs.append(r)
        costs.append(t)  # realized trust spent (exact for <=18-slot brute-force branch)
    return {"mean_revenue": sum(revs) / len(revs), "mean_trust": sum(costs) / len(costs)}

# ------------------------------------------------------------------ loading

def load_features(path: Path, scores_path: Optional[Path] = None) -> List[Conversation]:
    import pandas as pd
    df = pd.read_parquet(path)
    fit_cols = [c for c in df.columns if c.startswith("fit_")]

    # optional learned-controller scores, keyed by (conv_id, slot_idx)
    score_map: Dict[Tuple[str, int], float] = {}
    if scores_path is not None and Path(scores_path).exists():
        sdf = pd.read_parquet(scores_path)
        for _, r in sdf.iterrows():
            score_map[(str(r["conv_id"]), int(r["slot_idx"]))] = float(r["score"])

    convs: List[Conversation] = []
    for cid, g in df.sort_values(["conv_id", "slot_idx"]).groupby("conv_id"):
        slots = []
        for _, row in g.iterrows():
            max_fit = int(max(row[c] for c in fit_cols)) if fit_cols else 3
            slots.append(Slot(
                receptivity=float(row["receptivity"]),
                trust_hit=float(row["trust_hit"]),
                best_rev=float(row["best_rev"]),
                max_fit=max_fit,
                score=score_map.get((str(cid), int(row["slot_idx"]))),
            ))
        convs.append(Conversation(conv_id=str(cid), slots=slots))
    return convs

def make_synthetic(n_convs: int = 120, seed: int = 7) -> List[Conversation]:
    """Synthetic data with a planted structure: receptive turns tend to have
    LOW trust_hit and decent revenue; non-receptive turns have HIGH trust_hit.
    A good 'when' policy should therefore Pareto-beat random/always. (This tests
    the machinery, it does NOT prove the real hypothesis.)"""
    rng = random.Random(seed)
    convs = []
    for i in range(n_convs):
        n_slots = rng.randint(2, 6)
        slots = []
        for _ in range(n_slots):
            receptive = rng.random() < 0.45
            if receptive:
                recept = rng.uniform(0.6, 1.0)
                trust = rng.uniform(0.05, 0.3)
                rev = rng.uniform(0.8, 2.8)
            else:
                recept = rng.uniform(0.0, 0.45)
                trust = rng.uniform(0.4, 0.9)
                rev = rng.uniform(0.2, 1.6)
            slots.append(Slot(receptivity=recept, trust_hit=trust,
                              best_rev=round(rev, 3), max_fit=rng.randint(1, 5)))
        convs.append(Conversation(conv_id=f"syn_{i}", slots=slots))
    return convs

# ------------------------------------------------------------------ demo / main

def demo(convs: List[Conversation], budget: float = 1.0) -> None:
    named: List[Tuple[str, Policy]] = [
        ("P0 never", p_never()),
        ("P1 always", p_always()),
        ("P2 random(.5)", p_random(0.5)),
        ("P3 static(theta=4)", p_static_coherence(4)),
        ("P4 recept(tau=.6)", p_receptivity_gated(0.6)),
        ("P5 value(lam=3)", p_value_greedy(3.0)),
    ]
    print(f"\nBudget B={budget}  |  {len(convs)} conversations")
    print(f"{'policy':22} {'mean_rev':>9} {'mean_trust':>11}")
    print("-" * 44)
    for name, pol in named:
        m = evaluate(convs, pol, budget)
        print(f"{name:22} {m['mean_revenue']:9.3f} {m['mean_trust']:11.3f}")
    orc = evaluate_oracle(convs, budget)
    print(f"{'ORACLE (upper bound)':22} {orc['mean_revenue']:9.3f} {'--':>11}")
    print("\nRead: a good 'when' policy (P4/P5) should reach high revenue at LOWER "
          "trust than P1/P2, and approach the ORACLE. Full Pareto sweep -> evaluate.py.")


def main() -> None:
    ap = argparse.ArgumentParser(description="Ad-insertion policies + oracle demo")
    ap.add_argument("--features", type=str, default="cache/features.parquet")
    ap.add_argument("--budget", type=float, default=1.0)
    ap.add_argument("--synthetic", action="store_true", help="force synthetic data")
    args = ap.parse_args()

    path = Path(args.features)
    if args.synthetic or not path.exists():
        if not args.synthetic:
            print(f"[info] {path} not found -> using synthetic demo data.")
        convs = make_synthetic()
    else:
        convs = load_features(path)
        print(f"Loaded {len(convs)} conversations from {path}.")
    demo(convs, budget=args.budget)


if __name__ == "__main__":
    main()
