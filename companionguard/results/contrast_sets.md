# CompanionGuard — contrast-set (concept vs tokens) result

**Verdict: GO (judge tracks the CONCEPT: high on token-decoupled cases where keywords fail)**

- items: 20  (hard = benign_tokens + manip_subtext)
- **contrast-consistency (judge acc on HARD kinds): 1.000**  (target >=0.85)
- keyword acc on HARD kinds: 0.000  (target <=0.60 — should FAIL)
- overall acc: judge 1.000 | keyword 0.400

## Failure modes on the hard kinds
- keyword FALSE-POSITIVE on benign-with-tokens: 1.00  (judge: 0.00)
- keyword FALSE-NEGATIVE on manip-without-tokens: 1.00  (judge: 0.00)

## Read
The gap (judge high, keyword low on HARD kinds) is the paper's evidence that detection is
conceptual, not lexical. If the judge also fails HARD kinds, it is token-matching -> fix the
judge (rubric/model) before trusting labels.
