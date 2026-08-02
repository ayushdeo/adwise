# CompanionGuard — day-1 kill-test review (GO)

**Date:** 2026-07-31. Local run, qwen2.5:7b-instruct as generator AND judge, 64 replies
(32 pressured / 32 healthy), human labels provided.

## Result: strong GO
| signal | value | bar | pass |
|---|---|---|---|
| AUC judge vs condition | **0.987** | ≥0.75 | ✅ |
| AUC keyword baseline | 0.828 | ≤0.72 (insufficient) | ⚠️ higher than ideal |
| judge − keyword AUC | **+0.159** | ≥0.10 (learned detector justified) | ✅ |
| mean judge: pressured vs healthy | 0.766 / 0.153 | separation | ✅ |
| human-vs-judge Cohen's κ | **0.906** | ≳0.5 (construct real) | ✅✅ |

Tactics in pressured replies: guilt 26, pressure_to_respond 21, fomo 20, emotional_neglect 2,
false_urgency 1.

**Read:** manipulation is reliably elicitable, an LLM-judge detects it near-perfectly *and*
meaningfully beyond keywords, and it agrees with a human at κ=0.91. The construct is real and the
problem is non-trivial. Commit to building CompanionGuard.

## Honest caveats → these become the build tasks
1. **Keyword AUC 0.828 is not tiny.** The learned-detector edge is real but moderate; the paper's
   detector value lives in the ~15% of cases keywords miss → analyze/curate the *subtle* manipulation.
2. **Elicited, in-distribution.** Pressured-vs-healthy prompts are a proxy. Biggest remaining
   validity risk = detecting manipulation in **real deployed companion transcripts**. Retire next.
3. **Judge = generator** (shared-model bias). κ=0.906 with human labels largely defuses it, but the
   real benchmark should use a hosted judge ≠ generator.
4. **Tactic skew** — 3 dominant tactics; the CDT-37 taxonomy is broader → expand coverage.

## Build plan (v1 benchmark, ~5–6 weeks; reuses our stack)
- **W1–2 — Benchmark v1.** Expand scenarios + operationalize the full CDT/HBS taxonomy; make it
  **multi-turn** (not single reply); add a **real-transcript** slice (audit companion/roleplay
  transcripts from public data + elicited-from-multiple-models). Human-label a validation set;
  report κ across 2+ judges (judge ≠ generator).
- **W3–4 — Learned detector.** Frozen-7B features + small classifier/probe (our controller stack)
  vs baselines (keyword, sycophancy, zero-shot judge). Emphasize the subtle-manipulation subset
  where keywords fail. Report cost (probe ≪ LLM-judge).
- **W5–6 — Mitigation + write-up.** A prompt/steering intervention that cuts manipulation while
  preserving helpfulness → helpfulness-vs-manipulation Pareto (our Pareto tooling). Human eval.

## Venues
FAccT (~Jan/Feb 2027, verify), AIES (~spring 2027), CHI/CSCW, ACL/EMNLP + NeurIPS D&B; workshop
landing pad AI4GOOD @ NeurIPS 2026. Judge-reliability (Plan B) folds in as the measurement backbone.

## Next concrete step
Turn the kill-test harness into the **Benchmark v1 builder**: (a) broaden scenarios + tactics to the
full taxonomy, (b) add multi-turn dialogues, (c) add a real-transcript validity slice, (d) dual-judge
labeling. Then the learned detector. Priority order: **validity (real transcripts) → coverage →
detector → mitigation.**
