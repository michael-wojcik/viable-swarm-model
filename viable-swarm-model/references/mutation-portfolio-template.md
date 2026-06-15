# Mutation Portfolio Review Template

> **Purpose**: Output template for `vsm_learning_curator` agent.
> **Location**: `.kimi/mutation-portfolio-review.md` in build directory.

---

# Mutation Portfolio Review — [Build ID]
**Date**: [YYYY-MM-DD]
**Curator**: vsm_learning_curator

## Portfolio Health Metrics
| Metric | Value | Target | Status |
|---|---|---|---|
| Total active mutations | [N] | < 70 | [OK/WARNING/CRITICAL] |
| Probationary ratio | [N%] | < 30% | [OK/WARNING/CRITICAL] |
| Measured effect fill rate | [N%] | ≥ 80% | [OK/WARNING/CRITICAL] |
| Removal rate (last 5 builds) | [N] | ≥ 2 | [OK/WARNING/CRITICAL] |

## Promotions (Autonomous)
| Mutation ID | New Status | Rationale |
|---|---|---|
| [ID] | [effective/monitor] | [builds tested, score, evidence] |

## Removals (Require Approval)
| Mutation ID | Target Failure | Builds Tested | Score | Removal Rationale |
|---|---|---|---|---|
| [ID] | [failure] | [N] | [1–2] | [why it's ineffective] |

## Consolidations Proposed
| Primary Mutation | Secondary Mutation | Rationale | Merge Strategy |
|---|---|---|---|
| [ID] | [ID] | [overlap] | [keep primary, archive secondary] |

## Binding Recommendations
1. [Specific recommendation with evidence]

## HARD BLOCK (if applicable)
If portfolio health metrics show CRITICAL status in ≥ 2 categories:
"HARD BLOCK: Mutation portfolio is critically unhealthy. S5 MUST NOT declare build complete until [specific action] is taken."
