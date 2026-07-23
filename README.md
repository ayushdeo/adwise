# Cost/Trust-Aware Monetization of Conversational Agents

Research project targeting **WWW 2027** (deadline Oct 11, 2026). We recast native-ad
insertion in multi-turn assistants as a **metareasoning** problem: an agent spends a
shared per-session **trust budget** across {think, act, answer, monetize}, deciding
*when* a sponsored suggestion is welcome vs. corrosive — with the "cost of an ad"
**measured** via a human study rather than assumed.

## Repository layout
```
docs/         research plans + de-risk harness spec
  research-deep-dive.md          landscape + candidate directions
  research-plan-combined.md      the combined thesis, whitespace, timeline
  derisk-harness-spec.md         the 2-week de-risk design + go/no-go criteria
literature/   annotated literature review + gap matrix (papers to beat)
derisk/       the de-risk experiment (see derisk/README.md, derisk/SETUP.md)
  src/        subsample -> label -> policies -> evaluate -> plot
```

## Quick start
See [`derisk/SETUP.md`](derisk/SETUP.md) for the full run on a GPU laptop.
Validate the harness with no GPU/data:
```bash
cd derisk
pip install -r requirements.txt
python src/evaluate.py --synthetic && python src/plot.py   # -> results/pareto.png + go_no_go.md
```

## Status
Critical-path harness built & tested (synthetic dry-run passes). Next: label real
WildChat/LMSYS conversations on the GPU box → real go/no-go verdict.

## Data & licensing
Raw conversations (WildChat-1M / LMSYS-Chat-1M) are **not** committed — they are
research-license / HF-gated. Regenerate locally with `derisk/src/subsample.py`.
