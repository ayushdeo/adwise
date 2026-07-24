# CLAUDE.md — project guide for the coding agent

Read this first. It tells you what this repo is, how we work across two machines,
and the hard rules.

## Hard rules (do not violate)
1. **No Claude/AI attribution anywhere in git.** Never add `Co-Authored-By: Claude`
   (or any Claude/Anthropic mention) to commit messages or PR bodies. Commits are
   authored solely by the user (`ayushdeo`). This is a firm, standing preference.
2. **Never commit data/derived artifacts.** `derisk/data/`, `derisk/cache/`, and
   `derisk/results/` are gitignored. Raw WildChat/LMSYS conversations are
   research-license / HF-gated — do not commit them. They regenerate locally.
3. **Confirm before anything outward-facing** beyond ordinary `git push` to this
   repo (e.g., publishing, deleting remote data, posting).

## What this project is
Research toward **WWW 2027** (deadline **Oct 11, 2026**): reframing native-ad
insertion in multi-turn AI assistants as a **metareasoning** problem — an agent
spends a shared per-session **trust budget** across {think, act, answer, monetize}
and learns *when* a sponsored suggestion is welcome vs. trust-corroding, with the
"cost of an ad" **measured** via a (later) human study rather than assumed.

Full context in:
- `docs/research-plan-combined.md` — the thesis, confirmed whitespace, timeline.
- `docs/derisk-harness-spec.md` — the 2-week de-risk design + pre-registered go/no-go.
- `literature/literature-review.md` — annotated review + the gap matrix (papers to beat).

## Two-machine workflow
- **This machine = RTX 4070 laptop (8 GB VRAM):** the *runner*. Do the labeling +
  training runs here. Ollama serves the frozen judge (`qwen2.5:7b-instruct`).
- **Other machine = 3050 laptop:** ideation + results review.
- **Sync = git only** (`github.com/ayushdeo/adwise`). Code/docs sync; data/cache/results
  do not (by design). Protocol: `git pull` before work, `git commit && git push` after.
  Commit results *figures* only if deliberately needed (drop them in `docs/`).

## The de-risk pipeline (all built & tested)
Run everything from `derisk/`. Setup + commands: **`derisk/SETUP.md`**.
```
subsample.py  WildChat/LMSYS/file  -> data/subset.jsonl      (manual; needs HF login)
label.py      frozen judge (Ollama) -> cache/features.parquet (GPU, hours, resumable)
embed.py      bge-small context vecs -> cache/embeddings.parquet
controller.py oracle behavior-clone -> cache/controller_scores.parquet (+ model)
evaluate.py   policy knob sweep     -> results/pareto.csv     (auto-adds P6 if scores exist)
plot.py       figure + verdict      -> results/pareto.png, results/go_no_go.md
```
One-shot: `python src/run_all.py --input data/subset.jsonl`
Verify install (no GPU/data): `python src/run_all.py --synthetic`

Policies compared: P0 never, P1 always, P2 random, P3 static-coherence (the
published-baseline analogue), P4 receptivity-gated (ours), P5 value-greedy (ours),
P6 learned controller (ours). Exact knapsack **oracle** = upper bound.
`plot.py` auto-scores the pre-registered GO criteria into `results/go_no_go.md`.

## Environment notes
- Windows + Python 3.13. `pip install -r derisk/requirements.txt`.
- Only `label.py` uses the GPU (~6 GB for the 7B judge). Everything else is CPU/seconds.
- If HF gating blocks WildChat: `huggingface-cli login` + accept terms on the dataset page,
  or use `subsample.py --source file` on a local dump.

## Status / next
Critical path + trained controller complete; synthetic dry-runs pass. **Next real
step: run the pipeline on real WildChat/LMSYS data here on the 4070, then review
`results/go_no_go.md` for the real verdict.** If GO, run the calibration subset
(SETUP.md §4) before writing the paper.
