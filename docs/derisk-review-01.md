# De-risk Review 01 — first real run (WildChat-1M, 350 convos / 1600 slots)

**Date:** 2026-07-22 · **Judge:** local qwen2.5:7b-instruct · **Verdict:** ✅ GO (with caveats that reshape the paper)

## Headline
The mechanism works: **smart insertion massively beats naive insertion.** At matched
trust, our best policy delivers +38–467% revenue over random/static, hits ~100%+ of
the (local) oracle, GO criteria pass. The core bet — that *when/whether* you insert
matters enormously — is validated on real data.

**But** the per-policy breakdown reveals the win is driven by **value-density
(revenue-per-trust), not receptivity**, and the **trained controller doesn't yet beat
the simple heuristic.** Four findings below change what the paper should claim and test.

## Per-policy revenue at matched trust (the money table)
| trust | P2 random | P4 receptivity (ours) | P5 value-greedy (ours) | P6 learned (ours) | Oracle |
|---|---|---|---|---|---|
| 0.3 | 1.67 | **1.74** | 4.52 | 4.33 | 4.18 |
| 0.5 | 2.76 | **2.89** | 5.36 | 5.33 | 5.02 |
| 0.7 | 3.87 | **4.05** | 6.21 | 6.20 | 5.88 |

## Findings

### F1 — Receptivity-gating (P4) barely beats random. ⚠️
P4 ≈ P2 across the whole range (1.74 vs 1.67 at trust 0.3). In the figure, the blue P4
line sits *down with the baselines*, not up with P5/P6. **Cause:** the 7B judge's
receptivity is compressed — median 0.85, p25–p75 = 0.80–0.85, 90% of mass in 0.7–0.9,
with dead gaps (no values in 0.3–0.5). It barely discriminates, so gating on it ≈ random.
*Implication:* your original "receptivity-timing" instinct is **not** yet supported by
this judge. The signal that works is trust-cost + revenue (value density).

### F2 — Trained controller (P6) ≈ value-greedy heuristic (P5). ⚠️
P6 (0.728 OOF Spearman) tracks P5 almost exactly and doesn't beat it. **Cause:** we fed
the controller the judge scores (`--use both`), so it just re-learns `best_rev/trust_hit`
— a heuristic already computes that. A learned controller currently earns its keep on
nothing. *Fix (cheap, next step):* retrain with **`--use emb`** — predict insertion value
from **context embeddings only**, no per-turn judge scores at inference. If emb-only P6
approaches P5 (which sees the judge scores), that's the real result: *context alone
predicts when to monetize* — and it's the deployable story (no expensive judge per turn).

### F3 — Genre monoculture. ⚠️
`best_genre` = travel_experiences for **1460/1600 (91%)** slots. It has both the highest
mean fit (3.97) and a high bid (2.68), so it wins almost always → the revenue proxy is
effectively one-dimensional. Partly a WildChat topic skew, partly a **bid-vector
artifact**. *Fix:* rebalance bids (don't let one genre dominate), expand/normalize the
genre set, or z-score fit within genre before picking best.

### F4 — Oracle isn't a true upper bound. 🐛
P5/P6 exceed "Oracle" (106%). **Cause:** our oracle solves a per-conversation knapsack at
a *uniform* budget B for every conversation, while P5/P6 implicitly allocate different
trust to different conversations. The true ceiling is a **global knapsack across all
slots** at a total budget. *Fix:* implement a global/cross-conversation oracle; until
then, read "% of oracle" as "≈ near a conservative ceiling," not a hard bound.

## What still looks healthy ✓
- 1600/1600 slots labeled, **0 errors**; receptivity/trust/rev all have real variance
  (11–14 unique values, not collapsed).
- Directionality correct: `corr(receptivity, trust_hit) = -0.23`; **sensitive** intent has
  lowest receptivity (0.65) and highest trust (0.51) — the judge does flag sensitive
  contexts as ad-inappropriate.
- Controller scores well-spread (1468 unique, std 0.27) — the model itself is fine; it's
  the *task* that's too easy in `--use both`.

## Recommended next steps (in order)
1. **Emp-only controller ablation (do now — no GPU, no re-label):**
   `python src/controller.py --use emb` → `evaluate.py` → `plot.py`. Tests F2 directly.
2. **Fix the oracle (F4):** add a global knapsack ceiling so "% of oracle" is meaningful.
3. **Rebalance genres/bids (F3):** kill the travel monoculture; re-run `--assemble-only`
   (no re-labeling — just reprice) after editing `bids.json`, or improve the genre design.
4. **Calibration subset (C3, ~$5–10):** re-label 150–200 convos with a stronger hosted
   judge. Key question: does **receptivity spread out** with a better judge (fixing F1)?
   Also sharpen the J2 prompt (rubric / finer scale) to force discrimination.
5. Then decide the paper's spine: if emb-only P6 works + receptivity sharpens, the
   "learned, context-driven, trust-aware timing" story is fully supported.

## Repo hygiene
The review artifacts (features.parquet, controller_scores.parquet, results/*) were
force-added to share across machines. After review: `git rm --cached` them so they don't
live in permanent history (they're regenerable and gitignored by default).
