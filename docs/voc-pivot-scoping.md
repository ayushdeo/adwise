# VoC pivot — whitespace & feasibility reality-check (before building)

**Date:** 2026-07-22. Applying the ad-timing lesson: verify novelty AND feasibility *before* committing.

## Good news
Unlike ad-timing, **learned control demonstrably beats heuristics here** — this risk is retired:
- Adaptive compute allocation via learned classifier beats uniform/heuristic by **+12.8%** on
  MATH, tracks a Lagrangian oracle at 91% imitation (arXiv 2604.14853).
- A linear probe on hidden states predicts tool-necessity, cutting tool calls **48% at −1.7%
  accuracy**, no fine-tuning (When2Tool, arXiv 2605.09252).

So "does learning add value" is already answered *yes*. That's the opposite of ad-timing.

## The problem: the obvious version is already crowded (mid-2026)
The generic "learned controller for adaptive test-time compute" is now a busy area:
- **arXiv 2604.14853** — Lagrangian oracle + lightweight classifier from cheap features.
  **This is essentially the exact oracle-behavior-cloning + GBM method I built for our ad
  de-risk, applied to compute allocation. Already published.** Building it = scooped.
- 2602.03975 (learned heuristics over categorical structure), 2509.03581 (Learning When to
  Plan for agents), 2606.30852 (cost-aware early exits), 2605.00737 / 2605.18882 (to call or
  not to call). The single-turn reasoning-length slice is saturated.

## The real whitespace — and its catch
Two genuinely open gaps stand out:
1. **Agentic (multi-step, tool-using) cost–accuracy Pareto.** Existing learned-allocation work
   is single-turn MATH/GSM8K. The 5–30× token multiplier actually bites in *agentic*
   workflows (SWE-bench, GAIA, τ²-bench, WebArena), which almost nobody has done with learned
   control. Cited explicitly: **"0 of 15 agent benchmarks score cost"**, and "the first
   benchmark with a pass-rate-vs-dollars Pareto will do for agents what MLPerf did for
   inference." High impact.
2. **Shared / workload-level budget across many tasks** (vs. today's per-instance allocation).

**The catch (this is the feasibility problem):** the agentic Pareto angle requires *running
real LLM agents on SWE-bench/GAIA/τ-bench*. That needs either strong models (an 8 GB 4070
can't run capable agentic models) or **paid API calls at scale — realistically hundreds to
thousands of dollars** for a credible eval. Cited: agent evals "cost tens of thousands of
dollars per benchmark run." **This collides head-on with our budget (4070/8 GB + $10 Colab +
~$300–800 total).** And it's contested (Galileo + academic groups racing on it).

## Honest options, filtered by OUR compute budget

| Angle | Novel? | Fits 4070+$? | Notes |
|---|---|---|---|
| Generic learned allocation (MATH/GSM8K) | ❌ crowded / method published | ✅ | Don't. |
| **Agentic cost–accuracy Pareto (SWE/GAIA)** | ✅ high | ❌ **expensive + contested** | The prize, but wrong budget. |
| **Probe-based control on small local models** | ⚠️ builds on When2Tool | ✅ (7B on 4070, hidden states, linear probes) | Cheap; extend probes to "reason-more/stop/shared-budget". Incremental risk. |
| Shared-budget across a cheap task workload | ⚠️ moderate | ✅ if tasks are cheap (small models) | Needs a careful cheap testbed. |

## Where this leaves us (the honest read)
- VoC's **highest-impact** slice (agentic cost Pareto) is a **budget mismatch** for a solo
  student on a 4070 — the same way ad-timing was a *novelty* mismatch. I'd be doing you a
  disservice to march into an eval that costs more than your entire budget per run.
- The **budget-feasible** VoC slices (probe-based small-model control, shared-budget on cheap
  tasks) are workable but sit closer to incremental than landmark.
- Worth remembering: the **agent-memory supersession** idea (the other option on the table)
  is *synthetic, small-model, self-contained* — a much better fit for our compute, and its
  whitespace ("no trainable environment rewarding supersession-correctness") is still open.

## Recommendation
Don't commit to the expensive agentic-Pareto version. Two sane paths:
- **VoC-lite:** a probe/small-model *shared-budget* controller runnable on the 4070 — pick a
  cheap task family, show learned cross-task allocation beats per-task heuristics. I'll scope a
  1-week de-risk that tests heuristic-vs-learned on day 1 (the lesson).
- **Reconsider memory-supersession**, which fits our compute far better and is cleaner
  whitespace.

Given ~12 weeks to WWW 2027 and a tight budget, I lean toward whichever we can *fully run
ourselves*. Your call.
