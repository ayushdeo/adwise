# Literature Review — Cost/Trust-Aware Monetization of Conversational Agents

**Prepared:** 2026-07-21 · **Status:** Living document (v1) · **Target:** WWW 2027 (primary)

**Scope.** Four clusters bear on our thesis: (A) inserting ads into LLM/agent responses — the *application*; (B) value-of-computation / adaptive test-time compute — the *engine*; (C) session/feed ad-load RL — the *pre-LLM analogue*; (D) trust, disclosure, receptivity — the *behavioral grounding*. For each paper: what it does, why it matters to us, and precisely how we differ. The centerpiece is the **gap matrix (§6)**, which shows no prior work occupies our cell.

---

## Cluster A — Ad insertion in LLM/agent responses (the application)

### A1. Ad Insertion in LLM-Generated Responses (arXiv 2601.19435, Jan 2026) — **THE precursor to beat**
- **What:** Formalizes conversational ad monetization as a **VCG auction** with *genre-based bidding* (advertisers bid on stable categories like "hotels," not queries). Ads are pre-approved and inserted at paragraph boundaries where a **coherence score** (sentence-embedding cosine or LLM-as-judge, 1–5) is high. Provides approximate DSIC/IR guarantees with error bounds (valuation error ε_V, coherence error ε_C).
- **Empirical grounding:** Human study — **64.6% of users find ads unacceptable; mean acceptability 2.23/5.** Concerns: hidden ads bias choices, misinformation, irrelevance.
- **Relevance:** Defines the problem we extend and gives us a baseline (static-coherence placement) and a user-acceptability anchor.
- **How we differ (their own future-work list = our contribution):** they are **static, single-response, auction-theoretic, no user modeling.** They explicitly flag as open: *sequences of interdependent responses, budget constraints over time, user heterogeneity / personalized coherence, adaptive partitioning.* We deliver exactly that via a sequential VoC controller + human-grounded trust cost.

### A2. NaiAD: Data-Driven Research for LLM Advertising (arXiv 2605.09918) — **closest data competitor**
- **What:** A **dataset + pipeline** (58,999 ad-embedded query→response samples) with a *decoupled generation pipeline* and a **VC-PPI** (Variance-Calibrated Prediction-Powered Inference) framework to align automated scores with human labels.
- **Metrics (reuse these 4 axes):** user utility = **Response Relevance (Q1)** + **Expression Coherence (Q2)**; commercial utility = **Ad Effectiveness (Q3)** + **Click-Through Intent (Q4)**.
- **Four ad-integration "bridge" strategies** (useful priors for our ad-quality control): (1) *Value & Vision / Mindset Bridge*, (2) *Aesthetic & Lifestyle / Vibe Bridge*, (3) *Emotional & Psychological / Empathy Bridge*, (4) *Methodological Abstraction / Craftsmanship Bridge*.
- **Headline numbers:** SFT model **+28.2% avg** across dimensions; Response Relevance **+44.3% rel (+26.18pp)**; ICL gives **+14pp** on discordant target profiles. Built with Claude-4.5-Opus (generation) + Qwen3.5/3.6-Plus (synthesis/scoring); YouTube SponsorBlock as a human-sponsorship comparison.
- **Relevance:** The go-to dataset/benchmark for *response-level* ad quality; reuse its 4 utility axes and the VC-PPI calibration trick to align our LLM-judge `trust_hit`/receptivity scores to human labels in the later study.
- **How we differ (confirmed by full read):** authors **explicitly state NaiAD "focuses on single-turn, query-response interactions"** with **no cross-turn budget**. It is response-quality-focused ("given we insert here, make it good"), with **no whether/when decision, no shared trust budget, no metareasoning/compute allocation.** We consume its per-turn quality notion and add the sequential decision + budget layer.

### A3. RELATE (arXiv 2602.11780) — ad-text generation, complementary
- **What:** GRPO-based RL to generate ad *titles/descriptions* with multi-dimensional rewards (quality + diversity + CTCVR), granularity-aware credit assignment. 400k Baidu samples; +9.19% online CTCVR, 93.98% compliance.
- **Relevance/diff:** Optimizes **what the ad says**, not **when/whether to show it.** Orthogonal — cite as the creative layer that sits *below* our decision layer.

### A4. Ecosystem (bidding/market): OOM-RL (2604.11477), RTBAgent (2502.00792), Meta AdLlama
- Real-time bidding agents, market alignment, industrial ad-text RL. Orthogonal layers (auction/bidding/creative). Cite to show we occupy the *policy/timing* layer, not the market layer.

### A5. Industry reality (motivation, not baselines)
- **OpenAI "Sponsored Suggestions" in ChatGPT (Feb 9, 2026)**; Imprezia/ChatAds/AdsBind insert brand mentions inside replies (some during the reasoning step). **YouTube "Peak Points"** (Gemini) = receptive-moment ads for video. These prove the problem is live money — strong motivation paragraph.

---

## Cluster B — Value-of-Computation / adaptive test-time compute (the engine)

### B1. Rational Metareasoning for LLMs (arXiv 2410.05563) — **methodological spine**
- **What:** Trains an LLM to use reasoning steps *only when worthwhile* via a reward that subtracts a **Value of Computation** penalty for unnecessary reasoning; optimized with **Expert Iteration**. **20–37% fewer tokens** across three models with preserved accuracy.
- **Relevance:** Gives us the formal VoC objective and a training recipe we adapt — except our "computation" set includes a **revenue-bearing, trust-costing action** (the ad), and our budget is **conversation-level**.

### B2. Reasoning on a Budget (survey, arXiv 2507.02076) — **citation anchor + gap evidence**
- **Taxonomy:** L1 *controllable* (fixed budget) vs. L2 *adaptive* (input-difficulty-driven) × sequential/parallel × prompting/SFT/RL/merging. Representative methods: TALE, SelfBudgeter, BudgetThinker, MetaReasoner, CoT-Valve, O1-Pruner, etc.
- **Open problems it names:** budget adherence failures, over/under-thinking, task-specific tuning (poor generality), cross-model scalability, RL instability.
- **Key confirmation for us:** the survey **does not address whether a model should decline a task, nor cross-task/heterogeneous allocation.** Our conversation-level shared budget with a monetization action sits in that unaddressed space.

### B3. Per-task budget methods: TALE / SelfBudgeter / BudgetThinker (e.g., 2508.17196)
- Model estimates/emits a token budget **before answering, per task.** **Limitation we exploit:** no budget links decisions *across* turns; the ad decision is never in scope. These become a baseline family (per-turn budgeting without cross-turn coupling).

### B4. Strategy-selection & metacognition: MetaReasoner, CoT2-Meta (2603.28135), TRIAGE (2605.13414)
- Contextual-bandit strategy selection; budgeted metacognitive control; prospective metacognition under resource limits. Useful priors for our controller design (a contextual bandit is a natural v1 for P5).

---

## Cluster C — Session/feed ad-load RL (pre-LLM analogue)

### C1. Session-Level Dynamic Ad Load Optimization via Offline Robust RL (arXiv 2501.05591) — **direct RL analogue**
- **What:** Robust **Dueling DQN** over *user + session + prior-action* state; discrete low/high ad-load action; reward = revenue + α·engagement. Handles confounding via prior-actions-in-state and robust MDP (IPM uncertainty sets). ~80% offline AUCC gain vs. causal baseline; double-digit online trade-off improvement.
- **Relevance:** The closest *methodological* analogue — RL that trades revenue vs. engagement over a session. We borrow the state design (include prior ad actions) and the robustness concern (distribution shift).
- **How we differ:** it curates *how many* ads in an existing **feed**; we decide *whether/where* to inject sponsored content into **generated text**, coupled with a **compute-allocation** decision and a **trust-denominated** (not engagement-proxy) cost. Their own future work asks for **Pareto frontiers and nonlinear scalarization** — which we provide.

### C2. RecoMind (2508.00201), Pinterest DRL ranking utility (2509.05292)
- In-session RL for satisfaction / utility tuning. Cite as evidence the field is moving to session-level RL objectives; neither touches generative-text ad insertion or compute allocation.

---

## Cluster D — Trust, disclosure, receptivity (behavioral grounding for the trust-cost model)

### D1. AI-disclosure → trust/credibility (a convergent 2025 literature)
- Across multiple 2025 experiments (2×2 designs, **N≈201–395**, grounded in the **Persuasion Knowledge Model** / SOR framework), **AI disclosure lowers ad credibility, trust, and purchase intent**, mediated by credibility and moderated by consumer attitudes toward AI. Reps: "Disclaimer! This Content Is AI-Generated" (J. Interactive Advertising 2025); "Examining the effect of AI advertising involvement disclosure…" (JRIM 2025); "Effect of disclosing AI-generated content on prosocial advertising evaluation" (Int. J. Advertising 2024). *(Full effect sizes behind paywalls — abstract-level cite; direction is robust and consistent.)*
- **Implication for us:** the FTC-mandated "Sponsored" label is **not free** — it interacts with our trust cost. Makes disclosure design a first-class ablation (labeled vs. unlabeled insertion) rather than an afterthought.

### D2. Personalized to Persuade (arXiv 2605.31275) — **template for our human study**
- **Design:** between-subjects, **N=380**, 2×2 (contextualization × warmth); measures trust, reliance, persuasiveness. **Findings:** contextualization alone lowers persuasion but warmth restores it (crossover); trust predicts persuasion/reliance but the manipulations don't act *through* trust; more AI-literate users trust less yet are *more* persuaded/reliant. **Manipulation warning:** users over-defer to AI vs. human experts.
- **Relevance:** A concrete, right-sized human-study template (N≈380, factorial, Prolific-feasible) and a caution that "trust" is multi-dimensional — informs how we operationalize `trust_hit`.

### D3. Others
- Dual-source recommender trust asymmetries (Int. J. HCI 2026): convergent + explained recs raise adoption. CHI 2024 ad-placement choice: *timing* matters more than *choice* of placement — supports our receptivity-timing thesis. CHI 2025 "Ad-Blocked Reality": user perceptions of blocking.

---

## 6. The gap matrix (why our cell is empty)

| Work | Sequential / multi-turn | Learned policy (RL/bandit) | Value-of-Computation (compute allocation) | Trust cost **measured** on humans | Generative-text ad insertion |
|---|:--:|:--:|:--:|:--:|:--:|
| Ad Insertion / VCG (A1) | ✗ (single response) | ✗ (auction) | ✗ | partial (acceptability survey) | ✓ |
| NaiAD (A2) | ✗ | ✗ (dataset) | ✗ | partial (VC-PPI calibration) | ✓ |
| RELATE (A3) | ✗ | ✓ (text gen) | ✗ | ✗ | ✓ (creative only) |
| Session ad-load RL (C1) | ✓ | ✓ | ✗ | ✗ (engagement proxy) | ✗ (feed) |
| Rational Metareasoning (B1) | ✗ (per task) | ✓ | ✓ | ✗ | ✗ |
| Budget methods (B3) | ✗ (per task) | ✓ | ✓ (token budget) | ✗ | ✗ |
| **THIS PROJECT** | **✓** | **✓** | **✓ (ad = budgeted action)** | **✓ (human-calibrated `trust_hit`)** | **✓** |

**No prior work has all five ticks.** The defensible novelty is the *combination*: a conversation-level shared budget where a sponsored suggestion is one more budgeted "computation," priced by a human-grounded trust cost.

---

## 7. Positioning statement (paste-ready for the intro)

> Prior work on conversational ad monetization is **static and single-response** — auction-theoretic (A1) or dataset-driven (A2) — and prices "user experience" with unvalidated proxies. Prior work on adaptive compute (B1–B3) allocates a **per-task** budget over *reasoning* only, never coupling decisions across a session and never treating monetization as an action. Session-level ad-load RL (C1) is multi-turn but operates on **feeds**, not generated text, and optimizes an engagement proxy rather than a measured trust cost. **We unify these:** a sequential metareasoning controller that allocates a **shared session budget** across {think, act, answer, monetize}, where the sponsored-suggestion action is priced by a **human-calibrated trust/receptivity cost**, yielding a controllable trust–utility–revenue Pareto frontier that dominates the static VCG (A1) and static multi-objective (A2) baselines.

---

## 8. Confirmed deadlines (locked 2026-07-21)

- **WWW 2027 (primary):** research-track paper deadline **October 11, 2026 (AoE)**; Dublin, Ireland; conf May 10, 2027; notification Dec 10, 2026. → **~12 weeks of runway.**
- **ARR fallback:** **Oct 12, 2026** cycle (feeds ACL/NAACL 2027; venue TBA) — one day after WWW, so a WWW miss reroutes with zero lost work. (The Aug 3, 2026 ARR cycle → EACL 2027 is too tight.)
- **ICLR 2027 (stretch):** ~Sept 16–24, 2026 — only viable if the de-risk + controller land fast.

## 8b. Reading queue (remaining)

- [x] NaiAD — full metrics, 4 strategies, single-turn confirmed (see A2).
- [x] AI-disclosure trust literature — direction + N confirmed (see D1); exact effect sizes paywalled.
- [x] WWW 2027 / ARR dates — locked above.
- [ ] OOM-RL (2604.11477) full — confirm it's market-layer, not policy-layer (low priority).
- [ ] CHI 2024 "Choice in Video Ad Placement" — ACM page is 403; find author PDF for the precise timing>choice numbers.
- [ ] Constrained-RL spine for method section — **candidate canonical cites:** Altman (1999) *Constrained MDPs*; Achiam et al. 2017 *CPO*; Tessler et al. 2019 *Reward-Constrained Policy Optimization*; Stooke et al. 2020 *PID Lagrangian*. Pick 2–3.

---

## 9. BibKey shortlist (for the .bib)

`ad-insertion-vcg-2601.19435` · `naiad-2605.09918` · `relate-2602.11780` · `oomrl-2604.11477` · `rtbagent-2502.00792` · `rational-metareasoning-2410.05563` · `reasoning-on-budget-survey-2507.02076` · `budgetthinker-2508.17196` · `cot2meta-2603.28135` · `triage-2605.13414` · `session-adload-rl-2501.05591` · `recomind-2508.00201` · `pinterest-drl-2509.05292` · `ai-disclosure-trust-2025` · `personalized-to-persuade-2605.31275` · `dualsource-trust-2026`
