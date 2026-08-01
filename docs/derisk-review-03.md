# De-risk Review 03 — receptivity thesis falsified; reassessment

**Date:** 2026-07-22 · Fork B, run B1 (v2 anchored-rubric prompts on local 7B).
**Bottom line: the receptivity-aware timing thesis is dead. Two independent judge
configurations both show receptivity has no useful signal — gating on it is *worse than
random*. Decision time on the paper's direction.**

## What B1 tested
Review-01/02 found the 7B judge's receptivity was compressed at ~0.85 (P4 ≈ random). B1
re-labeled all 1600 slots with a **v2 anchored 6-level rubric** to force discrimination.

## What happened
The rubric *did* change the distribution — receptivity center moved 0.85 → 0.60, mass
spread into 0.4–0.7, sensitive turns correctly lowest (0.35). **But it did not help the
policy, it hurt it:**

| trust/session | random | **P4 receptivity (v2)** | P5 value-greedy | oracle |
|---|---|---|---|---|
| 0.30 | 1.89 | **1.62** | 4.41 | 4.03 |
| 0.50 | 3.11 | **2.94** | 5.68 | 5.33 |
| 0.70 | 4.34 | **4.26** | 6.95 | 6.40 |

**P4 receptivity-gated is now −7% vs random** (worse) across the operating regime.

## Why (the key diagnostic)
`corr(receptivity, trust_hit)` collapsed from **−0.23 (v1) → −0.00 (v2)**. Under the
anchored rubric, receptivity and trust-cost became *independent*. So gating on receptivity
no longer selects low-trust or high-revenue slots — it's noise w.r.t. value, and slightly
anti-correlated with what matters. **Receptivity, as an LLM-judged per-turn signal on
WildChat, does not predict where an ad is actually worth inserting.**

## Consolidated verdict across all three reviews
1. ✅ **Smart insertion ≫ naive** — real and large (+60–250% in operating regime).
2. ❌ **Receptivity-timing** (your original YouTube instinct) — *falsified* twice.
3. ⚠️ **The winning signal is pure value-density** (`revenue / trust_hit`) — a one-line
   heuristic; no learning needed for the static problem.
4. ⚠️ **Learned controller** — adds nothing with judge features, loses with embeddings-only.
5. 🎯 **Only untested source of novelty:** the **online/sequential shared-budget** setting,
   where lookahead (rationing budget for future high-value turns) could beat greedy.

## The fork (this is the decision)
- **A — Test the online/sequential value (bounded, ~a few days).** Build an online
  simulator: decide per turn *without* future slots, under a depleting per-session budget;
  offline knapsack = clairvoyant ceiling. If a learned policy meaningfully beats online-
  greedy at tight budgets → there's a real ML paper (online budgeted monetization). If
  online-greedy already ≈ oracle → the monetization-timing paper is not viable; pivot.
- **B — Pivot now** to a stronger topic from the original deep-dive (e.g. **value-of-
  computation for agentic cost**, or **agent-memory supersession**), reusing the harness/
  infra skills but not the ad-timing framing. Cuts losses early.
- **C — Reframe as an empirical/negative-result paper**: "Does receptivity-aware ad timing
  help? A large-scale study" — rigorous but a weaker top-venue sell.

## Online-gap probe — RESULT (decides A vs B)
Measured the gap between the best **online** value-density policy (causal, no lookahead)
and the **offline** oracle at matched per-session budgets, on the v2 data:

| budget B | online best | offline oracle | gap |
|---|---|---|---|
| 0.2 | 2.78 | 2.84 | **2.3%** |
| 0.4 | 4.00 | 4.28 | **6.5%** |
| 0.6 | 5.06 | 5.32 | **5.0%** |
| 0.8 | 6.03 | 6.38 | **5.5%** |

**The gap is 2–6%.** Even a *clairvoyant* offline optimum barely beats a one-line online
threshold. So a learned sequential/online controller has ≤~6% room over a heuristic —
nowhere near enough for a top-venue ML contribution. (Cause: WildChat convos are short,
~4.5 slots; lookahead matters only with many items + high future-value variance.)

## Recommendation → PIVOT (Fork B)
The ad-timing angle has now failed at every level: receptivity is falsified, the static
problem is a heuristic, and the online problem leaves ≤6% for learning. **This is not a
viable top-venue ML paper.** The de-risk did its job — it cost ~a week and saved ~3 months.
Recommend pivoting to a stronger topic from the original deep-dive where learned policies
demonstrably beat heuristics (value-of-computation for agentic cost, or agent-memory
supersession), reusing the harness/eval infrastructure we built. Fork C (negative-result
paper) is a fallback but a weak top-venue sell.
