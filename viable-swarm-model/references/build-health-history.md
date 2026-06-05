# Build Health History

> Longitudinal health metrics across all fitness builds.
> **Updated by**: build-health-dashboard.py

---

## 2026-06-05 — S5 Orchestrator Iteration (R19)

### Diagnosed Constraint
**System 4* (Variety Engineer) / S4*→S5 response channel**: The `vsm_variety_engineer` has a **0% exercise rate** — no `variety-assessment.md` artifacts exist in any build directory. While `organism-vitals.py` (R8) pre-computes health metrics and algedonic signals, there is **no bridge between sensing and acting**. When organism-vitals.py reports "CRITICAL: Probationary mutations 21" or "WARNING: Skill variety 0.48," S5 must manually diagnose what to do. The variety engineer's prompt instructs it to "emit algedonic signals" and "write recommendations," but without a concrete tool for translating signals into specific actions, the S4*→S5 channel is one-way: S4* senses problems, but S5 has no structured input for decision-making. This reactive-only pattern wastes S5 cognitive capacity and delays intervention.

### Change Made
**Structural mutation R19**: Created `scripts/algedonic-action-plan.py` — an S4*→S5 response bridge.
- `algedonic-action-plan.py`: Reads organism state (mutation-state.md, hypotheses.md, skill registry, build history), identifies triggered algedonics, and generates SPECIFIC actions per signal:
  - **Mutation actions**: Lists specific demotion/promotion candidates with IDs, scores, and build counts. Skips HISTORICAL and REMOVED sections to avoid false positives.
  - **Hypothesis actions**: Categorizes untested hypotheses by domain (frontend/backend/infra/arch) and suggests specific gym batches.
  - **Variety actions**: Lists unused skills and underutilized agents with concrete spawn suggestions.
- `agents/vsm_variety_engineer.md`: Implicitly supported — the agent now has a pre-computed action plan to verify rather than inventing recommendations from scratch.
- `hooks/test-automation.sh`: Added Tests 47–48.

### Test Results
- `bash hooks/test-automation.sh`: **53 passed, 0 failed** (was 51 passed, 0 failed)
- Test 47: Action plan generates specific demotion, gym batch, and skill exercise recommendations for multi-algedonic state
- Test 48: Action plan outputs "No algedonic signals triggered" when all metrics are within thresholds

### Files Modified
- `viable-swarm-model/scripts/algedonic-action-plan.py` (created)
- `viable-swarm-model/hooks/test-automation.sh`
- `viable-swarm-model/references/mutation-state.md`
- `viable-swarm-model/references/mutation-log.md`
- `viable-swarm-model/references/build-health-history.md`

### Git Commit
- See `git log` for commit hash

### Next Highest-Leverage Constraint
**System 1 (Implementation) / S5→S1 channel**: The `vsm_backend_tester` (65% success) and `vsm_frontend_tester` (60% success) consistently time out in Tier 2+ builds. The "Adaptive Task Sizing" rule (≤500 lines) is **Tier C (prompt-only)** and agents frequently violate it under pressure. An end-to-end integration test that exercises the FULL pipeline — from Phase 0 (variety engineer) through Phase 8 (stop-verifier) — on a simulated Tier 2+ build would catch cascade failures. But more importantly, a **tool-enforced task size boundary** (e.g., a pre-flight script that counts lines in agent outputs and blocks oversized spawns) would be more reliable than prompt-only discipline. Alternatively, **System 3* (Process Audit)**: The `vsm_process_auditor` has a 60% success rate with declining scores. SM2 (process auditor HARD BLOCK) is probationary with 0 builds tested. Pre-computation (R9) helps but the agent itself still times out.

---

## 2026-06-05 — S5 Orchestrator Iteration (R18)

### Diagnosed Constraint
**System 4* (Learning Curator) / S4→S4 curation channel**: The hypothesis backlog had **23 untested hypotheses** (CRITICAL threshold > 10), but 11 were actually confirmed from fitness build evidence and never archived. Another 10 had strong build evidence (H206–H208, H210–H212, H301–H304) but still showed "untested" status because FB-era update sections appended new status lines without updating main entries or the index. The `vsm_learning_curator` agent (S4* Curation) was designed to do this work but has a **0% exercise rate**. Without autonomous curation, the organism's primary learning loop — hypothesis → experiment → confirmation → prevention rule — was clogged with stale data, producing a permanent CRITICAL algedonic that masked the true state of scientific inquiry.

### Change Made
**Structural mutation R18**: Created `scripts/hypothesis-backlog-curator.py` and applied it to clean the backlog.
- `hypothesis-backlog-curator.py`: Parses hypotheses.md, resolves the latest status per hypothesis (main entry vs FB update section), archives confirmed/rejected/superseded hypotheses to hypotheses-archive.md with full provenance, rebuilds the index, and reports remaining untested count.
- Updated 10 hypothesis statuses from "untested" → "confirmed" based on build evidence (FB25–FB32).
- Fixed stale index entries (H150, H151, H154 showed "untested" despite being confirmed).
- Fixed H213 duplicate status (was "untested" + "testing → monitor", now single "monitor" status).
- Archived 21 confirmed hypotheses to hypotheses-archive.md.
- `hooks/test-automation.sh`: Added Tests 44–46.

### Test Results
- `bash hooks/test-automation.sh`: **51 passed, 0 failed** (was 48 passed, 0 failed)
- Test 44: Curator archives confirmed hypotheses and updates index
- Test 45: Curator picks latest status from FB update section over main entry
- Test 46: Dry-run mode makes no file modifications

### Files Modified
- `viable-swarm-model/scripts/hypothesis-backlog-curator.py` (created)
- `viable-swarm-model/references/hypotheses.md`
- `viable-swarm-model/references/hypotheses-archive.md`
- `viable-swarm-model/hooks/test-automation.sh`
- `viable-swarm-model/references/mutation-state.md`
- `viable-swarm-model/references/mutation-log.md`
- `viable-swarm-model/references/build-health-history.md`

### Git Commit
- See `git log` for commit hash

### Next Highest-Leverage Constraint
**System 4* (Variety Engineer) / S4→S1 environmental scanning channel**: The `vsm_variety_engineer` still has a **0% exercise rate**. While `organism-vitals.py` (R8) pre-computes health metrics, there is no automated mechanism that acts on the algedonic signals it produces. For example, the variety assessment currently reports:
- **Skill variety: 0.48** (11/23 skills exercised) — WARNING
- **Agent variety: 0.74** (14/19 agents) — OK but 5 agents never referenced
- **19 untested hypotheses** — still WARNING (though no longer CRITICAL)

The next iteration should either (a) create a script that auto-acts on algedonic signals (e.g., spawn gym batches when untested > 7), or (b) expand the integration-test-closeout.py to include stop-verifier.sh and verify zero warnings from session-end.sh on a complete Tier 2+ mock build.

---

## 2026-06-05 — S5 Orchestrator Iteration (R17)

### Diagnosed Constraint
**System 3* (Audit/Control) / S3→S5 compliance channel**: The `stop-verifier.sh` script has 6 checks that block session completion, but **zero tests** in `test-automation.sh`. This is critical Tier A/B enforcement infrastructure. A bug in stop-verifier could either (a) prevent legitimate session stops, trapping S5 in an infinite loop, or (b) allow illegitimate stops, bypassing mandatory Phase 8 checks. The organism had invested heavily in session-end.sh testing (13 checks, 30+ tests) but completely neglected stop-verifier.sh.

### Change Made
**Refinement mutation R17**: Added test coverage for `stop-verifier.sh`.
- `hooks/test-automation.sh`: Added syntax check for stop-verifier.sh in the Preliminary section.
- Added Tests 41–43:
  - Test 41: Verifies stop-verifier **blocks** stop when `mutations-applied.md` is missing for a completed build
  - Test 42: Verifies stop-verifier **allows** stop when all required artifacts are present (mutations-applied.md, meta-report.md, process-audit.md, mutation-portfolio-review.md, mutation-state.md with build ID)
  - Test 43: Verifies stop-verifier **blocks** stop when `mutation-portfolio-review.md` is missing
- Tests mock `$HOME` to isolate from real `mutation-log.md` PENDING entries that could interfere with Check 2.

### Test Results
- `bash hooks/test-automation.sh`: **48 passed, 0 failed** (was 44 passed, 0 failed)
- Tests 41–43 verify:
  - Missing mutations-applied.md → blocked
  - All artifacts present → allowed
  - Missing portfolio-review.md → blocked

### Files Modified
- `viable-swarm-model/hooks/test-automation.sh`
- `viable-swarm-model/references/mutation-state.md`
- `viable-swarm-model/references/mutation-log.md`
- `viable-swarm-model/references/build-health-history.md`

### Git Commit
- See `git log` for commit hash

### Next Highest-Leverage Constraint
**System 1 (Implementation) / S5→S1 channel**: The `vsm_backend_coder` has an 85% success rate but still times out on 500+ line tasks. The "Adaptive Task Sizing" rule (≤500 lines) is Tier C (prompt-only) and agents frequently violate it under pressure. A tool-enforced boundary — such as a pre-flight script that estimates output size before spawning — would be more reliable than prompt-only discipline. Alternatively, **System 4→S4 channel**: The organism now has 7 pre-computation scripts, 1 orchestrator, 13 session-end checks, 6 stop-verifier checks, and 48 automation tests. There is no integration test that verifies the FULL pipeline from Phase 0 (variety engineer) through Phase 8 (stop-verifier) on a single mock build. A comprehensive end-to-end integration test would catch cascade failures across the entire workflow.

---

## 2026-06-05 — S5 Orchestrator Iteration (R16)

### Diagnosed Constraint
**System 4→S4 channel / meta-system curation gap**: The `vsm_learning_curator` agent had a 0% exercise rate, but further investigation revealed that `stop-verifier.sh` Check 6 already enforces `mutation-portfolio-review.md` for builds reaching Phase 8. The real gap was in the pre-computation script: `mutation-portfolio-health.py` computed metrics but did NOT implement the curator's "effective → historical" promotion rule. With **76 active mutations** (target < 50), the organism needed autonomous curation to reduce bloat. The script was identifying zero promotions/demotions because it only checked probationary and monitor mutations, missing the most obvious candidates: proven effective mutations with ≥5 builds tested.

### Change Made
**Refinement mutation R16**: Added the "effective → historical" promotion rule to `mutation-portfolio-health.py`.
- Added `historical_promotions_ready` field to PortfolioHealth dataclass.
- Added rule: `effective` + `builds_tested >= 5` + `score >= 4` → `historical`.
- Added Markdown output section: "Effective → Historical Promotions (Autonomous)".
- Added `--mutation-state` CLI argument for testability.
- Real scan identified **10 mutations** ready for historical promotion (e.g., FB25-S1, FB24-1, FB21-8), which would reduce active mutations from 76 to 66.

### Test Results
- `bash hooks/test-automation.sh`: **44 passed, 0 failed** (was 43 passed, 0 failed)
- Test 40 verifies:
  - Mock effective mutations with builds ≥5 and score ≥4 are flagged for historical promotion
  - Effective mutations with builds <5 are correctly excluded

### Files Modified
- `viable-swarm-model/scripts/mutation-portfolio-health.py`
- `viable-swarm-model/hooks/test-automation.sh`
- `viable-swarm-model/references/mutation-state.md`
- `viable-swarm-model/references/mutation-log.md`
- `viable-swarm-model/references/build-health-history.md`

### Git Commit
- See `git log` for commit hash

### Next Highest-Leverage Constraint
**System 3* (Audit/Control) / S3→S5 compliance channel**: The `stop-verifier.sh` script has 6 checks that block session completion, but **zero tests** in `test-automation.sh`. This is critical infrastructure with no test coverage. A bug in stop-verifier could either (a) prevent legitimate session stops, trapping S5 in an infinite loop, or (b) allow illegitimate stops, bypassing mandatory Phase 8 checks. The organism has invested heavily in session-end.sh testing (13 checks, 30+ tests) but neglected stop-verifier.sh. Adding even 3-4 tests for the most critical checks (mutations-applied.md, process-audit.md, portfolio-review.md) would close this blind spot.

---

## 2026-06-05 — S5 Orchestrator Iteration (R15)

### Diagnosed Constraint
**System 1 (Implementation) / S5→S1 channel**: The `vsm_backend_tester` (65% success) and `vsm_frontend_tester` (60% success) consistently time out in Tier 2+ builds. R10 created `test-split-orchestrator.py` to generate concrete spawn plans, but S5 must still remember to run it under time pressure. SKILL.md Phase 4 used hardcoded example domains (`test_auth.py`, `test_recipes.py`) instead of referencing the orchestrator, making splits ad-hoc and unreliable. The tester agent prompts only mentioned the orchestrator as an optional recommendation. `session-end.sh` had no check for missing `test-spawn-plan.md`, making omission invisible during closeout.

### Change Made
**Structural mutation R15**: Made test spawn plan generation mandatory for Tier 2+ builds and wired spawn plan compliance into tester agent prompts.
- `SKILL.md` Phase 4: Replaced hardcoded 3-sub-wave example with MANDATORY `test-split-orchestrator.py` invocation. S5 MUST generate `.kimi/test-spawn-plan.md` before spawning ANY tester agents.
- `agents/vsm_backend_tester.md`: Added "Spawn Plan Compliance — MANDATORY" section. Agent MUST read `.kimi/test-spawn-plan.md` and follow its domain groupings.
- `agents/vsm_frontend_tester.md`: Added "Spawn Plan Compliance — MANDATORY" section. Same requirement as backend tester.
- `hooks/session-end.sh`: Added Check 13: flags missing `test-spawn-plan.md` when `plan.md` indicates Tier 2+.

### Test Results
- `bash hooks/test-automation.sh`: **43 passed, 0 failed** (was 40 passed, 0 failed)
- New Tests 37–39 verify:
  - Tier 2 build with missing test-spawn-plan.md flagged
  - Tier 1 build with missing test-spawn-plan.md NOT flagged
  - Tier 3 build with test-spawn-plan.md present NOT flagged

### Files Modified
- `viable-swarm-model/SKILL.md`
- `viable-swarm-model/agents/vsm_backend_tester.md`
- `viable-swarm-model/agents/vsm_frontend_tester.md`
- `viable-swarm-model/hooks/session-end.sh`
- `viable-swarm-model/hooks/test-automation.sh`
- `viable-swarm-model/references/mutation-state.md`
- `viable-swarm-model/references/mutation-log.md`
- `viable-swarm-model/references/build-health-history.md`

### Git Commit
- See `git log` for commit hash

### Next Highest-Leverage Constraint
**System 4→S4 channel / meta-system curation gap**: The `vsm_variety_engineer` and `vsm_learning_curator` still have **0% empirical exercise rate** — no `variety-assessment.md` or `mutation-portfolio-review.md` artifacts exist in any build directory. Pre-computation scripts (R7, R8) generate fallback data, but the agents themselves are never spawned. The organism cannot autonomously promote/demote mutations or detect environmental drift. A SKILL.md Phase 8c-iii update making vsm_learning_curator mandatory for builds with ≥5 probationary mutations, or a session-end auto-spawn mechanism, could close this gap.

---

## 2026-06-05 — S5 Orchestrator Iteration (R14)

### Diagnosed Constraint
**System 5 (Policy/Meta-learning) channel failure / S5→S5 evaluation gap**: The `vsm_meta` agent had a **60% success rate** with declining scores (3, 3, 2). Its primary failure mode was "false TBD claims" — the agent marked metrics as "to be determined" when they were verifiable from build artifacts. This corrupted the entire cross-build learning loop: inaccurate meta-reports produced invalid hypotheses, wrong mutation scores, and misleading build health data. The agent's workload (read 10+ artifacts, run independent tests, score 12+ agents, write report) exceeded reliable completion bounds. The proven pre-computation pattern (R7–R10) had not yet been applied to meta-evaluation.

### Change Made
**Structural mutation R14**: Created `scripts/meta-metrics-precompute.py` and wired it into the vsm_meta agent prompt.
- `meta-metrics-precompute.py`: Reads all `.kimi/*.md` and `.kimi/*.log` files, extracts ground-truth metrics from 10 artifact types (phase4-gate, security-report, foundation/implementation audits, meta-report, process-audit, mutations-applied, lessons, synthesis, pytest log). Handles markdown bold syntax by stripping `**` before regex extraction. Outputs structured `.kimi/meta-metrics-precomputed.md`.
- `agents/vsm_meta.md`: Added "Pre-computed Metrics (READ FIRST)" section. vsm_meta MUST read `meta-metrics-precomputed.md` before individual artifacts. Explicit anti-TBD rule: "Do NOT claim TBD for any metric present in this file."

### Test Results
- `bash hooks/test-automation.sh`: **40 passed, 0 failed** (was 37 passed, 0 failed)
- New Tests 34–36 verify:
  - Metric extraction from mock build artifacts (test counts, security findings, BLOCKERs, lessons, mutations)
  - Rejection of nonexistent build directory
  - Graceful handling of empty `.kimi/` directory

### Files Modified
- `viable-swarm-model/scripts/meta-metrics-precompute.py` (created)
- `viable-swarm-model/agents/vsm_meta.md`
- `viable-swarm-model/hooks/test-automation.sh`
- `viable-swarm-model/references/mutation-state.md`
- `viable-swarm-model/references/mutation-log.md`
- `viable-swarm-model/references/build-health-history.md`

### Git Commit
- See `git log` for commit hash

### Next Highest-Leverage Constraint
**System 1 (Implementation) / S5→S1 channel**: The `vsm_backend_tester` (65% success) and `vsm_frontend_tester` (60% success) still time out in Tier 2+ builds despite R10's test-split-orchestrator.py. The orchestrator provides a spawn plan, but S5 must still manually execute it under time pressure. A more radical fix would be to automate the orchestrator invocation within SKILL.md Phase 4, or to add a session-end.sh check that verifies `.kimi/test-spawn-plan.md` exists for Tier 2+ builds. Alternatively, **System 4→S4 channel**: The `vsm_variety_engineer` and `vsm_learning_curator` now have pre-computation scripts (R8, R7) but still have **0% empirical exercise rate** — no `variety-assessment.md` or `mutation-portfolio-review.md` artifacts exist in any build directory. The session-end checks flag these omissions, but no agent is actually spawned to produce them. The organism still lacks autonomous curation.

---

## 2026-06-05 — S5 Orchestrator Iteration (R13)

### Diagnosed Constraint
**System 5→S1 channel / S4→S5 intelligence gap**: The `vsm_product` agent (S4 Product) had only 1 lesson mention across 26+ fitness builds, indicating it was rarely spawned. Yet H[N+1] (gym experiment) confirmed that product briefs are a proven guardrail against architect scope creep — the control architect (no brief) added an entire auth subsystem, while the treatment architect (with brief) eliminated auth entirely and produced a design with only 3 core features and 12+ explicit scope exclusions. SKILL.md only required vsm_product for "problem-oriented prompts," making it skippable for prescriptive Tier 2+ builds. Additionally, `vsm_architect.md` had no instruction to read `product-brief.md`, and `session-end.sh` had no check for missing product briefs, making underutilization invisible during closeout. A secondary issue: `session-end.sh` contained duplicate Checks 6 and 10 both testing for missing `process-audit.md`.

### Change Made
**Structural mutation R13**: Made `vsm_product` mandatory for Tier 2+ builds and wired product brief guardrails into the architect prompt and session-end closeout.
- `SKILL.md` Phase 0: Changed conditional vsm_product spawn ("if problem-oriented") to mandatory for ALL Tier 2+ builds. Prescriptive Tier 2+ prompts get a lightweight "Build Confirmation Brief" with acceptance criteria and out-of-scope list.
- `agents/vsm_architect.md`: Added "Product Brief Guardrail — MANDATORY" section. Architects must read `product-brief.md` and use its out-of-scope list as design guardrails. Missing brief for Tier 2+ is a BLOCKER-level escalation.
- `hooks/session-end.sh`: Removed duplicate Check 6 (superseded by Check 10 with auto-generation). Added Check 12: if `plan.md` indicates Tier 2+ but `product-brief.md` is missing, flag the omission as a process violation.

### Test Results
- `bash hooks/test-automation.sh`: **37 passed, 0 failed** (was 34 passed, 0 failed)
- New Tests 31–33 verify:
  - Tier 2 build with missing product-brief.md flagged
  - Tier 1 build with missing product-brief.md NOT flagged
  - Tier 3 build with product-brief.md present NOT flagged

### Files Modified
- `viable-swarm-model/SKILL.md`
- `viable-swarm-model/agents/vsm_architect.md`
- `viable-swarm-model/hooks/session-end.sh`
- `viable-swarm-model/hooks/test-automation.sh`
- `viable-swarm-model/references/mutation-state.md`
- `viable-swarm-model/references/mutation-log.md`
- `viable-swarm-model/references/build-health-history.md`

### Git Commit
- See `git log` for commit hash

### Next Highest-Leverage Constraint
**System 5 (Policy/Meta-learning) channel failure / S5→S5 evaluation gap**: The `vsm_meta` agent has a **60% success rate** with last 3 scores of 3, 3, 2. Its primary failure mode is "false TBD claims" — the agent marks metrics as "to be determined" when they are actually verifiable from build artifacts. This corrupts the entire cross-build learning loop: inaccurate meta-reports produce invalid hypotheses, wrong mutation scores, and misleading build health data. The agent's workload (read 10+ artifacts, run independent tests, score 12+ agents, write report) exceeds reliable completion bounds. The proven pre-computation pattern (R7–R10) has not yet been applied to meta-evaluation. A `scripts/meta-metrics-precompute.py` that extracts ground-truth metrics from all `.kimi/` artifacts would eliminate TBD claims by providing pre-verified data.

---

## 2026-06-05 — S5 Orchestrator Iteration (R11+R12)

### Diagnosed Constraint (R11)
**System 3* (Security Audit) → System 1 (Implementation) channel failure**: The `vsm_security` agent was **bypassed entirely in FB30** — manual audit was used instead of spawning the security agent. The session-end closeout hook had checks for missing process-audit.md, portfolio-review.md, and variety-assessment.md, but no check for missing `security-report.md`. This made the bypass invisible during closeout.

### Change Made (R11)
**Structural mutation R11**: Added Check 11 to `session-end.sh` for security gate bypass detection.
- If `meta-report.md` exists but `security-report.md` is missing AND the build contains security-relevant code, flag a **CRITICAL** process violation.
- Grep-based security surface detection across `.py`, `.ts`, `.tsx`, `.js` files.
- Static sites and builds with no security surface are correctly excluded.

### Diagnosed Constraint (R12)
**System 4→S4 channel / meta-system integration gap**: The organism has 5 closeout scripts and `session-end.sh` with 11 checks. Each is tested in isolation, but there is no integration test that exercises them together on a single mock build directory. This creates a **cascade failure risk**: a format change in `mutation-state.md` could break 3 scripts simultaneously.

### Change Made (R12)
**Structural mutation R12**: Created `scripts/integration-test-closeout.py` and added it to the automation suite.
- Runs all 4 closeout scripts sequentially on the SAME mock build directory.
- Verifies mutual consistency between script outputs.
- Runs `session-end.sh` and verifies no false CRITICAL warnings when all artifacts present.

### Test Results
- `bash hooks/test-automation.sh`: **34 passed, 0 failed** (was 30 passed, 0 failed before R11)
- Tests 27–29: Security bypass detection, static-site exclusion, existing-report exclusion
- Test 30: Full closeout pipeline integration test

### Files Modified
- `viable-swarm-model/hooks/session-end.sh` (R11: Check 11)
- `viable-swarm-model/hooks/test-automation.sh` (R11: Tests 27–29; R12: Test 30)
- `viable-swarm-model/scripts/integration-test-closeout.py` (R12: created)
- `viable-swarm-model/references/mutation-state.md`
- `viable-swarm-model/references/mutation-log.md`
- `viable-swarm-model/references/build-health-history.md`

### Git Commit
- See `git log` for commit hash

### Next Highest-Leverage Constraint
**System 5→S1 channel / S4→S5 intelligence gap**: The `vsm_product` agent (S4 Product) has only 1 lesson mention across 26+ fitness builds, suggesting it is rarely spawned. Yet H[N+1] (gym experiment) confirmed that product briefs are a proven guardrail against architect scope creep. Builds routinely skip the product brief phase because SKILL.md only requires it for "problem-oriented prompts." A session-start check for `product-brief.md` or an update to SKILL.md Phase 1 could close this gap and prevent scope creep at the source.

---

### Diagnosed Constraint
**System 3* (Security Audit) → System 1 (Implementation) channel failure / S3→S5 compliance gap**: The `vsm_security` agent was **bypassed entirely in FB30** — manual audit was used instead of spawning the security agent. This represents a critical quality gate failure: vulnerabilities that should have been caught by the security agent could have leaked into the delivered build. The session-end closeout hook had checks for missing process-audit.md, portfolio-review.md, and variety-assessment.md, but no check for missing `security-report.md`. This made the bypass invisible during closeout. Unlike process auditor timeout (addressed by R9), a security bypass has higher downstream risk because undetected auth/GraphQL/WebSocket vulnerabilities directly compromise user data and system integrity.

### Change Made
**Structural mutation R11**: Added Check 11 to `session-end.sh` for security gate bypass detection.
- `session-end.sh` Check 11: If `meta-report.md` exists (build reached Phase 8) but `security-report.md` is missing AND the build directory contains security-relevant code (auth, GraphQL, WebSocket, CORS, rate limiting), flag a **CRITICAL** process violation.
- Grep-based security surface detection across `.py`, `.ts`, `.tsx`, `.js` files with pattern groups for auth, GraphQL, WebSocket, and security middleware.
- No auto-generation fallback — security audits require human/agent judgment and cannot be safely pre-computed.
- Static sites and builds with no security surface are correctly excluded.

### Test Results
- `bash hooks/test-automation.sh`: **33 passed, 0 failed** (was 30 passed, 0 failed)
- New Tests 27–29 verify:
  - CRITICAL flag when auth code (`jwt`, `passlib`) present but security-report.md missing
  - No false positive for static HTML site with no security surface
  - No false positive when security-report.md exists alongside auth code

### Files Modified
- `viable-swarm-model/hooks/session-end.sh`
- `viable-swarm-model/hooks/test-automation.sh`
- `viable-swarm-model/references/mutation-state.md`
- `viable-swarm-model/references/mutation-log.md`
- `viable-swarm-model/references/build-health-history.md`

### Git Commit
- See `git log` for commit hash

### Next Highest-Leverage Constraint
**System 4→S4 channel / meta-system integration gap**: The organism now has 5 closeout scripts (build-health-dashboard, mutation-portfolio-health, organism-vitals, process-compliance-precompute, test-split-orchestrator) plus session-end.sh with 11 checks. Each is tested in isolation via `test-automation.sh`, but there is no integration test that exercises them together on a single mock build directory. A format change in `mutation-state.md` could break 3 scripts simultaneously; a session-end.sh bug could suppress multiple checks. A `scripts/integration-test-closeout.py` that simulates a full build closeout and verifies mutual consistency would catch these cascade failures before they reach production.

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

---

## 2026-06-05 — S5 Orchestrator Iteration (R8)

### Diagnosed Constraint
**System 4* (Variety Engineer) 0% exercise rate / S4→S1 environmental scanning channel failure**: The `vsm_variety_engineer` agent (created during 2026-06-04 audit as SM1) has never been empirically exercised. No `variety-assessment.md` artifacts exist in any build directory. Without proactive environmental scanning, the organism cannot detect systemic strain before it causes build failures. The variety engineer's algedonic thresholds — agent timeout rate > 10%, probationary mutations > 12, untested hypotheses > 7 — are designed to trigger early intervention, but without the agent being spawned, these thresholds are never checked. This creates a reactive-only organism: problems are only addressed after they cause build failures, not before.

### Change Made
**Structural mutation R8**: Created `scripts/organism-vitals.py` and wired it into the closeout pipeline.
- `organism-vitals.py`: Multi-source health scanner that reads mutation-state.md, hypotheses.md, knowledge-broker.md, build-health-history.md, and fitness build directories. Computes 7 health metrics (probationary mutations, untested hypotheses, score drop, broker age, days since build, fill rate, variety score), checks algedonic thresholds, and writes a Markdown report matching the variety-assessment-template.md format.
- `session-end.sh`: Added Check 9 — if `meta-report.md` exists but `variety-assessment.md` does not, flag the omission and auto-invoke `organism-vitals.py` to generate fallback data.
- `vsm_variety_engineer.md`: Added "Pre-computed Vitals Data (READ FIRST)" section instructing the agent to read `.kimi/organism-vitals.md` before computing metrics manually.

### Test Results
- `bash hooks/test-automation.sh`: **24 passed, 0 failed** (was 21 passed, 0 failed)
- New Tests 18–20 verify:
  - Organism vitals computation across all reference files
  - CRITICAL algedonic detection (11 untested hypotheses > 10 threshold)
  - Session-end auto-generation of organism vitals when assessment is missing
- Real organism vitals scan (2026-06-05) revealed systemic strain:
  - **15 probationary mutations** → WARNING (threshold: > 12)
  - **23 untested hypotheses** → CRITICAL (threshold: > 10)
  - **Fill rate 65.6%** → WARNING (threshold: < 75%)
  - **Variety score 0.62** → WARNING (threshold: < 0.70)
  - Agent variety: 0.74 (14/19 agents referenced) — good
  - Skill variety: 0.48 (11/23 skills exercised) — low
  - Broker age: 1 day — OK
  - Days since last fitness build: 1 — OK

### Files Modified
- `viable-swarm-model/scripts/organism-vitals.py` (created)
- `viable-swarm-model/hooks/session-end.sh`
- `viable-swarm-model/agents/vsm_variety_engineer.md`
- `viable-swarm-model/hooks/test-automation.sh`
- `viable-swarm-model/references/mutation-state.md`
- `viable-swarm-model/references/mutation-log.md`

### Git Commit
- Hash: 254f478

### Next Highest-Leverage Constraint
**System 1 (Implementation) agent timeout → S5 (Policy) overload**: The `vsm_backend_tester` (65% success rate) and `vsm_frontend_tester` (60% success rate) consistently time out in Tier 2+ builds. When testers timeout, S5 is forced to manually write tests — violating the confirmed H222 finding that prompt-only manual work caps fail under time pressure. The FB31-2 mutation (tester 3-sub-wave split) is effective but has only been tested once. The R8 organism vitals scan confirms this is a systemic pattern: agent timeout rate > 10% triggers a WARNING algedonic, yet no proactive intervention occurs because S5 is already under pressure.

A practical fix: create `scripts/test-split-orchestrator.py` that S5 runs BEFORE spawning testers. Given a list of domains/endpoints, it estimates test lines per domain and outputs a structured spawn plan with chunk sizes < 300 lines. This would make the FB31-2 3-sub-wave split concrete and repeatable, not dependent on S5's judgment under pressure.

Alternatively, **System 3* (Process Audit) timeout**: SM2 (process auditor HARD BLOCK) remains probationary with 0 builds tested. The process auditor's 10-check compliance matrix is still too large for reliable completion within timeout limits. Splitting it into 2 focused sub-tasks (core compliance + extended compliance) would improve its 60% success rate.

---

## 2026-06-05 — S5 Orchestrator Iteration (R9)

### Diagnosed Constraint
**System 3* (Process Audit) agent timeout / S3→S5 compliance channel failure**: The `vsm_process_auditor` agent has a **60% success rate** and timed out in FB30. SM2 (process auditor HARD BLOCK) is probationary with 0 builds tested. The agent's 10-check compliance matrix requires reading 15+ files across the build directory and skill references — a workload that exceeds timeout budgets in Tier 2+ builds. When the process auditor times out, Phase 8b/8c compliance checks are skipped, allowing process violations to go undetected. The session-end hook previously had no check for missing `process-audit.md`, so timeouts were invisible to S5.

### Change Made
**Structural mutation R9**: Created `scripts/process-compliance-precompute.py` and wired it into the closeout pipeline.
- `process-compliance-precompute.py`: 10-check compliance scanner that reads `.kimi/` artifacts and skill references. Computes overall compliance score (0-100) with PASS/ISSUES/FAIL per check. Emits HARD BLOCK if score < 50, ISSUES if < 80. Covers: Phase 4 gate, Phase 7 re-audit, Phase 7c security re-check, Phase 8 reflection, Phase 8b mutations, broker freshness, Phase 0 broker read, portfolio review, causal index, and stack skill references.
- `session-end.sh`: Added Check 10 — if `meta-report.md` exists but `process-audit.md` does not, flag the omission and auto-invoke `process-compliance-precompute.py` to generate fallback data.
- `vsm_process_auditor.md`: Added "Pre-computed Compliance Data (READ FIRST)" section instructing the agent to read `.kimi/process-compliance-precomputed.md` before scanning files manually. Includes explicit timeout rationale.

### Test Results
- `bash hooks/test-automation.sh`: **27 passed, 0 failed** (was 24 passed, 0 failed)
- New Tests 21–23 verify:
  - Compliance scoring across all 10 checks with mixed artifacts
  - HARD BLOCK emission for empty build directory (score 10-15/100)
  - Session-end auto-generation of compliance data when process audit is missing
- Real compliance scan (2026-06-05) on empty build directory:
  - Score: 10/100 (10.0%) → HARD BLOCK
  - All 10 checks failed except Phase 7c Security (no auth files modified)

### Files Modified
- `viable-swarm-model/scripts/process-compliance-precompute.py` (created)
- `viable-swarm-model/hooks/session-end.sh`
- `viable-swarm-model/agents/vsm_process_auditor.md`
- `viable-swarm-model/hooks/test-automation.sh`
- `viable-swarm-model/references/mutation-state.md`
- `viable-swarm-model/references/mutation-log.md`

### Git Commit
- Hash: 4440272

### Next Highest-Leverage Constraint
**System 1 (Implementation) agent timeout → S5 (Policy) overload**: The `vsm_backend_tester` (65% success rate) and `vsm_frontend_tester` (60% success rate) consistently time out in Tier 2+ builds. When testers timeout, S5 is forced to manually write tests — violating the confirmed H222 finding that prompt-only manual work caps fail under time pressure. The FB31-2 mutation (tester 3-sub-wave split) is effective but has only been tested once.

R7, R8, and R9 have now addressed the three meta-system agents (learning curator, variety engineer, process auditor) by creating pre-computation scripts that reduce their workload. The same pattern could be applied to S1 testers: create a `scripts/test-split-orchestrator.py` that analyzes the build plan and outputs a concrete spawn schedule with chunk sizes < 300 lines. This would make the FB31-2 3-sub-wave split deterministic rather than dependent on S5 judgment under pressure.

Alternatively, **System 5→S1 channel**: The `vsm_product` agent (S4 Product) has only a 1 lesson mention in the lesson patterns report, suggesting it is rarely spawned. The product brief is a proven guardrail against architect scope creep (H[N+1] confirmed), yet builds often skip it. A pre-computation script or hook check for missing `product-brief.md` could close this gap.

---

## 2026-06-05 — S5 Orchestrator Iteration (R10)

### Diagnosed Constraint
**System 1 (Implementation) agent timeout → S5 (Policy) overload**: The `vsm_backend_tester` (65% success rate) and `vsm_frontend_tester` (60% success rate) consistently time out in Tier 2+ builds. When testers timeout, S5 is forced to manually write tests — violating the confirmed H222 finding that prompt-only manual work caps fail under time pressure. The FB31-2 mutation (tester 3-sub-wave split) is effective but has only been tested once, and S5 has no concrete tool for deciding HOW to split domains. The existing "Adaptive Task Sizing" rule in tester prompts is Tier C (prompt-only) and agents frequently violate it under pressure.

### Change Made
**Structural mutation R10**: Created `scripts/test-split-orchestrator.py` and updated tester agent prompts.
- `test-split-orchestrator.py`: Deterministic domain-based test spawn planner. Accepts `--domains`, `--tier`, `--backend/--frontend`, `--max-lines`. Uses first-fit-decreasing bin packing (largest domains first) to group domains into chunks < 300 lines. Outputs Markdown spawn plan with agent type, domain groupings, estimated lines, and copy-paste task templates. Supports `--json` for programmatic consumption. Writes to `.kimi/test-spawn-plan.md` when `--build-dir` is provided.
- Heuristics derived from fitness builds FB25–FB32: auth (120), graphql (100), uploads (70), basic CRUD (50-60) for backend; auth (90), pages (60), components (50) for frontend.
- `vsm_backend_tester.md` and `vsm_frontend_tester.md`: Added explicit orchestrator tool reference in Adaptive Task Sizing section so agents can request splits with concrete data.

### Test Results
- `bash hooks/test-automation.sh`: **30 passed, 0 failed** (was 27 passed, 0 failed)
- New Tests 24–26 verify:
  - Backend multi-domain split into 2 spawns (auth/graphql/uploads = 290 lines, courses/users/recipes/ingredients = 230 lines)
  - Frontend JSON output with correct spawn count and estimated lines
  - Build-directory plan file writing
- Example plan for 7 backend domains (Tier 2):
  - Spawn 1: auth, graphql, uploads (290 lines)
  - Spawn 2: courses, users, recipes, ingredients (230 lines)

### Files Modified
- `viable-swarm-model/scripts/test-split-orchestrator.py` (created)
- `viable-swarm-model/agents/vsm_backend_tester.md`
- `viable-swarm-model/agents/vsm_frontend_tester.md`
- `viable-swarm-model/hooks/test-automation.sh`
- `viable-swarm-model/references/mutation-state.md`
- `viable-swarm-model/references/mutation-log.md`

### Git Commit
- Hash: 73fd742

### Next Highest-Leverage Constraint
**System 5→S1 channel / S4→S5 intelligence gap**: The `vsm_product` agent (S4 Product) has only 1 lesson mention across 26 fitness builds, suggesting it is rarely spawned. Yet H[N+1] (gym experiment) confirmed that product briefs are a proven guardrail against architect scope creep — the control architect (no brief) added an entire auth subsystem, while the treatment architect (with brief) eliminated auth entirely and produced a design with only 3 core features and 12+ explicit scope exclusions. Despite this strong empirical evidence, builds routinely skip the product brief phase, and the `vsm_product` agent is underutilized.

R7–R10 have now systematically addressed the meta-system timeout problem (learning curator, variety engineer, process auditor, testers) by creating pre-computation and orchestration scripts. The next frontier is upstream: ensuring the product discovery phase happens BEFORE architecture, so scope creep is prevented at the source rather than caught during audit. A session-start hook check for `product-brief.md` or an update to SKILL.md Phase 1 could close this gap.

Alternatively, **System 4→S4 channel**: The organism now has 4 pre-computation scripts (build-health-dashboard, mutation-portfolio-health, organism-vitals, process-compliance-precompute) and 1 orchestrator (test-split). None of these scripts are automatically tested in an integration sense — they run in isolation in test-automation.sh but are not exercised together in a simulated build closeout. A `scripts/integration-test-closeout.py` that runs all 5 scripts against a mock build directory and verifies their outputs are mutually consistent would catch regressions when one script's output format changes.
