# Variety Assessment Template

> **Purpose**: Output template for `vsm_variety_engineer` agent.
> **Location**: `.kimi/variety-assessment.md` in build directory.

---

# Variety Assessment — [Build ID or Session ID]
**Date**: [YYYY-MM-DD]
**Engineer**: vsm_variety_engineer

## Health Metrics
| Metric | Value | Threshold | Status |
|---|---|---|---|
| Probationary mutations | [N] | > 12 | [OK/WARNING/CRITICAL] |
| Untested hypotheses | [N] | > 7 | [OK/WARNING/CRITICAL] |
| Score drop (last→current) | [N] | > 0.2 | [OK/WARNING/CRITICAL] |
| Knowledge broker age | [N days] | > 5 days | [OK/WARNING/CRITICAL] |
| Days since last fitness build | [N days] | > 5 days | [OK/WARNING/CRITICAL] |
| Measured effect fill rate | [N%] | < 75% | [OK/WARNING/CRITICAL] |
| Agent timeout rate | [N%] | > 10% | [OK/WARNING/CRITICAL] |

## Algedonic Signals
### [CRITICAL/WARNING]: [Signal Name]
**Metric**: [which metric triggered]
**Current Value**: [value]
**Threshold**: [threshold]
**Recommendation**: [specific action S5 must take]
**Blocking**: [YES/NO]

## Proactive Recommendations
1. [Recommendation with rationale]

## Cross-Skill Integration Health
| Link | Status | Evidence |
|---|---|---|
| Gym → Main | [functional/partial/broken] | [evidence] |
| Coach → Main | [functional/partial/broken] | [evidence] |
| All → Broker | [functional/partial/broken] | [evidence] |
