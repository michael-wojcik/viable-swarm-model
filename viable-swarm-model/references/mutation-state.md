# Mutation State — Unified Lifecycle Tracking

> **Purpose**: Track every mutation from hypothesis → experiment → application → measurement → keep/remove.
> **Updated by**: S5 during Phase 8c-ii, coach trainer during Phase 2, gym after experiments.
> **Read by**: All skills at Phase 0 to understand which rules are active, probationary, or removed.
> **Schema version**: 1.0

---

## Legend

| Status | Meaning |
|---|---|
| `probation` | Applied < 3 builds ago; awaiting measurement |
| `effective` | Scored 4–5 on effectiveness; permanently active |
| `monitor` | Scored 3; under extended observation |
| `ineffective` | Scored 1–2; marked for removal or redesign |
| `removed` | Moved to mutation-cemetery.md; no longer active |
| `superseded` | Replaced by a newer mutation addressing same failure mode |

---

## Active Mutations (Currently Enforced)

| ID | Source | Type | Target Failure | Status | Builds Tested | Effectiveness Score | Linked Hypothesis | Linked Experiment |
|---|---|---|---|---|---|---|---|---|
| FB25-S1 | FB25 Coach | structural | False hook claim | effective | 2 | 5 | H300 | E17 |
| FB25-S2 | FB25 Coach | structural | Mutation checkpoint bypass | ineffective | 2 | 1 | H209 | — |
| FB24-1 | FB24 Build | append-only | Phase 4 gate bypass | effective | 3 | 5 | H154 | — |
| FB24-2 | FB24 Build | append-only | Enum type safety | effective | 3 | 5 | H203 | — |
| FB23-4 | FB23 Build | append-only | Frontend build verification | effective | 4 | 5 | H154 | — |
| FB22-2 | FB22 Build | append-only | Frontend stub prevention | effective | 4 | 5 | H157 | — |
| FB21-8 | FB21 Build | append-only | Duplicate L-numbers | effective | 5 | 5 | — | — |
| FB21-24 | FB21 Build | refinement | Process auditor spawn | monitor | 5 | 3 | — | — |
| FB9 / P46 | FB9 Build | append-only | Test-First Exit Gate | effective | 5 | 5 | H154 | — |
| R19 | FB23 Build | refinement | Contract repopulation | effective | 3 | 4 | — | — |
| R20 | FB23 Build | refinement | Validate agent files | effective | 3 | 4 | — | — |
| FB26-1 | FB26 Build | append-only | UploadFile.read() wrong API | effective | 1 | 5 | — | — |
| FB26-2 | FB26 Build | append-only | Auth endpoints missing rate limits | effective | 1 | 5 | — | — |
| FB26-3 | FB26 Build | append-only | Path traversal in file upload | effective | 1 | 5 | — | — |
| FB26-4 | FB26 Build | append-only | Socket.IO arbitrary room access | effective | 1 | 5 | — | — |
| FB26-5 | FB26 Build | append-only | Hardcoded config defaults | effective | 1 | 5 | — | — |
| FB26-A3 | FB26 Build | append-only | Score trend tracking | effective | 1 | 4 | — | — |
| FB26-S1 | FB26 Build | append-only | CORS wildcard severity | effective | 1 | 5 | H211 | — |
| FB26-S2 | FB26 Build | append-only | .dockerignore co-creation | effective | 1 | 5 | H210 | — |
| FB26-S3 | FB26 Build | structural | H209 hard gate | effective | 1 | 5 | H209 | E20 |
| FB26-S4 | FB26 Build | structural | Phase 0 broker/state read | effective | 1 | 5 | — | — |
| FB26-S5 | FB26 Build | structural | Session-start auto-injection | **removed** | 2 | 2 | — | FB28 |
| FB26-S6 | FB26 Build | structural | Process auditor broker scored check | effective | 1 | 5 | — | — |

---

## Ineffective Mutations (Awaiting Removal/Redesign)

| ID | Source | Type | Target Failure | First Ineffective | Builds Failed | Action Required | Deadline Build |
|---|---|---|---|---|---|---|---|
| *(none currently)* | | | | | | | |

---

## Removed Mutations (In Cemetery)

| ID | Source | Type | Removal Build | Rationale | Replacement |
|---|---|---|---|---|---|
| R-1 / FB19-7 | FB19 Build | append-only | 2026-06-02 | Cross-skill log separation artificial; skills share git repo | None — remove constraint entirely |
| R-2 / FB23-3 | FB23 Build | refinement | 2026-06-02 | Redundant with hook + vsm-main.md Layer 1 | Strengthen boundary-guardian.sh |
| FB18-10 | FB18 Build | structural | 2026-06-03 | Failed FB23, FB24, FB25, FB26 (4 consecutive builds). Redesign to vsm_meta.md did not work. | FB26-S3 (tool-enforced hard gate) |

---

## Integration Health

| Link | Active Mutations | Ineffective Mutations | Removal Rate |
|---|---|---|---|
| Gym experiment → Mutation | 3 | 0 | 0% |
| Fitness build → Mutation | 15 | 1 | 6.7% |
| Hypothesis → Mutation | 6 | 0 | 0% |

**Target for FB26–FB30**: Removal rate ≥ 20% (at least 1 ineffective mutation removed per 5 builds).

---

## Usage Instructions

**When applying a new mutation**:
1. Assign a unique ID (format: `FB[N]-[M]` for build-derived, `E[N]-[M]` for experiment-derived, `R[N]` for refinement)
2. Set status to `probation`
3. Link to hypothesis ID and experiment ID if applicable
4. Set `Builds Tested` to 0

**When a fitness build completes**:
1. Increment `Builds Tested` for all probation/monitor mutations
2. Score effectiveness 1–5 based on whether target failure recurred
3. If score ≥ 4: status → `effective`
4. If score = 3: status → `monitor`
5. If score ≤ 2: status → `ineffective`

**When removing a mutation**:
1. Move row from Active/Ineffective to Removed
2. Fill `Removal Build` and `Rationale`
3. If replaced, fill `Replacement`
4. Append entry to `mutation-cemetery.md`

---

*Created during comprehensive audit: 2026-06-02*

## FB26 Update — 2026-06-03

### Status Changes
| ID | Old Status | New Status | Score | Rationale |
|---|---|---|---|---|
| FB25-S1 | probation | effective | 5 | No build prompt claimed hook enforcement for background agents |
| FB25-S2 | probation | ineffective | 1 | mutations-applied.md still missing in FB26 (4th consecutive build) |
| FB24-1 | probation | effective | 5 | Phase 4 gate legitimate (45 tests, 0 failures) |
| FB24-2 | probation | effective | 5 | All enums used sa.Enum; no .value crashes |
| FB23-4 | probation | effective | 5 | Frontend build green in FB26 |
| FB18-10 | ineffective | **REMOVED** | 1 | Failed FB23, FB24, FB25, FB26. Redesign to vsm_meta.md did not work. |
| FB23-3 | ineffective | **REMOVED** | — | Redundant with hook + vsm-main.md Layer 1. Already removed per comprehensive audit. |
| FB19-7 | ineffective | **REMOVED** | — | Cross-skill log separation no longer relevant. Already removed per comprehensive audit. |

### New Mutations (FB26 Build-Derived)
| ID | Source | Type | Target Failure | Status | Builds Tested | Effectiveness Score | Linked Hypothesis |
|---|---|---|---|---|---|---|---|
| FB26-1 | FB26 Build | append-only | UploadFile.read() wrong API | probation | 0 | — | — |
| FB26-2 | FB26 Build | append-only | Auth endpoints missing rate limits | probation | 0 | — | — |
| FB26-3 | FB26 Build | append-only | Path traversal in file upload | probation | 0 | — | — |
| FB26-4 | FB26 Build | append-only | Socket.IO arbitrary room access | probation | 0 | — | — |
| FB26-5 | FB26 Build | append-only | Hardcoded config defaults | probation | 0 | — | — |

### Remaining Ineffective Mutations
| ID | Action | Deadline |
|---|---|---|
| FB22-2 | **KEEP** — Effective in FB26. Zero stub pages detected. No redesign needed. | FB27 |
| FB9/P46 | **KEEP** — Effective in FB26. Phase 4 gate legitimate (45 tests, 0 failures). No redesign needed. | FB27 |

---

## FB26-1: UploadFile.read() API signature rule
**Status**: probation
**Type**: append-only
**Target**: python-pitfalls
**Applied**: 2026-06-03
**Rationale**: FB26 documents.py used `await file.read(max_bytes=...)` causing TypeError.
**Next review**: FB27

---

## FB26-2: Password minimum length ≥ 8
**Status**: probation
**Type**: append-only
**Target**: security-patterns
**Applied**: 2026-06-03
**Rationale**: FB26 auth.py used `min_length=6` instead of spec-mandated 8.
**Next review**: FB27

---

## FB26-3: Dockerfile non-root USER directive
**Status**: probation
**Type**: append-only
**Target**: security-patterns
**Applied**: 2026-06-03
**Rationale**: FB26 Dockerfile initially lacked `USER` directive (root container).
**Next review**: FB27

---

## FB26-4: Celery task ownership re-verification
**Status**: probation
**Type**: append-only
**Target**: security-patterns
**Applied**: 2026-06-03
**Rationale**: FB26 Celery tasks did not re-verify ownership before processing.
**Next review**: FB27

---

## FB26-5: Env-var port parity check
**Status**: probation
**Type**: append-only
**Target**: docker-pitfalls
**Applied**: 2026-06-03
**Rationale**: FB26 .env.example VITE_WS_URL port 8000 did not match compose realtime port 8001.
**Next review**: FB27

---

## FB26-S1: CORS wildcard severity elevation LOW→MEDIUM
**Status**: probation
**Type**: append-only
**Target**: security-patterns
**Applied**: 2026-06-03
**Rationale**: FB26 CORS wildcards consistently deferred because rated LOW. Elevating to MEDIUM forces fix.
**Next review**: FB27

---

## FB26-S2: .dockerignore co-creation with Dockerfile
**Status**: probation
**Type**: append-only
**Target**: docker-pitfalls
**Applied**: 2026-06-03
**Rationale**: FB26 .dockerignore missing despite being a BLOCKER. No agent owned its creation.
**Next review**: FB27

---

## FB26-S3: H209 hard gate (structural mutation)
**Status**: probation
**Type**: structural
**Target**: stop-verifier.sh + SKILL.md Phase 8 sequencing
**Applied**: 2026-06-03
**Rationale**: H209 confirmed for 4th consecutive build (FB23→FB26). Prompt-only mutations failed. Tool-enforced gate with retroactive creation detection + Phase 8c-ii moved BEFORE 8b.
**Next review**: FB27
**Human approval**: Yes — hook gate (2026-06-03)

---

## FB26-S4: Phase 0 broker/state read verification
**Status**: probation
**Type**: structural
**Target**: SKILL.md Phase 0
**Applied**: 2026-06-03
**Rationale**: Post-mortem confirmed plan.md had zero references to knowledge-broker.md or mutation-state.md despite SKILL.md mandating them. Added explicit Step 8 requiring S5 to log active traps and probationary mutations in plan.md.
**Next review**: FB27

---

## FB26-S5: Session-start hook auto-injection of broker traps
**Status**: probation
**Type**: structural
**Target**: hooks/session-start.sh
**Applied**: 2026-06-03
**Rationale**: FB26-S4 relies on S5 compliance. History shows S5 forgets. Auto-injection makes broker consumption unavoidable by writing .kimi/session-context.md before any agent spawns.
**Next review**: FB27

---

## FB26-S6: Process auditor Phase 0 broker read scored check
**Status**: probation
**Type**: structural
**Target**: agents/vsm_process_auditor.md
**Applied**: 2026-06-03
**Rationale**: FB26 process auditor gave broker freshness 5/10 (informational PASS) even though broker wasn't actually read by S5. A 10-point scored check makes Phase 0 broker read a first-class compliance issue.
**Next review**: FB27

---

## FB26-A3: Score trend tracking rule
**Status**: probation
**Type**: append-only
**Target**: references/meta-reflection.md
**Applied**: 2026-06-03
**Rationale**: FB26 score dropped 4.0→3.6 (-0.4) with no regression alarm. Trend tracking makes decay visible before it becomes entrenched.
**Next review**: FB27


---

## FB27 Update — 2026-06-03

### Status Changes (All FB26 Probationary Mutations Tested)
| ID | Old Status | New Status | Builds Tested | Effectiveness Score | Rationale |
|---|---|---|---|---|---|
| FB26-1 | probation | **effective** | 1 | 5 | UploadFile API used correctly in all file uploads |
| FB26-2 | probation | **effective** | 1 | 5 | All password fields have `min_length=8` |
| FB26-3 | probation | **effective** | 1 | 5 | Both Dockerfiles have `USER appuser` before `CMD` |
| FB26-4 | probation | **effective** | 1 | 5 | Celery task verifies vehicle assignment ownership |
| FB26-5 | probation | **effective** | 1 | 5 | `.env.example` ports match `docker-compose.yml` |
| FB26-S1 | probation | **effective** | 1 | 5 | Zero CORS wildcards found; H211 confirmed |
| FB26-S2 | probation | **effective** | 1 | 5 | `.dockerignore` exists in both backend/ and frontend/ |
| FB26-S3 | probation | **effective** | 1 | 5 | `mutations-applied.md` written BEFORE `vsm_meta` spawn. Hook test passed. |
| FB26-S4 | probation | **effective** | 1 | 5 | `plan.md` contains Active Constraints from broker and mutation-state |
| FB26-S5 | probation | **monitor** | 1 | 3 | Session-start hook did not fire (build context limitation). Cannot confirm effectiveness. |
| FB26-S6 | probation | **effective** | 1 | 5 | Process auditor scored Phase 0 broker read as 8/10 (EXCELLENT) |
| FB26-A3 | probation | **effective** | 1 | 4 | Score trend table included in meta-report. Alarm triggered on 3.4 < 3.6 target. |

### New Mutations Proposed (from FB27 Lessons)
| ID | Type | Target | Rationale |
|---|---|---|---|
| FB27-1 | append-only | `python-pitfalls` | Pydantic V2 UUID→str coercion does not happen with `from_attributes=True` | **redesigned** | 2 | 2 | — | FB28 | |
| FB27-2 | append-only | `backend-patterns` | Missing `await` on async service calls returns coroutine object |
| FB27-3 | append-only | `security-patterns` | `JWT_SECRET` default fallback allows token forgery |
| FB27-4 | append-only | `graphql-pitfalls` | GraphQL resolvers must re-implement RBAC; no inheritance from FastAPI deps |

### Integration Health Update
- **Mutation removal rate**: 2 mutations removed in FB26 audit (R-1, R-2). Target ≥2 per 5 builds: ON TRACK.
- **Measured effect fill rate**: 12/12 FB26 mutations now have measured effects (100%). Target ≥80%: EXCEEDED.
- **S5 bypassed gates**: 0. Target 0: MET.

---

## FB28 Post-Build Mutations — 2026-06-03

### Additional Mutations Applied (post-trainer evaluation)

| ID | Source | Type | Target Failure | Status | Builds Tested | Effectiveness Score | Linked Hypothesis |
|---|---|---|---|---|---|---|---|
| A4 | FB28 Build | append-only | Phase 4 gate weak / bypassable | probation | 0 | — | H214 |
| A5 | FB28 Build | append-only | Phase 6 skip / coordinator timeout | probation | 0 | — | H217 |
| S5 | FB28 Build | structural | Agent timeout → S5 manual work | probation | 0 | — | H217 |
| S6 | FB28 Build | append-only | GraphQL context builder not fail-closed | probation | 0 | — | — |
| A6 | FB28 Build | structural | Knowledge broker stale (>7 days) | probation | 0 | — | H213 |
| R3 | FB28 Build | refinement | Process audit score not in fitness bar | probation | 0 | — | — |
| A7 | FB28 Build | append-only | Timeout avalanche (>2 per phase) | probation | 0 | — | H217 |
| A8 | FB28 Build | append-only | Vite config contains `test` property | probation | 0 | — | — |
| R4 | FB28 Build | refinement | Phase 3c coordinator skipped under pressure | probation | 0 | — | — |
| A9 | FB28 Build | append-only | Pydantic ORM test fixture reinvention | probation | 0 | — | — |

### Mutation Details

---

## S6: GraphQL Context Builder Must Never Return Anonymous Context
**Status**: probation
**Type**: append-only
**Target**: `graphql-pitfalls/SKILL.md`
**Applied**: 2026-06-03
**Rationale**: FB28 security audit caught `context_getter=lambda` as BLOCKER. The fix
was a fail-closed `get_context` that raises on ALL failure paths. Existing
"Context Builder Fail-Closed" rule was too abstract. S6 adds concrete code
patterns showing correct (raise) vs incorrect (return user=None) behavior,
plus auditor verification steps.
**Next review**: FB29

---

## A6: Knowledge Broker Phase 8d Manual Update Requirement
**Status**: probation
**Type**: structural
**Target**: `SKILL.md` Phase 8d
**Applied**: 2026-06-03
**Rationale**: Knowledge broker last updated 2026-06-02, stale by FB28 end.
Session-end hooks failed for 2 consecutive builds (FB26-S5 removed). Making
knowledge broker update an explicit Phase 8d step removes reliance on automation.
**Next review**: FB29

---

## R3: Process Auditor Score ≥80 Fitness Bar Threshold
**Status**: probation
**Type**: refinement
**Target**: `vsm-fitness-coach/SKILL.md` + `evaluation-rubric.md`
**Applied**: 2026-06-03
**Rationale**: FB28 trainer scored 3.8/5.0 but process auditor scored 70/100.
Without a process audit threshold, the fitness system produces false positives.
R3 adds "Process Compliance" criterion to evaluation rubric and hard-checks
process audit ≥80 in Coach Phase 1c and Phase 2.
**Next review**: FB29

---

## A7: Timeout Budget Ledger
**Status**: probation
**Type**: append-only
**Target**: `SKILL.md` Phase 2
**Applied**: 2026-06-03
**Rationale**: FB28 had 5 agent timeouts across multiple phases. S5's fallback
protocol (S5) addresses what to do when ONE agent times out, but does not
prevent the avalanche pattern. A7 adds a timeout budget tracker in plan.md
and BLOCKs the build if >2 timeouts occur in a single phase.
**Next review**: FB29

---

## A8: Vite Config Must Not Contain `test` Property
**Status**: probation
**Type**: append-only
**Target**: `typescript-pitfalls/SKILL.md`
**Applied**: 2026-06-03
**Rationale**: FB28 `vite.config.ts` had a `test` block that caused `tsc -b` to fail
because `test` is not in `UserConfigExport`. The fix was separating into
`vite.config.ts` + `vitest.config.ts`. This is a reproducible TypeScript+Vite+Vitest
trap that will hit every build using this stack.
**Next review**: FB29

---

## R4: Phase 3c Coordinator MANDATORY for Tier 2+
**Status**: probation
**Type**: refinement
**Target**: `SKILL.md` Phase 3 (flow diagram + text)
**Applied**: 2026-06-03
**Rationale**: Phase 3c was "conditional" for Tier 2+. History shows S5 skips
coordinator checks under time pressure (FB25–FB28). Making it mandatory removes
the "should I spawn it?" decision point. The coordinator mid-wave check is the
primary mechanism for catching contract drift before it cascades to Phase 4/5.
**Next review**: FB29

---

## A9: Pydantic V2 + SQLAlchemy ORM Test Fixture Pattern
**Status**: probation
**Type**: append-only
**Target**: `python-pitfalls/SKILL.md`
**Applied**: 2026-06-03
**Rationale**: FB28 `conftest.py` required ~230 lines of monkeypatching for ORM
UUID coercion in tests. Each build reinvents this workaround differently. Documenting
the pattern prevents reinvention and provides a reusable template. Also signals
that this is a known Pydantic V2 + SQLAlchemy sharp edge.
**Next review**: FB29
