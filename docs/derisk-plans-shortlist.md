# De-risk plans — head-to-head (CompanionGuard vs Judge-Reliability)

**Date:** 2026-07-22. Two 1-page plans, each front-loaded with a **day-1 kill-test** (verify the
signal/heuristic-beat *before* building). Both fit the 4070 + small budget and reuse our stack.

---

## Plan A — CompanionGuard: manipulation benchmark + detector for social agents

**Thesis.** A comprehensive, automated, *companion-specific* benchmark + lightweight detector for
manipulative/dark-pattern behaviors in **multi-turn** social-agent conversations, grounded in the
CDT-37 / HBS taxonomies, human-validated, with a helpfulness-vs-manipulation mitigation probe.

**Precise gap.** Existing artifacts are each narrow: Dark-Bench (6 patterns, general chatbots),
CDT (37-pattern taxonomy but *qualitative policy*), HBS (landmark but *farewells only*). None is a
reproducible, automated, companion-specific, full-taxonomy, multi-turn benchmark **+ detector**.

**Day-1 kill-test (≤1 day, ~$10).** Elicit ~100–150 companion snippets from an open model
role-playing a companion (esp. at goodbye / emotional-disclosure / upsell moments); hand-label a
subset for manipulation. Test: does a simple probe/LLM-judge detector separate manipulative vs
benign **meaningfully above a keyword/sycophancy baseline** AND agree with human labels (κ)? 
*Kill if:* no separation over keywords, or human agreement is too low to define the construct.

**Build (if it passes).**
- W1–2: operationalize taxonomy → multi-turn scenario schema; assemble transcripts (elicited +
  audited real from WildChat/roleplay dumps); label with a taxonomy-grounded rubric + human subset.
- W3–4: train detector (frozen 7B features + small classifier/probe — *our stack*); baselines:
  keyword lexicon, sycophancy-only, zero-shot LLM-judge, Dark-Bench-style.
- W5–6: mitigation probe (prompt/steer to cut manipulation, keep helpfulness) → Pareto (our tooling);
  human validation; write-up.

**Compute/cost.** Frozen 7B on 4070; modest API to elicit companion behavior; optional ~$300–800
Prolific for human labels. ✅ fits budget.

**Baselines to beat.** keyword/lexicon, sycophancy classifier, zero-shot LLM-judge, Dark-Bench.

**Venues.** FAccT (~Jan/Feb 2027, verify), AIES (~spring 2027), CHI/CSCW, ACL/EMNLP + NeurIPS D&B;
workshop landing pad: AI4GOOD @ NeurIPS 2026.

**Risks.** (a) label subjectivity → taxonomy rubric + report human κ; (b) elicited transcripts feel
artificial → mix in real audited ones; (c) crowding (fast-moving) → differentiate on
comprehensiveness + detector + mitigation, and move fast.

**Ceiling / floor.** High ceiling (buzzy, FAANG + regulatory relevance, narrative continuity with
this project's origin). Floor risk: someone drops a similar benchmark first.

---

## Plan B — Judge-Reliability Diagnostic: a pre-deployment trust battery for LLM judges

**Thesis.** A cheap battery that **predicts, before deployment, when an LLM judge's scores are
untrustworthy** — across *scoring* (not just pairwise) and *long-form* — via perturbation probes
(paraphrase/format/rubric-order/score-ID/position/verbosity/self-preference) + calibration vs humans.

**Precise gap (cited).** "No principled framework to assess a judge's trustworthiness *before*
deployment"; scoring-bias + long-form under-studied. Most work *catalogs* biases; few build a
*predictive* pre-deploy reliability score. We also hold a firsthand case study (our 7B receptivity
judge collapsing to ~0.85; correlations breaking under a prompt tweak).

**Day-1 kill-test (≤1 day, ~$10).** Take a public human-rated eval set (e.g., MT-Bench human votes /
summarization ratings / RewardBench-style). Run several judges (local 7B + cheap APIs). Test: does
our perturbation-sensitivity battery **predict each judge's disagreement with humans** better than
chance / than a "bigger model = more reliable" heuristic? *Kill if:* perturbation-sensitivity does
not correlate with actual judge-human unreliability (i.e., the battery has no predictive value).

**Build (if it passes).**
- W1–2: assemble judge×task matrix over public human-labeled sets; implement the perturbation battery.
- W3–4: fit a reliability score predicting judge-human agreement; validate on **held-out judges/tasks**.
- W5–6: findings (which judges/tasks fail), a recommended minimal battery, optional debias/ensemble
  mitigation; write-up.

**Compute/cost.** ~$0 GPU (API/model outputs; local 7B optional). **Cheapest option.**

**Baselines to beat.** single-run judge, verbosity-only check, "use a bigger judge" heuristic.

**Venues.** ACL/EMNLP + NeurIPS D&B, ICLR; workshop landing pad: JUDGe 2026 / UncertaiNLP @ EMNLP 2026.

**Risks.** (a) needs human ground truth → use existing labeled sets; (b) bias literature is busy →
differentiate on *predictive pre-deploy battery* (not another bias catalog) + scoring/long-form
focus; (c) may read as incremental → the predictive-validity + generalization-to-held-out-judges
result must be crisp.

**Ceiling / floor.** Lower ceiling (analysis-flavored), but **highest floor** — cheapest, safest to
finish, we already have data. Reusable as a *component* of CompanionGuard (its measurement backbone).

---

## Head-to-head

| | CompanionGuard (A) | Judge-Reliability (B) |
|---|---|---|
| Novelty / buzz | ●●●● | ●●● |
| FAANG + policy relevance | ●●●●● | ●●●● |
| Cost | ~$300–800 (human study) | **~$0–50** |
| Risk to finish | moderate | **low** |
| Crowding risk | moderate (fast-moving) | moderate (bias lit) |
| Infra reuse | ●●●● | ●●● |
| Narrative continuity | ●●●●● (origin instinct) | ●●● |
| Best venues | FAccT/AIES/NeurIPS-D&B | ACL/EMNLP/NeurIPS-D&B |

**Recommendation.** They're complementary, and B is literally a *component* of A. Smart sequencing:
run **A's day-1 kill-test first** (higher ceiling, more differentiated, continues your origin
thread). If it passes → build CompanionGuard, using B's perturbation battery as its judge-trust
backbone (two contributions in one paper). If A's kill-test fails → fall back to **B standalone**
(cheapest, safe floor). Either way we spend one cheap day before committing — exactly the discipline
that's been paying off.

**Immediate next step:** I can build the **A day-1 kill-test harness** now — elicit companion
snippets from an open model, a taxonomy-grounded labeling rubric, a keyword baseline vs a probe/
LLM-judge detector, and an AUC/κ readout — mirroring the de-risk harness we already have. Say go.
