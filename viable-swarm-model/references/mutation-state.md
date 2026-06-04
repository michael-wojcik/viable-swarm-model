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
| **EFFECTIVE (Score 4–5)** |
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
| FB26-1 | FB26 Build | append-only | UploadFile.read() wrong API | effective | 2 | 5 | — | — | — |
| FB26-2 | FB26 Build | append-only | Auth endpoints missing rate limits | effective | 2 | 5 | — | — | — |
| FB26-3 | FB26 Build | append-only | Path traversal in file upload | effective | 2 | 5 | — | — | — |
| FB26-4 | FB26 Build | append-only | Socket.IO arbitrary room access | effective | 2 | 5 | — | — | — |
| FB26-5 | FB26 Build | append-only | Hardcoded config defaults | effective | 2 | 5 | — | — | — |
| FB26-S1 | FB26 Build | append-only | CORS wildcard severity LOW→MEDIUM | effective | 2 | 5 | H211 | — | — |
| FB26-S2 | FB26 Build | append-only | .dockerignore co-creation with Dockerfile | effective | 2 | 5 | H210 | — | — |
| FB26-S3 | FB26 Build | structural | H209 hard gate (tool-enforced) | effective | 2 | 5 | H209 | E20 | — |
| FB26-S4 | FB26 Build | structural | Phase 0 broker/state read verification | effective | 2 | 5 | — | — | — |
| FB26-S6 | FB26 Build | structural | Process auditor broker scored check | effective | 2 | 5 | — | — | — |
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
| **REMOVED / REDESIGNED** |
| ~~FB25-S2~~ | FB25 Coach | structural | Mutation checkpoint bypass | **REMOVED** | 1 | 1 | H209 | — | R-3 in cemetery |
| ~~FB26-S5~~ | FB26 Build | structural | Session-start hook auto-injection | **REMOVED** | 1 | 3 | — | — | R-4 in cemetery |
| ~~FB18-10~~ | FB18 Build | structural | Mutation tracking checkpoint | **REMOVED** | 4 | 1 | — | — | Superseded by FB26-S3 |
| ~~FB23-3~~ | FB23 Build | refinement | Inline fix prevention (prompt-only) | **REMOVED** | 2 | 1 | — | — | R-2 in cemetery |
| ~~FB19-7~~ | FB19 Build | append-only | Cross-skill mutation log review | **REMOVED** | 7 | 1 | — | — | R-1 in cemetery |
| FB27-1 | FB27 Build | append-only | UUID coercion `model_validator` | **REDESIGNED** | 1 | 2 | — | — | New rule applied FB28 |

---

## Integration Health

| Metric | Current | Target | Status |
|---|---|---|---|
| Active mutations | 28 | — | — |
| Effective mutations | 27 | >80% of active | ✅ 96% |
| Probationary mutations | 10 | <15 at any time | ⚠️ 10 |
| Removed mutations | 5 | ≥2 per 5 builds | ✅ 5 (exceeds target) |
| Measured effect fill rate | 31/32 | ≥80% | ✅ 97% |
| Removal rate (last 5 builds) | 2/5 = 40% | ≥20% | ✅ Exceeds |

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

**When removing a mutation**:
1. Update Status to `removed` in the SAME row
2. Move row to "REMOVED / REDESIGNED" section
3. Append entry to `mutation-cemetery.md`

**When redesigning a mutation**:
1. Update Status to `redesigned` in the SAME row
2. Create NEW mutation row with new ID
3. Link old ID in "Next Review" column

---

*Consolidated during comprehensive audit: 2026-06-04. Previous append-only structure (404 lines, 20+ duplicates) replaced with single master table.*
