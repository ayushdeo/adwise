# De-risk go/no-go verdict (auto-generated)

**Overall: ✅ GO**

## Pre-registered criteria
- **C1 Pareto dominance** (ours beats baselines by ≥15% across ≥60% of range): **PASS** — median gain +38.5%, won at 74% of trust levels.
- **C2 Oracle gap** (ours reaches ≥70% of oracle): **PASS** — median 106% of oracle.
- **C3 Robustness across judges**: run the calibration subset (`label.py` against a hosted model) and re-run this script; compare verdicts.

## Revenue at matched trust (ours = best of P4/P5, baseline = best of P2/P3)
| trust | baseline rev | ours rev | rel. gain | % of oracle |
|---|---|---|---|---|
| 0.092 | 0.504 | 2.861 | +467.1% | 103% |
| 0.184 | 1.010 | 3.691 | +265.3% | 101% |
| 0.276 | 1.536 | 4.408 | +187.0% | 108% |
| 0.368 | 2.055 | 4.702 | +128.8% | 105% |
| 0.460 | 2.547 | 5.151 | +102.3% | 106% |
| 0.552 | 3.043 | 5.557 | +82.7% | 106% |
| 0.644 | 3.554 | 5.960 | +67.7% | 106% |
| 0.736 | 4.062 | 6.356 | +56.5% | 105% |
| 0.828 | 4.557 | 6.753 | +48.2% | 105% |
| 0.920 | 5.150 | 7.131 | +38.5% | 106% |
| 1.012 | 6.071 | 7.507 | +23.6% | 106% |
| 1.104 | 6.543 | 7.863 | +20.2% | 106% |
| 1.196 | 6.747 | 8.205 | +21.6% | 106% |
| 1.288 | 7.382 | 8.682 | +17.6% | 107% |
| 1.380 | 7.886 | 8.811 | +11.7% | 104% |
| 1.472 | 8.016 | 8.829 | +10.1% | n/a |
| 1.564 | 8.516 | 9.283 | +9.0% | n/a |
| 1.656 | 9.032 | 9.593 | +6.2% | n/a |
| 1.748 | 9.735 | 9.836 | +1.0% | n/a |

*Note:* on synthetic data this only validates the harness. The real verdict requires `cache/features.parquet` from a labeling run on real conversations.
