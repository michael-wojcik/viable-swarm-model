# VSM Knowledge Broker — Cross-Skill Digest

> **Updated by**: S5 during Phase 8 / coach Phase 5 / gym Phase 5 (curated tables)
> **Read by**: All three skills at Phase 0 (MANDATORY)
> **Schema version**: 1.2
> **Last updated**: 2026-06-06

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
| G10 | GraphQL security parity gap | FB25 | FB29 | M1 | **PARTIALLY RESOLVED** — FB34 achieved parity after fix wave; needs test enforcement to sustain |
| G16 | Frontend security source scan gap | FB34 | FB34 | FB34-A1 | **ACTIVE** — `vsm_security` did not scan `frontend/src/**/*.ts*`; missed localStorage JWT, fallback URIs |
| G17 | GraphQL mutation test coverage gap | FB34 | FB34 | FB34-A2 | **ACTIVE** — 33/33 tests passed while 6 mutations returned `INTERNAL_ERROR` |
| G18 | Mandatory stack skill read gap | FB34 | FB34 | FB34-A3 | **ACTIVE** — `sqla-patterns`, `backend-patterns`, `frontend-patterns`, `testing-patterns`, `tester-backend` not cited as read |

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
| FB31-5 | Knowledge broker auto-update reminder | FB34 | FB34 | **REDESIGNED** — manual reminder ineffective; to be replaced by tool-enforced session-end backfill (FB34-C1) |
| FB34-1 | GraphQL mutation completeness checklist | FB34 | FB34 | **REDESIGNED** — prompt-only checklist ignored; to be replaced by `scripts/check-graphql-stubs.py` (FB34-C1) |
| FB34-2 | GraphQL session cleanup extension pattern | FB34 | FB34 | **REDESIGNED** — prompt-only pattern ignored; to be enforced by hard-gates script (FB34-C1) |
| FB34-3 | SocketProvider authenticate event protocol | FB34 | FB34 | **REDESIGNED** — prompt-only protocol ignored; to be enforced by hard-gates script (FB34-C1) |

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
| All → Broker | ✅ Functional | Updated 2026-06-04 with FB27-FB29 entries, gym batch results, and curated tables |

---

## Coach Action Items (Gym → Coach Feedback Loop)

| Experiment | Hypothesis Confirmed? | Recommended Coach Build Focus | Priority |
|---|---|---|---|
| E17 | H107: Domain fix agents outperform generic — CONFIRMED | Test domain-specific fix agents (vsm_backend_fix_agent, vsm_frontend_fix_agent) in comprehensive build context | HIGH |
| Gym-Batch-FB32 | H150: Dependency verification prevents bad imports — CONFIRMED | Verify backend coders check requirements.txt before adding imports | MEDIUM |
| Gym-Batch-FB32 | H151: Pydantic `class Config:` deprecated — CONFIRMED | Verify backend coders use `ConfigDict` exclusively | MEDIUM |
| Gym-Batch-FB32 | H154: `npm run build` as Phase 4 hard gate — CONFIRMED | Verify frontend builds run `npm run build` before Phase 5 | HIGH |

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


---

## Gym Batch Results — FB32 (2026-06-04)

**Batch**: 8 oldest untested hypotheses (H104, H150-H156)
**Tested**: 3/8 (H150, H151, H154) — top 3 by impact
**Deferred**: 5/8 (H104, H152, H153, H155, H156) — next batch

### Confirmed Hypotheses

| Hypothesis | Result | Experiment | Skill Mutation Applied |
|---|---|---|---|
| **H150**: Verify dependencies against requirements.txt before importing | ✅ CONFIRMED | `fake_package` import → `ModuleNotFoundError` | Strengthened `python-pitfalls` "Dependency Manifest Drift" to BLOCKER with explicit pre-import check |
| **H151**: Elevate Pydantic `class Config:` from ISSUE to BLOCKER | ✅ CONFIRMED | `class Config:` → `PydanticDeprecatedSince20` warning; `-W error` breaks build | Strengthened `python-pitfalls` "Pydantic ConfigDict" to BLOCKER with `pytest -W error::DeprecationWarning` recommendation |
| **H154**: `npm run build` as Phase 4 hard gate | ✅ CONFIRMED | Unused import passes Vitest but fails `tsc -b` (`TS6133`) | Added `testing-patterns` rule: "Frontend `npm run build` as Phase 4 Hard Gate" |

### Key Findings

1. **All 3 confirmed hypotheses had related rules already in skills**, but they were
too weak (ISSUE-level or advisory). The gym experiments provided empirical evidence
to justify elevating them to BLOCKER-level enforcement.

2. **H154 is the highest-impact**: Without `npm run build` as a hard gate, TypeScript
errors leak from Phase 4 → Phase 6, wasting the most agent time. FB23 experienced this.

3. **H150 and H151 are preventable at the coder level**: If the backend coder prompt
explicitly checks requirements.txt before adding imports and rejects `class Config:`,
these failure modes disappear.

### Remaining Untested (Next Batch)

| Hypothesis | Status | Rationale |
|---|---|---|
| H104: ApolloClient `uri` parameter stderr noise | untested | Frontend-specific, lower impact |
| H152: Pre-build environment smoke tests | untested | Env-specific, partially addressed by Phase 0 checks |
| H153: Vite alias key `"@"` vs `"@/"` | untested | Already in `typescript-pitfalls` as BLOCKER |
| H155: Module-level settings audit across ALL files | untested | Backend-specific, wiring agent partially addresses |
| H156: Dependency manifest-environment parity | untested | Env-specific, related to H150 |

**Backlog after this batch**: 19 untested hypotheses (was 22, now 19)
**Algedonic status**: WARNING (backlog reduced from CRITICAL to below 20)

*Updated: 2026-06-04*

---

*End of broker.*

---

## Gym Batch Results — E21-E23 (2026-06-06)

**Batch**: 3 hypotheses (H202, H201, H155) — selected by auto-gym-trigger + active gap prioritization
**Tested**: 3/3
**Confirmed**: 1 (H201)
**Rejected**: 1 (H155)
**Not confirmed**: 1 (H202)

### Results

| Experiment | Hypothesis | Result | Mutation Applied |
|---|---|---|---|
| **E21** | H202: Tool-enforced read-only boundaries > prompt-only | **NOT CONFIRMED** | None — gap discovered (WriteFile in auditor tool list) but structural mutation blocked by re-audit-report.md requirement |
| **E22** | H201: Custom agent files reduce context >30% | **CONFIRMED** | None — validates existing architecture (85.2% reduction) |
| **E23** | H155: Exhaustive module-level settings audit catches 100% | **REJECTED** | None — `vsm_wiring` already checks all `*.py` files |

### Key Findings

1. **H201 is the highest-impact validation**: Custom agent files save 85.2% of per-subagent task prompt characters. In a typical Tier 2+ build with 6-12 backend coder spawns, this avoids injecting 11,500-23,000 redundant characters into context.

2. **H202 reveals latent risk**: The prompt-only boundary worked in this single test, but `WriteFile` IS available in `vsm_auditor.yaml`. The auditor's prompt even trains it to use `WriteFile` for `.kimi/re-audit-report.md`. Under stronger social engineering or context pressure, the boundary could blur. A future experiment with multiple stress-test variants (varying social engineering intensity) is needed to truly test this hypothesis.

3. **H155 validates existing capability**: The wiring agent already performs exhaustive module-level instantiation audits. The FB23 miss was an execution lapse, not a systematic checklist gap.

### Remaining Untested (Next Batch)

| Hypothesis | Status | Rationale |
|---|---|---|
| H104: ApolloClient `uri` parameter stderr noise | untested | Frontend-specific, lower impact |
| H152: Pre-build environment smoke tests | untested | Env-specific, partially addressed by Phase 0 checks |
| H153: Vite alias key `"@"` vs `"@/"` | untested | Already in `typescript-pitfalls` as BLOCKER |
| H156: Dependency manifest-environment parity | untested | Env-specific, related to H150 |
| H[N+3]: Native YAML custom subagents | untested | Large-scope structural experiment |
| H[N+4]: Full product swarm | untested | Requires 10+ problem-oriented prompts |

**Backlog after this batch**: 6 untested hypotheses (was 9, now 6)
**Algedonic status**: ✅ OK (backlog well below 10)

### Coach Action Items

| Experiment | Hypothesis Result | Recommended Coach Build Focus | Priority |
|---|---|---|---|
| E22 | H201 CONFIRMED — 85.2% context reduction | No action needed; validates architecture | LOW |
| E21 | H202 NOT CONFIRMED — latent auditor boundary risk | Design build with explicit "auditor fix request" trap to stress-test boundary under real context pressure | MEDIUM |
| E23 | H155 REJECTED — wiring already exhaustive | Verify wiring agent checklist execution in next build (not just capability) | LOW |

*Updated: 2026-06-06*

---

## Fitness Build FB33 — StreamLine (2026-06-06)

**Build type**: Coach build (Tier 2, content streaming platform)
**Score**: 3.5 / 5.0 (trainer rubric) | 6.3 / 10 (meta-evaluation)
**Agents spawned**: 15+ (product, variety, architect×4, backend, frontend, wiring, coordinator, tester×2, devops, security, fix×3, meta, process auditor)
**Timeouts**: 0 (FB31-1 4-spawn split validated)
**Tests**: 25 backend ✅, 23 frontend ✅, build ✅

### New Active Gaps

| ID | Gap | Severity | Mutations Applied |
|---|---|---|---|
| G11 | Frontend 0% GraphQL usage despite complete layer | ISSUE | FB33-2 (frontend-patterns append-only) |
| G12 | Socket.IO wired but zero server-side emissions | ISSUE | FB33-3 (backend-patterns append-only) |
| G13 | Insecure defaults in `os.environ.get(..., default)` outside Settings classes | HIGH | FB33-1-EXT (security-patterns append-only), structural hook approved |
| G14 | Process artifact staleness post-fix wave | MEDIUM | FB33-4-PROPOSED (append-only checklist) |
| G15 | Cross-layer dead code undetected | ISSUE | integration-patterns skill created (structural, approved) |

### Key Findings

1. **Prompt-only mutations are hitting a ceiling**: FB32-1 (Zero-Default) failed for the second consecutive build. Three non-empty defaults escaped. Tool-enforced shell hook `check-zero-defaults.sh` created as structural mutation.

2. **Architect/tester task splitting is highly effective**: Zero timeouts across 15+ agents. FB31-1 and FB31-2 are validated.

3. **GraphQL RBAC parity achieved**: REST and GraphQL enforce identical role/ownership checks after fixes. Historical weakness closed.

4. **Backend tester caught production-breaking bug**: `AsyncSessionLocal(bind=engine)()` double-call would have broken every content endpoint. Test-first discipline validated.

### Mutations Applied

| Mutation | Type | File | Status |
|---|---|---|---|
| FB33-1-EXT | append-only | `security-patterns/SKILL.md` | Applied |
| FB33-2 | append-only | `frontend-patterns/SKILL.md` | Applied |
| FB33-3 | append-only | `backend-patterns/SKILL.md` | Applied |
| FB33-5 | structural | `hooks/check-zero-defaults.sh` | **User approved**, created |
| FB33-6 | structural | `integration-patterns/SKILL.md` | **User approved**, created |

### Hypotheses Tested

| Hypothesis | Result | Evidence |
|---|---|---|
| H213 (mutation-state not updated) | **CONFIRMED** — S5 only updated after process audit flagged gap | mutation-state.md updated post-audit |
| H217 (agent task sizing prevents timeouts) | **CONFIRMED** — zero timeouts with 4-spawn split | 1,601 design docs, 15+ agents |

### New Hypotheses Proposed

- H400: Tool-enforced shell hooks > prompt-only for Zero-Default
- H401: GraphQL mandate prevents 100% REST dead code
- H402: Socket.IO emission checklist prevents non-functional real-time
- H403: Pre-closeout artifact gate prevents missing Phase 8 artifacts
- H404: Fix agents must update stale `.kimi/` artifacts post-resolution

*Updated: 2026-06-06*

---

*End of broker.*

---

## Fitness Build FB34 — ShipTrack (2026-06-06)

**Build type**: Coach build (Tier 2, multi-tenant logistics/fleet management)
**Score**: 4.0 / 5.0 (trainer rubric) | Process audit 100/100
**Agents spawned**: 15+ (variety, architect×4, backend, frontend, wiring, coordinator, tester×2, devops, security, fix×2, meta, process auditor)
**Timeouts**: 0 (4-spawn architect split and 2-sub-wave tester split validated)
**Tests**: 33 backend ✅, 4 frontend ✅, frontend build ✅

### New Active Gaps

| ID | Gap | Severity | Mutations Applied |
|---|---|---|---|
| G16 | Frontend security source scan gap | MEDIUM | FB34-A1 (append-only, proposed) |
| G17 | GraphQL mutation test coverage gap | MEDIUM | FB34-A2 (append-only, proposed) |
| G18 | Mandatory stack skill read gap | MEDIUM | FB34-A3 (append-only, proposed) |

### Resolved or Downgraded Gaps

| ID | Gap | Resolution |
|---|---|---|
| G10 | GraphQL security parity gap | **RESOLVED in FB34** — REST and GraphQL RBAC/tenant/ownership checks aligned after fix wave |
| G13 | Insecure defaults outside Settings | **CONTAINED** — FB33-1-EXT extension caught the recurrence; tool hook `check-zero-defaults.sh` now enforced |

### Key Findings

1. **Prompt-only mutations are hitting a hard ceiling**: FB34-1, FB34-2, FB34-3 (all prompt-only probation mutations) were ignored until Phase 6 audit. Removal gate triggered. Consolidation structural mutation FB34-C1 proposes tool-enforced `scripts/integration-hard-gates.py`.

2. **All 5 deliberate traps caught or documented**: T1 (zero-default) caught by foundation auditor; T2 (GraphQL unwired frontend) caught by coordinator; T3 (zero Socket.IO emissions) caught by coordinator; T4 (dead code) caught by coordinator; T5 (Phase 8 pressure) prevented by mutation checkpoint discipline.

3. **Agent performance polarized**: `vsm_coordinator`, `vsm_auditor`, `vsm_wiring`, `vsm_backend_fix_agent` scored 5/5. `vsm_backend_coder` (3/5) shipped 6 GraphQL stubs. `vsm_devops_coder` (3/5) shipped broken realtime command and missing Dockerfile USER.

4. **Process audit perfect score**: 100/100 compliance, zero HARD BLOCKs. Phase 8 artifacts (lessons.md, mutations-applied.md, meta-report.md, process-audit.md) all produced.

### Mutations Applied

| Mutation | Type | File | Status |
|---|---|---|---|
| FB33-1-EXT | append-only | `security-patterns/SKILL.md` | Measured effective (5/5) in FB34 |
| FB33-2 | append-only | `frontend-patterns/SKILL.md` | Measured effective (5/5) in FB34 |
| FB33-3 | append-only | `backend-patterns/SKILL.md` | Measured effective (5/5) in FB34 |
| FB33-6 | structural | `integration-patterns/SKILL.md` | Measured effective (5/5) in FB34 |
| FB31-1 | structural | `agents/vsm_architect.md` | Measured effective (5/5) in FB34 |
| FB31-2 | structural | `agents/vsm_backend_tester.md` | Measured effective (4/5) in FB34 — 2-sub-wave sufficient, 3-sub-wave may be safer |
| FB31-3 | append-only | `agents/vsm_coordinator.md` | Measured effective (4/5) in FB34 |
| FB31-4 | append-only | `agents/vsm_backend_tester.md` | Measured effective (5/5) in FB34 |
| FB31-5 | append-only | `agents/vsm_meta.md` | **INEFFECTIVE** (2/5) — manual reminder ignored |
| FB32-1 | append-only | `security-patterns/SKILL.md` | **INEFFECTIVE** (2/5) — caught only by extension FB33-1-EXT |
| FB32-2 | append-only | `graphql-pitfalls/SKILL.md` | Measured effective (5/5) in FB34 |
| FB34-1 | append-only | `agents/vsm_backend_coder.md` | **INEFFECTIVE** (2/5) — prompt-only checklist ignored |
| FB34-2 | append-only | `agents/vsm_backend_coder.md` | **INEFFECTIVE** (2/5) — prompt-only pattern ignored |
| FB34-3 | append-only | `agents/vsm_frontend_coder.md` | **INEFFECTIVE** (2/5) — prompt-only protocol ignored |

### Proposed Closeout Mutations (Phase 8b)

- **FB34-C1** (structural): Tool-enforced integration hard-gates script; consolidates FB31-5 + FB34-1/2/3.
- **FB34-C2** (structural): Mandatory frontend fix-agent sign-off.
- **FB34-A1** (append-only): Security agent frontend source scan.
- **FB34-A2** (append-only): GraphQL mutation test coverage floor.
- **FB34-A3** (append-only): Mandatory stack skill reads.
- **FB34-R1** (refinement): Skill variety tracker parses agent reports.

### Hypotheses Tested

| Hypothesis | Result | Evidence |
|---|---|---|
| H401 (tool-enforced stub detection) | **UNTESTED** | Proposed; experiment in FB35+ |
| H217 (agent task sizing) | **CONFIRMED** — 4-spawn architect + 2-sub-wave tester, zero timeouts | 1,600+ design lines, 33 tests, 15+ agents |

### New Hypotheses Proposed

- H401–H406 (see `references/hypotheses.md`)

*Updated: 2026-06-06*

---

*End of broker.*


---

## FB35 ShipTrack Regression Build — 2026-06-08

### Score
- **FB35**: 3.0/5.0
- **Gold standard (FB34)**: 4.0/5.0
- **Delta**: -1.0 (SIGNIFICANT regression)

### Primary Finding: Agent Runtime Reliability Crisis
The skill's rulebook is sound; the agent execution layer is broken. Background agent session isolation causes:
1. **CWD drift**: 5/8 agents wrote files to wrong directories
2. **Post-write hang loops**: 6 agents hung after completing deliverables
3. **S5 manual work avalanche**: ~15 files written by S5 (far exceeding 1-file cap)

### Mutations Measured
- FB31-1: Redesigned (3/4 architect spawns hung despite 400-line limit)
- FB33-1-EXT: Ineffective (T1 trap present in celery_app.py)
- FB33-3: Ineffective (T3 Socket.IO trap confirmed)
- FB33-5: Ineffective (shell hook not auto-invoked for background agents)
- FB34-C1: Ineffective (script exists but not wired into build flow)
- FB34-A1: Ineffective (security agent did not scan frontend)
- FB34-A2: Ineffective (0 GraphQL tests; only 3 trivial smoke tests)
- FB34-R1: Ineffective (not observable in build artifacts)

### New Mutations Applied
- **FB35-1** (structural): Absolute path requirement for all background agent WriteFile operations
- **FB35-2** (structural): Termination rule to prevent post-write hang loops

### New Hypotheses
- H500: Background agent cwd drift due to session isolation
- H501: Agent hangs correlate with Shell verification failures
- H502: Explicit termination rule prevents post-write hang loops

### Recommendation
HALT regression builds until H500/H501 are validated via gym experiment. The -1.0 delta reflects agent infrastructure failure, not skill rule degradation. Code quality from agents that completed (vehicles.py, models.py) remains excellent (5/5).

*Updated: 2026-06-08*

---

*End of broker.*
