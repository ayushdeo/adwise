# Sync cheatsheet — moving work between the 4070 and 3050

Two machines, one repo (`github.com/ayushdeo/adwise`). Code + docs sync normally;
data/cache/results are gitignored, so run outputs must be **force-added** to share.

## After a RUN on the 4070 → send results to review
Run from `adwise/derisk`:
```bash
git add -f cache/*.parquet results/*
git commit -m "results: <short label>"
git pull --no-edit        # fold in any code/plan I pushed (won't conflict — different files)
git push
```

## Before starting work on EITHER machine → get the latest
```bash
git pull --no-edit
```

## On the 3050 (my side) → I pull your results
```bash
git pull --no-edit        # I run this after you push
```

## Notes
- `-f` is needed because `cache/` and `results/` are gitignored. Force-adding is fine;
  the files are small and text-free (scores/metrics, no conversation text).
- `label_cache*.jsonl` is the resumable scratch file — **don't** share it (large, not needed).
- Never force-add `data/*.jsonl` — those are the raw licensed conversations.
- Cleanup later: when a phase is done we can `git rm --cached` the shared artifacts.
  (Not now — it would delete them from the other machine's working tree on pull.)
```bash
# reusable one-liners
alias push-results='git add -f cache/*.parquet results/* && git commit -m "results" && git pull --no-edit && git push'
```
