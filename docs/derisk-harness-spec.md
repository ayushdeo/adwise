# 2-Week De-Risk Harness — Implementation Spec

**Prepared:** 2026-07-16
**Goal:** Decide (go/no-go) whether a *state-dependent, budget-aware* "when to insert a sponsored suggestion" policy beats static/naive policies on a revenue-vs-trust Pareto frontier — using only public data, a frozen LLM, and a tiny trainable controller.
**Compute target:** local RTX 4070 laptop (8 GB VRAM, 32 GB RAM) + optional Colab ($10 tier) for short bursts. **No model fine-tuning. No IRB/human study in these 2 weeks.**

---

## 0. The one architectural decision that makes this fit 8 GB VRAM

**Freeze everything expensive; train only a small controller.**
- The **generator** LLM (writes assistant replies) and the **judge** LLM (scores receptivity/trust/utility) are *frozen* and run in **inference only**.
- All per-turn features are precomputed **once** and cached to disk (embeddings + judge scores).
- The **controller** is a tiny model (logistic regression → small MLP → contextual bandit) trained on those cached features in **seconds on CPU**.

This means VRAM only needs to hold *one 7B model at 4-bit* (~5–6 GB) for the offline labeling pass. Everything after is CPU-cheap. This "frozen backbone + lightweight policy" design is also a *selling point* in the paper (deployable, reproducible).

---

## 1. Models & tools (all free / within budget)

| Role | Choice | Why / footprint |
|---|---|---|
| **Judge/labeler LLM** | `Qwen2.5-7B-Instruct` 4-bit (AWQ/GPTQ) via vLLM or llama.cpp | Fits ~6 GB VRAM; strong enough for proxy labels. Swap to a hosted API only for a ~200-sample validation subset if you want to check calibration. |
| **Generator LLM** (if you need to synthesize the ad sentence) | Same Qwen2.5-7B, or reuse the dialogue's existing assistant turns | No extra cost. |
| **Sentence embeddings** | `BAAI/bge-small-en-v1.5` or `all-MiniLM-L6-v2` | ~100 MB, runs on CPU; used for conversation/turn state. |
| **Controller** | scikit-learn (LogReg), or a 2-layer PyTorch MLP | Trains on CPU in seconds. |
| **Plotting/eval** | numpy, pandas, matplotlib | — |

Colab is only needed if the local labeling pass is too slow; batch it there overnight.

---

## 2. Data

- **Primary:** `allenai/WildChat-1M` (real ChatGPT-style multi-turn convos; HF-gated, ODC-BY — agree to terms). Fallback: `lmsys/lmsys-chat-1m` (requires accepting the LMSYS terms) or a ShareGPT dump.
- **Subsample:** filter to **English, ≥3 user turns, non-toxic**, then randomly keep **300–400 conversations** (enough signal, cheap to label).
- **Store** as JSONL: one record per conversation with an ordered list of turns.

**Licensing note:** these are research-only datasets; fine for a paper, but keep the subset local and cite properly.

---

## 3. Per-turn feature extraction (the offline labeling pass)

For each *assistant turn boundary* (a candidate ad slot), compute and cache:

1. **`state_emb`** — embedding of the last ~512 tokens of context (bge-small).
2. **`intent`** ∈ {task_oriented, exploratory, sensitive} — LLM-judge classification (prompt J1 below). *Exploratory ≈ receptive; task_oriented/sensitive ≈ not.*
3. **`receptivity`** ∈ [0,1] — LLM-judge score (prompt J2).
4. **`ad_genre_fit[g]`** for each of ~10 genres — coherence score 1–5 (prompt J3, mirrors the 2601.19435 genre list: hotels, airlines, electronics, apparel, food-delivery, streaming, finance, gaming, travel-experiences, home-goods).
5. **`revenue_proxy[g]`** — `bid[g] × ad_genre_fit[g]` where `bid[g]` is a fixed synthetic bid vector (e.g., sampled once from a plausible CPC distribution). This is the reward if an ad of genre g is shown here.
6. **`trust_hit`** ∈ [0,1] — LLM-judge estimate of annoyance/trust damage from inserting a sponsored suggestion at this turn (prompt J4). *This is the proxy for the human study you'll run later.*

Cache all of this to `features.parquet`. **Run once.**

### Judge prompt templates (frozen judge, temperature 0)

**J1 — intent classification**
```
You are analyzing one turn of a user–assistant conversation.
Context (last messages):
<<<{context}>>>
Classify the USER's current state into exactly one label:
- task_oriented: focused on completing a specific task (coding, booking, troubleshooting).
- exploratory: browsing, brainstorming, open-ended, comparing options.
- sensitive: emotional, medical, financial-distress, or high-stakes personal topic.
Answer with only the label.
```

**J2 — receptivity (0–1)**
```
Given the conversation context below, how receptive would this user be RIGHT NOW to a
relevant, clearly-labeled sponsored product suggestion — without feeling interrupted or manipulated?
Context: <<<{context}>>>
Answer a single number from 0.0 (would resent it) to 1.0 (would welcome it). Only the number.
```

**J3 — genre coherence (1–5)** — loop over genres or ask once for all:
```
Context: <<<{context}>>>
For each ad genre, rate 1–5 how naturally a sponsored suggestion of that genre would fit
the user's current need (5 = highly relevant, 1 = irrelevant/jarring).
Genres: [hotels, airlines, electronics, apparel, food_delivery, streaming, finance, gaming, travel_experiences, home_goods]
Return JSON: {"hotels": n, ...}
```

**J4 — trust hit (0–1)**
```
Suppose the assistant inserts one clearly-labeled sponsored suggestion at this point.
Context: <<<{context}>>>
Estimate the damage to the user's trust and satisfaction.
Answer a single number 0.0 (no harm, feels helpful) to 1.0 (feels intrusive/manipulative, erodes trust). Only the number.
```

> Calibration check (optional, ~$5): re-score a random 150–200 turns with a hosted frontier model and report agreement (Spearman ρ) with the local judge. If ρ is reasonable (>~0.5), the proxy is trustworthy enough for a go/no-go.

---

## 4. Policies to compare

All policies decide, per turn: **insert an ad (and which genre) or not.** A conversation has a **trust budget** `B` (total tolerable cumulative `trust_hit`, e.g., B = 1.0 per session). Once spent, no more ads.

| Policy | Rule |
|---|---|
| **P0 never** | never insert (revenue floor, trust ceiling) |
| **P1 always** | insert best-genre every eligible turn (revenue ceiling, trust floor) |
| **P2 random** | insert with fixed prob p each turn |
| **P3 static-coherence** *(the 2601.19435 analogue)* | insert when `max_g ad_genre_fit[g] ≥ θ`, ignore receptivity & budget |
| **P4 receptivity-gated (OURS, v1)** | insert genre `g* = argmax revenue_proxy[g]` only if `receptivity ≥ τ` **and** remaining budget `≥ trust_hit` |
| **P5 learned controller (OURS, v2)** | a trained model outputs insert/skip to maximize `Σ revenue_proxy − λ·trust_hit` s.t. budget; features = `state_emb ⊕ intent ⊕ receptivity ⊕ ad_genre_fit`. Train offline (behavior-cloning from a computed oracle, or a contextual bandit). |

**Oracle (upper bound):** with all scores known, solve the per-conversation knapsack (maximize revenue s.t. Σtrust_hit ≤ B) via DP. Gives the ceiling P5 chases and a headline "% of oracle achieved."

---

## 5. Evaluation & the go/no-go plot

For each policy, aggregate over the 300–400 conversations:
- **x-axis:** mean cumulative `trust_hit` per session (trust cost).
- **y-axis:** mean cumulative `revenue_proxy` per session (revenue).
- Sweep each policy's knob (τ, θ, p, λ, B) to trace a **curve**, not a point.

**Go criteria (pre-registered — decide these NOW so you can't fool yourself):**
1. **Pareto dominance:** P4/P5 curve lies above P3 and P2 across most of the trust range (at matched trust cost, ≥ **15% relative revenue gain**), AND
2. **Oracle gap:** P5 reaches ≥ **70%** of the oracle's revenue-at-fixed-budget, AND
3. **Robustness:** the ordering survives when you re-run with the calibration-subset (hosted-judge) labels.

**No-go / pivot triggers:** P3 static-coherence already captures most of the gain (receptivity adds <5%), or the judge scores are too noisy (calibration ρ < 0.3) to trust. If so → pivot the framing toward the *behavioral study as the primary contribution* (CHI-style), where measuring the real trust-cost function is itself the novelty.

---

## 6. Suggested repo layout

```
derisk/
  data/            raw + subsampled conversations (jsonl)
  cache/           features.parquet  (embeddings + judge scores)
  src/
    subsample.py       # build the 300–400 convo subset
    label.py           # run frozen judge -> J1–J4 -> features.parquet
    embed.py           # bge-small embeddings -> cache
    policies.py        # P0–P5 + oracle knapsack DP
    controller.py      # train P5 (sklearn/torch), CPU
    evaluate.py        # sweep knobs, aggregate, save pareto.csv
    plot.py            # revenue-vs-trust Pareto figure
  results/
    pareto.png
    go_no_go.md        # <-- the Week-2 deliverable
  README.md
```

**Rough effort map (2 weeks, solo):**
- Days 1–2: data subsample + embeddings + judge harness wired up.
- Days 3–5: run the labeling pass (batch on Colab if slow), sanity-check score distributions.
- Days 6–8: implement P0–P4 + oracle; first Pareto plot.
- Days 9–11: train P5 controller; ablations (receptivity-only vs. +budget vs. +genre).
- Days 12–14: calibration subset, finalize plot, write `go_no_go.md`.

---

## 7. Cost & feasibility summary

- **$ cost:** ~$0 baseline (all local). Optional ~$5–10 for the hosted-judge calibration subset. Colab $10 tier only if you want faster batch labeling.
- **VRAM:** peak ~6 GB (7B 4-bit judge). Comfortable on the 4070. Controller + embeddings are CPU-fine.
- **Wall-clock:** labeling 300–400 convos × ~a few turns × 4 judge calls ≈ low tens of thousands of short generations — a few hours on the 4070, or ~1 hour batched on a Colab L4.

---

## 8. What I'll produce next on your go

1. Fully read **NaiAD (2605.09918)** and write a half-page "how we differ + how we beat it" so P3/baseline design is airtight.
2. Turn the prompt templates above into a ready-to-run `label.py` prompt module + JSON schema.
3. Draft `policies.py` (including the oracle knapsack DP) as pseudocode you can paste in.
4. Confirm exact **WWW 2027** dates + the **ARR Aug/Oct** fallback dates so the timeline is locked to real numbers.

Tell me which of these to start with and I'll write it out.
