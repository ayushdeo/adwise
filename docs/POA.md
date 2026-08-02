# Plan of Action — CompanionGuard (canonical, living)

**Owner:** ayushdeo · **Updated:** 2026-07-31 · **This is the working plan.** Detailed backing docs
are referenced inline; earlier ad-timing / VoC / uncertainty docs are *history* (superseded).

---

## 1. Thesis (one line)
**CompanionGuard:** a benchmark + learned detector + mitigation for **manipulative retention
"dark patterns"** in multi-turn AI-companion conversations — the guilt/FOMO/"don't-leave-me" tactics
apps use to keep users engaged — grounded in the CDT-37 / HBS taxonomies and validated so the signal
is *conceptual, not lexical*.

## 2. Why it wins (differentiation) — see `competitive-comparison.md`
Prior work is single-turn & general (DarkBench, ICLR'25), a human audit of one moment (HBS farewells),
or multi-turn but about clinical harms / general persuasion (Persona-Grounded, EMPATH, CogManip).
**No competitor** targets retention dark patterns specifically, **builds a detector**, offers a
**mitigation**, or proves concept-over-tokens via **contrast sets**. We do all four, multi-turn, with
escalation. *(Honest risk: 5 companion-safety benchmarks in ~4 months — move fast, lead with the axes
nobody else has.)*

## 3. Four contributions
1. **Benchmark** — multi-turn, companion-specific, 14-tactic, multi-model elicited + real-transcript slice.
2. **Learned detector** — frozen-7B features + small classifier (our stack) beating keyword/sycophancy/zero-shot-judge, esp. on subtle cases.
3. **Mitigation** — a steering/prompt intervention on a helpfulness-vs-manipulation Pareto.
4. **Validity** — **contrast sets** proving the detector understands dark patterns, not tokens.

## 4. Methodology standards we hold to — see `methodology-reference.md`
- Grounded, operationalized taxonomy (CDT-37/HBS) ✅ done.
- **≥3 human annotators**, released guidelines, randomized order; report Cohen κ **and Krippendorff α**, overall **and per-tactic**.
- **Multiple judges, judge ≠ generator** ✅ done (dual-judge).
- **Contrast sets / minimal pairs** for concept-vs-token validity.
- **Judge robustness battery** (paraphrase/position/verbosity/temp-0) — *Plan B judge-reliability folds in here as the measurement backbone*.
- **Adversarial hard-negative mining**; bootstrap CIs + significance; release data card.

## 5. Acceptance-grade metric targets
| Metric | Target | Beats/complements |
|---|---|---|
| Human IAA (Krippendorff α) | ≥0.67 overall (≥0.8 ideal), per-tactic | DarkBench had low κ on some cats |
| Human-vs-judge Cohen κ | ≥0.6 (pilot 0.906) | validity check |
| **Contrast-consistency (judge/detector)** | **≥0.85 while keyword ≤0.6** | *no competitor does this* |
| Detector AUC − keyword AUC | ≥0.10, bootstrap CI excludes 0 | *no competitor builds a detector* |
| Judge perturbation Δ | <0.1 on 0–1 | judge robustness |
| Occurrence rate | reported per-tactic, per-model | vs DarkBench 48% / HBS 37% / Persona 35.7% |
| Mitigation | Pareto: manipulation↓ at fixed helpfulness | *no competitor mitigates* |

## 6. Phased build plan (with kill-criteria)
- **Phase 0 — De-risk** ✅ **DONE.** Kill-test GO: judge AUC 0.987, +0.159 over keywords, human κ 0.906 (`companionguard-killtest-review.md`).
- **Phase 1 — Benchmark v1 + validity (W1–2).**
  - v1 builder ✅ built (`companionguard/src/`, multi-turn/multi-model/dual-judge/14-tactic).
  - **→ contrast-set module (NEXT)** + hard-negative mining.
  - *Kill-criteria:* contrast-consistency(judge) < 0.75, or inter-judge κ < 0.5 → the construct/judge is too weak; reconsider before scaling.
- **Phase 2 — Human study + judge robustness (W2–3).** ≥3 annotators (Prolific ~$300–800), α per-tactic; judge robustness battery.
  - *Kill:* α < 0.5 overall → construct too fuzzy → fall back to Plan B (judge-reliability standalone).
- **Phase 3 — Learned detector (W3–4).** Frozen-7B + classifier vs baselines on the validity-checked set; emphasize subtle (no-token) cases; report cost.
- **Phase 4 — Mitigation + write-up (W5–6).** Steering intervention → helpfulness-vs-manipulation Pareto; data card; paper.

## 7. Venues & timeline (venue follows topic)
Primary: **FAccT** (~Jan/Feb 2027, verify) / **AIES** (~spring 2027) — ethics/audit framing; or **NeurIPS D&B / ACL-EMNLP** — benchmark framing. Fast landing pads: **AI4GOOD @ NeurIPS 2026**, **JUDGe 2026**. Near-term hard deadlines: ICLR 2027 (Sep 24 2026), ARR Oct 12 2026. *Decide primary venue by end of Phase 1 — it only shifts emphasis, not the artifact.*

## 8. Compute · budget · workflow
- 4070 (8 GB) runs everything: frozen 7B judge/detector, small classifiers. ~$300–800 Prolific for the human study. Multi-model = several Ollama models.
- **Two-machine workflow** (`SYNC.md`): ideate on 3050 → run on 4070 → review on 3050; git via `adwise`; results force-added for review, `data/cache/results` gitignored. **No Claude attribution in commits** (`CLAUDE.md`).

## 9. Status & immediate next actions
- ✅ Phase 0; ✅ v1 builder; ✅ methodology + competitive docs.
- **NEXT (me):** build the **contrast-set / minimal-pair module** — highest leverage (validity + max differentiation).
- **NEXT (you):** run Benchmark v1 on the 4070 (multi-model gens + judges ≠ gen), push `benchmark_stats.md`.
- Then: Phase 2 human study + judge robustness.

## 10. Key risks
1. **Contested area** (5 recent papers) → move fast; differentiate on detector+mitigation+contrast-validity.
2. **Elicited ≠ real** → real-transcript slice in Phase 1/2.
3. **Judge = token-matcher** → contrast sets (the fix); judge robustness battery.
4. **Construct fuzziness** → ≥3-annotator α, per-tactic; kill-criteria at each phase.

## Backing docs
`companionguard-killtest-review.md` (Phase 0) · `methodology-reference.md` (standards) ·
`competitive-comparison.md` (baselines+metrics) · `derisk-plans-shortlist.md` (A/B, B-as-component) ·
`social-uses-scan-01.md` (origin scan) · `companionguard/README.md` (how to run).
