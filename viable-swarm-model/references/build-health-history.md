# Build Health History

> Longitudinal health metrics across all fitness builds.
> **Updated by**: build-health-dashboard.py

---

## 2026-06-05 — S5 Orchestrator Iteration (R5)

### Diagnosed Constraint
**System 3 (Audit/Control) → System 5 (Policy) channel failure**: The `auto-broker-update.sh` hook, which automates the knowledge broker update (a mandatory Phase 8d step and the #1 process violation across FB23–FB29), was silently crashing due to a `pipefail` interaction with `grep` when `mutation-log.md` existed but contained no entries for the current date. `set -euo pipefail` caused the entire script to abort before writing to the broker file or updating its timestamp. This meant S5 could not rely on broker automation, forcing manual updates that were consistently missed under time pressure.

### Change Made
**Refinement mutation R5**: Added `|| true` to two `$(...)` pipeline commands in `hooks/auto-broker-update.sh`.

### Test Results
- `bash hooks/test-automation.sh`: **13 passed, 0 failed** (was 12 passed, 1 failed)

### Git Commit
- Hash: e902f57

### Next Highest-Leverage Constraint
**System 4 (Intelligence) → System 4 (Intelligence) channel / S4 data starvation**: `references/build-health-history.md` is essentially empty. The `build-health-dashboard.py` script exists and is tested, but longitudinal health metrics have not been persisted. Without historical score trends, predictive alerts, and mutation bloat tracking, S4 agents cannot perform proactive health assessment or evidence-based adaptation.

## FB32 — 2026-06-05

- Score: 3.85
- Process: 72
- Mutations active: 65
- Hypotheses untested: 23
- Broker staleness: 1 days

---

## 2026-06-05 — S5 Orchestrator Iteration (R6)

### Diagnosed Constraint
**System 4 (Intelligence) → System 4 (Intelligence) channel / S4→S5 intelligence channel failure**: The `build-health-dashboard.py` longitudinal health recorder had four metric-accuracy bugs that produced actively misleading S4 intelligence: (1) `/100` fitness-coach scores parsed as `None`, breaking score trend calculations; (2) agent risk assessment regex captured efficiency baseline rows (e.g., "Context compactions") as CRITICAL-risk fake agents; (3) mutation bloat velocity computed `removed=0` because regex was case-sensitive against `**REMOVED**`, inflating ratio to 65.0 (CRITICAL) instead of actual ~9.3; (4) blocker count counted every string occurrence of "BLOCKER" rather than actual findings, reporting 30 blockers for FB24 when reality was 5. Additionally, the dashboard was not wired into any automated closeout hook, so `build-health-history.md` accumulated data only when manually run — which was never.

### Change Made
**Refinement mutation R6**: Fixed four accuracy bugs in `scripts/build-health-dashboard.py` and wired automatic invocation into `hooks/session-end.sh`.
- `extract_score_from_build`: Supports both `/5.0` and `/100` score formats; normalizes `/100` to `/5.0` scale.
- `get_agent_risk_assessment`: Fixed regex to stop at end of capability matrix table, excluding subsequent sections.
- `compute_mutation_bloat_velocity`: Made `removed` regex case-insensitive and explicit for `**REMOVED**` format.
- `extract_blocker_count`: Switched from naive string-count to markdown-heading-based count (`^#{1,3}.*BLOCKER`), excluding summary lines.
- `session-end.sh`: Added automatic dashboard invocation before self-healing diagnostic for every build with `plan.md`.
- `test-automation.sh`: Added 4 new tests (Tests 10–13) covering all four fixes.

### Test Results
- `bash hooks/test-automation.sh`: **17 passed, 0 failed** (was 13 passed, 0 failed)
- All dashboard metrics now match ground truth:
  - FB32 score: 3.85 (was None)
  - Agent risk: 12 actual agents only (was 15 including 3 fake agents)
  - Mutation bloat: Ratio 9.3 (was 65.0)
  - FB24 blockers: 5 (was 30)

### Files Modified
- `viable-swarm-model/scripts/build-health-dashboard.py`
- `viable-swarm-model/hooks/session-end.sh`
- `viable-swarm-model/hooks/test-automation.sh`
- `viable-swarm-model/references/mutation-state.md`
- `viable-swarm-model/references/mutation-log.md`
- `viable-swarm-model/references/build-health-history.md`

### Git Commit
- Hash: [to be filled after commit]

### Next Highest-Leverage Constraint
**System 3* (Process Audit) agent timeout and S4→S5 learning loop closure**: The `vsm_process_auditor` agent has a 60% success rate and timed out in FB30. SM2 (process auditor HARD BLOCK) is probationary and awaits measurement. Without reliable process auditing, Phase 8b/8c compliance checks are inconsistent. Additionally, the `vsm_learning_curator` (S5* Curation, Phase 8c-iii) has never been empirically exercised — no `mutation-portfolio-review.md` artifacts exist in any build directory. This means mutations are never autonomously promoted/demoted, and portfolio health is only assessed manually by S5. The next iteration should either (a) split process auditor tasks to prevent timeout, or (b) enforce learning curator spawn via a hook or stop-verifier check, or (c) both.

---

## 2026-06-05 — S5 Orchestrator Iteration (R7)

### Diagnosed Constraint
**System 3* (Process Audit) agent timeout and S4→S5 learning loop closure**: The `vsm_process_auditor` agent has a 60% success rate and timed out in FB30, leaving Phase 8b/8c compliance checks inconsistent. SM2 (process auditor HARD BLOCK) is probationary and awaits measurement. More fundamentally, the `vsm_learning_curator` (S5* Curation, Phase 8c-iii) has a **0% exercise rate** — no `mutation-portfolio-review.md` artifacts exist across 32+ fitness builds. Without portfolio review, mutations are never autonomously promoted/demoted, and the organism cannot manage its own learning rules. The S4→S5 intelligence channel is effectively one-way: S4 produces mutations, but S5* never curates them. Additionally, `session-end.sh` exited early when the telemetry directory was missing, skipping all bypass audit checks.

### Change Made
**Structural mutation R7**: Created `scripts/mutation-portfolio-health.py` and wired it into the closeout pipeline.
- `mutation-portfolio-health.py`: Parses the multi-section master mutation table from `mutation-state.md`, computes 10 portfolio health metrics (total active, probationary ratio, fill rates, removal velocity), identifies promotion/demotion candidates using the curator's own rules, and suggests consolidations for overlapping failure modes. Outputs both JSON (for machine consumption) and Markdown (for human/agent review).
- `session-end.sh`: Removed the early-exit guard on missing telemetry (which caused all audit checks to be skipped). Added Check 8: if `meta-report.md` exists but `mutation-portfolio-review.md` does not, flag the omission as a process violation AND auto-invoke `mutation-portfolio-health.py` to generate fallback data.
- `vsm_process_auditor.md`: Fixed duplicate check numbering — Causal Index is now Check 9, Stack Skill Read Compliance is now Check 10 (was also Check 9).
- `vsm_learning_curator.md`: Added "Pre-computed Portfolio Data (READ FIRST)" section instructing the agent to read `.kimi/mutation-portfolio-health.md` before computing metrics manually.

### Test Results
- `bash hooks/test-automation.sh`: **21 passed, 0 failed** (was 17 passed, 0 failed)
- New Tests 14–17 verify:
  - Portfolio metrics computation across mixed-status mutation tables
  - Promotion detection (probation + builds ≥ 3 + score ≥ 4)
  - Demotion detection (probation + builds ≥ 3 + score ≤ 2)
  - Session-end auto-generation of portfolio health when review is missing
- Real mutation-state.md parse: 67 active mutations, 15 probationary, 5 monitor, 7 removed, 0 promotions/demotions currently ready.

### Files Modified
- `viable-swarm-model/scripts/mutation-portfolio-health.py` (created)
- `viable-swarm-model/hooks/session-end.sh`
- `viable-swarm-model/agents/vsm_process_auditor.md`
- `viable-swarm-model/agents/vsm_learning_curator.md`
- `viable-swarm-model/hooks/test-automation.sh`
- `viable-swarm-model/references/mutation-state.md`
- `viable-swarm-model/references/mutation-log.md`

### Git Commit
- Hash: 5633fef

### Next Highest-Leverage Constraint
**System 1 (Implementation) agent timeout → S5 (Policy) overload**: The `vsm_backend_tester` (65% success rate) and `vsm_frontend_tester` (60% success rate) consistently time out in Tier 2+ builds. When testers timeout, S5 is forced to manually write tests — violating the S5 manual work cap (H222 confirmed: prompt-only cap fails under time pressure). The FB31 mutation FB31-2 (tester 3-sub-wave split) is effective but has only been tested once. A more robust fix would be to:
1. Create a `scripts/test-split-orchestrator.py` that automatically divides test files into chunks < 300 lines and spawns tester agents sequentially, or
2. Reduce tester agent prompt size by moving common test patterns into a shared `tester-patterns.md` reference that the agent reads on demand rather than inline.

Alternatively, **System 4→S1 channel**: The `vsm_variety_engineer` (S4* environmental scanning) has never been empirically exercised. No proactive health scans or environmental drift reports exist. This agent was created during the 2026-06-04 audit (SM1) but has a 0% exercise rate — even lower than the learning curator was. The variety engineer is meant to scan for dependency updates, framework deprecations, and ecosystem shifts that could invalidate existing skill rules. Without it, the organism operates on stale environmental assumptions.
