# Next run plan — Fork B (label-quality, reassess before committing)

Goal: find out whether **better labels change the story** (especially: does receptivity
un-compress so P4/receptivity-timing gains real power?). All cheap; no big build.
Run on the 4070, then push results back for review (`git add -A && git commit && git pull --no-edit && git push`).

## B1 — Sharper prompts on the SAME local 7B (free, ~80 min, do first)
`label.py` now uses **v2 anchored-rubric** prompts for receptivity (J2) and trust (J4)
— 6 discrete levels tied to concrete situations, to break the ~0.85 clustering.
```bash
cd derisk
# relabel into a fresh cache so we can compare against the v1 run:
python src/label.py --input data/subset.jsonl --workers 4 \
    --out cache/features_v2.parquet --cache cache/label_cache_v2.jsonl
```
Then eyeball whether receptivity/trust spread out:
```bash
python - <<'PY'
import pandas as pd, numpy as np
for tag,f in [("v1","cache/features.parquet"),("v2","cache/features_v2.parquet")]:
    d=pd.read_parquet(f)
    print(tag, "receptivity std=%.3f nunique=%d | trust std=%.3f"%(
        d.receptivity.std(), d.receptivity.nunique(), d.trust_hit.std()))
PY
```
**Read:** if v2 receptivity std jumps (say >0.20) and spreads across levels, the flatness
was a prompt problem (free fix). If still clustered, it's a model-capacity problem → B3.

## B2 — Genre reprice (free, seconds) — remove the travel monoculture
```bash
python src/reprice.py --scheme lift --features cache/features_v2.parquet \
    --out cache/features_v2_repriced.parquet
```
(Already validated: top-genre share drops 91% -> ~50%, core result held.)

## B3 — Calibration subset with a STRONGER judge (~$5–10, needs an API key)
Only if B1 didn't fix receptivity, or for the C3 robustness check.
```bash
python src/subsample.py --source file --input data/subset.jsonl --n 180 --out data/calib.jsonl
python src/label.py --input data/calib.jsonl \
    --base-url https://<hosted-endpoint>/v1 --api-key <KEY> --model <strong-model> \
    --out cache/features_calib.parquet --cache cache/calib_cache.jsonl
```
Compare receptivity spread + re-evaluate on the overlap.

## Evaluate any variant (operating-regime metric is now the default)
```bash
python src/evaluate.py --features cache/features_v2_repriced.parquet \
    --scores cache/_none.parquet --out results/pareto_v2.csv
python src/plot.py --pareto results/pareto_v2.csv --png results/pareto_v2.png \
    --verdict results/go_no_go_v2.md            # scores trust <= 0.7; tail reported separately
```

## What we're deciding at reassess
- Did receptivity spread (B1/B3)? If yes → the receptivity-timing thesis is alive and P4
  should climb above the baselines. If no → drop receptivity as a headline; lean on the
  sequential/budget contribution (Fork A) instead.
- Does genre diversity (B2) change anything? (Already: no — result robust.)
- Net: decide whether the paper's spine is "receptivity-aware timing" or "online sequential
  budgeted control", and whether to green-light Fork A.

## Note on the go/no-go metric
`plot.py` now scores the **operating regime (trust ≤ 0.7/session)** and reports the
saturated tail separately. On the existing emb run this reads **GO, +127% median gain** —
the earlier "NO-GO" was a full-range averaging artifact (see docs/derisk-review-02.md).
