#!/usr/bin/env python3
"""
embed.py — Per-slot context embeddings for the trained controller.

Reuses label.py's EXACT slot enumeration (build_context / enumerate_slots) so the
(conv_id, slot_idx) keys align 1:1 with cache/features.parquet. Embeds each slot's
context with a small sentence-transformer (default BAAI/bge-small-en-v1.5, 384-dim,
CPU-friendly) and writes cache/embeddings.parquet:

    conv_id, slot_idx, emb_0 ... emb_{d-1}

Run
---
    python src/embed.py --input data/subset.jsonl
    python src/embed.py --input data/subset.jsonl --model sentence-transformers/all-MiniLM-L6-v2
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import List

import label  # reuse the tested slot enumeration -> guarantees alignment with features


def main() -> None:
    ap = argparse.ArgumentParser(description="Per-slot context embeddings -> cache/embeddings.parquet")
    ap.add_argument("--input", type=str, required=True, help="conversations JSONL (same as label.py)")
    ap.add_argument("--out", type=str, default="cache/embeddings.parquet")
    ap.add_argument("--model", type=str, default="BAAI/bge-small-en-v1.5")
    ap.add_argument("--max-context-chars", type=int, default=4000,
                    help="MUST match label.py --max-context-chars for identical contexts")
    ap.add_argument("--batch-size", type=int, default=64)
    args = ap.parse_args()

    try:
        from sentence_transformers import SentenceTransformer
    except ImportError:
        raise SystemExit("Missing dependency: pip install sentence-transformers")
    try:
        import pandas as pd
    except ImportError:
        raise SystemExit("Missing dependency: pip install pandas pyarrow")

    convs = label.load_conversations(Path(args.input), None)

    keys: List[tuple] = []
    contexts: List[str] = []
    for conv in convs:
        for slot_idx, _turn_number, ctx in label.enumerate_slots(conv, args.max_context_chars):
            keys.append((conv["conv_id"], slot_idx))
            contexts.append(ctx)

    if not contexts:
        raise SystemExit("No slots found. Check the input file.")

    print(f"Embedding {len(contexts)} slot contexts with {args.model} ...")
    model = SentenceTransformer(args.model)  # CPU by default; auto-uses CUDA if available
    embs = model.encode(contexts, batch_size=args.batch_size,
                        show_progress_bar=True, normalize_embeddings=True)

    dim = embs.shape[1]
    data = {
        "conv_id": [k[0] for k in keys],
        "slot_idx": [k[1] for k in keys],
    }
    for j in range(dim):
        data[f"emb_{j}"] = embs[:, j]
    df = pd.DataFrame(data)

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(out, index=False)
    print(f"Wrote {len(df)} rows x {dim}-dim embeddings -> {out}")
    print("  next: python src/controller.py")


if __name__ == "__main__":
    main()
