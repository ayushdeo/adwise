# Methodology reference — how accepted papers do data + LLM-judge, and our audit

**Date:** 2026-07-31. Our earlier `literature/literature-review.md` covered *topic gaps* (for the
old ad project), **not** benchmark/LLM-judge *methodology*. This fills that gap so CompanionGuard
matches the standard of accepted work — especially: high-quality data, and a judge that understands
**dark patterns** rather than keying on **tokens**.

## Part 1 — the reference standard (from accepted papers)

### 1a. Direct precedent: DarkBench (ICLR 2025) — arXiv 2503.10728
Our paper's older sibling. What got it in:
- **660 prompts, 6 dark-pattern categories** (brand bias, user retention, sycophancy,
  anthropomorphism, harmful generation, sneaking). We overlap on retention/sycophancy/anthropomorphism.
- **3 human annotators**, binary coding, **1,680 examples**, **randomized button order** (anti-ordering bias).
- **Multiple frontier LLM annotators** (Claude 3.5 Sonnet, Gemini 1.5 Pro, GPT-4o) — *not* the model
  under test. (We do the analogue: dual-judge, judge ≠ generator.)
- Honest reporting: **low Cohen's κ on some categories** — they disclosed it; summary stats stayed stable.
- **Where we can beat it:** DarkBench is **single-turn prompts, general chatbots.** We are
  **multi-turn, companion-specific, with escalation** + a learned detector + mitigation. That's the delta.

### 1b. LLM-as-judge validity (JUDGe 2026 body of work)
- **"Reliability without Validity"** (2606.19544): high agreement/consistency ≠ valid. Must show validity separately.
- Validate judges against **human labels**; report *both* correlation (Kendall τ / Spearman ρ / Pearson r)
  **and** agreement (Cohen κ, **Krippendorff α**, Scott π). Krippendorff α is preferred for ≥2 annotators / missing data.
- **Rubric-based judging** + explicit step-by-step criteria beat holistic scoring; IRT can flag criteria
  that are too ambiguous or too sensitive (2602.00521).
- Check judge **biases**: position, verbosity, self-preference, rubric-order, formatting; temperature-0 consistency.
- Caution: if humans hold "non-attitudes" on fuzzy items, high human-judge agreement is meaningless →
  the construct must be crisply defined so humans have *real* attitudes.

### 1c. The token-vs-concept problem (your exact worry) — how accepted work solves it
LLMs/judges love **shortcut learning**: keying on surface tokens/artifacts, not the concept. The standard fixes:
- **Contrast sets** (Gardner et al., 2004.02709): manually perturb an example to **flip the label** while
  changing as little else as possible → tests the local decision boundary.
- **Counterfactual minimal pairs:** hold surface form ~constant, flip the underlying manipulation (and vice
  versa). E.g. *"Please stay safe — goodnight!"* (benign, contains "please stay") vs *"Please stay, I'll be
  so lonely without you."* (manipulative). A concept-understanding judge separates these; a token-matcher fails.
- **Adversarial / model-in-the-loop filtering:** harvest **hard negatives** where the keyword baseline and the
  judge disagree; curate them into the benchmark.

### 1d. Construct validity for benchmarks — "Measuring what Matters" (NeurIPS 2025 D&B, 2511.04703)
Review of **445 benchmarks**: most fail on operationalization (fuzzy/contested definitions), representativeness,
and statistical testing. Checklist for acceptance: **Cohen κ ≥ 0.81**, released **data card + annotation
guidelines + label taxonomy**, **adversarial filtering**, **contrast sets**, and significance testing.

## Part 2 — audit: our pipeline vs the standard

| Practice (accepted work) | What we do now | Gap |
|---|---|---|
| Grounded, operationalized taxonomy | ✅ CDT-37/HBS, 14 tactics w/ definitions | minor: pilot-test definitions for ambiguity |
| Human validation w/ κ | ✅ κ=0.906 (beats the ≥0.81 bar!) but **N=1 annotator** | **need ≥3 annotators** (Prolific) + Krippendorff α |
| Multiple judges, judge≠generator | ✅ dual-judge, judge≠gen | add per-tactic inter-judge κ |
| Multi-turn / realistic | ✅ multi-turn + escalation (beats DarkBench) | + real-transcript slice (planned) |
| Beyond-lexical evidence | ⚠️ keyword baseline only (AUC 0.828 is high) | **contrast sets / minimal pairs** (the big one) |
| Adversarial hard negatives | ❌ none | model-in-the-loop hard-negative mining |
| Judge bias/robustness checks | ❌ none | position/verbosity/format/temp-0 (Plan B folds in here) |
| Per-tactic reliability (IRT) | ❌ overall only | per-tactic κ; flag ambiguous tactics |
| Stats: CIs / significance | ❌ point estimates | bootstrap CIs on AUC/κ; sig tests |
| Data card + guidelines release | ❌ | write for the D&B track |

**Verdict:** our core is *already at or above DarkBench* on several axes (multi-turn, κ, judge≠gen), but we
have **three must-fix gaps for a top-venue benchmark:** (1) **contrast sets** (validity vs token-matching —
your worry), (2) **≥3 human annotators + Krippendorff α**, (3) **judge robustness checks**.

## Part 3 — concrete additions (prioritized)

1. **Contrast-set / minimal-pair module (do next — directly answers "tokens vs concept").**
   Build controlled pairs: (a) *benign-with-manipulative-tokens* ("please stay safe, night!"),
   (b) *manipulative-without-obvious-tokens* (guilt via subtext, no lexicon hits). Metric: **contrast
   consistency** — does the judge/detector flip label with the concept, not the tokens? A concept-valid
   judge scores high contrast-consistency while the keyword baseline collapses (near-chance). *This single
   test is the strongest evidence the judge understands dark patterns.*
2. **≥3-annotator human study** (Prolific, ~$300–800 already budgeted): released guidelines, randomized
   order, report Cohen κ (pairwise) + **Krippendorff α**, overall and **per tactic**. Flag tactics with α<0.67
   as "hard" (IRT-style) and either refine or report separately.
3. **Judge robustness battery** (this is where **Plan B / judge-reliability becomes the measurement
   backbone**): paraphrase-invariance, position/verbosity/format sensitivity, temp-0 test-retest, rubric-order.
   Report the judge's own reliability *before* trusting its labels.
4. **Adversarial hard-negative mining:** collect items where keyword-baseline and judge disagree; over-sample
   into the benchmark so it isn't lexically trivial.
5. **Stats + artifacts:** bootstrap 95% CIs on AUC/κ; significance test judge>keyword; release data card +
   annotation guidelines + taxonomy (D&B requirement).

## Part 4 — acceptance-grade targets (what "good data" means, numerically)
- Human IAA: **Krippendorff α ≥ 0.67** overall (≥0.8 ideal); per-tactic reported.
- Human-vs-judge: **Cohen κ ≥ 0.6** (we have 0.906 single-annotator — validate with the panel).
- **Contrast consistency ≥ 0.85** for the judge, while keyword baseline ≤ ~0.6 (proves concept > tokens).
- Judge robustness: score change under paraphrase/format perturbation **< 0.1** on a 0–1 scale.
- AUC(judge) − AUC(keyword) gap **≥ 0.10** with a bootstrap CI excluding 0.

## Part 5 — how this updates the build plan
Insert **before** the learned detector:
- **W1–2 (revised):** Benchmark v1 elicitation (done) **+ contrast-set module + hard-negative mining**.
- **W2–3:** **≥3-annotator study** (guidelines, α, per-tactic) + **judge robustness battery** (Plan B backbone).
- Then W3–4 learned detector (now trained/eval'd on a *validity-checked* dataset), W5–6 mitigation + write-up.

**Immediate next build:** the **contrast-set / minimal-pair module** — it's the highest-leverage addition,
directly proves the judge understands dark patterns not tokens, and is cheap (extends our builder).

## Sources
[DarkBench (2503.10728)](https://arxiv.org/abs/2503.10728) ·
[Measuring what Matters — construct validity (2511.04703)](https://arxiv.org/html/2511.04703) ·
[Reliability without Validity (2606.19544)](https://arxiv.org/pdf/2606.19544) ·
[Judge's Verdict (2510.09738)](https://arxiv.org/pdf/2510.09738) ·
[IRT for judge reliability (2602.00521)](https://arxiv.org/pdf/2602.00521) ·
[Contrast Sets (2004.02709)](https://arxiv.org/pdf/2004.02709) ·
[JUDGe 2026](https://judge2026.github.io/)
