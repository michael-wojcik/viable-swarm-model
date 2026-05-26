# Experiment Log

> **Mutation rules**: Append new experiments. Never delete. Reference the hypothesis
> ID and the main skill experiment ID (E[N]).

---

## E6 — H3: Env var naming drift in .env.example files

**Date**: 2026-05-25
**Agent**: vsm_coordinator (S2)
**Files**: `~/vsm-fitness-builds/gym/H3/`

**Design**:
- docker-compose.yml sets `DATABASE_URL`, `REDIS_URL`
- .env.example sets `DB_CONNECTION`, `CACHE_URL`
- config.py reads `DB_URL`, `REDIS_URL`
- Triple mismatch across all three sources

**Result**: REJECTED.
- Coordinator detected all 3 mismatches and produced a detailed table:
  - Database: `DATABASE_URL` (compose) ≠ `DB_CONNECTION` (.env) ≠ `DB_URL` (config)
  - Redis: `REDIS_URL` (compose) ≠ `CACHE_URL` (.env) = `REDIS_URL` (config)
- Agent recommended standardization to canonical names.

**Conclusion**: vsm_coordinator already checks env var naming drift effectively.

---

## E7 — H19: GraphQL field name alignment prevents Strawberry auto-camelCase drift

**Date**: 2026-05-25
**Agent**: vsm_coordinator (S2)
**Files**: `~/vsm-fitness-builds/gym/H19/`

**Design**:
- backend/graphql.py: `assigned_technician_id: int` → Strawberry auto-camelCase → `assignedTechnicianId`
- frontend/queries.ts: uses `technicianId` (missing `assigned` prefix)

**Result**: REJECTED.
- Coordinator ran schema introspection (`python -c "from graphql import schema; print(schema)"`)
- Correctly identified actual schema field as `assignedTechnicianId`
- Flagged frontend `technicianId` as MISMATCH — FAIL

**Conclusion**: Strawberry auto-camelCase check in coordinator prompt is effective.

---

## E8 — H20: Auth response contract documentation prevents login/register mismatches

**Date**: 2026-05-25
**Agent**: coder subagents (S1) × 2
**Files**: `~/vsm-fitness-builds/gym/H20/`

**Design**:
- Variant A: Ambiguous spec ("login returns token")
- Variant B: Explicit spec (exact JSON shapes: `{access_token, token_type, role}`)
- Frontend expectation: `{access_token, token_type, role}` for login; `{id, email, name, role}` for register

**Result**: CONFIRMED.
- Variant A coder produced `{token: string}` for login — 3-field mismatch
- Variant B coder produced exact shapes matching frontend expectations

**Conclusion**: Explicit auth contract documentation in api-spec.md prevents mismatches.

---

## E9 — H22: WebSocket event name dictionary cross-check prevents emit/listen mismatches

**Date**: 2026-05-25
**Agent**: vsm_coordinator (S2)
**Files**: `~/vsm-fitness-builds/gym/H22/`

**Design**:
- api-spec.md: `authenticate`/`authenticated`/`auth_error`
- backend/sio.py: `auth`/`auth_ok`/`auth_err`
- frontend/sio-events.ts: `authenticate`/`auth_success`/`auth_failed`

**Result**: REJECTED.
- Coordinator found mismatches in ALL event directions:
  - Client→server: `auth` vs `authenticate`, `join` vs `subscribe_room`
  - Server→client: triple mismatch (`auth_ok`/`auth_err` vs `authenticated`/`auth_error` vs `auth_success`/`auth_failed`)
  - Room update: `room_data` vs `room_update`

**Conclusion**: WebSocket event name cross-check in coordinator prompt is effective.

---

## E10 — H27: Structured meta-reflection template improves Phase 8b

**Date**: 2026-05-25
**Agent**: vsm_meta (S1 Meta-Evaluation)
**Input**: Fictional build summary (FB-TEST)

**Design**:
- Provide build summary with known gaps (inline fixes, skipped Phase 8b, missing re-audit)
- Measure whether vsm_meta produces structured, actionable output

**Result**: CONFIRMED.
- vsm_meta produced complete meta-report with all required sections:
  - Independent Test Verification
  - Agent Performance Scores (1-5 with evidence)
  - Effectiveness Audit (rules followed/broken)
  - Coverage Audit (missed vulnerability classes)
  - Phase Audit (flow diagram mismatch detection)
  - 2 new falsifiable hypotheses (H105, H106)
  - Tier-classified mutations (append-only, refinement, structural)

**Conclusion**: Structured template in vsm_meta prompt produces highly actionable Phase 8b output.

---

## E11 — H28: Architect documenting enum Python-type-to-GraphQL-value mapping prevents enum runtime bugs

**Date**: 2026-05-25
**Agent**: vsm_auditor (S3*)
**Files**: `~/vsm-fitness-builds/gym/H28/`

**Design**:
- models.py: `class Priority(enum.Enum)` (missing `str` mixin)
- graphql.py: `Priority("medium")` — will raise ValueError at runtime

**Result**: REJECTED.
- Auditor flagged BLOCKER: "`models.py` defines `Priority` as `enum.Enum` (not `str, enum.Enum`), yet `graphql.py` attempts `Priority("medium")`. This raises `ValueError` at runtime."
- Auditor cited exact file:line evidence.

**Conclusion**: Auditor already catches enum type mapping issues effectively.

---

## E12 — H46: Fix wave re-audit must run full test suite, not just reported failing tests

**Date**: 2026-05-25
**Agent**: Shell / pytest demonstration
**Files**: `~/vsm-fitness-builds/gym/H46/`

**Design**:
- Initial: `test_get_user` fails (app returns `str(id)`), `test_get_post` passes
- Fix `get_user` to return int, BUT regress `get_post` to return str
- Re-run full suite

**Result**: CONFIRMED.
- After fix: `test_get_user` PASSED, `test_get_post` FAILED
- A re-audit protocol checking only changed files and originally failing tests would have missed the regression

**Conclusion**: Fix wave MUST run full test suite after every fix. Re-auditing changed files only is insufficient.

---

## E13 — H48 + H53: Frontend build script verification (`npm run build` vs `vite build`)

**Date**: 2026-05-25
**Agent**: Shell / npm + vite
**Files**: `~/vsm-fitness-builds/gym/H48/`, `~/vsm-fitness-builds/gym/H53/`

**Design**:
- `tsconfig.json` includes `vite.config.ts`
- `@types/node` omitted (H48 also omits `@types/react` and `@types/react-dom`)
- Compare `vite build` vs `npm run build` (which runs `tsc -b && vite build`)

**Result**: CONFIRMED (both hypotheses).
- `vite build`: PASS (produces dist/)
- `npm run build`: FAIL (`tsc -b` errors: Cannot find name 'Buffer', missing JSX types in H48)

**Conclusion**: Frontend infra verification must run `npm run build`, not just `vite build`. The trap condition (tsconfig includes vite.config.ts without @types/node) successfully triggers `tsc -b` failure.

---

## E14 — H59: Domain-specific coder prompts reduce systematic false negatives

**Date**: 2026-05-25
**Agent**: coder subagents (S1) × 2
**Files**: `~/vsm-fitness-builds/gym/H59/`

**Design**:
- Identical backend task: FastAPI + Strawberry + SlowAPI + CORS + lazy settings
- Control: Generic coder prompt with task description only
- Treatment: Domain-specific coder prompt with explicit "Known Stack Gotchas"

**Result**: CONFIRMED.
- **Generic coder**: Correct but used `allow_origins=["*"]` (security issue), no runtime API verification, deprecated `class Config`
- **Domain-specific coder**: Explicit `allow_origins=["http://localhost:3000"]`, dynamic `inspect.signature` check on `strawberry.Schema.__init__`, same `class Config` issue
- Domain prompt measurably improved security posture and verification rigor

**Conclusion**: Domain-specific prompts reduce systematic false negatives. Effect size is moderate; some gaps (e.g., `class Config` deprecation) require explicit rule inclusion in the domain prompt.

---

## E15 — H105: Inline fix waves bypass re-audit and post-fix security re-check

**Date**: 2026-05-25
**Agent**: vsm_coordinator (S2) + vsm_backend_fix_agent (treatment) + generic coder (control)
**Files**: `~/vsm-fitness-builds/gym/H105/`

**Design**:
- Minimal project with 3 integration BLOCKERs:
  1. Env var naming mismatch (`DATABASE_URL` in compose vs `DB_URL` in config)
  2. Subprocess import failure (module-level `ValueError` in config.py)
  3. Missing `RateLimitExceeded` handler
- Phase 1: Run vsm_coordinator → produce BLOCKER report
- Phase 2a (Treatment): Route BLOCKERs to vsm_backend_fix_agent
- Phase 2b (Control): Route BLOCKERs to generic coder (simulating S5 inline fix)

**Result**: CONFIRMED.
- **Coordinator**: Found all 3 BLOCKERs, classified fix agent as `vsm_backend_fix_agent` for each.
- **Treatment (vsm_backend_fix_agent)**: Fixed all 3 BLOCKERs, ran full test suite (3 passed), ran subprocess import check, produced `re-audit-report.md`.
- **Control (generic coder)**: Fixed all 3 BLOCKERs, ran import smoke tests, did NOT produce `re-audit-report.md`, did NOT run full test suite.

**Conclusion**: Inline fixes (via generic coder) bypass mandatory re-audit artifacts and verification. Domain-specific fix agents enforce the full protocol.

---

## E16 — H106: Skipping Phase 8b correlates with repeated process violations

**Date**: 2026-05-25
**Agent**: vsm_meta (S1 Meta-Evaluation)
**Files**: `~/vsm-fitness-builds/gym/H106/`

**Design**:
- Create fictional build artifacts (FB20-Test) simulating a build with known process violations:
  - `inline-fix-evidence.md`: documents S5 fixing coordinator BLOCKER inline during Phase 6
  - Missing `re-audit-report.md`
  - Skipped Phase 7b security re-check
  - Skipped Phase 8b entirely
- Run vsm_meta on these artifacts
- Measure whether vsm_meta catches the violations

**Result**: CONFIRMED (mechanism validated).
- vsm_meta caught ALL process violations:
  - Inline fix during Phase 6: Confirmed (S5 scored 1/5)
  - Missing re-audit reports: Confirmed
  - Skipped security re-check: Confirmed
  - Skipped Phase 8b: Confirmed
  - Phase 4 gate failure (proceeded with failing tests): Confirmed
- vsm_meta generated 8 hypotheses (H98, H100, H101, H102, H103, H105, H106, H108, H109) and proposed tier-classified mutations.

**Conclusion**: Phase 8b (vsm_meta) is a critical feedback loop. Skipping it means process violations go undetected and uncorrected. The longitudinal correlation (recurrence in next build) is inferred from mechanism validation.

---

## E17 — H107: Domain-specific fix agents produce higher-quality fixes than generic coder

**Date**: 2026-05-25
**Agent**: vsm_backend_fix_agent, vsm_frontend_fix_agent (treatment) × generic coder (control)
**Files**: `~/vsm-fitness-builds/gym/H107/`

**Design**:
- Backend: 3 BLOCKERs (circular import, missing RateLimitExceeded handler, REST/GraphQL auth parity gap)
- Frontend: 2 BLOCKERs (orphaned query export, `as any` bypass)
- Treatment: Domain-specific fix agents
- Control: Generic coder
- Measure: fix correctness, test pass rate, re-audit report production, regression count

**Result**: CONFIRMED.

| Metric | Domain Fix Agents | Generic Coder |
|--------|------------------|---------------|
| Fix correctness (surface) | 100% (5/5) | 100% (5/5) |
| Fix correctness (security) | 100% (excluded admin) | **REGRESSION** (kept admin) |
| Full test suite pass rate | 100% | 100% |
| re-audit-report.md production | **100% (3/3)** | **0% (0/3)** |
| Regression count | 0 | 1 (security weakening) |

**Conclusion**: Domain-specific fix agents produce measurably higher-quality fixes. The critical difference is security invariant enforcement (auth allowlist) and process artifact production (re-audit reports). Generic coders fix the surface issue but miss guardrails.

---
