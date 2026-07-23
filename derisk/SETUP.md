# Setup & run on the 4070 laptop

Everything here is self-contained — copy the whole `D:\agent-monetization-research\`
folder to the laptop and run from `derisk/`. No Claude CLI needed; the VS Code
Claude extension can execute each command in the integrated terminal, or you can
run them yourself.

## 0. Prereqs (one time)
```bash
# Python 3.10+ (you have 3.13). From the derisk/ folder:
python -m pip install -r requirements.txt

# Judge model via Ollama (frozen, inference only):
#   download Ollama from https://ollama.com, then:
ollama pull qwen2.5:7b-instruct      # 4-bit, ~5-6 GB VRAM -> fits the 4070's 8 GB
ollama serve                         # exposes http://localhost:11434 (usually auto-starts)
```
VRAM check: only the 7B judge lives on the GPU (~6 GB). Embeddings/controller/plots
are CPU-only. If VRAM is tight, close other GPU apps or use `qwen2.5:3b-instruct`.

## 1. Build the data subset
```bash
# real data (needs `huggingface-cli login` + accept the dataset's terms on its HF page):
python src/subsample.py --source wildchat --n 350 --out data/subset.jsonl
# OR a local dump, no download:
python src/subsample.py --source file --input data/your_dump.json --n 350
```

## 2. Label (the only GPU-heavy, multi-hour step — resumable)
```bash
python src/label.py --input data/subset.jsonl \
    --base-url http://localhost:11434/v1 --model qwen2.5:7b-instruct --workers 4
# -> cache/features.parquet   (Ctrl-C safe; re-run to resume from cache)
```
Smoke-test first with `--make-sample data/sample.jsonl` then `--input data/sample.jsonl --limit 2`.

## 3. Evaluate + plot + verdict (seconds, CPU)
```bash
python src/evaluate.py                # -> results/pareto.csv (uses cache/features.parquet)
python src/plot.py                    # -> results/pareto.png + results/go_no_go.md
```
Open `results/go_no_go.md` — it auto-scores the pre-registered GO criteria.

## 4. C3 robustness (calibration subset, ~$5–10, optional but recommended)
```bash
# re-label a 150-200 convo subset with a stronger hosted judge:
python src/subsample.py --source file --input data/subset.jsonl --n 200 --out data/calib.jsonl
python src/label.py --input data/calib.jsonl \
    --base-url https://<hosted-endpoint>/v1 --api-key $KEY --model <strong-model> \
    --out cache/features_calib.parquet --cache cache/calib_cache.jsonl
python src/evaluate.py --features cache/features_calib.parquet --out results/pareto_calib.csv
python src/plot.py --pareto results/pareto_calib.csv \
    --png results/pareto_calib.png --verdict results/go_no_go_calib.md
# GO holds iff both verdicts agree.
```

## Verify the harness anytime (no GPU, no data)
```bash
python src/policies.py --synthetic     # sanity table
python src/evaluate.py --synthetic && python src/plot.py   # full synthetic dry-run
```

## Troubleshooting
- **`Could not load allenai/WildChat-1M`** → `huggingface-cli login`, then click "Agree and access" on the dataset's HF page. Or use `--source file`.
- **Connection refused on :11434** → `ollama serve` isn't running.
- **Slow labeling** → lower `--workers` if the GPU thrashes, or batch overnight / on Colab.
- **`ModuleNotFoundError`** → `pip install -r requirements.txt` in the active interpreter.
