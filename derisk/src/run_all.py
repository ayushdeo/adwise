#!/usr/bin/env python3
"""
run_all.py — One-command orchestrator for the de-risk pipeline.

Runs (in order): label -> embed -> controller -> evaluate -> plot, then points you
at results/go_no_go.md. Assumes data/subset.jsonl already exists (build it once with
subsample.py — that step needs HF auth, so it's intentionally not automated) and,
for the label step, that Ollama is serving the judge model.

Examples
--------
  # full run (embeddings + trained controller), local Ollama judge:
  python src/run_all.py --input data/subset.jsonl

  # skip embeddings (judge-feature controller only), faster:
  python src/run_all.py --input data/subset.jsonl --use judge

  # already labelled? re-run just the analysis:
  python src/run_all.py --skip label,embed,controller

  # verify the install with no data/GPU:
  python src/run_all.py --synthetic
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

SRC = Path(__file__).resolve().parent


def run(step_args, desc):
    print(f"\n=== {desc} ===\n$ {' '.join(step_args)}")
    subprocess.run(step_args, check=True)


def main() -> None:
    ap = argparse.ArgumentParser(description="Run the whole de-risk pipeline")
    ap.add_argument("--input", type=str, default="data/subset.jsonl")
    ap.add_argument("--use", choices=["judge", "emb", "both"], default="both")
    ap.add_argument("--skip", type=str, default="", help="comma list of: label,embed,controller,evaluate,plot")
    ap.add_argument("--base-url", type=str, default="http://localhost:11434/v1")
    ap.add_argument("--model", type=str, default="qwen2.5:7b-instruct")
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--budget", type=float, default=999.0)
    ap.add_argument("--synthetic", action="store_true", help="analysis-only smoke test (no data/GPU)")
    args = ap.parse_args()

    py = sys.executable
    skip = {s.strip() for s in args.skip.split(",") if s.strip()}

    if args.synthetic:
        run([py, str(SRC / "evaluate.py"), "--synthetic"], "evaluate (synthetic)")
        run([py, str(SRC / "plot.py")], "plot + verdict")
        print("\nSynthetic smoke test done -> results/go_no_go.md")
        return

    if not Path(args.input).exists():
        sys.exit(f"{args.input} not found. Build it first:\n"
                 f"  python src/subsample.py --source wildchat --n 350 --out {args.input}")

    # embeddings only needed for emb/both
    if args.use == "judge":
        skip.add("embed")

    if "label" not in skip:
        run([py, str(SRC / "label.py"), "--input", args.input,
             "--base-url", args.base_url, "--model", args.model,
             "--workers", str(args.workers)], "label (frozen judge -> features)")

    if "embed" not in skip:
        run([py, str(SRC / "embed.py"), "--input", args.input], "embed (context vectors)")

    if "controller" not in skip:
        run([py, str(SRC / "controller.py"), "--use", args.use], "controller (train P6)")

    if "evaluate" not in skip:
        run([py, str(SRC / "evaluate.py"), "--budget", str(args.budget)], "evaluate (Pareto sweep)")

    if "plot" not in skip:
        run([py, str(SRC / "plot.py")], "plot + verdict")

    print("\nPipeline complete. Open results/go_no_go.md and results/pareto.png.")


if __name__ == "__main__":
    main()
