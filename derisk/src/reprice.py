#!/usr/bin/env python3
"""
reprice.py — Recompute the revenue proxy from already-labeled genre fits.

Fixes the genre monoculture (docs/derisk-review-01.md F3): with raw `bid * fit/5`,
one genre (travel_experiences) both fits highest and bids high, so it wins ~91% of
slots and the revenue signal collapses to one dimension. No re-labeling needed — we
only recompute the rev_* / best_genre / best_rev columns from the existing fit_* columns.

Schemes
-------
  bids  : rev_g = bid[g] * fit_g / 5                        (original)
  lift  : rev_g = bid[g] * rank01(fit_g within genre)       (default; kills monoculture —
          rewards slots that fit a genre UNUSUALLY well vs. that genre's own baseline)
  zscore: rev_g = bid[g] * sigmoid(z(fit_g within genre))

Run
---
  python src/reprice.py                       # cache/features.parquet -> cache/features_repriced.parquet (lift)
  python src/reprice.py --scheme bids         # reproduce the original pricing
  python src/evaluate.py --features cache/features_repriced.parquet   # then re-evaluate
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

GENRES = ["hotels", "airlines", "electronics", "apparel", "food_delivery",
          "streaming", "finance", "gaming", "travel_experiences", "home_goods"]


def main() -> None:
    ap = argparse.ArgumentParser(description="Recompute revenue proxy from genre fits")
    ap.add_argument("--features", type=str, default="cache/features.parquet")
    ap.add_argument("--bids", type=str, default="cache/bids.json")
    ap.add_argument("--out", type=str, default="cache/features_repriced.parquet")
    ap.add_argument("--scheme", choices=["bids", "lift", "zscore"], default="lift")
    args = ap.parse_args()

    import numpy as np
    import pandas as pd

    df = pd.read_parquet(args.features)
    bids = json.loads(Path(args.bids).read_text(encoding="utf-8"))
    fit_cols = [f"fit_{g}" for g in GENRES if f"fit_{g}" in df.columns]
    genres = [c[len("fit_"):] for c in fit_cols]

    # per-genre transform of the fit column across all slots
    def transformed(col):
        x = df[col].to_numpy(float)
        if args.scheme == "bids":
            return x / 5.0
        if args.scheme == "lift":
            order = x.argsort().argsort()  # ranks 0..n-1
            return order / max(len(x) - 1, 1)
        # zscore -> sigmoid
        mu, sd = x.mean(), x.std() or 1.0
        return 1.0 / (1.0 + np.exp(-(x - mu) / sd))

    rev = {}
    for g, col in zip(genres, fit_cols):
        rev[g] = bids[g] * transformed(col)
        df[f"rev_{g}"] = np.round(rev[g], 4)

    R = np.vstack([rev[g] for g in genres])  # (n_genres, n_rows)
    best_idx = R.argmax(axis=0)
    df["best_genre"] = [genres[i] for i in best_idx]
    df["best_rev"] = np.round(R.max(axis=0), 4)

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(out, index=False)

    print(f"Repriced with scheme='{args.scheme}' -> {out}")
    print(f"best_rev: mean={df.best_rev.mean():.3f} std={df.best_rev.std():.3f}")
    vc = df.best_genre.value_counts()
    top = vc.iloc[0] / len(df) * 100
    print(f"best_genre concentration: top genre '{vc.index[0]}' = {top:.0f}% (was ~91% with 'bids')")
    print(vc.to_string())
    print(f"\n  next: python src/evaluate.py --features {out} && python src/plot.py")


if __name__ == "__main__":
    main()
