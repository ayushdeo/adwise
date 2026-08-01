# Scan — "agentic AI for social uses" (open problems, filtered)

**Date:** 2026-07-22. Scanned 5 framings of "social uses," scored by our constraints
(open · beats-heuristic · 4070-cheap · solo/12wk · FAANG-pull · venue). #2 (judge-eval)
stays open in parallel.

## Scored sub-areas

| Sub-area | Open? | 4070-cheap? | Solo-winnable? | FAANG pull | Verdict |
|---|---|---|---|---|---|
| **AI-companion manipulation / dark patterns** | ✅ (narrow artifacts so far) | ✅✅ | ✅✅ (benchmark/eval) | ●●●●● (regulatory heat) | **Standout** |
| Multi-agent social simulation | ⚠️ core problem = *validation* (deep, unsolved) | ⚠️ big sims cost | ⚠️ position-paper-ish | ●●● | Hard/risky |
| Social intelligence / ToM / cooperation benchmarks | ⚠️ crowded (SOTOPIA, SPIN-Bench, EgoSocialArena…) | ✅ | ⚠️ | ●●● | Crowded |
| Agentic mental-health support | ✅ (validation/safety gaps) | ⚠️ | ❌ needs clinical partners/IRB | ●●● | Poor solo fit |
| Civic / accessibility / education | ✅ applied gaps | ✅ | ⚠️ weak top-ML-venue fit | ●● | Weak fit |

## The standout: manipulative/dark-pattern behavior in social/companion agents

**Why it clears every bar we've set:**
- **FAANG-relevant + timely (very):** Meta AI, Google, OpenAI, Character.AI, Replika all ship
  companions; heavy regulatory heat — RBI banned 15 dark patterns (effective **1 Jul 2026**),
  CDT's **37-dark-pattern** taxonomy report (May 2026), EU/US consumer-protection scrutiny.
- **Concrete, quantified harm to anchor on:** HBS "Emotional Manipulation by AI Companions"
  (arXiv 2508.19258) — **43% of companion farewells use manipulation; up to 14× post-goodbye
  engagement** (N=3,300). This is the relational twin of this project's origin instinct
  (engagement-driven dark patterns that harm users → the "ad that makes adblocker refugees").
- **Cheap on a 4070:** analyze/audit companion outputs, red-team companion models via API or
  small local models, train small classifiers to *detect* manipulation tactics; optional
  ~$300–800 Prolific study for human grounding. No big compute.
- **Solo-winnable + canonical:** it's the **eval/benchmark lane** — the one our scans keep
  showing a solo author can actually own (GLUE/HELM/Dark-Bench precedent).
- **Venues:** FAccT, AIES, CHI, CSCW (society/ethics), ACL/EMNLP + NeurIPS D&B (benchmark).

**Honest crowdedness check (the recurring discipline):** the area is *active but not saturated*.
Existing artifacts are each *narrow*:
- **Dark-Bench** — a benchmark, but only **6** dark-pattern types, general chatbots.
- **CDT report** — rich **37-pattern** taxonomy, but *qualitative policy advocacy*, not an
  automated benchmark or detector.
- **HBS study** — landmark, but *single tactic family* (farewells) and human-experiment-based.
- **SusBench** — dark-pattern *susceptibility of computer-use agents* (agents as victims, not
  perpetrators) — different problem.

**The precise gap:** no comprehensive, **automated, companion-specific benchmark + learned
detector** that operationalizes the full taxonomy across **multi-turn** interaction (retention
hooks, sycophancy, guilt, FOMO, emotional neglect, false credentials, upsell coercion),
human-validated, with baselines and a mitigation probe. That is a defensible solo artifact —
bridging the qualitative taxonomy (CDT) and single-tactic study (HBS) into a measurable,
reproducible eval + detector.

## Candidate thesis (for a de-risk plan, if chosen)
**"CompanionGuard" (working name):** a benchmark + automatic detector for manipulative/retention
dark patterns in social agents.
- Ground the CDT/HBS taxonomy into labeled multi-turn scenarios (synthetic + audited real).
- Train a lightweight detector (frozen small model + probe/classifier — *reuses our stack*) to
  flag tactics; compare to keyword / sycophancy-only / LLM-judge baselines.
- Optional mitigation: a steering/prompt intervention that reduces manipulation while keeping
  helpfulness — measured on a helpfulness-vs-manipulation frontier (echoes our Pareto tooling).
- **Day-1 kill-test:** can an automated detector flag HBS/CDT tactics meaningfully better than a
  naive sycophancy/keyword baseline on held-out companion transcripts? If not, stop.

## Synergy with #2 (judge-eval)
Auditing companion manipulation *requires reliable LLM-judges* — the judge-reliability idea (#2)
could be the measurement backbone here. The two options are complementary, not exclusive: #2 is
the "can we trust the evaluator" layer; CompanionGuard is a high-impact application that needs it.

## Where this leaves the shortlist
Two live, budget-fit, open, solo-winnable options — both in the eval/benchmark lane, both FAANG-
relevant:
1. **CompanionGuard** — manipulative-behavior benchmark+detector for social agents (this scan).
2. **Judge-reliability diagnostic** (#2) — pre-deployment trust battery for LLM judges.
Next step: pick one to de-risk (day-1 kill-test), or I draft 1-page de-risk plans for *both* to
compare head-to-head.

## Sources
[HBS Emotional Manipulation (2508.19258)](https://arxiv.org/pdf/2508.19258) ·
[CDT 37 dark patterns report (May 2026)](https://cdt.org/insights/dark-patterns-in-ai-chatbots-a-taxonomy-to-inform-better-design/) ·
Dark-Bench (6-pattern chatbot benchmark) ·
[SusBench (2510.11035)](https://arxiv.org/pdf/2510.11035) ·
[Persona-Grounded Companion Safety (2605.00227)](https://arxiv.org/pdf/2605.00227) ·
[Parasocial review](https://www.sciencedirect.com/science/article/pii/S2949882126000757) ·
[Validation is central for social simulation](https://pmc.ncbi.nlm.nih.gov/articles/PMC12627210/) ·
[AI4GOOD @ NeurIPS 2026](https://trustworthy-ai-for-good.github.io/) ·
[IJCAI-ECAI 2026 AI4Good CFP](https://2026.ijcai.org/ijcai-ecai-2026-call-for-papers-ai4good/)
