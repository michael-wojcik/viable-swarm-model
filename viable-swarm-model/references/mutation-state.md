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
| FB25-S1 | FB25 Coach | structural | False hook claim | probation | 1 | 5 | H300 | E17 |
| FB25-S2 | FB25 Coach | structural | Mutation checkpoint bypass | probation | 1 | 1 | H209 | — |
| FB24-1 | FB24 Build | append-only | Phase 4 gate bypass | probation | 2 | 5 | H154 | — |
| FB24-2 | FB24 Build | append-only | Enum type safety | probation | 2 | 5 | H203 | — |
| FB23-4 | FB23 Build | append-only | Frontend build verification | probation | 3 | 5 | H154 | — |
| FB21-8 | FB21 Build | append-only | Duplicate L-numbers | effective | 4 | 5 | — | — |
| FB21-24 | FB21 Build | refinement | Process auditor spawn | monitor | 4 | 3 | — | — |
| R19 | FB23 Build | refinement | Contract repopulation | effective | 2 | 4 | — | — |
| R20 | FB23 Build | refinement | Validate agent files | effective | 2 | 4 | — | — |

---

## Ineffective Mutations (Awaiting Removal/Redesign)

| ID | Source | Type | Target Failure | First Ineffective | Builds Failed | Action Required | Deadline Build |
|---|---|---|---|---|---|---|---|
| FB23-3 | FB23 Build | refinement | Inline fix prevention | FB23 | FB23, FB24 | **REMOVE** — replace with tool-enforced boundary | FB26 |
| FB22-2 | FB22 Build | append-only | Frontend stub prevention | FB23 | FB23, FB24 | **KEEP** — Effective in FB26 (score 5/5, zero stub pages) | FB26 |
| FB19-7 | FB19 Build | append-only | Cross-skill log review | FB19 | FB19–FB25 | **REMOVE** — no longer relevant | FB26 |
| FB18-10 | FB18 Build | structural | Mutation checkpoint | FB23 | FB23, FB24, FB25 | **REDESIGN** — hard gate in vsm_meta.md | FB26 |
| FB9 / P46 | FB9 Build | append-only | Test-First Exit Gate | FB20 | FB20, FB21, FB24 | **KEEP** — Effective in FB26 (score 5/5, legitimate gate, 45 tests pass) | FB26 |

---

## Removed Mutations (In Cemetery)

| ID | Source | Type | Removal Build | Rationale | Replacement |
|---|---|---|---|---|---|
| *(none yet)* | | | | | |

---

## Integration Health

| Link | Active Mutations | Ineffective Mutations | Removal Rate |
|---|---|---|---|
| Gym experiment → Mutation | 3 | 0 | 0% |
| Fitness build → Mutation | 6 | 5 | 0% |
| Hypothesis → Mutation | 4 | 2 | 0% |

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
