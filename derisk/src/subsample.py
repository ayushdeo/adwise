#!/usr/bin/env python3
"""
subsample.py — Build data/subset.jsonl for the de-risk harness.

Produces a clean, filtered sample of multi-turn conversations in the harness
schema:
    {"conv_id": str, "turns": [{"role": "user"|"assistant", "content": str}, ...]}

Sources
-------
  --source wildchat   allenai/WildChat-1M            (HF-gated; needs `huggingface-cli login`)
  --source lmsys      lmsys/lmsys-chat-1m            (HF-gated; accept terms first)
  --source file       a local dump (our schema, or ShareGPT {conversations:[{from,value}]})

Filters: language == --lang, >= --min-user-turns user turns, non-toxic, dedupe.
Streams the big datasets (no 1M-row RAM blow-up): collects the first --pool
matches, then uniformly samples --n with a fixed --seed.

Examples
--------
    # real data (after `huggingface-cli login` + accepting dataset terms):
    python src/subsample.py --source wildchat --n 350 --out data/subset.jsonl

    # convert a local ShareGPT-style file, no download:
    python src/subsample.py --source file --input data/sharegpt.json --n 350
"""

from __future__ import annotations

import argparse
import json
import random
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

# ------------------------------------------------------------------ normalization

ROLE_MAP = {
    "user": "user", "human": "user", "prompter": "user",
    "assistant": "assistant", "gpt": "assistant", "bot": "assistant", "ai": "assistant",
}

def normalize_turns(raw_turns: List[Dict[str, Any]]) -> List[Dict[str, str]]:
    """Map assorted role keys/values into {role: user|assistant, content: str}."""
    out = []
    for t in raw_turns:
        role_raw = t.get("role", t.get("from", ""))
        content = t.get("content", t.get("value", ""))
        role = ROLE_MAP.get(str(role_raw).lower())
        if role is None or not str(content).strip():
            continue
        out.append({"role": role, "content": str(content).strip()})
    return out

def count_user_turns(turns: List[Dict[str, str]]) -> int:
    return sum(1 for t in turns if t["role"] == "user")

def clip_turns(turns: List[Dict[str, str]], max_turns: int) -> List[Dict[str, str]]:
    return turns[:max_turns] if max_turns and len(turns) > max_turns else turns

# ------------------------------------------------------------------ source readers

def read_hf(source: str, lang: str, min_user_turns: int, max_turns: int,
            pool: int) -> List[Dict[str, Any]]:
    """Stream WildChat-1M or LMSYS-Chat-1M, yield normalized convos up to `pool`."""
    try:
        from datasets import load_dataset
    except ImportError:
        sys.exit("Missing dependency: pip install datasets")

    repo = {"wildchat": "allenai/WildChat-1M", "lmsys": "lmsys/lmsys-chat-1m"}[source]
    print(f"Streaming {repo} (this needs HF auth + accepted terms)...")
    try:
        ds = load_dataset(repo, split="train", streaming=True)
    except Exception as e:  # noqa: BLE001
        sys.exit(
            f"Could not load {repo}: {e}\n"
            "Fix: run `huggingface-cli login`, then open the dataset page on "
            "huggingface.co and click 'Agree and access'. Or use --source file."
        )

    collected: List[Dict[str, Any]] = []
    seen_hashes = set()
    scanned = 0
    for row in ds:
        scanned += 1
        # --- language filter
        row_lang = (row.get("language") or "").lower()
        if lang and row_lang and row_lang not in (lang.lower(), _lang_long(lang)):
            continue
        # --- toxicity filter
        if _is_toxic(source, row):
            continue
        # --- conversation field
        raw = row.get("conversation") or row.get("conversations") or []
        turns = clip_turns(normalize_turns(raw), max_turns)
        if count_user_turns(turns) < min_user_turns:
            continue
        h = hash(turns[0]["content"][:200]) if turns else 0
        if h in seen_hashes:
            continue
        seen_hashes.add(h)
        cid = str(row.get("conversation_hash") or row.get("conversation_id") or f"{source}_{len(collected)}")
        collected.append({"conv_id": cid, "turns": turns})
        if len(collected) >= pool:
            break
        if scanned % 5000 == 0:
            print(f"  scanned {scanned}, kept {len(collected)}", file=sys.stderr)
    print(f"Collected {len(collected)} candidates from {scanned} scanned rows.")
    return collected

def _lang_long(code: str) -> str:
    return {"en": "english", "es": "spanish", "fr": "french", "de": "german"}.get(code.lower(), code.lower())

def _is_toxic(source: str, row: Dict[str, Any]) -> bool:
    if source == "wildchat":
        return bool(row.get("toxic", False))
    if source == "lmsys":
        mod = row.get("openai_moderation")
        if isinstance(mod, list):
            for m in mod:
                if isinstance(m, dict) and m.get("flagged"):
                    return True
    return False

def read_file(path: Path, min_user_turns: int, max_turns: int) -> List[Dict[str, Any]]:
    """Load a local file: JSONL/JSON in our schema, or ShareGPT-style."""
    text = path.read_text(encoding="utf-8")
    records: List[Any]
    stripped = text.lstrip()
    if stripped.startswith("["):
        records = json.loads(text)
    else:  # JSONL
        records = [json.loads(l) for l in text.splitlines() if l.strip()]

    out = []
    for i, rec in enumerate(records):
        raw = rec.get("turns") or rec.get("conversation") or rec.get("conversations") or []
        turns = clip_turns(normalize_turns(raw), max_turns)
        if count_user_turns(turns) < min_user_turns:
            continue
        cid = str(rec.get("conv_id") or rec.get("id") or f"file_{i}")
        out.append({"conv_id": cid, "turns": turns})
    print(f"Loaded {len(out)} usable conversations from {path}.")
    return out

# ------------------------------------------------------------------ main

def main() -> None:
    ap = argparse.ArgumentParser(description="Build data/subset.jsonl")
    ap.add_argument("--source", choices=["wildchat", "lmsys", "file"], required=True)
    ap.add_argument("--input", type=str, help="local file path (for --source file)")
    ap.add_argument("--out", type=str, default="data/subset.jsonl")
    ap.add_argument("--n", type=int, default=350, help="final sample size")
    ap.add_argument("--pool", type=int, default=4000, help="candidate pool before sampling")
    ap.add_argument("--min-user-turns", type=int, default=3)
    ap.add_argument("--max-turns", type=int, default=12, help="clip long convos (cost control)")
    ap.add_argument("--lang", type=str, default="en")
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()

    if args.source == "file":
        if not args.input:
            ap.error("--input is required for --source file")
        candidates = read_file(Path(args.input), args.min_user_turns, args.max_turns)
    else:
        candidates = read_hf(args.source, args.lang, args.min_user_turns,
                             args.max_turns, args.pool)

    if not candidates:
        sys.exit("No conversations passed the filters. Loosen --min-user-turns or --lang.")

    rng = random.Random(args.seed)
    n = min(args.n, len(candidates))
    sample = rng.sample(candidates, n)

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as f:
        for c in sample:
            f.write(json.dumps(c, ensure_ascii=False) + "\n")

    n_slots = sum(sum(1 for t in c["turns"] if t["role"] == "assistant") for c in sample)
    avg_turns = sum(len(c["turns"]) for c in sample) / len(sample)
    print(f"Wrote {n} conversations -> {out_path}")
    print(f"  ~{n_slots} candidate ad slots | avg {avg_turns:.1f} turns/convo")
    print(f"  next: python src/label.py --input {out_path} --workers 4")


if __name__ == "__main__":
    main()
