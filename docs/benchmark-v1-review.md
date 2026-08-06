# Benchmark v1 + contrast-set — first real results & diagnosis

**Date:** 2026-08-02. Gen = qwen2.5:7b-instruct; judges = gemma2:9b + llama3.1:8b (judge ≠ gen ✓);
216 items. Contrast-set judge = qwen2.5:7b.

## Results
**Benchmark v1 (`benchmark_stats.md`)**
- AUC(judge) **0.926**, keyword 0.815, gap **+0.111** (just over 0.10 target).
- **Inter-judge κ 0.66, Spearman 0.85** — two different-family judges agree ≥0.6 ✅ (defuses judge=generator).
- Tactic coverage broad: 13 tactics (reciprocity-guilt 94, love-bombing 86, emotional-neglect 76…) ✅.
- **Escalation FAILED: t0=0.55, t1=0.56, t2=0.36** (expected t0<t1<t2). ⚠️

**Contrast-set (`contrast_sets.md`) — WEAK**
- contrast-consistency (qwen 7B) **0.667** (target ≥0.85); keyword 0.000 (as designed).
- Judge FALSE-POSITIVE on benign-with-tokens **0.00** → NOT a token-matcher ✅.
- Judge FALSE-NEGATIVE on manip-subtext **0.67** → **under-detects implicit/subtext manipulation** ⚠️.

## Diagnosis
The 7–9B judges catch **overt** manipulation (AUC 0.926, κ 0.66) but **miss subtext**. That's also why
the keyword gap is thin (+0.111): the judges mostly catch the obvious cases keywords already catch, and
miss the subtle, keyword-proof cases — which are the scientifically interesting ones. Per our **pre-
registered Phase-1 kill-criteria** (contrast-consistency <0.75 → judge too weak; fix before scaling),
we must strengthen the judge before the human study. (Inter-judge κ 0.66 is healthy → construct is real
and reproducible; this is a *judge-sensitivity* problem, not a construct problem.)

## Actions (both should lift contrast-consistency AND widen the keyword gap)
1. **Rubric fix — DONE:** `taxonomy.JUDGE_PROMPT` now explicitly instructs the judge to score *implicit*
   manipulation (self-pity, martyrdom, passive-aggression) with positive/negative examples. Flows into
   both `contrast_sets.py` and `build_benchmark.py`.
2. **Stronger hosted judge** for the hard cases: re-run the 20-item contrast set (costs pennies) with a
   frontier model via `--judge-base-url/--judge-api-key/--judge-model`. Target contrast-consistency ≥0.85.
3. **Escalation:** the scripted "please let me leave" pushback likely makes even a pressured model relent.
   Options: softer/ambiguous pushback, drop escalation as a headline, or study the de-escalation as a
   finding, or defer to the real-transcript slice. Not blocking; revisit in Phase 1/2.

## Re-run to verify the fix
```bash
cd companionguard
# improved rubric on local 7B (did it help?):
python src/contrast_sets.py --judge-model qwen2.5:7b-instruct
# stronger hosted judge (recommended — 20 items, cheap):
python src/contrast_sets.py --judge-base-url https://<host>/v1 --judge-api-key $KEY --judge-model <frontier>
```
Push `contrast_sets.md`. If contrast-consistency ≥0.85 with a stronger judge → judge fixed → proceed to
Phase 2 (≥3-annotator study + judge-robustness battery) using that judge for labeling.

## Status vs POA
Phase 1 in progress. Gate to Phase 2 = contrast-consistency ≥0.85 (stronger judge) + inter-judge κ ≥0.6
(have 0.66). Escalation reframed as an open sub-question, not a blocker.
