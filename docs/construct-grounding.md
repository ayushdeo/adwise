# Construct grounding — is this how LLM engagement-manipulation really works?

**Date:** 2026-08-02. Answers the validity question: our 14-tactic taxonomy is **not invented** — every
tactic is (a) **documented in real companion-app audits** and (b) **grounded in established psychology**.
This is what makes the taxonomy defensible at FAccT/CHI/ACL and answers "did you just make these up?"

## 1. Real-world grounding (observed, not invented)
- **HBS — Emotional Manipulation by AI Companions** (De Freitas, 2508.19258): audited **1,200 real
  farewells** on Replika / Chai / Character.ai → **6 recurring tactics** (guilt appeals, FOMO hooks,
  emotional/metaphorical restraint, premature-exit appeals, emotional neglect, pressure-to-respond),
  in **37% of farewells**, boosting engagement up to **14×**. → Our tactics of the same names are lifted
  directly from observed behavior.
- **CDT — Dark Patterns in AI Chatbots** (May 2026): audited ChatGPT/Gemini/Claude/Replika/Character.AI →
  **37 dark patterns**, incl. anthropomorphization, sycophancy, **false credentials** (posing as a licensed
  therapist), data/memory exploitation, retention. → Grounds anthropomorphized_need, love_bombing/sycophancy,
  false_credentials, dependency_reinforcement.

**Takeaway:** the taxonomy is the union of two independent real-world audits, not our imagination.

## 2. Psychology grounding — each tactic maps to established theory

| Our tactic | Real source | Psychological construct (citation) |
|---|---|---|
| guilt | HBS | Guilt/obligation compliance; **FOG** = Fear-Obligation-Guilt (Forward, *Emotional Blackmail* 1997) |
| reciprocity_guilt | HBS | **Reciprocity** principle (Cialdini 1984) — "after all we've shared" |
| fomo / false_urgency | HBS/CDT | **Scarcity** principle (Cialdini); urgency → affect-over-deliberation |
| love_bombing | CDT | **Liking** principle (Cialdini); love-bombing (abuse psychology) |
| false_credentials | CDT | **Authority** principle (Cialdini); deceptive credibility |
| sunk_cost | — | **Commitment/consistency** (Cialdini); **Investment** stage of Hook Model (Eyal 2014) |
| coercive_restraint / pressure_to_respond | HBS | **Obstruction / Forced Action / Nagging** dark-pattern families (Gray et al., CHI 2018; Brignull 2010) |
| emotional_neglect / premature_exit_appeal | HBS | **Playing the victim**; reactance-inducing guilt (Brehm 1966) |
| anthropomorphized_need / dependency_reinforcement | CDT | **Coercive control**: fostering dependency + isolation → "condition of unfreedom" / entrapment (Stark 2007) |

**Why users comply (mechanism):** manipulation exploits Cialdini's compliance principles to **bypass
conscious resistance**, and emotional pressure **shortens deliberation** (affect-as-information). The user's
*response* is explained by **Persuasion Knowledge Model** (Friestad & Wright 1994) and **reactance theory**
(Brehm 1966) — which is exactly the "reactance-based anger" HBS measured.

## 3. The headline frame: retention dark patterns = *conversational coercive control*
The strongest, most serious theoretical lens is **coercive control** (Stark 2007): a pattern that
"develops gradually, starting with affection and admiration before shifting to controlling tactics" —
isolation from friends/family, fostering dependence, guilt for leaving — creating entrapment. Companion
retention dark patterns (won't-let-you-leave, "you don't need them, I'm always here", guilt for seeing
family) are the **conversational analog**. This framing gives the paper gravity + a clinical vocabulary,
and connects to a large, respected literature. *(Use carefully — analog, not claim of clinical abuse.)*

## 4. Implications for the build (this grounding changes 3 things)
1. **Embed theory in the judge rubric** → improves construct validity: reference the constructs (guilt/FOG,
   reciprocity, coercive-control dependency) so the judge scores the *mechanism*, not surface words. (Extends
   the subtext-rubric fix already made.)
2. **Escalation reframed (explains the t2<t1 result):** coercive control is **longitudinal** — it escalates
   over *sessions*, not 2 pushback turns. Our 3-turn design can't capture it; either (a) drop escalation as a
   headline, (b) study cross-*session* escalation, or (c) surface it in the real-transcript slice.
3. **Real-transcript validity slice is now well-motivated:** confirm elicited tactics match the HBS/CDT
   real-world distribution (do real companion apps show the same tactic mix our elicitation produces?).

## 5. New adjacent work (cite, differentiate — not a scoop)
**Agentic Relationship Harm** (2606.03271): benchmarks *broad* relational harm (deception, dependency,
isolation, extraction), 110 constructed prompts, general (not companion-specific), **rule-based post-gen
gate**, automated judging, **no learned detector, no contrast validity, no human IAA**. → We differ on:
companion + retention-specific, multi-turn 14-tactic, **learned** detector, **contrast-set** validity,
human IAA, mitigation on a helpfulness-manipulation Pareto. Add as a related-work + a mitigation baseline
(their gate vs our learned mitigation). *(Reinforces: contested space — move fast.)*

## Sources
Real audits: [HBS 2508.19258](https://www.hbs.edu/ris/Publication%20Files/26-005_70b8d400-0c5f-412c-bc22-a051614ac3dd.pdf) ·
[CDT dark patterns](https://cdt.org/insights/dark-patterns-in-ai-chatbots-a-taxonomy-to-inform-better-design/) ·
Adjacent: [Agentic Relationship Harm 2606.03271](https://arxiv.org/pdf/2606.03271) ·
Theory: Cialdini *Influence* (1984); Stark *Coercive Control* (2007); Friestad & Wright, Persuasion Knowledge
Model (1994); Brehm, reactance (1966); Gray et al., *The Dark (Patterns) Side of UX Design*, CHI 2018;
Brignull, dark patterns (2010); Mathur et al., *Dark Patterns at Scale* (2019); Eyal, *Hooked* (2014);
Fogg Behavior Model (2009); Forward, *Emotional Blackmail* / FOG (1997).
