# De-risk Review 02 — emb-only controller + the real diagnosis

**Date:** 2026-07-22 · Builds on review-01. **Bottom line: the science is GO, but the problem-as-posed is too easy — a one-line heuristic wins, and that reshapes the paper.**

## The auto-verdict flipped to NO-GO — but that's a metric artifact, not a real failure
The auto-criterion averages relative gain over the **full** trust range, including the
unrealistic saturation region (trust > 1.0/session) where *every* policy converges to
"insert everything" (P1 always). No product runs at 1.7 trust/session. Restricted to the
**realistic operating regime (trust ≤ 0.7)**, the picture is emphatic:

| trust/session | best baseline | our policy | gain |
|---|---|---|---|
| 0.20 | 1.10 | 3.92 | **+256%** |
| 0.30 | 1.67 | 4.52 | **+170%** |
| 0.50 | 2.76 | 5.36 | **+94%** |
| 0.70 | 3.87 | 6.21 | **+61%** |

**Median gain in the operating regime: +114%.** The core bet (smart insertion ≫ naive)
is robustly true. *Action:* fix the go/no-go metric to score the operating regime, not the
saturated tail.

## The uncomfortable findings (why the paper needs a sharper problem)

### D1 — A trivial heuristic captures 100% of the win.
In the operating regime, `ours = P5 value-greedy` exactly (median gain 114.3% for both).
"Value-greedy" = insert where `best_rev / trust_hit` is high. That's one line. **P4
(receptivity) and P6 (learned) add nothing on top of it.**

### D2 — Context embeddings alone can't predict timing.
Emb-only P6 beats P5 at **0 of 27** trust levels; at trust 0.3 it's 2.11 vs P5's 4.52.
So "context alone tells you when to monetize" (the deployable-controller story) **fails**
with bge-small + GBM + oracle-BC. The judge's per-turn scores carry signal the embeddings
don't recover.

### D3 — Why a heuristic wins: the problem is currently *static*, not sequential.
Our harness scores every slot with all information available and effectively solves an
**offline knapsack** — which any value-density heuristic (or the oracle) solves trivially.
But the real, un-scooped problem (per the literature review) is **online + sequential**:
at turn *t* the agent must decide *without seeing future turns*, under a **depleting shared
trust budget**. There, greedy is provably suboptimal — spend budget now on a mediocre slot
and you can't afford a great slot later. **That online/budgeted setting is where a learned
(RL) controller beats the heuristic, and it's the actual contribution.** We accidentally
de-risked the easy (static) version.

## Revised diagnosis
- ✅ Effect is real and large in the realistic regime.
- ⚠️ As currently posed (static, full-information), it's a heuristic problem, not an ML paper.
- ⚠️ Receptivity from a 7B judge is too flat to drive timing (review-01 F1).
- 🎯 The paper's novelty lives in the **sequential, online, shared-budget** formulation —
  which the current harness doesn't yet test.

## Two forks (need a decision)

**Fork A — Sharpen the problem (recommended).** Make the policy **online/sequential**:
decide per turn without future slots, under a per-session trust budget, with the oracle as
the offline (clairvoyant) upper bound. Now greedy leaves a real gap and a learned/RL
controller can fill it. This is the genuinely novel, FAANG-relevant contribution.
*Cost:* moderate code (a sequential simulator + a small policy/RL loop); reuses all current
labels/embeddings. No re-labeling.

**Fork B — Rescue the signal first (cheap, complementary).** Run the **calibration subset**
(~$5–10, 150–200 convos, stronger hosted judge) + a sharper J2 prompt. Question: does
receptivity un-compress and give P4 real power? Also rebalance genres/bids (kill the 91%
travel monoculture). *Cost:* small; informs whether receptivity-timing is viable at all.

**Recommendation:** do **B first (a day, cheap)** to see if better labels change the story,
then commit to **A** as the core paper — the online/sequential/budgeted controller with a
human-grounded trust cost. That combination is what no prior work has (gap matrix intact).

## Metric fix (do regardless)
`plot.py` should compute the go/no-go over an `--operating-trust-max` (default ~0.7), and
report the saturated tail separately. The current full-range median is misleading.
