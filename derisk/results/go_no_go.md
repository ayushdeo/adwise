# De-risk go/no-go verdict (auto-generated)

**Overall: ⚠️ NO-GO / investigate**

## Pre-registered criteria
- **C1 Pareto dominance** (ours beats baselines by ≥15% across ≥60% of range): **FAIL** — median gain +10.5%, won at 42% of trust levels.
- **C2 Oracle gap** (ours reaches ≥70% of oracle): **PASS** — median 88% of oracle.
- **C3 Robustness across judges**: run the calibration subset (`label.py` against a hosted model) and re-run this script; compare verdicts.

## Revenue at matched trust (ours = best of P4/P5, baseline = best of P2/P3)
| trust | baseline rev | ours rev | rel. gain | % of oracle |
|---|---|---|---|---|
| 0.092 | 0.504 | 2.861 | +467.1% | 103% |
| 0.184 | 1.010 | 2.861 | +183.1% | 78% |
| 0.276 | 1.536 | 4.409 | +187.0% | 108% |
| 0.368 | 2.055 | 4.449 | +116.4% | 100% |
| 0.460 | 2.547 | 4.449 | +74.7% | 92% |
| 0.552 | 3.043 | 4.449 | +46.2% | 85% |
| 0.644 | 3.554 | 4.449 | +25.2% | 79% |
| 0.736 | 4.062 | 4.802 | +18.2% | 79% |
| 0.828 | 4.557 | 5.203 | +14.2% | 81% |
| 0.920 | 5.150 | 5.605 | +8.8% | 83% |
| 1.012 | 6.071 | 6.025 | -0.8% | 85% |
| 1.104 | 6.543 | 6.473 | -1.1% | 88% |
| 1.196 | 6.747 | 6.922 | +2.6% | 89% |
| 1.288 | 7.382 | 7.370 | -0.2% | 91% |
| 1.380 | 7.886 | 8.711 | +10.5% | 103% |
| 1.472 | 8.016 | 8.711 | +8.7% | n/a |
| 1.564 | 8.516 | 8.908 | +4.6% | n/a |
| 1.656 | 9.032 | 9.300 | +3.0% | n/a |
| 1.748 | 9.735 | 9.836 | +1.0% | n/a |

*Note:* on synthetic data this only validates the harness. The real verdict requires `cache/features.parquet` from a labeling run on real conversations.
