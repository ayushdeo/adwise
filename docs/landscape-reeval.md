# Full re-evaluation — research gaps & options, filtered by what we actually learned

**Date:** 2026-07-22. Fresh landscape scan after ad-timing was falsified and generic VoC was
found crowded + compute-mismatched. This replaces guesswork with the real constraints.

## The filter (hard constraints, learned the hard way)
1. **Compute-feasible on a 4070 (8 GB) + $10 Colab + ~$300–800 total.** Rules out: training
   >~3B, running frontier agents on SWE-bench/GAIA, evals costing $100s–$1000s/run. Favors:
   *frozen small models + probes*, *synthetic data*, *cheap-API analysis*, *benchmark/method*.
2. **Must beat a heuristic** (the ad-timing lesson) — real learnable structure, not a one-liner.
3. **Genuinely open** — not already published/crowded.
4. Top venue (NeurIPS/ICLR/ACL/EMNLP/KDD incl. Datasets & Benchmarks tracks; WWW).
5. FAANG-interesting; solo; ~12 weeks.
6. Bonus: reuses our infra (OpenAI-compatible judge harness, oracle-BC controller, eval/Pareto
   scaffolding, embeddings pipeline, 2-machine git workflow).

## Scoring matrix (candidate families)

| Family | Whitespace (mid-2026) | Beats heuristic? | 4070+$ feasible? | FAANG pull | Infra reuse | Verdict |
|---|---|---|---|---|---|---|
| **A. Judge / eval science** | ✅ open (no pre-deploy trust framework; scoring-bias, long-form, novel biases) | ✅ (methods beat naive judges) | ✅✅ (API/outputs, little training) | ●●●● | ●●●● | **Top pick** |
| **B. Internal-uncertainty-aware control** (act on what the model knows) | ✅ open ("models verbalize uncertainty but don't act on it") | ✅✅ (probes ≫ verbalized conf) | ✅✅ (frozen 7B + linear probes) | ●●●● | ●●●●● | **Top pick** |
| C. Hidden-state probing (hallucination) | ⚠️ hot, crowding; but *generalization failure* is open | ✅ | ✅✅ | ●●● | ●●●● | Strong, crowded |
| D. Agent memory / supersession | ⚠️ narrowing fast (Supersede/TOKI/SSGM already out) | ✅ | ✅ (synthetic) | ●●● | ●●● | Only a sub-angle |
| E. Data contamination / leakage | ⚠️ active (CoDeC→ICLR'26) | ✅ | ✅✅ | ●● | ●● | Niche, cheap |
| F. Calibration / UQ | ✅ ("know but don't act") overlaps B | ✅ | ✅✅ | ●●●● | ●●●● | Merge into B |
| G. VoC / adaptive compute (generic) | ❌ crowded (2604.14853 = our exact method) | ✅ | ✅ | ●●● | ●●●● | Skip |
| H. Agentic cost–accuracy Pareto | ✅ high | ✅ | ❌ **too expensive** | ●●●●● | ●●● | Budget mismatch |
| I. Generative rec / semantic IDs | ⚠️ industry out-scales you | ✅ | ⚠️ moderate | ●●●● | ●● | Weak fit |

## The three that survive the filter

### 1. Internal-uncertainty-aware control — *"close the knowing–doing gap"*  ⭐ (best fit)
**The gap (cited, 2026):** models can represent/verbalize uncertainty but **fail to use it to
guide action** — verbalized confidence diverges from internal states and from accuracy; RLHF
degrades calibration. Internal activations detect uncertainty the model won't verbalize.
**The idea:** a *lightweight controller that reads a frozen model's own hidden states* to decide
**when to abstain / ask / verify / call a tool / stop** — turning latent uncertainty into
better decisions. This is your "when to act" VoC instinct, but grounded in *internal
uncertainty* (cheap + learnable + open) instead of ad-timing (heuristic) or agentic-cost
(expensive). **Beats heuristics by construction** (probes ≫ verbalized confidence — established).
**Compute:** frozen 7B on the 4070, extract hidden states once, train tiny probes/controllers —
*exactly our existing oracle-BC + eval stack*. **Venue:** NeurIPS/ICLR/ACL. **FAANG:** high
(reliable agents, hallucination-gating). *Kill-test (week 1): does an internal-state controller
beat verbalized-confidence and entropy baselines on a decision task? If not, stop.*

### 2. Judge / evaluation science — *"can we trust the judge before we deploy it?"*  ⭐
**The gap (cited):** LLM-as-judge is now the default evaluator, yet there's **no principled way
to assess a judge's trustworthiness before using it**; scoring-bias, long-form, and novel biases
(rubric-order, score-ID, reference-score) are under-studied; frontier judges fail >50% of bias
tests. **We have firsthand data:** our 7B judge's receptivity collapsed to ~0.85 and its
score↔score correlations broke under a prompt change — that *is* the phenomenon.
**The idea:** a **pre-deployment judge-reliability diagnostic + benchmark** — a cheap battery
that predicts when an LLM judge's scores are unreliable (sensitivity to paraphrase/formatting/
rubric order, calibration vs. humans), across scoring (not just pairwise) and long-form.
**Compute:** ~$0 GPU — just API/model outputs. **Venue:** ACL/EMNLP + NeurIPS D&B; JUDGe 2026
workshop as a landing pad. **FAANG:** high (everyone ships LLM-judge eval). Strongest *cheap*
option; leans benchmark/analysis rather than heavy ML.

### 3. Agent memory — a *narrow* sub-angle only
Core supersession whitespace **closed** in 2026 (Supersede 2606.27472 already built the
trainable supersession-reward env we'd have targeted). Remaining open: **cross-session identity
& per-user memory isolation**, temporal abstraction at scale. Feasible (synthetic) but you'd be
sprinting against a crowded, fast-moving field. Lower priority unless a specific sub-angle grabs you.

## What's OUT (and why)
- **Generic VoC / adaptive compute (G):** our exact oracle-BC+classifier method already published
  (arXiv 2604.14853, MATH/GSM8K). Building it = scooped.
- **Agentic cost–accuracy Pareto (H):** the real prize, but needs $100s–$1000s/eval — budget
  mismatch (this is *why* we're re-evaluating).
- **Generative rec (I):** industry out-scales a solo student.

## Recommendation
Both top picks fit the 4070 + budget, are open, beat heuristics, and reuse our stack:
- If you want a **methods/ML paper** that keeps your "when to act" thread → **#1 internal-
  uncertainty-aware control.** (My lean — best novelty × fit × infra reuse, and it's *your*
  instinct done right.)
- If you want the **cheapest, safest-to-finish** paper leveraging what we just lived → **#2
  judge-reliability diagnostic.** (~$0 compute, we already have the war story + data.)

Next step regardless: a 1-page de-risk plan for the chosen one with a **day-1 heuristic-vs-
learned kill-test** — so we never again spend a week before knowing if it beats a one-liner.

## Sources
Memory: [Supersede 2606.27472](https://arxiv.org/abs/2606.27472), [state-of-agent-memory 2026](https://mem0.ai/blog/state-of-ai-agent-memory-2026) ·
Probing: [MultiHaluDet 2605.24919](https://arxiv.org/abs/2605.24919), [ICR Probe 2507.16488](https://arxiv.org/pdf/2507.16488) ·
Judge: [JUDGe 2026](https://judge2026.github.io/), [Scoring Bias 2506.22316](https://arxiv.org/abs/2506.22316), [Are we on the right way 2512.16041](https://arxiv.org/pdf/2512.16041) ·
Contamination: [CoDeC/ICLR26 survey](https://arxiv.org/pdf/2404.00699) ·
Calibration: [ConfidenceBench 2607.20526](https://arxiv.org/html/2607.20526), [UQ sources 2604.10495](https://arxiv.org/pdf/2604.10495) ·
VoC: [Constrained TTC 2604.14853](https://arxiv.org/abs/2604.14853), [When2Tool 2605.09252](https://arxiv.org/abs/2605.09252)
