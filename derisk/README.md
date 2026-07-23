# De-risk harness

Answers the go/no-go question: does a **state-dependent, budget-aware** "when to insert a sponsored suggestion" policy beat static/naive policies on a revenue-vs-trust Pareto frontier? Full spec: [`../docs/derisk-harness-spec.md`](../docs/derisk-harness-spec.md).

## Setup
```bash
pip install -r requirements.txt
# local judge (recommended on the 4070): install Ollama, then
ollama pull qwen2.5:7b-instruct     # ~4-bit, fits ~6 GB VRAM
```

## Pipeline (critical path all ✅ built & tested)
1. **`src/subsample.py`** — WildChat/LMSYS/file → `data/subset.jsonl`. ✅
2. **`src/label.py`** — frozen judge → per-slot features (`cache/features.parquet`). ✅
3. **`src/policies.py`** — P0–P5 + exact oracle knapsack. ✅
4. **`src/evaluate.py`** — knob sweep → `results/pareto.csv`. ✅
5. **`src/plot.py`** — `results/pareto.png` + auto `results/go_no_go.md`. ✅

Optional strengthening pass (not needed for go/no-go): `src/embed.py` (bge-small
per-slot embeddings) + `src/controller.py` (a *trained* P5 replacing the value-greedy
stand-in). Full run steps: [`SETUP.md`](SETUP.md).

## Quickstart (label.py)
```bash
cd derisk
# smoke test, no model needed:
python src/label.py --make-sample data/sample.jsonl
# label the sample against local Ollama:
python src/label.py --input data/sample.jsonl \
    --base-url http://localhost:11434/v1 --model qwen2.5:7b-instruct --workers 4
# -> writes cache/features.parquet  (+ cache/bids.json fixed once)
```
Key flags: `--limit N` (cap convos), `--workers` (concurrency), `--assemble-only`
(rebuild parquet from cache after editing `bids.json`), `--base-url/--api-key/--model`
(point at a hosted model for the calibration subset). The run is **resumable** —
re-running skips slots already in `cache/label_cache.jsonl`.

## features.parquet schema (per candidate ad slot)
`conv_id, slot_idx, turn_number, intent{task_oriented|exploratory|sensitive},
receptivity[0..1], trust_hit[0..1], context_chars, fit_<genre>[1..5]×10,
rev_<genre>×10, best_genre, best_rev`. Revenue = `bid[g] * fit[g]/5`, bids in `cache/bids.json`.

## Data
`subsample.py` (to write) builds `data/subset.jsonl` (300–400 English, ≥3-user-turn convos
from WildChat-1M / LMSYS-Chat-1M). Input format: one JSON per line
`{"conv_id": str, "turns": [{"role": "user"|"assistant", "content": str}, ...]}`.
