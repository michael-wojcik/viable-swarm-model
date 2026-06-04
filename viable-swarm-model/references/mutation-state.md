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
| **HISTORICAL EFFECTIVE (Score 4–5, ≥5 builds — proven, no longer monitored)** |
| FB25-S1 | FB25 Coach | structural | False hook claim removal | effective | 5 | 5 | H300 | E17 | — |
| FB24-1 | FB24 Build | append-only | Phase 4 gate bypass when 1 test fails | effective | 6 | 5 | H154 | — | — |
| FB24-2 | FB24 Build | append-only | Enum type safety audit | effective | 6 | 5 | H203 | — | — |
| FB23-4 | FB23 Build | append-only | Frontend build script verification | effective | 7 | 5 | H154 | — | — |
| FB22-2 | FB22 Build | append-only | Frontend stub prevention | effective | 7 | 5 | H157 | — | — |
| FB21-8 | FB21 Build | append-only | Security-lessons topical reorg | effective | 9 | 5 | — | — | — |
| FB21-24 | FB21 Build | refinement | Process auditor spawn | effective | 9 | 4 | — | — | — |
| FB9 / P46 | FB9 Build | append-only | Test-First Exit Gate | effective | 9 | 5 | H154 | — | — |
| R19 | FB23 Build | refinement | Contract repopulation | effective | 7 | 4 | — | — | — |
| R20 | FB23 Build | refinement | Validate agent files script | effective | 7 | 4 | — | — | — |

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
| A4 | FB28 Build | append-only | Phase 4 gate strengthening | probation | 0 | — | H214 | — | FB30 |
| A5 | FB28 Build | append-only | Phase 6 skip prevention | probation | 0 | — | H217 | — | FB30 |
| S5 | FB28 Build | structural | Agent timeout fallback protocol | probation | 0 | — | H217 | — | FB30 |
| S6 | FB28 Build | append-only | GraphQL context builder fail-closed | probation | 0 | — | — | — | FB30 |
| A6 | FB28 Build | structural | Knowledge broker manual update requirement | probation | 0 | — | H213 | — | FB30 |
| R3 | FB28 Build | refinement | Process audit ≥80 fitness bar threshold | probation | 0 | — | — | — | FB30 |
| A7 | FB28 Build | append-only | Timeout budget ledger (>2 per phase = BLOCK) | probation | 0 | — | H217 | — | FB30 |
| A8 | FB28 Build | append-only | Vite config must not contain `test` property | probation | 0 | — | — | — | FB30 |
| R4 | FB28 Build | refinement | Phase 3c coordinator MANDATORY for Tier 2+ | probation | 0 | — | — | — | FB30 |
| A9 | FB28 Build | append-only | Pydantic V2 + SQLAlchemy ORM test fixture pattern | probation | 0 | — | — | — | FB30 |
| **FB29 MUTATIONS (Awaiting Measurement)** |
| PM1 | FB29 Build | structural | Hook-enforced process auditor spawn | probation | 0 | — | — | — | FB30 |
| PM2 | FB29 Build | append-only | Meta-report artifact disk verification | probation | 0 | — | — | — | FB30 |
| PM3 | FB29 Build | structural | Mutation-state auto-update hook | probation | 0 | — | — | — | FB30 |
| PM4 | FB29 Build | append-only | GraphQL parity admin override specificity | probation | 0 | — | — | — | FB30 |
| PM5 | FB29 Build | append-only | Enum `.value` in conftest.py | probation | 0 | — | — | — | FB30 |
| PM7 | FB29 Build | append-only | S5 manual work cap (≤1 file) | probation | 0 | — | — | — | FB30 |
| C1 | FB29 Build | append-only | FastAPI lifespan context manager for DB init | probation | 0 | — | — | — | FB30 |
| C2 | FB29 Build | append-only | `@field_validator` for comma-separated env strings | probation | 0 | — | — | — | FB30 |
| **REMOVED / REDESIGNED** |
| ~~FB25-S2~~ | FB25 Coach | structural | Mutation checkpoint bypass | **REMOVED** | 1 | 1 | H209 | — | R-3 in cemetery |
| ~~FB26-S5~~ | FB26 Build | structural | Session-start hook auto-injection | **REMOVED** | 1 | 3 | — | — | R-4 in cemetery |
| ~~FB18-10~~ | FB18 Build | structural | Mutation tracking checkpoint | **REMOVED** | 4 | 1 | — | — | Superseded by FB26-S3 |
| ~~FB23-3~~ | FB23 Build | refinement | Inline fix prevention (prompt-only) | **REMOVED** | 2 | 1 | — | — | R-2 in cemetery |
| ~~FB19-7~~ | FB19 Build | append-only | Cross-skill mutation log review | **REMOVED** | 7 | 1 | — | — | R-1 in cemetery |
| FB26-S6 | FB26 Build | structural | Process auditor broker scored check | **REDESIGNED** | 2 | 5→redesign | — | — | PM1 replaces |
| FB27-1 | FB27 Build | append-only | UUID coercion `model_validator` | **REDESIGNED** | 1 | 2 | — | — | New rule applied FB28 |

---

## Integration Health

| Metric | Current | Target | Status |
|---|---|---|---|
| Active mutations | 51 | — | — |
| Historical effective (≥5 builds) | 10 | >15% of active | ✅ 20% |
| Effective (<5 builds, monitored) | 16 | >30% of active | ✅ 31% |
| Probationary mutations | 18 | <15 at any time | ⚠️ 18 (exceeds target) |
| Removed / redesigned | 7 | ≥2 per 5 builds | ✅ 7 (exceeds target) |
| Measured effect fill rate (scored) | 33/51 | ≥80% | ⚠️ 65% (18 pending) |
| Measured effect fill rate (any entry) | 51/51 | ≥80% | ✅ 100% |
| Removal rate (last 5 builds) | 6/5 = 120% | ≥20% | ✅ Exceeds |

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
| Agent | Domain | Success Rate | Last 3 Scores | Known Failure Modes |
|-------|--------|-------------|---------------|---------------------|
| vsm_backend_coder | Python/FastAPI | 85% | 4, 4, 4 | Import loops, missing deps |
| vsm_frontend_coder | React/TS/Vite | 70% | 4, 3, 2 | Stub pages (improving), void-referenced imports |
| vsm_security | Auth/GraphQL | 80% | 4, 4, 3 | Misses enum runtime bugs, CORS wildcard severity |
| vsm_auditor | Code review | 80% | 4, 4, 3 | Duplicates checks across foundation/implementation |
| vsm_architect | Design | 85% | 4, 4, 5 | Scope creep without product brief guardrails |
| vsm_coordinator | Integration | 75% | 4, 3, 4 | Drift detection only active on Tier 2+ builds |
| vsm_wiring | Entry-point wiring | 80% | 4, 4, 3 | Router registration misses, module-level instantiation |
| vsm_backend_tester | Test writing | 75% | 4, 3, 4 | Incomplete coverage, missing edge cases |
| vsm_frontend_tester | Test writing | 70% | 4, 3, 3 | Build verification gaps |
| vsm_devops_coder | Docker/CI | 75% | 4, 3, 4 | Health check omissions, .dockerignore absence |
| vsm_meta | Meta-evaluation | 70% | 3, 3, 3 | Cannot enforce mutations-applied.md |
| vsm_process_auditor | Process compliance | 65% | 3, 3, 2 | Broker freshness scored as informational |
| vsm_variety_engineer | Environmental scanning | — | — | New agent — unmeasured |
| vsm_learning_curator | Portfolio management | — | — | New agent — unmeasured |

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
- **T6**: Score regression alarm — ACTIVE (4.0→3.6→3.4, reversed to 4.2 in FB29)
- **T7**: Architecture→implementation handoff weakest link — ACTIVE (Check 16 added)
- **T8**: Mutation bloat without removal — ACTIVE (51 active, 18 probationary — new structural mutation SM9 addresses)
- **T9**: Knowledge broker manual update failure — ACTIVE (auto-broker-update.sh addresses)

### Efficiency Baselines
| Metric | Rolling Avg (5 builds) | Last Build | Trend |
|--------|----------------------|------------|-------|
| Agents spawned | 13.6 | 14 | → |
| File writes | 50.0 | 52 | → |
| Session time (min) | 40 | 38 | → |
| Context compactions | 2.6 | 3 | → |
| Tool calls per build | ~192 | ~195 | → |
| Process violations per build | 2.4 | 2 | ↓ |
| Mutation backfill rate | 0.12 | 0 | ↓ |

---

*Skill state merged during comprehensive audit: 2026-06-04*

| **2026-06-04 AUDIT MUTATIONS (Awaiting Measurement)** |
| SM1 | 2026-06-04 Audit | structural | vsm_variety_engineer agent | probation | 0 | — | — | — | FB31 |
| SM2 | 2026-06-04 Audit | structural | Process auditor HARD BLOCK | probation | 0 | — | — | — | FB31 |
| SM3 | 2026-06-04 Audit | structural | Causal tracing automation | probation | 0 | — | — | — | FB31 |
| SM4 | 2026-06-04 Audit | structural | Auto-broker-update hook | probation | 0 | — | — | — | FB31 |
| SM5 | 2026-06-04 Audit | refinement | skill-state→mutation-state merge | probation | 0 | — | — | — | FB31 |
| SM6 | 2026-06-04 Audit | structural | Build health dashboard | probation | 0 | — | — | — | FB31 |
| SM7 | 2026-06-04 Audit | structural | Coach heartbeat mode | probation | 0 | — | — | — | FB31 |
| SM8 | 2026-06-04 Audit | refinement | kimi-code-migration skill | probation | 0 | — | — | — | FB31 |
| SM9 | 2026-06-04 Audit | structural | vsm_learning_curator agent | probation | 0 | — | — | — | FB31 |

