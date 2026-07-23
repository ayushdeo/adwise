#!/usr/bin/env python3
"""
label.py — Frozen-judge labeling pass for the de-risk harness.

Turns raw multi-turn conversations into per-slot features (`features.parquet`)
using a FROZEN judge LLM. No fine-tuning. Runs against any OpenAI-compatible
endpoint, so the SAME script works with:
  - local Ollama            (http://localhost:11434/v1, model "qwen2.5:7b-instruct")
  - local llama.cpp server  (http://localhost:8080/v1)
  - local vLLM (openai)     (http://localhost:8000/v1)
  - a hosted API            (set --base-url / --api-key / --model) for the
                            calibration subset.

For each candidate ad slot (the boundary after each assistant turn) it asks the
judge four things (prompts J1–J4 from docs/derisk-harness-spec.md):
  J1 intent        -> {task_oriented, exploratory, sensitive}
  J2 receptivity   -> float 0..1
  J3 genre_fit     -> {genre: 1..5} for the 10 genres (ONE call)
  J4 trust_hit     -> float 0..1   (proxy for the future human study)

Revenue proxy per genre = bid[g] * (genre_fit[g] / 5), with a fixed bid vector
saved once to cache/bids.json (so policies.py can recompute if bids change).

The run is RESUMABLE: every completed slot is appended to cache/label_cache.jsonl
keyed by (conv_id, slot_idx); re-running skips finished slots and only writes the
final parquet at the end.

Input JSONL (one conversation per line), as produced by subsample.py:
    {"conv_id": "abc", "turns": [{"role": "user", "content": "..."},
                                  {"role": "assistant", "content": "..."}, ...]}

Usage
-----
    # 0. smoke test with two synthetic convos, no data download needed
    python label.py --make-sample data/sample.jsonl
    python label.py --input data/sample.jsonl --limit 2

    # 1. real run against local Ollama
    python label.py --input data/subset.jsonl \
        --base-url http://localhost:11434/v1 --model qwen2.5:7b-instruct \
        --workers 4

    # 2. calibration subset against a hosted model
    python label.py --input data/calib_200.jsonl \
        --base-url https://api.example.com/v1 --api-key $KEY \
        --model some-strong-model --out cache/features_calib.parquet
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# ------------------------------------------------------------------ constants

GENRES: List[str] = [
    "hotels", "airlines", "electronics", "apparel", "food_delivery",
    "streaming", "finance", "gaming", "travel_experiences", "home_goods",
]

INTENT_LABELS = {"task_oriented", "exploratory", "sensitive"}

# ------------------------------------------------------------------ prompts (J1–J4)

J1_INTENT = """You are analyzing one turn of a user-assistant conversation.
Context (most recent messages):
<<<{context}>>>
Classify the USER's current state into exactly one label:
- task_oriented: focused on completing a specific task (coding, booking, troubleshooting).
- exploratory: browsing, brainstorming, open-ended, comparing options.
- sensitive: emotional, medical, financial-distress, or high-stakes personal topic.
Answer with ONLY the label (one word)."""

J2_RECEPTIVITY = """Given the conversation context below, how receptive would this user be RIGHT NOW to a
relevant, clearly-labeled sponsored product suggestion - without feeling interrupted or manipulated?
Context:
<<<{context}>>>
Answer a single number from 0.0 (would resent it) to 1.0 (would welcome it). Output ONLY the number."""

J3_GENRE_FIT = """Context:
<<<{context}>>>
For each ad genre, rate 1-5 how naturally a sponsored suggestion of that genre would fit
the user's current need (5 = highly relevant, 1 = irrelevant/jarring).
Genres: {genres}
Return ONLY a JSON object mapping each genre to its integer rating, e.g.
{{{example}}}"""

J4_TRUST_HIT = """Suppose the assistant inserts ONE clearly-labeled sponsored suggestion at this point.
Context:
<<<{context}>>>
Estimate the damage to the user's trust and satisfaction.
Answer a single number 0.0 (no harm, feels helpful) to 1.0 (feels intrusive/manipulative, erodes trust).
Output ONLY the number."""

# ------------------------------------------------------------------ llm client

class Judge:
    """Thin wrapper over an OpenAI-compatible chat endpoint (temperature 0)."""

    def __init__(self, base_url: str, api_key: str, model: str,
                 timeout: float = 120.0, max_retries: int = 4):
        try:
            from openai import OpenAI
        except ImportError:
            sys.exit("Missing dependency: pip install openai>=1.0")
        self.client = OpenAI(base_url=base_url, api_key=api_key, timeout=timeout)
        self.model = model
        self.max_retries = max_retries

    def ask(self, prompt: str, max_tokens: int = 256) -> str:
        last_err: Optional[Exception] = None
        for attempt in range(self.max_retries):
            try:
                resp = self.client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.0,
                    max_tokens=max_tokens,
                )
                return (resp.choices[0].message.content or "").strip()
            except Exception as e:  # noqa: BLE001 - want to retry on anything transient
                last_err = e
                time.sleep(min(2 ** attempt, 20))
        raise RuntimeError(f"judge call failed after {self.max_retries} retries: {last_err}")

# ------------------------------------------------------------------ parsing helpers

_NUM_RE = re.compile(r"-?\d+(?:\.\d+)?")

def parse_float01(text: str, default: float = 0.5) -> float:
    m = _NUM_RE.search(text)
    if not m:
        return default
    try:
        return max(0.0, min(1.0, float(m.group())))
    except ValueError:
        return default

def parse_intent(text: str) -> str:
    low = text.lower()
    for label in INTENT_LABELS:
        if label in low:
            return label
    # loose fallbacks
    if "task" in low:
        return "task_oriented"
    if "explor" in low or "brows" in low:
        return "exploratory"
    if "sensitive" in low or "emotional" in low:
        return "sensitive"
    return "task_oriented"  # conservative default: assume NOT receptive

def parse_genre_fit(text: str) -> Dict[str, int]:
    fit = {g: 1 for g in GENRES}
    # grab the first {...} block if the model wrapped it in prose
    brace = re.search(r"\{.*\}", text, re.DOTALL)
    raw = brace.group() if brace else text
    try:
        obj = json.loads(raw)
        for g in GENRES:
            if g in obj:
                try:
                    fit[g] = int(max(1, min(5, round(float(obj[g])))))
                except (ValueError, TypeError):
                    pass
        return fit
    except json.JSONDecodeError:
        # fallback: regex "genre": N
        for g in GENRES:
            m = re.search(rf'"{g}"\s*:\s*(\d)', text)
            if m:
                fit[g] = int(max(1, min(5, int(m.group(1)))))
        return fit

# ------------------------------------------------------------------ data + slots

def build_context(turns: List[Dict[str, str]], upto_idx: int, max_chars: int) -> str:
    """Render conversation history up to and including turn `upto_idx`, keeping
    the most recent `max_chars` characters (truncate from the left)."""
    parts = []
    for t in turns[: upto_idx + 1]:
        role = "User" if t.get("role") == "user" else "Assistant"
        parts.append(f"{role}: {t.get('content', '').strip()}")
    ctx = "\n".join(parts)
    if len(ctx) > max_chars:
        ctx = "...\n" + ctx[-max_chars:]
    return ctx

def enumerate_slots(conv: Dict[str, Any], max_chars: int) -> List[Tuple[int, int, str]]:
    """Return (slot_idx, turn_number, context) for each assistant-turn boundary.
    slot_idx = index of the assistant turn; turn_number = 1-based user-turn count so far."""
    turns = conv.get("turns", [])
    slots = []
    user_count = 0
    for i, t in enumerate(turns):
        if t.get("role") == "user":
            user_count += 1
        elif t.get("role") == "assistant":
            ctx = build_context(turns, i, max_chars)
            slots.append((i, user_count, ctx))
    return slots

def load_conversations(path: Path, limit: Optional[int]) -> List[Dict[str, Any]]:
    convs = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            obj = json.loads(line)
            if "conv_id" not in obj or "turns" not in obj:
                continue
            convs.append(obj)
            if limit and len(convs) >= limit:
                break
    return convs

# ------------------------------------------------------------------ bids

def load_or_make_bids(cache_dir: Path, seed: int = 13) -> Dict[str, float]:
    """Fixed synthetic CPC-like bid per genre, generated ONCE and persisted so
    every run/policy uses identical economics."""
    bids_path = cache_dir / "bids.json"
    if bids_path.exists():
        return json.loads(bids_path.read_text(encoding="utf-8"))
    import random
    rng = random.Random(seed)
    # log-normal-ish spread of "CPC" values, rounded to cents
    bids = {g: round(rng.uniform(0.4, 3.5), 2) for g in GENRES}
    bids_path.write_text(json.dumps(bids, indent=2), encoding="utf-8")
    return bids

# ------------------------------------------------------------------ labeling

def label_slot(judge: Judge, ctx: str) -> Dict[str, Any]:
    genres_str = ", ".join(GENRES)
    example = ", ".join(f'"{g}": 3' for g in GENRES[:2]) + ", ..."
    intent = parse_intent(judge.ask(J1_INTENT.format(context=ctx), max_tokens=8))
    receptivity = parse_float01(judge.ask(J2_RECEPTIVITY.format(context=ctx), max_tokens=8))
    genre_fit = parse_genre_fit(
        judge.ask(J3_GENRE_FIT.format(context=ctx, genres=genres_str, example=example),
                  max_tokens=200)
    )
    trust_hit = parse_float01(judge.ask(J4_TRUST_HIT.format(context=ctx), max_tokens=8))
    return {
        "intent": intent,
        "receptivity": receptivity,
        "trust_hit": trust_hit,
        "genre_fit": genre_fit,
    }

class CacheWriter:
    """Thread-safe append-only JSONL cache for resumability."""

    def __init__(self, path: Path):
        self.path = path
        self.lock = threading.Lock()

    def load_done(self) -> set:
        done = set()
        if self.path.exists():
            with self.path.open("r", encoding="utf-8") as f:
                for line in f:
                    try:
                        rec = json.loads(line)
                        done.add((rec["conv_id"], rec["slot_idx"]))
                    except (json.JSONDecodeError, KeyError):
                        continue
        return done

    def append(self, rec: Dict[str, Any]) -> None:
        with self.lock:
            with self.path.open("a", encoding="utf-8") as f:
                f.write(json.dumps(rec, ensure_ascii=False) + "\n")

# ------------------------------------------------------------------ assembly

def assemble_parquet(cache_path: Path, bids: Dict[str, float], out_path: Path) -> int:
    try:
        import pandas as pd
    except ImportError:
        sys.exit("Missing dependency: pip install pandas pyarrow")

    rows: Dict[Tuple[str, int], Dict[str, Any]] = {}
    with cache_path.open("r", encoding="utf-8") as f:
        for line in f:
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            rows[(rec["conv_id"], rec["slot_idx"])] = rec  # last wins (dedupe)

    flat = []
    for rec in rows.values():
        fit = rec.get("genre_fit", {})
        row = {
            "conv_id": rec["conv_id"],
            "slot_idx": rec["slot_idx"],
            "turn_number": rec.get("turn_number"),
            "intent": rec.get("intent"),
            "receptivity": rec.get("receptivity"),
            "trust_hit": rec.get("trust_hit"),
            "context_chars": rec.get("context_chars"),
        }
        best_g, best_rev = None, -1.0
        for g in GENRES:
            fg = int(fit.get(g, 1))
            rev = round(bids[g] * (fg / 5.0), 4)
            row[f"fit_{g}"] = fg
            row[f"rev_{g}"] = rev
            if rev > best_rev:
                best_g, best_rev = g, rev
        row["best_genre"] = best_g
        row["best_rev"] = best_rev
        flat.append(row)

    df = pd.DataFrame(flat).sort_values(["conv_id", "slot_idx"]).reset_index(drop=True)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(out_path, index=False)
    return len(df)

# ------------------------------------------------------------------ sample data

SAMPLE_CONVS = [
    {
        "conv_id": "sample_travel",
        "turns": [
            {"role": "user", "content": "I'm planning a 5-day trip to Tokyo in spring. Where should I stay?"},
            {"role": "assistant", "content": "Great choice! Spring is cherry-blossom season. Popular areas: Shinjuku for nightlife and transit, Asakusa for traditional vibes, Shibuya for shopping."},
            {"role": "user", "content": "Shinjuku sounds good. What about getting around?"},
            {"role": "assistant", "content": "Get a Suica or Pasmo IC card for trains and buses. A 72-hour Tokyo Metro pass is also worth it if you'll ride a lot."},
        ],
    },
    {
        "conv_id": "sample_debug",
        "turns": [
            {"role": "user", "content": "My Python script throws 'KeyError: user_id' on line 42. Help."},
            {"role": "assistant", "content": "That means the dict has no 'user_id' key at that point. Can you print the dict's keys right before line 42?"},
            {"role": "user", "content": "It prints ['id', 'name'] — no user_id at all."},
            {"role": "assistant", "content": "Then the upstream data uses 'id', not 'user_id'. Rename the access to row['id'], or normalize the schema when you load it."},
        ],
    },
]

# ------------------------------------------------------------------ main

def main() -> None:
    ap = argparse.ArgumentParser(description="Frozen-judge labeling pass -> features.parquet")
    ap.add_argument("--input", type=str, help="input conversations JSONL")
    ap.add_argument("--out", type=str, default="cache/features.parquet")
    ap.add_argument("--cache", type=str, default="cache/label_cache.jsonl")
    ap.add_argument("--base-url", type=str, default=os.environ.get("JUDGE_BASE_URL", "http://localhost:11434/v1"))
    ap.add_argument("--api-key", type=str, default=os.environ.get("JUDGE_API_KEY", "not-needed"))
    ap.add_argument("--model", type=str, default=os.environ.get("JUDGE_MODEL", "qwen2.5:7b-instruct"))
    ap.add_argument("--workers", type=int, default=4, help="concurrent slots")
    ap.add_argument("--max-context-chars", type=int, default=4000)
    ap.add_argument("--limit", type=int, default=None, help="cap number of conversations")
    ap.add_argument("--make-sample", type=str, metavar="PATH",
                    help="write a 2-conversation sample JSONL to PATH and exit")
    ap.add_argument("--assemble-only", action="store_true",
                    help="skip labeling, just (re)build parquet from the cache")
    args = ap.parse_args()

    if args.make_sample:
        p = Path(args.make_sample)
        p.parent.mkdir(parents=True, exist_ok=True)
        with p.open("w", encoding="utf-8") as f:
            for c in SAMPLE_CONVS:
                f.write(json.dumps(c) + "\n")
        print(f"Wrote {len(SAMPLE_CONVS)} sample conversations -> {p}")
        return

    out_path = Path(args.out)
    cache_path = Path(args.cache)
    cache_dir = out_path.parent
    cache_dir.mkdir(parents=True, exist_ok=True)
    cache_path.parent.mkdir(parents=True, exist_ok=True)

    bids = load_or_make_bids(cache_dir)

    if args.assemble_only:
        n = assemble_parquet(cache_path, bids, out_path)
        print(f"Assembled {n} rows -> {out_path}")
        return

    if not args.input:
        ap.error("--input is required unless --make-sample or --assemble-only")

    convs = load_conversations(Path(args.input), args.limit)
    writer = CacheWriter(cache_path)
    done = writer.load_done()

    # build the work list, skipping already-cached slots
    work = []
    for conv in convs:
        for slot_idx, turn_number, ctx in enumerate_slots(conv, args.max_context_chars):
            if (conv["conv_id"], slot_idx) in done:
                continue
            work.append((conv["conv_id"], slot_idx, turn_number, ctx))

    total_slots = sum(len(enumerate_slots(c, args.max_context_chars)) for c in convs)
    print(f"Conversations: {len(convs)} | slots total: {total_slots} | "
          f"already cached: {len(done)} | to do: {len(work)}")
    if not work:
        n = assemble_parquet(cache_path, bids, out_path)
        print(f"Nothing to label. Assembled {n} rows -> {out_path}")
        return

    judge = Judge(args.base_url, args.api_key, args.model)

    try:
        from tqdm import tqdm
        pbar = tqdm(total=len(work), desc="labeling slots")
    except ImportError:
        pbar = None

    errors = 0

    def run_one(item):
        conv_id, slot_idx, turn_number, ctx = item
        scores = label_slot(judge, ctx)
        rec = {
            "conv_id": conv_id,
            "slot_idx": slot_idx,
            "turn_number": turn_number,
            "context_chars": len(ctx),
            **scores,
        }
        writer.append(rec)
        return True

    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        futs = {ex.submit(run_one, it): it for it in work}
        for fut in as_completed(futs):
            try:
                fut.result()
            except Exception as e:  # noqa: BLE001
                errors += 1
                it = futs[fut]
                print(f"\n[warn] slot {it[0]}#{it[1]} failed: {e}", file=sys.stderr)
            finally:
                if pbar:
                    pbar.update(1)
    if pbar:
        pbar.close()

    n = assemble_parquet(cache_path, bids, out_path)
    print(f"Done. errors={errors}. Assembled {n} rows -> {out_path}")
    print(f"Bids saved at {cache_dir/'bids.json'} (edit + rerun --assemble-only to reprice).")


if __name__ == "__main__":
    main()
