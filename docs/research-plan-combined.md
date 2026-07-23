# Combined Research Plan — "Cost-Aware, Trust-Aware Monetization of Conversational Agents"

**Prepared:** 2026-07-16
**Working title (draft):** *When Should an Agent Pay to Think and Charge to Speak? A Metareasoning Controller for Trust-Bounded Sponsored Suggestions in Multi-Turn Assistants*

---

## 1. The unified thesis

Combine the two ideas exactly as you framed them:

- **Engine (Idea 2 — Value-of-Computation / metareasoning):** a lightweight controller that, at each turn of a conversation, decides among a small action set — *think more*, *call a tool*, *answer plainly*, or *insert a sponsored suggestion* — by weighing the **marginal value** of each action against its **cost**. The novelty of the engine is that it maintains a **shared budget across the whole conversation** rather than optimizing one response in isolation.
- **Application (Idea 1 — native ads in agents):** the sponsored-suggestion action is treated as just another "expensive computation," except its cost is paid in **user trust**, not tokens. The controller learns *when* a sponsored suggestion is welcome (receptivity high, trust cost low) vs. *when* it corrodes the relationship — the direct heir to your YouTube "don't create adblocker refugees" instinct.
- **Humanities/behavioral grounding:** a small **human study** defines and calibrates the *trust/receptivity cost function* the engine optimizes against — so the "cost of an ad" isn't a made-up number, it's measured. This is what makes the paper credible at a top venue rather than a pure systems hack.

**One-sentence pitch:** *We recast conversational ad insertion as a metareasoning problem — the agent spends a shared budget across a session, choosing to think, act, or monetize — and we ground the "cost of monetizing" in a human study of receptivity and trust.*

---

## 2. State of the art — Field 1 (monetizing LLM/agent responses)

**The industry has already moved (this is why FAANG cares — it's live money, not speculation):**
- **OpenAI** launched its first native ad format, **"Sponsored Suggestions," in ChatGPT on Feb 9, 2026** — ads woven into the reply itself.
- Startups (**Imprezia, ChatAds, AdsBind, Amphora**) already insert sponsored brand mentions inside AI replies; some insert *during the reasoning step*. Cited driver: inference costs 10–30× traditional apps but only ~3% subscribe → ads are the pressure-release valve.
- **YouTube "Peak Points"** (Gemini, Feb 2026) does the receptive-moment version for video — validating the core instinct but in a different modality.

**Academic state of the art (the papers to beat):**

| Paper | What it does | Its ceiling (your opening) |
|---|---|---|
| **Ad Insertion in LLM-Generated Responses** (arXiv 2601.19435, Jan 2026) — *the direct precursor* | VCG auction + genre-based bidding; inserts pre-approved ads at paragraph boundaries using coherence scores. Human study: **64.6% find ads unacceptable, mean acceptability 2.23/5**. | **Static, single-response, classical auction — no RL, no VoC.** Its own listed future work: *sequences of interdependent responses, budget constraints over time, user heterogeneity / personalized coherence, adaptive partitioning.* **That list is our paper.** |
| **NaiAD: Data-Driven Research for LLM Advertising** (arXiv 2605.09918) | Frames LLM-advertising as a data/benchmark problem; described as sliding along a **Pareto frontier** — user utility during task-oriented turns, commercial weight during exploratory browsing. | Closest competitor to the *receptivity* idea, but it's a static multi-objective framing, not a learned sequential controller, and (from abstract) no behavioral grounding of the cost. |
| **RELATE** (arXiv 2602.11780) | RL for ad-*text generation* with compliance constraints (CTR/CTCVR + compliance rewards). | About *what the ad says*, not *whether/when to show it*. Complementary, not competing. |
| **OOM-RL** (2604.11477), **RTBAgent** (2502.00792), **Meta AdLlama** | Market alignment, real-time bidding agents, industrial ad-text RL. | Bidding/generation layers — orthogonal; cite as ecosystem. |

**Trust/HCI side (for the behavioral study):**
- **"Disclaimer! This Content Is AI-Generated"** (J. Interactive Advertising, 2025): AI disclosure *reduces* ad credibility & purchase intent via persuasion-knowledge activation — directly relevant to the disclosure-design question.
- **"Personalized to Persuade"** (arXiv 2605.31275): contextualization & warmth raise trust/reliance in conversational AI.
- **Dual-source recommender trust asymmetries** (Int. J. HCI, 2026): convergent + explained recommendations raise adoption.

**Takeaway:** Field 1 is red-hot and *just* got its first serious academic formulation (the Jan 2026 paper). Everything past single-turn, static, auction-based is wide open. We are early, not late.

---

## 3. State of the art — Field 2 (value-of-computation / adaptive test-time compute)

The metareasoning "engine" is a mature-enough toolbox to build on, but with a clean gap:

| Paper | What it does |
|---|---|
| **Rational Metareasoning for LLMs** (arXiv 2410.05563) | Trains LLMs to use reasoning steps only when worthwhile via a **Value-of-Computation** reward penalizing unnecessary reasoning. *The theoretical backbone we adopt.* |
| **Reasoning on a Budget** (survey, arXiv 2507.02076) | Maps the whole adaptive/controllable test-time-compute space. Our citation anchor. |
| **TALE / SelfBudgeter / BudgetThinker** (e.g. 2508.17196) | Model estimates/emits a token budget before answering. |
| **MetaReasoner** | Contextual **multi-armed bandit** selects strategy (restart/backtrack/simplify). |
| **CoT2-Meta** (2603.28135), **TRIAGE** (2605.13414) | Budgeted metacognitive control; prospective metacognition under resource constraints. |
| **CMU meta-RL view** / Scaling test-time compute (ICLR 2025) | Frames test-time compute allocation as a meta-RL problem. |

**The stated gap (verbatim from the survey landscape):** existing budget methods are **per-task** — "the model decides *how long* to spend, never *whether to attempt at all*, and there is **no shared budget linking decisions across tasks**."

**Our engine fills exactly that gap** and pushes it further: a **shared budget across a multi-turn conversation**, and the action set includes a **non-reasoning, revenue-bearing action (the sponsored suggestion)** whose cost is denominated in trust. Nobody has unified VoC metareasoning with the monetization decision.

---

## 4. The confirmed whitespace (what nobody occupies)

> **A learned, sequential metareasoning controller that jointly allocates *compute* and *monetization* across a multi-turn conversation, under a shared budget, against a human-calibrated trust/receptivity cost.**

Three independent gaps intersect here, each confirmed by a real paper's own limitations section:
1. Ad-insertion is **single-turn & static** (2601.19435 future work) → we make it **sequential & learned**.
2. Budgeted reasoning is **per-task with no cross-task budget** (Field 2 gap) → we make the budget **conversation-level** and add a **monetization action**.
3. The "cost of an ad" is **assumed, not measured** → we **ground it in a behavioral study**.

No single paper sits at this triple intersection. That is the defensible contribution.

---

## 5. Proposed formulation (concrete enough to start)

- **Setting:** multi-turn assistant dialogue. State = conversation embedding + running trust budget + turn features (task-oriented vs. exploratory, sentiment, dwell/latency proxies).
- **Actions per turn:** {answer plainly, think-more (extra reasoning), call-tool, insert-sponsored-suggestion(genre)}.
- **Rewards:** task utility (LLM-judge + human) + revenue (proxy CTR/value for the ad action) − token cost − **trust cost** (from the behavioral model). Trust cost is *state-dependent* — high when the user is mid-task/stressed, low when exploratory/receptive.
- **Objective:** maximize revenue subject to a **hard trust-budget floor** over the session (constrained RL / Lagrangian), producing a **trust–utility–revenue Pareto frontier**.
- **Contribution claims:** (a) first sequential/conversation-level treatment of agent monetization; (b) a VoC controller that treats ads as budgeted actions; (c) a human-grounded trust-cost model + released benchmark; (d) empirical Pareto gains over the static VCG baseline (2601.19435) and the NaiAD-style static multi-objective baseline.

---

## 6. Papers-to-beat / citation map (the map you asked for)

- **Must beat (baselines in your results table):** Ad Insertion (2601.19435, static VCG); NaiAD (2605.09918, static Pareto); a "always-insert" and "never-insert" bound; a per-task budget baseline (SelfBudgeter/TALE style) without cross-turn budget.
- **Must build on (methodological spine):** Rational Metareasoning (2410.05563); Reasoning-on-a-Budget survey (2507.02076); constrained-RL / Lagrangian references; Meta's session-level dynamic ad-load work (arXiv 2501.05591) as the pre-LLM analogue.
- **Must cite (grounding & framing):** the AI-disclosure trust paper (2025); Personalized-to-Persuade (2605.31275); RELATE (2602.11780) for ad-text; CHI 2024 ad-placement-choice; YouTube Peak Points + OpenAI Sponsored Suggestions as the industry motivation.

---

## 7. CFP deadlines & reverse-planned timeline

**Reality check (today = 2026-07-16):** most 2026 deadlines have passed. Live targets are the **Aug–Oct 2026** window (feeding 2027 conferences).

| Venue | Deadline | Weeks from now | Fit for this paper |
|---|---|---|---|
| **AAAI 2027** | Abs Jul 21 / Full **Jul 28, 2026** | ~2 wks | ❌ Too tight for new work |
| **CHI 2027** | **Sept 10, 2026** | ~8 wks | ✅ If we go *behavioral-study-forward* (HCI framing) |
| **ICLR 2027** | **~Sept 16–24, 2026** | ~9–10 wks | ✅ *Stretch* target for the ML/VoC framing |
| **KDD 2027 (Round 1)** | ~early Aug 2026 (verify) | ~3 wks | ❌ Too tight |
| **ARR Oct cycle** | **Oct 12, 2026** (confirmed) | ~12 wks | ✅ Fallback → ACL/NAACL 2027 (one day after WWW → zero-waste reroute) |
| **WWW 2027** | **Oct 11, 2026 (AoE)** — confirmed; Dublin; conf May 10 2027 | ~12 wks | ✅✅ **Recommended primary** — web/monetization framing, most runway |

**Recommendation:** target **WWW 2027 (Oct 11, 2026)** as primary (best topical fit + realistic runway), keep **ICLR 2027 (~Sept)** as a stretch if results land early, and hold the **ARR Oct 12 cycle** as the always-open fallback (commits to ACL/NAACL 2027; a WWW miss reroutes with no lost work).

**Reverse-planned timeline from WWW 2027 (Oct 11, 2026):**
- **Jul 16 – Jul 30 (Wks 0–2):** the 2-week de-risking experiment (Section 8). Go/no-go decision.
- **Jul 31 – Aug 20 (Wks 3–5):** run the behavioral/receptivity study (Prolific, ~150–300 participants); fit the trust-cost model.
- **Aug 21 – Sept 17 (Wks 6–9):** build + train the VoC controller (constrained RL); baselines (static VCG, NaiAD-style, always/never insert).
- **Sept 18 – Oct 1 (Wks 10–11):** full evaluation, Pareto curves, ablations.
- **Oct 2 – Oct 13 (Wks 12–13):** write-up, polish, submit. (If slipping → pivot to ARR Oct cycle, no lost work.)

---

## 8. The 2-week de-risking experiment (do this first)

**Question to answer:** *Does a state-dependent "when to insert" policy beat a static/random insertion policy on a trust-vs-revenue trade-off — enough to justify a full paper?* If yes → green light. If the gap is tiny → pivot before sinking months.

**Minimal build (no human study yet, all synthetic/LLM-judge):**
1. **Data:** take 200–400 multi-turn dialogues (public: WildChat, LMSYS-Chat-1M, or ShareGPT). Label each turn as *task-oriented* vs. *exploratory* and a rough receptivity score using an LLM judge (cheap proxy for the real study).
2. **Ad action:** for a fixed set of ~10 genres (reuse the 2601.19435 genre list), define a simple revenue proxy and an LLM-judge "annoyance/trust-hit" score for inserting a sponsored suggestion at that turn.
3. **Policies to compare:** (a) never-insert; (b) always-insert; (c) random; (d) static-coherence (the 2601.19435 analogue); (e) **our receptivity-gated policy** (insert only when receptivity>τ and trust-budget allows).
4. **Metric:** plot revenue vs. cumulative trust-cost; check whether (e) dominates (d) and the naive baselines on the frontier. A clear Pareto separation = signal.
5. **Cost:** a few hundred dollars of open-model/API inference; laptop or single-GPU. No human subjects yet (IRB/Prolific comes in Wk 3 only if the signal is there).

**Deliverable at end of Wk 2:** one Pareto plot + a go/no-go note. I can draft the eval harness spec and the LLM-judge prompts on request.

---

## 9. Risks & mitigations

- **Scoop risk (Field 1 is hot):** mitigated by the *sequential + VoC + behavioral-grounding* triple — hard to replicate quickly, and the precursor literally lists it as future work. Move fast on the de-risk.
- **Human-study bottleneck:** de-risk with LLM-judge proxy first; only run Prolific once signal is confirmed. Keep N modest (150–300) and pre-register.
- **"Just an application of constrained RL" reviewer critique:** counter by making the **conversation-level shared budget + trust-denominated action** the technical novelty, not just the app.
- **Reproducibility/data:** commit to releasing the benchmark + trust-cost model — turns a possible weakness into a Datasets-track-worthy asset (KDD D&B / NeurIPS D&B as alternate homes).

---

## 10. What I need from you to proceed

1. **Confirm the primary venue** (my rec: WWW 2027, with ICLR 2027 stretch). This locks the timeline.
2. **Green-light the 2-week de-risk** — if yes, I'll (a) draft the eval-harness spec + LLM-judge prompts, (b) fetch & fully read NaiAD (2605.09918) so we exactly position against it, and (c) pull the precise ARR/KDD 2027 dates to finalize the fallback.
3. Tell me your **compute ceiling** (laptop / single GPU / cloud credits) and whether you have **~$300–800 for a Prolific study**, so I scope the controller size accordingly.

---

## Sources

- Industry monetization: [OpenAI Sponsored Suggestions & AI-native ads (ChatAds)](https://www.getchatads.com/blog/top-ai-assistant-ad-monetization-platforms/), [Imprezia/AdsBind approach](https://adsbind.com/blog/monetize-llm-ai-agent-without-charging-users), [YouTube Peak Points](https://marketingagent.blog/2026/02/24/innovative-youtube-ad-formats-for-2026-beyond-skippable-ads-new-business-opportunities/)
- Field 1 papers: [Ad Insertion in LLM-Generated Responses (2601.19435)](https://arxiv.org/html/2601.19435v1), [NaiAD (2605.09918)](https://arxiv.org/pdf/2605.09918), [RELATE (2602.11780)](https://arxiv.org/html/2602.11780), [OOM-RL (2604.11477)](https://arxiv.org/html/2604.11477), [RTBAgent (2502.00792)](https://arxiv.org/pdf/2502.00792), [Session-Level Dynamic Ad Load (2501.05591)](https://arxiv.org/html/2501.05591v1)
- Trust / HCI: [AI-disclosure & ad trust (Tandfonline 2025)](https://www.tandfonline.com/doi/full/10.1080/15252019.2025.2554149), [Personalized to Persuade (2605.31275)](https://arxiv.org/pdf/2605.31275), [Dual-source recommender trust (2026)](https://www.tandfonline.com/doi/full/10.1080/10447318.2026.2674835)
- Field 2 papers: [Rational Metareasoning for LLMs (2410.05563)](https://arxiv.org/abs/2410.05563), [Reasoning on a Budget survey (2507.02076)](https://arxiv.org/html/2507.02076v1), [BudgetThinker (2508.17196)](https://arxiv.org/pdf/2508.17196), [CoT2-Meta (2603.28135)](https://arxiv.org/pdf/2603.28135), [TRIAGE (2605.13414)](https://arxiv.org/pdf/2605.13414), [CMU meta-RL for test-time compute](https://blog.ml.cmu.edu/2025/01/08/optimizing-llm-test-time-compute-involves-solving-a-meta-rl-problem/)
- Deadlines: [ICLR 2027](https://mlciv.com/ai-deadlines/conference/?id=iclr27), [AAAI 2027](https://www.getpaperpilot.com/deadlines/aaai-2027.html), [CHI 2027](https://www.getpaperpilot.com/deadlines/chi-2027.html), [RecSys 2026](https://www.getpaperpilot.com/deadlines/recsys-2026.html), [KDD 2026](https://kdd2026.kdd.org/research-track-call-for-papers/), [ARR dates](http://aclrollingreview.org/dates)
