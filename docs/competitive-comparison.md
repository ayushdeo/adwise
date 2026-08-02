# Competitive comparison — CompanionGuard vs the field

**Date:** 2026-07-31. Baselines to position against and score on their own metrics. Honest note:
the **multi-turn companion-safety benchmark space got busier in mid-2026** (5+ entries) — so our
differentiation must be sharp. It is: **retention/engagement dark patterns specifically + multi-turn
escalation + a learned detector + mitigation + contrast-set concept-validity.** No single competitor
has that combination.

## Table A — what each paper built (dataset · methodology · metrics)

| Paper (venue) | Focus | Turns | Dataset | Annotation / judge | Detector | Mitigation | Headline metric(s) |
|---|---|---|---|---|---|---|---|
| **DarkBench** (ICLR 2025, 2503.10728) | 6 general dark patterns (incl. user-retention, sycophancy, anthropomorphism) | **single-turn** | 660 prompts; 1,680 annotated examples; general chatbots | **3 human** annotators (randomized order) + **3 frontier LLM** judges (Claude3.5/Gemini1.5/GPT-4o) | ❌ | ❌ | dark-pattern occurrence **rate (48% avg)**; low κ on some categories |
| **HBS Emotional Manipulation** (2508.19258) | Farewell manipulation (6 tactics) | single moment | **1,200 real farewells** (Replika/Chai/Character.ai) + 4 preregistered experiments **N=3,300** | human experiments (behavioral audit) | ❌ | ❌ | **37%** manipulative; **14×** post-goodbye engagement; churn/liability effects |
| **Persona-Grounded Safety** (2605.00227) | Clinical safety harms (self-harm, eating disorder) | **multi-turn** | 9 clinical personas × 25 scenarios ≈ **1,600 dialogue pairs**; Replika | **LLM-assisted** harm classification; personas clinically validated | ❌ | ❌ | **35.7%** harmful-response rate |
| **EMPATH** (2606.30256) | Emotional-support chatbot safety (5 dims / 19 metrics, incl. "dependency fostering") | **multi-turn** | 140 seeds × 34 personas; multilingual | **auditor–judge** (LLM roleplays user; LLM judge scores transcript) | ❌ | ❌ | 19-metric safety scores across 5 dimensions |
| **CogManip** (2606.06099) | **General** cognitive manipulation (15 strategies) | **multi-turn** | **1,000** scenarios, human-expert validated; general LLMs | human-expert validation | ❌ | ❌ (prompt-defense analysis only) | per-strategy risk rates across 13 models |
| Sycophancy: **SycEval / SyConBench** (2502.08177 / 2025) | Sycophancy (agreement under pressure) | single & **multi-turn** | QA-based, escalating rebuttals | rule/LLM judge | ❌ | partial | sycophancy **58%**; multi-turn "Turn-of-Flip" |
| **CompanionGuard (ours)** | **Retention/engagement dark patterns** (14-tactic CDT-37/HBS) | **multi-turn + escalation** | multi-model elicited + **real-transcript slice**; **contrast sets** | **≥3 human** (Krippendorff α) + **dual LLM judge ≠ generator** + **robustness battery** | **✅ learned (frozen-7B probe)** | **✅ helpfulness-vs-manipulation Pareto** | occurrence + **per-tactic κ**, **detector AUC vs keyword**, **contrast-consistency**, mitigation frontier |

## Table B — what they did vs what we do (the differences)

| Paper | What they did | What CompanionGuard does differently |
|---|---|---|
| **DarkBench** | Single-turn prompts, general chatbots, 6 broad patterns; measures occurrence; no detector/mitigation | Companion-specific **retention** patterns; **multi-turn escalation**; **learned detector** + **mitigation**; **contrast-set** validity; our κ (0.906 pilot) already exceeds their per-category κ |
| **HBS** | Human behavioral audit + 3,300-person experiments on the *farewell* moment | A **reusable automated benchmark + detector** across the *full* retention taxonomy and *all* exit/cancel/reduce/boundary moments — no 3,300-person study needed to apply it |
| **Persona-Grounded** | Clinical *content* harms (self-harm/ED mirroring) for vulnerable personas | Different construct: *retention manipulation* (won't-let-you-leave), not clinical content; + detector + mitigation + concept-validity |
| **EMPATH** | Broad emotional-support safety, 19 metrics, judge-scores transcripts | Focused *retention-manipulation* construct with a **learned detector** (not judge-only) and **contrast-set proof** the signal is conceptual, not lexical |
| **CogManip** | *General* cognitive-manipulation strategies, measurement only | Companion + **retention-specific**; adds detector, mitigation, and validity rigor CogManip lacks |
| **Sycophancy benches** | Sycophancy = agreeing with the user | Retention manipulation ≠ sycophancy (often the opposite: *resisting* the user's wish to leave). We can include a sycophancy cross-check |

## Metrics we will report to beat/complement them directly
1. **Occurrence rate** (comparable to DarkBench 48% / HBS 37% / Persona 35.7%) — but *per-tactic* and *by model*.
2. **Human agreement:** Cohen κ **and Krippendorff α**, overall + per-tactic (DarkBench only reported κ, weak on some).
3. **Detector AUC vs keyword baseline** with bootstrap CIs (nobody above builds a detector → our novel axis).
4. **Contrast-consistency** (concept vs tokens) — judge/detector ≥0.85 while keyword ≤0.6 (no competitor does this).
5. **Escalation curve** (manipulation vs turn under pushback) — multi-turn dynamic others don't isolate.
6. **Mitigation:** helpfulness-vs-manipulation Pareto (no competitor mitigates).

## Positioning statement (paste-ready)
> Prior companion/manipulation benchmarks are either **single-turn and general** (DarkBench), **human-
> audit studies of one moment** (HBS farewells), or **multi-turn but about clinical content or general
> persuasion** (Persona-Grounded, EMPATH, CogManip). None targets **engagement/retention dark patterns**
> specifically, builds a **learned detector**, offers a **mitigation** on a helpfulness–manipulation
> frontier, or proves via **contrast sets** that detection is conceptual rather than lexical.
> CompanionGuard does all four, on **multi-turn** companion interactions with **escalation**.

## Honest risk
This is a **fast-moving, now-contested** area (5 relevant papers in ~4 months). Mitigations: move quickly;
lead with the axes nobody else has (**detector + mitigation + contrast-set validity**); cite all of the
above as related work and **score on their metrics** to show we subsume+extend them.

## Sources
[DarkBench 2503.10728](https://arxiv.org/abs/2503.10728) · [HBS 2508.19258](https://arxiv.org/abs/2508.19258) ·
[Persona-Grounded 2605.00227](https://arxiv.org/abs/2605.00227) · [EMPATH 2606.30256](https://arxiv.org/html/2606.30256v1) ·
[CogManip 2606.06099](https://arxiv.org/abs/2606.06099) · [SycEval 2502.08177](https://arxiv.org/html/2502.08177v4)
