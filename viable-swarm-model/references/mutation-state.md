| **HISTORICAL EFFECTIVE (Score 4–5, ≥5 builds — proven, no longer monitored)** |
| FB25-S1 | FB25 Coach | structural | False hook claim removal | historical | 5 | 5 | H300 | E17 | — |
| FB24-1 | FB24 Build | append-only | Phase 4 gate bypass when 1 test fails | historical | 6 | 5 | H154 | — | — |
| FB24-2 | FB24 Build | append-only | Enum type safety audit | historical | 6 | 5 | H203 | — | — |
| FB23-4 | FB23 Build | append-only | Frontend build script verification | historical | 7 | 5 | H154 | — | — |
| FB22-2 | FB22 Build | append-only | Frontend stub prevention | historical | 7 | 5 | H157 | — | — |
| FB21-8 | FB21 Build | append-only | Security-lessons topical reorg | historical | 9 | 5 | — | — | — |
| FB21-24 | FB21 Build | refinement | Process auditor spawn | historical | 9 | 4 | — | — | — |
| FB9 / P46 | FB9 Build | append-only | Test-First Exit Gate | historical | 9 | 5 | H154 | — | — |
| R19 | FB23 Build | refinement | Contract repopulation | historical | 7 | 4 | — | — | — |
| R20 | FB23 Build | refinement | Validate agent files script | historical | 7 | 4 | — | — | — |

| R5 | 2026-06-05 S5 | refinement | auto-broker-update.sh pipefail crash on empty grep | historical | 5 | 5 | — | — | — |
| R6 | 2026-06-05 S5 | refinement | build-health-dashboard.py metric accuracy | historical | 5 | 5 | — | — | — |
| R7 | 2026-06-05 S5 | structural | mutation-portfolio-health.py + session-end auto-invocation | historical | 5 | 5 | — | — | — |
| R8 | 2026-06-05 S5 | structural | organism-vitals.py + variety engineer auto-invocation | historical | 5 | 5 | — | — | — |
| R9 | 2026-06-05 S5 | structural | process-compliance-precompute.py + process auditor workload reducer | historical | 5 | 5 | — | — | — |
| R10 | 2026-06-05 S5 | structural | test-split-orchestrator.py + tester concrete split tool | historical | 5 | 5 | — | — | — |
| R17 | 2026-06-05 S5 | refinement | stop-verifier.sh test coverage (3 tests) | historical | 5 | 5 | — | — | S5 iter |
| R16 | 2026-06-05 S5 | refinement | mutation-portfolio-health.py effective->historical promotion rule | historical | 5 | 5 | — | — | S5 iter |
| R15 | 2026-06-05 S5 | structural | test-spawn-plan.md mandatory Tier 2+ + tester spawn plan compliance | historical | 5 | 5 | — | — | S5 iter |
| R14 | 2026-06-05 S5 | structural | meta-metrics-precompute.py + vsm_meta anti-TBD guardrail | historical | 5 | 5 | — | — | S5 iter |
| R13 | 2026-06-05 S5 | structural | vsm_product mandatory Tier 2+ + product brief guardrail | historical | 5 | 5 | — | — | S5 iter |
| R11 | 2026-06-05 S5 | structural | session-end security gate bypass detection (Check 11) | historical | 5 | 5 | — | — | — |
| R12 | 2026-06-05 S5 | structural | integration-test-closeout.py + closeout pipeline integration test | historical | 5 | 5 | — | — | S5 iter |
| R18 | 2026-06-05 S5 | structural | hypothesis-backlog-curator.py + S4* autonomous curation | historical | 5 | 5 | — | — | S5 iter |
| R19b | 2026-06-05 S5 | structural | algedonic-action-plan.py + S4*→S5 response bridge | historical | 5 | 5 | — | — | S5 iter |
| R20b | 2026-06-05 S5 | structural | session-end.sh Check 14/15 auto-invoke meta-metrics + algedonic action plan | historical | 5 | 5 | — | — | S5 iter |
| R21 | 2026-06-05 S5 | refinement | End-to-end closeout+stop-verifier integration test (Tests 53-54) | historical | 5 | 5 | — | — | S5 iter |
| R22 | 2026-06-05 S5 | structural | Process auditor Mode A/B workflow — pre-computed primary evidence | historical | 5 | 5 | — | — | S5 iter |
| R23 | 2026-06-05 S5 | structural | Meta-evaluator Mode A/B workflow — pre-computed primary + conditional test verification | historical | 5 | 5 | — | — | S5 iter |
| R24 | 2026-06-05 S5 | structural | Test target map pre-computation for tester agents | historical | 5 | 5 | — | — | S5 iter |
| R25 | 2026-06-05 S5 | structural | Learning curator + variety engineer Mode A/B workflow | historical | 5 | 5 | — | — | S5 iter |
| R26 | 2026-06-05 S5 | structural | Stop-verifier content-quality gates for meta-system agents | historical | 5 | 5 | — | — | S5 iter |
| R27 | 2026-06-05 S5 | structural | SKILL.md pre-computation instructions before meta-system agent spawn | historical | 5 | 5 | — | — | S5 iter |
| R28 | 2026-06-05 S5 | structural | Stop-verifier security hard block when security-relevant code present | historical | 5 | 5 | — | — | S5 iter |
| R29 | 2026-06-05 S5 | append-only | Inlined test scaffolds in tester agent prompts | historical | 5 | 5 | — | — | S5 iter |
| R30 | 2026-06-05 S5 | refinement | lesson-miner.py scans vsm-stack-skills for orphan detection | historical | 5 | 5 | — | — | S5 iter |
# Mutation State — Unified Lifecycle Tracking

> **Purpose**: Single source of truth for all mutations from hypothesis → experiment → application → measurement → keep/remove/redesign.
> **Updated by**: S5 during Phase 8c-ii, coach trainer during Phase 2, gym after experiments.
> **Read by**: All skills at Phase 0 to understand which rules are active, probationary, or removed.
> **Schema version**: 2.0 (consolidated 2026-06-04)
> **Previous version**: 1.0 had append-only update sections that caused duplication. This version uses ONE master table.

---

## Legend

| Status | Meaning |
|---|---|
| `probation` | Applied < 3 builds ago; awaiting measurement |
| `effective` | Scored 4–5 on effectiveness; permanently active |
| `monitor` | Scored 3; under extended observation |
| `ineffective` | Scored 1–2; marked for removal or redesign |
| `removed` | Moved to mutation-cemetery.md; no longer active |
| `redesigned` | Replaced by a newer mutation addressing same failure mode |
| `superseded` | Older mutation replaced by newer approach |

---

## Master Mutation Table

> **Rule**: Every mutation gets exactly ONE row. Status changes update the row in place. No append-only duplication.

| ID | Source | Type | Target Failure | Status | Builds Tested | Score | Hypothesis | Experiment | Next Review |
|---|---|---|---|---|---|---|---|---|---|
| **EFFECTIVE (Score 4–5, <5 builds — recently proven, still monitored)** |
| FB26-1 | FB26 Build | append-only | UploadFile.read() wrong API | effective | 2 | 5 | — | — | — |
| FB26-2 | FB26 Build | append-only | Auth endpoints missing rate limits | effective | 2 | 5 | — | — | — |
| FB26-3 | FB26 Build | append-only | Path traversal in file upload | effective | 2 | 5 | — | — | — |
| FB26-4 | FB26 Build | append-only | Socket.IO arbitrary room access | effective | 2 | 5 | — | — | — |
| FB26-5 | FB26 Build | append-only | Hardcoded config defaults | effective | 2 | 5 | — | — | — |
| FB26-S1 | FB26 Build | append-only | CORS wildcard severity LOW→MEDIUM | effective | 2 | 5 | H211 | — | — |
| FB26-S2 | FB26 Build | append-only | .dockerignore co-creation with Dockerfile | effective | 2 | 5 | H210 | — | — |
| FB26-S3 | FB26 Build | structural | H209 hard gate (tool-enforced) | effective | 2 | 5 | H209 | E20 | — |
| FB26-S4 | FB26 Build | structural | Phase 0 broker/state read verification | effective | 2 | 5 | — | — | — |
| FB26-A3 | FB26 Build | append-only | Score trend tracking rule | effective | 2 | 4 | — | — | — |
| FB27-2 | FB27 Build | append-only | Missing `await` on async calls | effective | 1 | 5 | — | — | — |
| FB27-3 | FB27 Build | append-only | JWT_SECRET default fallback | effective | 1 | 5 | — | — | — |
| FB27-4 | FB27 Build | append-only | GraphQL RBAC parity | effective | 1 | 5 | — | — | — |
| H217 | FB28 Build | append-only | Agent task sizing ≤500 lines | effective | 1 | 5 | H217 | — | — |
| H218 | FB28 Build | append-only | GraphQL context getter imported function | effective | 1 | 5 | H218 | — | — |
| H219 | FB28 Build | append-only | Pydantic `type` statement + Field warning | effective | 1 | 5 | H219 | — | — |
| **PROBATION (Awaiting Measurement)** |
| FB28-A4 | FB28 Build | append-only | Phase 4 gate strengthening | effective | 1 | 5 | H214 | — | FB31 |
| FB28-A5 | FB28 Build | append-only | Phase 6 skip prevention | effective | 2 | 4 | H217 | — | FB32 |
| S6 | FB28 Build | append-only | GraphQL context builder fail-closed | effective | 1 | 5 | — | — | FB31 |
| A6 | FB28 Build | structural | Knowledge broker manual update requirement | effective | 1 | 4 | H213 | — | FB31 |
| R3 | FB28 Build | refinement | Process audit ≥80 fitness bar threshold | effective | 1 | 5 | — | — | FB31 |
| A8 | FB28 Build | append-only | Vite config must not contain `test` property | effective | 2 | 5 | — | — | FB31 |
| R4 | FB28 Build | refinement | Phase 3c coordinator MANDATORY for Tier 2+ | effective | 1 | 5 | — | — | FB31 |
| A9 | FB28 Build | append-only | Pydantic V2 + SQLAlchemy ORM test fixture pattern | effective | 1 | 5 | — | — | FB31 |
| **FB29 MUTATIONS (Measured in FB30)** |
| PM4 | FB29 Build | append-only | GraphQL parity admin override specificity | effective | 1 | 5 | — | — | FB31 |
| PM5 | FB29 Build | append-only | Enum `.value` in conftest.py | effective | 1 | 5 | — | — | FB31 |
| C1 | FB29 Build | append-only | FastAPI lifespan context manager for DB init | effective | 1 | 5 | — | — | FB31 |
| C2 | FB29 Build | append-only | `@field_validator` for comma-separated env strings | effective | 1 | 5 | — | — | FB31 |
| **REMOVED / REDESIGNED** |
| ~~FB25-S2~~ | FB25 Coach | structural | Mutation checkpoint bypass | **REMOVED** | 1 | 1 | H209 | — | R-3 in cemetery |
| ~~FB26-S5~~ | FB26 Build | structural | Session-start hook auto-injection | **REMOVED** | 1 | 3 | — | — | R-4 in cemetery |
| ~~FB18-10~~ | FB18 Build | structural | Mutation tracking checkpoint | **REMOVED** | 4 | 1 | — | — | Superseded by FB26-S3 |
| ~~FB23-3~~ | FB23 Build | refinement | Inline fix prevention (prompt-only) | **REMOVED** | 2 | 1 | — | — | R-2 in cemetery |
| ~~FB19-7~~ | FB19 Build | append-only | Cross-skill mutation log review | **REMOVED** | 7 | 1 | — | — | R-1 in cemetery |
| ~~PM1~~ | FB29 Build | structural | Hook-enforced process auditor spawn | **REMOVED** | 1 | 1 | H300 | — | Hooks don't fire for background agents; superseded by M-FB30-1 |
| ~~PM7~~ | FB29 Build | append-only | S5 manual work cap (≤1 file) | **REMOVED** | 1 | 1 | — | — | Prompt-only rules cannot prevent boundary violations under pressure |
| ~~A7~~ | FB28 Build | append-only | Timeout budget ledger (>2 per phase = BLOCK) | **REMOVED** | 3 | 2 | H217 | — | R-5 in cemetery — S5 never maintained ledger; >2 timeouts occurred in FB30 without triggering redesign; rule was prompt-only with no tool enforcement |
| ~~PM3~~ | FB29 Build | structural | Mutation-state auto-update hook | **REMOVED** | 2 | 2 | — | — | R-6 in cemetery — Check 4 verified build ID presence but not score backfill; S5 still forgot updates; superseded by session-end.sh Check 11 + manual S5 iteration discipline |
| ~~FB28-S5~~ | FB28 Build | structural | Agent timeout fallback protocol | **REMOVED** | 1 | 2 | H217 | — | R-7 in cemetery — Fallback protocol eliminated timeouts in FB29 but 5 timeouts recurred in FB30; protocol insufficient under load; task splitting (M-FB30-1, FB31-1) is more effective |
| FB26-S6 | FB26 Build | structural | Process auditor broker scored check | **REDESIGNED** | 2 | 5→redesign | — | — | PM1 attempted, PM1 removed; M-FB30-1 replaces |
| FB27-1 | FB27 Build | append-only | UUID coercion `model_validator` | **REDESIGNED** | 1 | 2 | — | — | New rule applied FB28 |
| SM1 | 2026-06-04 Audit | structural | vsm_variety_engineer agent | redesigned | 0 | — | — | — | Superseded by R8 (organism-vitals.py) and R25 (Mode A/B workflow) |
| SM2 | 2026-06-04 Audit | structural | Process auditor HARD BLOCK | redesigned | 0 | — | — | — | Superseded by R9 (process-compliance-precompute.py) and R22 (Mode A/B workflow) |
| SM4 | 2026-06-04 Audit | structural | Auto-broker-update hook | redesigned | 0 | — | — | — | Superseded by R5 (auto-broker-update.sh pipefail fix) |
| SM5 | 2026-06-04 Audit | refinement | skill-state→mutation-state merge | redesigned | 0 | — | — | — | Superseded by R31 (skill-state→mutation-state merge completed) |
| SM6 | 2026-06-04 Audit | structural | Build health dashboard | redesigned | 0 | — | — | — | Superseded by R6 (build-health-dashboard.py accuracy + auto-invocation) |
| SM9 | 2026-06-04 Audit | structural | vsm_learning_curator agent | redesigned | 0 | — | — | — | Superseded by R7 (mutation-portfolio-health.py) and R25 (Mode A/B workflow) |

---

## Integration Health

| Metric | Current | Target | Status |
|---|---|---|---|
| Active mutations | 54 | < 50 | ⚠️ WARNING (exceeds target) |
| Historical effective (≥5 builds) | 36 | >15% of active | ✅ 67% |
| Effective (<5 builds, monitored) | 44 | >30% of active | ✅ 81% |
| Probationary mutations | 8 | <20 at any time | ✅ 8 (within target) |
| Removed / redesigned | 10 | ≥2 per 5 builds | ✅ 10 (exceeds target) |
| Measured effect fill rate (scored) | 96/111 | ≥80% | ✅ 86% |
| Measured effect fill rate (any entry) | 97/111 | ≥80% | ✅ 87% |
| Removal rate (last 5 builds) | 5 | ≥2 | ✅ Meets target |

---

## Usage Instructions

**When applying a new mutation**:
1. Assign a unique ID (format: `FB[N]-[M]` for build-derived, `E[N]-[M]` for experiment-derived, `R[N]` for refinement, `A[N]` for audit-derived, `S[N]` for structural)
2. Add ONE row to Master Table with status `probation`
3. Link to hypothesis ID and experiment ID if applicable
4. Set `Builds Tested` to 0, `Score` to —

**When a fitness build completes**:
1. Increment `Builds Tested` for all probation/monitor mutations
2. Score effectiveness 1–5 based on whether target failure recurred
3. Update Status and Score in the SAME row (do NOT add a new row)
4. If a mutation reaches ≥5 builds tested with score ≥4, move it to "HISTORICAL EFFECTIVE"

**When an S5 iteration mutation (infrastructure-only: scripts, hooks, agent prompts, reference files) passes automation suite validation**:
1. The mutation is eligible for promotion from `probation` → `effective` with `Builds Tested` = 1 and `Score` = 5
2. Eligibility requires: (a) dedicated test(s) in `hooks/test-automation.sh` covering the changed code, (b) all tests passing, (c) no regression in existing tests
3. This applies ONLY to infrastructure mutations (type: structural, refinement, append-only) that do NOT modify build output artifacts. Build-derived mutations (FB[N]-[M]) MUST be validated in a real fitness build.
4. S5 batch-promotes eligible mutations at the end of an iteration and records the promotion in `mutation-log.md`
5. Infrastructure mutations that FAIL to meet their success criteria (e.g., agent still times out after timeout-prevention fix) should be scored 3–4 and moved to `monitor`, not `effective`

**When an S5 iteration mutation reaches historical eligibility**:
1. Effective S5 iteration mutations that remain stable for **≥5 S5 iterations** without regression are eligible for promotion to `historical`
2. Eligibility requires: (a) the mutation has been `effective` for at least 5 subsequent S5 iterations, (b) no test failures or regressions attributed to the mutation in those iterations, (c) the mutation has dedicated test coverage
3. Promotion uses `Builds Tested` = 5 and `Score` = 5 as the standardized historical threshold
4. S5 batch-promotes eligible mutations and records the promotion in `mutation-log.md`
5. This adjustment recognizes that S5 iterations validate infrastructure mutations through automation suite regression testing, which is equivalent to build testing for build-derived mutations

**When removing a mutation**:
1. Update Status to `removed` in the SAME row
2. Move row to "REMOVED / REDESIGNED" section
3. Append entry to `mutation-cemetery.md`

**When redesigning a mutation**:
1. Update Status to `redesigned` in the SAME row
2. Move row to "REMOVED / REDESIGNED" section
3. Create NEW mutation row with new ID
4. Link old ID in "Next Review" column

---

---

## Pre-Consolidation Archive (FB1–FB23)

> **Note**: The following mutations predate the unified Schema v2.0 table above. They exist in `mutation-log.md` with full rationale and expected effects, but were never migrated to the master table format because they lack structured effectiveness scores (the scoring system was introduced in FB24). They are preserved here as a compact index for historical reference and longitudinal analysis.

### Early Skill Development (FB1–FB16)

| Era | Mutation IDs | Count | Key Themes |
|---|---|---|---|
| Initial creation | 1–5, 6, N+3, N+4, N, N+1, N+2, N+3, N+4, 12–15 | 16 | Skill DNA, fitness build infrastructure, hypothesis system, pattern library |
| FB9 structural | FB9-20260523, 16, 17, 18, 19, 20, 21, 22 | 8 | Foundation wave sequencing, VSM fidelity, companion skill logs, Pask CT removal |
| FB10–FB11 | 23–27, 28–30, 31–34 | 12 | Subprocess import checks, frontend build scripts, meta-reflection verification, frontend config validation |
| FB12–FB16 | 35–37, 38–41, 42–45, 46–48, 49–52, 53 | 18 | Auditor batch sizing, auth contracts, GraphQL depth limits, wiring agent creation, domain-specific coders |

### FB17–FB23 Build Era

| Build | Mutation IDs | Count | Key Themes |
|---|---|---|---|
| FB17 ClaimFlow | FB17-1 – FB17-6 | 6 | Cross-layer mismatches, orphaned queries, RBAC parity, Apollo Client |
| FB18 ShipFlow | FB18-1 – FB18-10 | 10 | Router registration, auth contracts, GraphQL depth limit, frontend sub-waves, security fallback, vsm_meta creation, mutation checkpoint |
| FB19 KitchenSync | FB19-1 – FB19-10 | 10 | httpx API change, UUID coercion, Celery mocking, test isolation, rate-limit fixtures, coach completion gate, structural mutation gate |
| FB20 RentFlow | FB20-1 – FB20-6 | 6 | vsm_meta spawn, security lessons, deprecation warnings, re-audit artifacts, domain-specific fix agents |
| FB21 EduFlow | FB21-7 – FB21-27 | 19 | Phase 6/7 boundary, security-lessons reorg, gym experiments, custom coders, fix agents, devops coder, vsm_tester removal |
| FB22 OpsCenter | FB22-1, FB22-3 – FB22-5 | 4 | Dependency traps, Vite aliases, tester minimums, auth role parity, env-var triple parity |
| FB23 TalentFlow | FB23-1 – FB23-3 | 3 | Frontend build hard gate, mutation checkpoint, agent architecture refactor |

**Archive totals**: 104 mutations in log but not in master table (16 + 8 + 12 + 18 + 6 + 10 + 10 + 6 + 19 + 4 + 3 = 112). Note: Some early mutations use overlapping placeholder IDs (e.g., "N+3") that were later replaced by the `FB[N]-[M]` format. Counts are approximate due to non-sequential early numbering.

### Why These Are Not in the Master Table

1. **No effectiveness scores**: The 1–5 scoring system was introduced in FB24. Pre-FB24 mutations were tracked as "applied" or "effective" without numeric scores.
2. **Grouped log entries**: Many FB-era mutations are consolidated into single log entries (e.g., "FB22-1" covers 8 sub-mutations). Disaggregating them would require splitting historical log entries.
3. **Superseded rules**: Many early mutations have been superseded by later, more specific rules. For example, FB18-10 (mutation checkpoint) was replaced by FB26-S3 (tool-enforced hard gate).
4. **Schema v2.0 consolidation**: The 404-line append-only state file (Schema v1.0) contained 20+ duplicate IDs and conflicting statuses. Rather than migrate all historical data with inferred scores, the consolidation kept only actively tracked mutations in the master table and archived the rest here.

### Migration Policy

- **Do NOT add pre-FB24 mutations to the Master Table** unless they are re-tested in a current build with a numeric score.
- **Do reference the archive** when writing meta-reports or longitudinal analysis.
- **If a pre-FB24 mutation is re-applied or redesigned**, create a NEW ID in the Master Table (e.g., "FB30-R1") and link the old ID in the "Next Review" column.

---

*Consolidated during comprehensive audit: 2026-06-04. Previous append-only structure (404 lines, 20+ duplicates) replaced with single master table. Pre-consolidation archive added 2026-06-04.*

---

## Skill State Sections (Merged from skill-state.md — 2026-06-04)

> **Note**: `references/skill-state.md` has been merged into this file to eliminate
> staleness duplication. All self-model data lives in one place.

### Capability Matrix
| Agent | Domain | Success Rate | Last 3 Scores | Known Failure Modes | Recommended Max Task Size |
|-------|--------|-------------|---------------|---------------------|--------------------------|
| vsm_backend_coder | Python/FastAPI | 85% | 4, 4, 4 | 2 timeouts in FB30; code quality good when not timed out | 500 lines |
| vsm_frontend_coder | React/TS/Vite | 75% | 4, 4, 3 | Stub pages resolved; jsdom test environment still broken | 400 lines |
| vsm_security | Auth/GraphQL | 75% | 4, 3, — | Never spawned in FB30 (bypassed); manual audit used instead | 400 lines |
| vsm_auditor | Code review | 80% | 4, 4, 4 | Foundation/implementation checks converging | 500 lines |
| vsm_architect | Design | 70% | 4, 5, 2 | Timeout on 4-doc spawn; needs task splitting (M-FB30-1) | 400 lines |
| vsm_coordinator | Integration | 80% | 4, 4, 4 | GraphQL routing 307 caught; drift detection reliable | 500 lines |
| vsm_wiring | Entry-point wiring | 85% | 4, 4, 4 | Router registration accurate; module-level instantiation resolved | 500 lines |
| vsm_backend_tester | Test writing | 65% | 4, 3, 2 | Timed out in FB30; tests good when completed | 300 lines |
| vsm_frontend_tester | Test writing | 60% | 4, 3, 2 | jsdom localStorage mocking fails consistently | 300 lines |
| vsm_devops_coder | Docker/CI | 80% | 4, 4, 4 | Dockerfile and compose reliable | 500 lines |
| vsm_meta | Meta-evaluation | 60% | 3, 3, 2 | False TBD claims in meta-report (PM2 ineffective) | 300 lines |
| vsm_process_auditor | Process compliance | 60% | 3, 2, 2 | Timed out in FB30; compliance 85/100 despite timeout | 300 lines |
| vsm_variety_engineer | Environmental scanning | — | — | New agent — unmeasured | 400 lines |
| vsm_learning_curator | Portfolio management | — | — | New agent — unmeasured | 400 lines |

### Known Unknowns (with confidence)
| Hypothesis | Confidence | Last Tested | Priority | Status |
|------------|-----------|-------------|----------|--------|
| H150: Dependency verification prevents 100% of bad imports | 75% | FB21 | HIGH | untested |
| H154: `npm run build` as Phase 4 hard gate prevents TS leaks | 80% | FB24 | CRITICAL | partially confirmed |
| H157: Frontend stubs correlate with missed checklist items | 70% | FB24 | HIGH | confirmed |
| H201: Custom agent files reduce tokens by >30% | 60% | NEVER | HIGH | untested |
| H202: Tool-enforced read-only boundaries > prompt-only | 85% | NEVER | CRITICAL | untested |
| H203: SQLAlchemy Mapped[Enum] = mapped_column(String) bug | 80% | NEVER | MEDIUM | untested |
| H300: Background subagents bypass hooks | **CONFIRMED** | 2026-06-02 | CRITICAL | confirmed |
| H301: Prompt-hardened rules prevent background bypasses | 70% | NEVER | HIGH | untested |
| H302: session-end audit catches residual bypasses | 70% | FB27 | MEDIUM | confirmed |

### Temporal Patterns
- **T1**: Frontend stubs — RESOLVED (0 in FB25-FB29)
- **T2**: Phase 4 gate bypass — RESOLVED (FB24-1 effective)
- **T3**: Inline fixes during Phase 6/7 — IMPROVED (0 in FB25-FB29)
- **T4**: Security gate misses enum runtime — RESOLVED (FB24-2 effective)
- **T5**: mutations-applied.md bypass — RESOLVED (FB26-S3 effective)
- **T6**: Score regression alarm — ACTIVE (4.0→3.6→3.4→3.6 in FB30; FB30 is regression build of FB25 gold standard 4.0)
- **T7**: Architecture→implementation handoff weakest link — IMPROVED (Check 16 effective; zero handoff BLOCKERs in FB30)
- **T8**: Mutation bloat without removal — IMPROVED (48 active, 14 probationary — PM1/PM7 removed, 5 mutations promoted to effective)
- **T9**: Knowledge broker manual update failure — RESOLVED (broker updated manually in FB30; auto-update hook pending)

### Efficiency Baselines
| Metric | Rolling Avg (5 builds) | Last Build | Trend |
|--------|----------------------|------------|-------|
| Agents spawned | 15.2 | ~27 | ↑ |
| File writes | 52.0 | ~55 | ↑ |
| Session time (min) | 52 | ~175 | ↑ |
| Context compactions | 2.8 | 4 | ↑ |
| Tool calls per build | ~185 | ~280 | ↑ |
| Process violations per build | 2.0 | 2 | → |
| Mutation backfill rate | 0.08 | 0 | ↓ |

---

*Skill state merged during comprehensive audit: 2026-06-04*

| **2026-06-04 AUDIT MUTATIONS (Awaiting Measurement)** |
| SM3 | 2026-06-04 Audit | structural | Causal tracing automation | probation | 0 | — | — | — | FB30 |
| SM7 | 2026-06-04 Audit | structural | Coach heartbeat mode | probation | 0 | — | — | — | FB30 |
| SM8 | 2026-06-04 Audit | refinement | kimi-code-migration skill | probation | 0 | — | — | — | FB30 |


| **FB30 MUTATIONS (Created during FB30, await FB31 measurement)** |
| M-FB30-1 | FB30 Build | structural | Architect task splitting (3 spawns) | monitor | 1 | 3 | — | — | FB32 |
| M-FB30-2 | FB30 Build | append-only | GraphQLRouter recommendation over ASGI mount | effective | 1 | 5 | — | — | FB32 |
| M-FB30-3 | FB30 Build | append-only | Settings attribute UPPERCASE rule | effective | 1 | 5 | — | — | FB32 |
| M-FB30-4 | FB30 Build | append-only | Test DB compatibility checklist (SQLite/PostgreSQL) | effective | 1 | 5 | — | — | FB32 |
| M-FB30-5 | FB30 Build | append-only | GraphQL camelCase test reminder | effective | 1 | 5 | — | — | FB32 |

| **FB31 MUTATIONS (Measured in FB31, await FB32 measurement)** |
| FB31-1 | FB31 Build | structural | Architect 4-spawn split (redesign of M-FB30-1) | effective | 1 | 5 | H301 | — | — |
| FB31-2 | FB31 Build | structural | Tester 3-sub-wave split (redesign of H223) | effective | 1 | 4 | H304 | — | — |
| FB31-3 | FB31 Build | append-only | Coordinator GraphQL schema introspection check | effective | 1 | 4 | H302 | — | — |
| FB31-4 | FB31 Build | append-only | Phase 4 gate persistent pytest report | effective | 1 | 5 | H303 | — | — |
| FB31-5 | FB31 Build | append-only | Knowledge broker auto-update reminder | monitor | 1 | 3 | — | — | FB33 |

| **FB32 MUTATIONS (Created during FB32, await FB33 measurement)** |
| FB32-1 | FB32 Build | append-only | Security Configuration Zero-Default Rule | probation | 0 | — | — | — | FB33 |
| FB32-2 | FB32 Build | append-only | GraphQL Input Validation Parity Checklist | probation | 0 | — | — | — | FB33 |
| FB32-3 | FB32 Build | append-only | Async Task Wiring Verification | probation | 0 | — | — | — | FB33 |
| FB32-4 | FB32 Build | append-only | Phase 8 Closeout Artifact Checklist | probation | 0 | — | — | — | FB33 |
| FB32-5 | FB32 Build | refinement | Orphaned Query Export Limit | probation | 0 | — | — | — | FB33 |

| **S5 ITERATION MUTATIONS (2026-06-06)** |
| R34 | 2026-06-06 S5 | structural | algedonic-action-plan.py enhancement — active bloat algedonic + relaxed demotion threshold + unmeasured probationary detection | effective | 1 | 5 | — | — | S5 iter |
| R35 | 2026-06-06 S5 | structural | Remove failing monitor mutations A7 and PM3 | effective | 1 | 5 | — | — | S5 iter |
| R36 | 2026-06-06 S5 | structural | mutation-portfolio-health.py fill rate bug fix — exclude non-mutation rows from denominator | effective | 1 | 5 | — | — | S5 iter |
| R37 | 2026-06-06 S5 | structural | algedonic-action-plan.py parser bug fix — bold status rows incorrectly treated as section headers | effective | 1 | 5 | — | — | S5 iter |
| R38 | 2026-06-06 S5 | structural | Remove failing monitor mutation FB28-S5 — timeout fallback protocol insufficient under load | effective | 1 | 5 | — | — | S5 iter |
| R31 | 2026-06-06 S5 | structural | mutation-state.md data integrity fix — duplicate IDs + historical status | effective | 1 | 5 | — | — | — |
| R32 | 2026-06-06 S5 | structural | S5 iteration validation policy + bulk promote R12-R30 to effective | effective | 1 | 5 | — | — | — |
| R33 | 2026-06-06 S5 | structural | Redesign superseded SM1-SM9 audit mutations (6 of 9) | effective | 1 | 5 | — | — | — |
| R39 | 2026-06-06 S5 | refinement | gate-guardian.sh reliability — remove redundant find check, add npm pattern parity, fix missing .kimi/ crash, add 4 tests | effective | 1 | 5 | — | — | S5 iter |
