#!/usr/bin/env python3
"""
controller.py — Train the learned insertion controller (P6, "ours v2 trained").

Idea: behavior-clone the ORACLE. For each conversation we ask the exact knapsack
oracle which slots it inserts across a range of trust budgets; a slot's soft target
is the fraction of budgets at which the oracle picks it (≈ its value-density rank).
We train a regressor to predict that target from slot features, then use honest
out-of-fold (grouped by conversation) predictions as the policy's score. evaluate.py
then sweeps a threshold on that score to trace the learned Pareto curve.

Feature sets (--use):
  judge : receptivity, trust_hit, best_rev, max_fit, intent one-hot   (needs only features.parquet)
  emb   : context embeddings + intent one-hot                          (needs embeddings.parquet)
  both  : judge + emb                                                  (default; strongest)

Outputs:
  cache/controller.joblib          trained model (fit on all data)
  cache/controller_scores.parquet  conv_id, slot_idx, score  (out-of-fold, leakage-free)

Run
---
  python src/controller.py                      # uses cache/features.parquet (+ embeddings if present)
  python src/controller.py --use judge          # no embeddings needed
  python src/controller.py --synthetic          # self-test, no data/Ollama
"""

from __future__ import annotations

import argparse
import os
# Silence loky's noisy Win11 `wmic`-not-found core probe before sklearn imports.
os.environ.setdefault("LOKY_MAX_CPU_COUNT", str(os.cpu_count() or 4))
from pathlib import Path
from typing import List, Tuple

import policies as P

INTENTS = ["task_oriented", "exploratory", "sensitive"]
BUDGET_FRACS = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]


# ------------------------------------------------------------------ targets

def oracle_targets(df) -> "list":
    """Soft BC target per row: fraction of (per-conversation) budgets at which the
    oracle inserts this slot. Returns a list aligned to df row order."""
    import numpy as np
    target = np.zeros(len(df), dtype=float)
    df = df.reset_index(drop=True)
    for _cid, g in df.groupby("conv_id"):
        idxs = list(g.index)
        slots = [P.Slot(receptivity=float(g.loc[i, "receptivity"]),
                        trust_hit=float(g.loc[i, "trust_hit"]),
                        best_rev=float(g.loc[i, "best_rev"]),
                        max_fit=int(g.loc[i].get("max_fit", 3))) for i in idxs]
        conv = P.Conversation("c", slots)
        total = sum(s.trust_hit for s in slots) or 1e-6
        counts = np.zeros(len(slots))
        for frac in BUDGET_FRACS:
            chosen, _, _ = P.oracle_select(conv, frac * total)
            for pos in chosen:
                counts[pos] += 1
        counts /= len(BUDGET_FRACS)
        for pos, i in enumerate(idxs):
            target[i] = counts[pos]
    return target


# ------------------------------------------------------------------ features

def build_matrix(df, use: str, emb_df):
    import numpy as np
    import pandas as pd

    if "max_fit" not in df.columns:
        fit_cols = [c for c in df.columns if c.startswith("fit_")]
        df["max_fit"] = df[fit_cols].max(axis=1) if fit_cols else 3

    parts = []
    names: List[str] = []

    if use in ("judge", "both"):
        parts.append(df[["receptivity", "trust_hit", "best_rev", "max_fit"]].to_numpy(float))
        names += ["receptivity", "trust_hit", "best_rev", "max_fit"]

    # intent one-hot (always included; cheap, categorical signal)
    intent = df.get("intent", pd.Series(["task_oriented"] * len(df)))
    onehot = np.zeros((len(df), len(INTENTS)))
    for r, val in enumerate(intent):
        if val in INTENTS:
            onehot[r, INTENTS.index(val)] = 1.0
    parts.append(onehot)
    names += [f"intent_{k}" for k in INTENTS]

    if use in ("emb", "both"):
        if emb_df is None:
            raise SystemExit("--use emb/both needs cache/embeddings.parquet (run embed.py first).")
        merged = df[["conv_id", "slot_idx"]].merge(emb_df, on=["conv_id", "slot_idx"], how="left")
        emb_cols = [c for c in emb_df.columns if c.startswith("emb_")]
        E = merged[emb_cols].to_numpy(float)
        if np.isnan(E).any():
            raise SystemExit("Embeddings missing for some slots — re-run embed.py with matching data.")
        parts.append(E)
        names += emb_cols

    return np.hstack(parts), names


# ------------------------------------------------------------------ synthetic self-test data

def synthetic_features_df():
    import pandas as pd
    convs = P.make_synthetic(n_convs=150, seed=7)
    rows = []
    for c in convs:
        for j, s in enumerate(c.slots):
            rows.append({
                "conv_id": c.conv_id, "slot_idx": j,
                "receptivity": s.receptivity, "trust_hit": s.trust_hit,
                "best_rev": s.best_rev, "max_fit": s.max_fit,
                "intent": "exploratory" if s.receptivity >= 0.5 else "task_oriented",
            })
    return pd.DataFrame(rows)


# ------------------------------------------------------------------ main

def main() -> None:
    ap = argparse.ArgumentParser(description="Train the learned insertion controller")
    ap.add_argument("--features", type=str, default="cache/features.parquet")
    ap.add_argument("--embeddings", type=str, default="cache/embeddings.parquet")
    ap.add_argument("--use", choices=["judge", "emb", "both"], default="both")
    ap.add_argument("--scores-out", type=str, default="cache/controller_scores.parquet")
    ap.add_argument("--model-out", type=str, default="cache/controller.joblib")
    ap.add_argument("--folds", type=int, default=5)
    ap.add_argument("--synthetic", action="store_true")
    args = ap.parse_args()

    import numpy as np
    import pandas as pd
    from sklearn.ensemble import HistGradientBoostingRegressor
    from sklearn.model_selection import GroupKFold, cross_val_predict
    from scipy.stats import spearmanr
    import joblib

    # ---- load data
    if args.synthetic:
        df = synthetic_features_df()
        emb_df = None
        use = "judge"
        print(f"[synthetic] {len(df)} slots, {df.conv_id.nunique()} conversations (judge features).")
    else:
        fpath = Path(args.features)
        if not fpath.exists():
            raise SystemExit(f"{fpath} not found. Run label.py first (or use --synthetic).")
        df = pd.read_parquet(fpath)
        use = args.use
        emb_df = None
        if use in ("emb", "both"):
            epath = Path(args.embeddings)
            if epath.exists():
                emb_df = pd.read_parquet(epath)
            else:
                print(f"[warn] {epath} not found -> falling back to --use judge.")
                use = "judge"
        print(f"{len(df)} slots, {df.conv_id.nunique()} conversations, features='{use}'.")

    # ---- targets + matrix
    y = oracle_targets(df)
    X, names = build_matrix(df, use, emb_df)
    groups = df["conv_id"].to_numpy()

    n_groups = len(np.unique(groups))
    folds = max(2, min(args.folds, n_groups))
    gkf = GroupKFold(n_splits=folds)

    base = HistGradientBoostingRegressor(max_depth=3, learning_rate=0.08,
                                         max_iter=300, l2_regularization=1.0,
                                         random_state=0)

    # ---- honest out-of-fold scores (grouped by conversation => no leakage)
    oof = cross_val_predict(base, X, y, cv=gkf, groups=groups)
    oof = np.clip(oof, 0.0, 1.0)
    rho = spearmanr(oof, y).correlation
    mae = float(np.mean(np.abs(oof - y)))
    print(f"OOF fit vs oracle target: Spearman rho={rho:.3f}, MAE={mae:.3f}")

    # ---- final model on all data (for deployment/inspection)
    base.fit(X, y)
    Path(args.model_out).parent.mkdir(parents=True, exist_ok=True)
    joblib.dump({"model": base, "feature_names": names, "use": use}, args.model_out)

    # ---- write OOF scores for the sweep
    out = pd.DataFrame({"conv_id": df["conv_id"], "slot_idx": df["slot_idx"], "score": oof})
    out.to_parquet(args.scores_out, index=False)
    print(f"Wrote {len(out)} scores -> {args.scores_out}")
    print(f"Saved model -> {args.model_out}")

    # ---- quick sanity: learned vs value-greedy at one budget
    convs = P.load_features(Path(args.features), Path(args.scores_out)) if not args.synthetic \
        else _synth_convs_with_scores(df, oof)
    B = 1.0
    m_learn = P.evaluate(convs, P.p_learned(0.5), B)
    m_val = P.evaluate(convs, P.p_value_greedy(3.0), B)
    orc = P.evaluate_oracle(convs, B)
    print(f"\n[B={B}] learned(thr .5): rev={m_learn['mean_revenue']:.3f} trust={m_learn['mean_trust']:.3f}"
          f" | value-greedy: rev={m_val['mean_revenue']:.3f} trust={m_val['mean_trust']:.3f}"
          f" | oracle rev={orc['mean_revenue']:.3f}")
    print("  full Pareto (incl. P6_learned) -> python src/evaluate.py && python src/plot.py")


def _synth_convs_with_scores(df, oof):
    """Rebuild synthetic Conversations with learned scores attached (test path)."""
    convs = []
    df = df.reset_index(drop=True)
    row = 0
    for cid, g in df.groupby("conv_id"):
        slots = []
        for i in g.index:
            slots.append(P.Slot(receptivity=float(df.loc[i, "receptivity"]),
                                 trust_hit=float(df.loc[i, "trust_hit"]),
                                 best_rev=float(df.loc[i, "best_rev"]),
                                 max_fit=int(df.loc[i, "max_fit"]),
                                 score=float(oof[i])))
        convs.append(P.Conversation(str(cid), slots))
    return convs


if __name__ == "__main__":
    main()
