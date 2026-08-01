# Venue + keyword scan for #1 (internal-uncertainty-aware control) — and the verdict

**Date:** 2026-07-22. Scanned the idea from every framing before drafting a plan (per the
ad-timing lesson). **Verdict: #1 is saturated — do not build it. Pivot.**

## Crowdedness map (varied keywords → what's already taken)

| Framing / keyword | State of the art (mid-2026) | Open? |
|---|---|---|
| abstention / selective prediction from internal states | **Two Axes of LLM Abstention** (2607.08456, Jul'26) — decomposes answerable-wrong vs unanswerable, separate risk budgets; hidden states read answerability 0.97–0.99. **Know Your Limits** survey (TACL). | ❌ |
| disentangle uncertainty axes → differentiated action | **Knowledge Knows, Verbalization Tells** (2607.05013), **Two Axes** (separate budgets per axis) | ❌ |
| confidence-gated retrieval / tool use | Self-RAG, FLARE, SUGAR-L, Probing-RAG, "Adaptive Retrieval w/o Self-Knowledge" | ❌ |
| probe cascade → abstain / escalate | **Deployed at Anthropic & DeepMind** ("probe-first cascade + LLM escalation"); Doomed-from-the-Start (2607.06503); Calibrate-Then-Delegate (2604.14251) | ❌ |
| cost-optimal cascade / model routing by confidence | UCCI (2605.18796), Cost-Saving Cascades w/ Early Abstention (2502.09054), Cluster-Route-Escalate (2606.27457) | ❌ |
| verbalized vs internal confidence / act-on-uncertainty | Are LLM Decisions Faithful to Verbal Confidence (2601.07767); Know–Act Gap (2603.22619) | ❌ |
| sequential / propagated uncertainty across steps | Uncertainty Propagation in LLM Systems (2604.23505); Beyond Self-Knowledge (2607.25600) | ⚠️ just opening, moving fast |

**Conclusion:** every framing of "read internal uncertainty → decide when to abstain/verify/
retrieve/escalate" is occupied, several by **July-2026** papers, and the core recipe is **already
in production at two FAANG labs.** A solo student with 12 weeks cannot win a novelty race here.

## The meta-pattern (this is the important part)
Three consecutive "learned method on the hot agent-reliability topic" ideas have now dissolved
under a hard scan:
1. **Ad-timing** — heuristic-solvable (no learnable structure).
2. **Generic VoC** — our exact method already published; high-impact slice too expensive.
3. **Uncertainty-aware control** — saturated + FAANG-deployed.

**Structural lesson:** the glamorous "better controller for the hottest problem" lane is picked
clean in 2026 by thousands of researchers + well-funded labs. That is *not* where a solo student
on a 4070 lands a top paper. The lane that our scans keep showing is **open + cheap + solo-
winnable** is **evaluation / measurement / benchmark science** — and that's not a consolation
prize: GLUE, HELM, MMLU, LMArena, MLPerf were "just" eval work and are among the field's most
cited, most FAANG-relevant artifacts. A solo author *can* produce a canonical benchmark; they
cannot out-run DeepMind on a controller.

## Venue × framing matrix + deadlines (relative to today, 2026-07-22)

| Venue | Deadline | Fit for eval/benchmark work | Fit for method work |
|---|---|---|---|
| **ICLR 2027** | abstract **Sep 19**, paper **Sep 24** 2026 | ✅ (D&B-friendly) | ✅ |
| **ARR Oct cycle** | **Oct 12, 2026** → ACL/NAACL 2027 | ✅ | ✅ |
| **ICML 2027** | ~Jan 2027 | ✅ | ✅ |
| **AAAI 2027** | Jul 28, 2026 | ❌ too soon | ❌ |
| **UncertaiNLP @ EMNLP 2026** (Budapest) | ~summer 2026 (workshop) | ✅ landing pad | ✅ |
| **JUDGe 2026** ("Can we trust the judge?") | workshop | ✅✅ ideal for judge-eval | — |
| NeurIPS 2027 | ~May 2027 (far) | ✅ D&B track | ✅ |
| WWW 2027 | Oct 11, 2026 | ⚠️ less NLP-fit | ⚠️ |

**Actionable near-term targets:** ICLR 2027 (Sep 24 — ~9 weeks), ARR Oct 12 → ACL/NAACL 2027,
with UncertaiNLP@EMNLP'26 / JUDGe'26 workshops as fast, lower-risk landing pads for an early
version.

## Recommendation — pivot to #2, reframed as the *strong* play
**#2: a pre-deployment LLM-judge reliability diagnostic + benchmark.** Why it's the structurally
smart bet, not a fallback:
- **Open:** cited gap — "no principled framework to assess a judge's trustworthiness before
  deployment"; scoring-bias, long-form, rubric-order/score-ID biases under-studied.
- **Cheap:** ~$0 GPU — API/model outputs; perfect for the 4070 + small budget.
- **We have the war story + data:** our own 7B judge's receptivity collapsed to ~0.85 and its
  score correlations broke under a prompt tweak — that *is* the phenomenon, already in hand.
- **Solo-winnable + canonical:** a good judge-reliability battery gets adopted → cited.
- **FAANG-relevant:** everyone ships LLM-judge eval; a pre-deploy trust check is wanted.
- **Venues:** ACL/EMNLP + NeurIPS D&B; JUDGe 2026 / UncertaiNLP for an early cut.

## Next
Draft the **#2 de-risk plan** with a day-1 kill-test (can a cheap battery *predict* judge
unreliability better than chance / than verbosity-bias baselines on held-out judges?). If you'd
rather keep hunting for a method paper, say so — but my honest counsel after three scans is to
stop fighting the saturated lane and take the open one.
