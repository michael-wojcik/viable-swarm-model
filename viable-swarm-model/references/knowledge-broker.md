# VSM Knowledge Broker — Cross-Skill Digest

> **Updated by**: S5 during Phase 8 / coach Phase 5 / gym Phase 5 (curated tables)
> **Read by**: All three skills at Phase 0 (MANDATORY)
> **Schema version**: 1.2
> **Last updated**: 2026-06-04

---

## How to Use This File

**Main skill (Phase 0)**: Read this file BEFORE reading other references. Adjust build strategy based on active gaps and confirmed patterns.

**Coach (Phase 0a)**: Read this file to learn main skill's recent gaps and gym's confirmed patterns. Design build traps that target known weaknesses.

**Gym (Phase 0)**: Read this file to learn main skill's recurring failures and coach's scored gaps. Prioritize hypotheses that address active pain points.

**Staleness check**: If this file is >7 days old, emit algedonic: "Knowledge broker stale. Cross-skill learning may be impaired."

---

## Active Gaps (Confirmed, Unfixed)

> Gaps that have recurred in 2+ builds and have no effective mutation preventing them.

| ID | Gap | First Seen | Last Seen | Mutations Attempted | Status |
|---|---|---|---|---|---|
| G1 | Foundation BLOCKERs in every build | FB1 | FB25 | R19, R20, FB21-8 | Partially effective — still recurring |
| G2 | Phase 4 gate bypass when 1 test fails | FB20 | FB24 | FB24-1, FB25-S1 | **RESOLVED** — FB25-FB29 zero bypasses |
| G3 | Frontend stub pages (no live data fetch) | FB21 | FB24 | FB22-2, H157 | **RESOLVED** — zero stubs in FB25-FB29 |
| G4 | Inline fixes during Phase 6/7 boundary | FB20 | FB23 | FB23-3, FB25-S2 | **RESOLVED** — zero inline fixes FB25-FB29 |
| G5 | Integration ISSUEs orphaned (not fixed or documented) | FB21 | FB25 | FB24-2, Phase 7d | **RESOLVED** — FB28-FB29 systematic ISSUE sweep |
| G6 | `mutations-applied.md` checkpoint bypassed | FB23 | FB25 | FB18-10, FB25-S2, FB26-S3 | **RESOLVED** — FB26-S3 effective; FB27-FB29 all produced file |
| G7 | Module-level Celery instantiation | FB23 | FB25 | H155 | **RESOLVED** — FB28 wiring audit caught it |
| G8 | Socket.IO non-functional | FB21 | FB24 | H66 | PENDING — not tested since FB24 |
| G9 | Agent timeout avalanche on Tier 2+ | FB28 | FB28 | H217 | **ACTIVE** — FB28 had 5 timeouts; FB29 had 0 after task sizing |
| G10 | GraphQL security parity gap | FB25 | FB29 | M1 | **ACTIVE** — mutations lack validation/ownership that REST enforces |

---

## Confirmed Patterns (Validated in 2+ Builds)

> Patterns that have been empirically validated and should be reinforced.

| ID | Pattern | Validated In | Effectiveness |
|---|---|---|---|
| P1 | `sa.Enum(...)` for SQLAlchemy enum columns (not `sa.String`) | FB25 | HIGH — prevented H203 crash |
| P2 | Frontend `npm run build` as Phase 4 hard gate | FB25 | HIGH — build did not leak to Phase 6 |
| P3 | Auditor batch-size limit (≤10 files) | FB25 | HIGH — 0 BLOCKER false positives |
| P4 | Phase 3c mid-wave S2 check on Tier 2+ | FB25 | MEDIUM — correlation suggestive |
| P5 | Domain-specific fix agents (vsm_backend_fix_agent) | FB25 | HIGH — 0 regressions on 6 modified files |
| P6 | Prompt-hardened structural gate rules (Layer 1) | FB25 | HIGH — no background agent bypasses detected |
| P7 | Agent task sizing ≤500 lines per spawn (H217) | FB29 | HIGH — 0 timeouts in FB29 vs 5 in FB28 |
| P8 | vsm_meta file verification protocol (H215) | FB28 | HIGH — zero file hallucinations |
| P9 | Early handoff verification Check 16 (H214) | FB28 | HIGH — caught auth raw-dict in Phase 2b |

---

## Ineffective Mutations (Score 1–2, Awaiting Removal)

> Mutations that have failed to prevent their target failure mode in 2+ builds.

| Mutation ID | Target Failure | First Ineffective | Builds Where It Failed | Action |
|---|---|---|---|---|
| FB22-2 | Frontend stub prevention | FB23 | FB23, FB24 | **REDESIGN** — needs live-data-fetch verification in agent prompt |
| FB18-10 | Mutation tracking checkpoint | FB23 | FB23, FB24, FB25 | **REDESIGN** — needs `vsm_meta` output template change + hard gate |
| FB9 / P46 | Test-First Exit Gate | FB20 | FB20, FB21, FB24 | **REDESIGN** — needs explicit S5 verification command, not just pattern |
| FB25-S2 | Mutation checkpoint hard gate (prompt-only) | FB26 | FB26 | **REMOVED** — R-3 in cemetery; superseded by FB26-S3 |
| FB27-1 | UUID coercion via `model_validator` | FB28 | FB28 | **REDESIGNED** — ORM path needed `field_validator`; new rule applied FB28 |

---

## Next Build Traps (Coach-Planned)

> Deliberate failure modes the coach plans to inject in the next fitness build.

| Build | Target Gap | Trap Description | Expected Agent Catch |
|---|---|---|---|
| FB30 | G9 (agent timeout) | Tier 2+ build with >15 source files; all agents must complete without timeout | Task splitting + timeout fallback protocol |
| FB30 | G10 (GraphQL parity) | GraphQL mutation must enforce same validation/ownership as REST equivalent | vsm_security checks parity; vsm_auditor cross-references |
| FB30 | G1 (foundation BLOCKERs) | Introduce subtle auth role enum mismatch in data models | Phase 2c S5 validation + Phase 2d Check 16 |

---

## Experiment Backlog (Gym-Validated)

> Recent gym experiments and their outcomes.

| Experiment | Hypothesis | Result | Mutation Applied |
|---|---|---|---|
| E15 | H105: Generic coder bypasses re-audit | CONFIRMED | vsm_backend_fix_agent prompt hardened |
| E16 | H106: vsm_meta catches process violations | CONFIRMED | No mutation needed — skill works |
| E17 | H107: Domain fix agents outperform generic | CONFIRMED | No mutation needed — skill works |
| E18 | H108: Stack skill reference validation | CONFIRMED | validate-agent-files.py updated |
| E19 | H109: Knowledge broker auto-update | INCONCLUSIVE | Hook failed; manual update required |

---

## Cross-Skill Integration Health

| Link | Status | Evidence |
|---|---|---|
| Gym → Main | ✅ Functional | E15–E17 produced mutations applied to main skill |
| Coach → Main | ⚠️ Partial | Trainer scores builds; mutation effectiveness unmeasured |
| Main → Coach | ⚠️ Partial | Meta-reports rarely referenced in coach Phase 0 |
| All → Broker | ✅ Functional | Updated 2026-06-04 with FB27-FB29 entries and curated tables |

---

---

## Raw Session Log

> Raw chronological session entries are written by `knowledge-broker.sh` to
> `.kimi/knowledge-broker-log.md` in the **build directory** (not in the skill repo).
> This keeps ephemeral session data with other build artifacts and avoids
> modifying tracked skill files.
>
> To review raw entries for a specific build:
> ```bash
> cat ~/vsm-fitness-builds/coach/FB[N]/.kimi/knowledge-broker-log.md
> ```

---

*Digest populated during comprehensive audit: 2026-06-02*
*Next update expected: after FB26 fitness build or next gym batch*

---

## Entry: FB27 — 2026-06-02

**Build**: FB27 (Tier 2, domain unknown)
**Score**: 3.4/5.0
**Stack**: FastAPI + SQLAlchemy 2.0 + Strawberry GraphQL + Celery + Redis + PostgreSQL | React 18 + Vite + Apollo Client v3 + Zustand

### Key Learnings
1. **H302 CONFIRMED**: Session-end audit catches residual bypasses (missing mutations-applied.md, missing process-audit.md)
2. **Score trend alarm T6 triggered**: 4.0→3.6→3.4 downward trend continues
3. **Architecture→implementation handoff weakest link**: Foundation, Architecture, Implementation all scored 3/5

### Mutations Applied
- FB27-1: UUID coercion via `model_validator` — **INEFFECTIVE** (ORM path bypassed)
- FB27-2: Missing `await` guard — **EFFECTIVE**
- FB27-3: JWT placeholder prevention — **EFFECTIVE**
- FB27-4: GraphQL RBAC parity — **EFFECTIVE**

---

## Entry: FB28 — 2026-06-03

**Build**: FB28 EduLearn (Tier 2+)
**Score**: 3.8/5.0
**Stack**: FastAPI + SQLAlchemy 2.0 + Strawberry GraphQL + Celery + Redis + PostgreSQL + MinIO | React 18 + Vite + Apollo Client v3 + Zustand

### Key Learnings
1. **H214 CONFIRMED**: Check 16 early handoff verification caught auth raw-dict in Phase 2b, zero Phase 3c handoff BLOCKERs
2. **H217 CONFIRMED**: Agent timeout is primary drag on Tier 2+ scores — 5 timeouts forced heavy S5 manual intervention
3. **H215 CONFIRMED**: vsm_meta file verification protocol works — zero hallucinations
4. **Downward trend reversed**: 3.4→3.8 (first improvement after 3-build decline)

### Metrics
- Backend tests: 40 passed, 0 failed
- Frontend tests: 82 passed, 34 failed (test setup issues, not app bugs)
- Agent timeouts: 5/10 (CRITICAL — primary score drag)
- BLOCKERs: 1 code-level (GraphQL context getter lambda)
- Fix iterations: 1 fix wave + security re-check

### Mutations Applied
- H217: Agent task sizing ≤500 lines per spawn (SKILL.md Phase 2)
- H218: GraphQL context getter must be imported function (graphql-pitfalls)
- H219: Pydantic `type` statement + `Field(alias=...)` warning (python-pitfalls)
- FB28-S3: Phase 2d Check 16 mandatory for Tier 2+ (structural)
- FB28-S4: Agent task sizing for Tier 2+ (structural)
- FB28-S5: Agent timeout fallback protocol (structural)

---

## Entry: FB29 — 2026-06-03

**Build**: FB29 ContentStream (Tier 2)
**Meta-Report Score**: 4.2/5.0 (code quality)
**Trainer Score**: 3.6/5.0 (independent evaluation)
**Process Compliance**: 60/100 — **FAILED fitness bar** (threshold: ≥80)
**Fitness Result**: FAILED
**Stack**: FastAPI + SQLAlchemy 2.0 + Strawberry GraphQL + Celery + Redis + PostgreSQL + MinIO | React 18 + Vite + Apollo Client v3 + Zustand

### Key Learnings
1. **H217 CONFIRMED**: Task splitting to <500 lines per agent eliminated all timeouts (0 vs FB28's 5)
2. **Python 3.14 enum breaking change**: `str(Enum.member)` now returns `"Class.member"` — broke role comparisons across 4 files
3. **GraphQL security parity gap (recurring)**: Mutations lack validation/ownership checks that REST enforces — pattern across FB25-FB29
4. **Module-level engine trap**: `create_async_engine()` at module level causes import side-effects — recurring across builds
5. **CRITICAL: Meta-report false claims**: vsm_meta claimed re-audit-report existed when it didn't. Process auditor never spawned during build.
6. **Process violations**: re-audit-report.md missing, process auditor retroactive, broker/mutation-state not updated

### Metrics
- Backend tests: 36/36 pass
- Frontend tests: 30/30 pass
- Agent timeouts: 0/32
- BLOCKERs found: 8 (all fixed)
- HIGH findings: 3 (all fixed)
- Process violations: 7 (2 CRITICAL, 2 HIGH, 3 MEDIUM)

### Mutations Proposed
- M1: GraphQL security parity rule (security-patterns)
- M2: Python 3.14 enum rule (python-pitfalls)
- M3: Module-level engine rule (sqla-patterns)
- M4: GraphQL mutation test templates (tester-backend)
- M5: JWT library confusion rule (python-pitfalls)
- M6: Split audit into REST/GraphQL passes (process)
- M7: Enum .value checklist (Phase 2a)

---

## Entry: UNKNOWN — 2026-06-04

**Build**: UNKNOWN
**Score**: N/A
**Process Audit**: N/A
**Domain**: N/A

### Key Learnings


### Mutations Applied
- ## Mutation PM1 — 2026-06-04 (Structural — USER APPROVED via trainer)
- ## Mutation PM2 — 2026-06-04 (Append-Only — Autonomous, trainer-proposed)
- ## Mutation PM3 — 2026-06-04 (Structural — USER APPROVED via trainer)
- ## Mutation PM4 — 2026-06-04 (Append-Only — Autonomous, trainer-proposed)
- ## Mutation PM5 — 2026-06-04 (Append-Only — Autonomous, trainer-proposed)

### Cross-Skill Findings
- (Auto-populated — review and expand manually if needed)

---

## Entry: FB31 — 2026-06-04

**Build**: FB31 RecipeHub
**Score**: 3.8/5.0
**Process Audit**: 42/100 (improved to ~70 after artifact backfill)
**Domain**: Recipe sharing, meal planning, shopping lists

### Key Learnings
1. **Architect 3-spawn split insufficient**: api-spec.md (2085 lines) still exceeds agent capacity. 4-spawn split now required.
2. **GraphQL schema ↔ frontend query decoupling**: Coordinator missed 10+ non-existent fields. Schema introspection check added to coordinator prompt.
3. **Phase 4 gate inflation**: S5 copied unverified test counts. Persistent pytest report now required.
4. **Tester 2-sub-wave split insufficient**: Split 2 still timed out. 3-sub-wave split now required.
5. **Security gate excellence**: 0 BLOCKERs/CRITICAL/HIGH on 4-service build with REST, GraphQL, WebSocket, Celery.

### Mutations Applied
- FB31-1: Architect 4-spawn split (structural redesign)
- FB31-2: Tester 3-sub-wave split (structural redesign)
- FB31-3: Coordinator GraphQL introspection check (append-only)
- FB31-4: Phase 4 persistent pytest report (append-only)
- FB31-5: Knowledge broker auto-update reminder (append-only)

### Cross-Skill Findings
- `graphql-pitfalls`: Need rule about frontend query validation against backend schema
- `testing-patterns`: SQLite async conftest pattern works but shared DB file causes suite-level lock contention
- `security-patterns`: All 5 critical traps passed — security agent performing at target level
