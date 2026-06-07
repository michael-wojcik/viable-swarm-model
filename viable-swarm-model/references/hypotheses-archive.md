# Hypothesis Archive

> **Mutation rules**: Append archived hypotheses with full provenance. Never edit —
> the archive is an auditable record of what was tested, what was confirmed,
> and what was rejected. Prevention rules from confirmed hypotheses are
> absorbed into `pattern-library.md` and/or `python-pitfalls/SKILL.md`.

---

## Confirmed

### H40: GraphQL RBAC parity with REST endpoints

**Status**: confirmed
**Proposed**: 2026-05-22
**Rationale**: GraphQL resolvers often lack the same access controls as REST
endpoints because they are written separately by different agents.
**Source**: Multiple fitness builds (FB4, FB10, FB21, FB24)
**Experiment**: Build with both REST and GraphQL. Auditor checks parity table.
**Expected**: 100% parity on admin-only mutations and ownership-filtered list queries.
**Tested by**: FB25
**Result**: GraphQL `delete_budget` admin-only (matches REST). All list queries
filter by `user_id` unless admin. Parity table: pass.

**Prevention rule absorbed into**: `pattern-library.md` — "Pattern: Explicit RBAC Arrays in api-spec.md"

---

### H157: Frontend pages generated as stubs (void-referenced imports, no real logic) correlate with missed integration checklist items

**Status**: confirmed
**Proposed**: 2026-05-26
**Rationale**: FB23 frontend pages (Dashboard, Jobs, Candidates, etc.) are all `<div>Name</div>` stubs. The integration report still PASSed them because they exist and routes are wired, not because they implement functionality.
**Source**: Fitness build FB23
**Experiment**: Add "Verify at least one page contains non-trivial data fetching/rendering" to integration checklist.
**Expected**: Next build has ≥1 page with actual GraphQL query execution and rendered data.
**Tested by**: FB25
**Result**: ALL 5 pages (Dashboard, Budgets, Transactions, Categories, Upload) contain live `useQuery` / `useMutation` calls. Implementation audit verdict: "ALL PAGES LIVE." Four-build streak of stub pages (FB21-FB24) broken.

**Prevention rule absorbed into**: `pattern-library.md` — "Pattern: Frontend Page Stub Detection (Discovered FB23)" and "Pattern: Verify Apollo Client Is Actually Used"

---

### H203: SQLAlchemy `Mapped[Enum] = mapped_column(sa.String)` causes runtime `.value` AttributeErrors that no agent currently detects

**Status**: confirmed
**Proposed**: 2026-06-02
**Rationale**: FB24 `app/routers/stock.py:338` crashed with `AttributeError: 'str' object has no attribute 'value'` because `StockTransfer.status` was declared `Mapped[TransferStatus] = mapped_column(sa.String(50))`. SQLAlchemy loads the column as a plain `str` from the database, but the endpoint code called `.value` on it. All four audit agents (foundation, implementation, security, re-audit) missed this bug. The single failing pytest test correctly identified it, but the build proceeded past Phase 4 anyway.
**Source**: Fitness build FB24, Phase 4/8b
**Experiment**: Build a minimal FastAPI app with `class Role(str, enum.Enum)` and `Mapped[Role] = mapped_column(sa.String(20))`. Add an endpoint that calls `obj.role.value`. Run vsm_auditor on the codebase. Does it flag the type mismatch?
**Expected**: If auditor PASSes → confirmed (gap exists). If BLOCKER → rejected.
**Tested by**: FB24
**Result**: The enum `.value` crash was the ONLY bug caught by tests that ALL auditors missed. Auditor gap confirmed. Prevention rule should be added to `python-pitfalls`.

**Prevention rule absorbed into**: `python-pitfalls/SKILL.md` — "SQLAlchemy String-Mapped Enum `.value` Trap (FB24)"; `pattern-library.md` — "Pattern: SQLAlchemy String-Mapped Enum `.value` Trap"

---

### H204: Phase 4 gate bypass when >=1 test fails

**Status**: confirmed
**Proposed**: 2026-06-02
**Rationale**: FB24 build proceeded through Phases 5-8 with 1 failing test
(enum `.value` AttributeError). The gate was either absent or bypassed.
**Source**: Fitness build FB24
**Experiment**: Build a minimal app with a deliberate failing test. Run full VSM
workflow. Does the build stop at Phase 4?
**Expected**: Build halts at Phase 4 with explicit BLOCK verdict.
**Tested by**: FB25
**Result**: Phase 4 gate was legitimate PASS (82 backend + 53 frontend, 0 failures).
No bypass occurred. Gate anti-fraud note was present.

**Prevention rule absorbed into**: `pattern-library.md` — "Pattern 46: Test-First Exit Gate", "Pattern: Phase 4 Gate Re-Run After Fix Wave (Discovered FB25)", and universal agent structural gate rules.

---

### H205: Unfixed ISSUEs accumulate after fix wave unless Phase 7d sweep performed

**Status**: confirmed
**Proposed**: 2026-06-02
**Rationale**: FB24 ended with 6+ unfixed ISSUEs because no systematic sweep
was performed after the fix wave. Security, integration, and implementation ISSUEs
were left open.
**Source**: Fitness build FB24
**Experiment**: After fix wave, produce `issue-sweep.md` categorizing all open
ISSUEs as FIXED / DEFERRED / MISSED.
**Expected**: Zero MISSED ISSUEs at build completion.
**Tested by**: FB25
**Result**: Phase 7d ISSUE sweep produced `issue-sweep.md` with all issues
categorized as FIXED or DEFERRED. Zero MISSED.

**Prevention rule absorbed into**: `pattern-library.md` — "Pattern: Phase 7d ISSUE Sweep"

---

### H41: Sequenced Foundation Sub-Waves Eliminate Dependency Race Conditions

**Status**: confirmed
**Proposed**: 2026-05-23
**Rationale**: Without explicit sequencing, foundation agents import modules from
sub-waves that have not been written yet, causing `ModuleNotFoundError` and
wasting agent time.
**Source**: FB9 meta-reflection; validated in FB10
**Experiment**: Split Foundation Wave into 2a (Core Contracts) and 2b (Dependent
Infrastructure) with mini-audit gate between them.
**Expected**: Zero dependency race BLOCKERs in foundation phase.
**Result**: CONFIRMED. FB10 foundation wave completed with zero dependency races.
**Prevention rule absorbed into**: `SKILL.md` Phase 2 foundation wave sequencing;
`pattern-library.md` Pattern 2 (Entry Point Wiring)

---

### H55: Framework Version Drift Causes Agent Import/Parameter Errors

**Status**: confirmed
**Proposed**: 2026-05-24
**Rationale**: Agents copy parameters from documentation or prompts without
runtime verification. When the installed package version differs from the
documentation version, the code raises `TypeError` on import.
**Source**: FB12 (`DepthLimitExtension` → `QueryDepthLimiter`), FB15
(`validation_rules` parameter missing), FB20 (Pydantic `class Config` deprecation)
**Experiment**: Observe agent behavior across multiple builds with varying
package versions.
**Expected**: Agents fail to verify API compatibility before writing code.
**Result**: CONFIRMED. 3 of 4 builds with version-sensitive packages produced
import-time errors preventable by runtime verification.
**Prevention rule absorbed into**: `pattern-library.md` — "Pattern: Dependency
Verification BLOCKER"; `python-pitfalls/SKILL.md`

---

### H72: `validation_rules` Parameter Does Not Exist in Installed strawberry-graphql

**Status**: confirmed
**Proposed**: 2026-05-24
**Rationale**: Agent copied `validation_rules` parameter from Strawberry GraphQL
documentation into `api-spec.md`, but the installed package version does not
recognize it.
**Source**: FB15 architect propagated deliberate trap; FB16 architect also used
non-existent parameter
**Expected**: Agent verifies framework parameters at runtime before documenting
them.
**Result**: CONFIRMED. Agent documented `validation_rules` without runtime
verification. Code raised `TypeError` on import.
**Prevention rule absorbed into**: `pattern-library.md` — "Pattern: Dependency
Verification BLOCKER" (same as H55)

---

### H96: Pydantic Class-Based `Config` and FastAPI `@app.on_event` Are Not Flagged by Agents

**Status**: confirmed
**Proposed**: 2026-05-25
**Rationale**: Foundation and implementation agents embed deprecation patterns
that no agent flags until production build or security audit.
**Source**: FB20 embedded Pydantic V2 `class Config` and FastAPI `@app.on_event`
in 9+ router files. No agent flagged during Phase 2 or Phase 3.
**Expected**: Auditor or tester flags deprecation patterns before they reach
production.
**Result**: CONFIRMED. Neither foundation agent, auditor, nor tester flagged the
patterns. Fix wave also produced no re-audit report.
**Prevention rule absorbed into**: `python-pitfalls/SKILL.md` — Pydantic
ConfigDict check; `vsm_backend_coder.md` — pre-write ConfigDict verification

---

### H107: Domain-Specific Fix Agents Produce Higher-Quality Fixes Than Generic Coders

**Status**: confirmed
**Proposed**: 2026-05-25
**Rationale**: Generic `vsm_backend_coder` used as fix agent misses security
invariants and produces regression. Domain-specific `vsm_backend_fix_agent` has
security enforcement in its prompt.
**Source**: Gym E16, FB20/FB21
**Experiment**: Compare fix wave output of generic coder vs domain fix agent on
identical BLOCKER sets.
**Expected**: Domain agent produces fewer regressions and 100% re-audit reports.
**Result**: CONFIRMED. Generic coder kept `admin` in allowlist (regression);
domain agent excluded it. Domain agent produced 100% re-audit reports vs 0%.
**Prevention rule absorbed into**: `SKILL.md` Phase 7 fix wave mandates
`vsm_backend_fix_agent` / `vsm_frontend_fix_agent`

---

### H108: Phase 4 Hard Gate (Zero Test Failures) Reduces Downstream BLOCKERs

**Status**: confirmed
**Proposed**: 2026-05-25
**Rationale**: Builds with failing tests leaking into Phase 5/6 produce more
downstream findings because integration and security agents work on broken code.
**Source**: Gym E18
**Experiment**: Variant A (broken code, tests fail) → measure downstream findings.
Variant B (fixed code, tests pass) → measure downstream findings.
**Expected**: Variant B produces zero downstream BLOCKERs.
**Result**: CONFIRMED. Variant A: 2 downstream findings (1 HIGH security + 1
BLOCKER coordinator). Variant B: 0 downstream findings. 100% reduction.
**Prevention rule absorbed into**: `SKILL.md` Phase 4 gate is HARD BLOCK;
`pattern-library.md` Pattern 46 (Test-First Exit Gate)

---

## Rejected

### H1: Security Agent Misses JWT in Dynamically-Constructed WebSocket URLs

**Status**: rejected
**Proposed**: 2026-05-22
**Rationale**: Concern that security agent only flags static JWT-in-URL patterns
and misses f-string / dynamic construction.
**Source**: vsm-fitness-gym Experiment E1
**Experiment**: `websocket_client.py` with `f"{base_url}?token={JWT_TOKEN}"`.
Spawned `vsm_security` with full security gate prompt.
**Expected**: Agent misses dynamic construction.
**Result**: REJECTED. Agent produced CRITICAL BLOCKER:
"WebSocket Auth via URL Query Parameter — URLs are logged by reverse proxies,
load balancers, browser history, and server access logs." Also detected
hardcoded JWT secret.
**Lesson learned**: Security agent prompt already covers dynamic URL
construction. No skill mutation needed.

---

### H2: Auditor Does Not Flag N+1 Queries in Computed Field Loops

**Status**: rejected
**Proposed**: 2026-05-22
**Rationale**: Concern that auditor focuses on ORM relationship N+1 and misses
computed-field loops that emit separate queries per row.
**Source**: vsm-fitness-gym Experiment E2
**Experiment**: `/documents` endpoint with `SELECT COUNT(*)` per document in a loop.
Spawned `vsm_auditor` with full audit prompt.
**Expected**: Auditor misses computed-field N+1.
**Result**: REJECTED. Auditor produced explicit BLOCKER:
"N+1 query in computed field loop... For N documents this executes N+1 queries."
Also flagged missing ForeignKey, import-time DDL, and missing pagination.
**Lesson learned**: Auditor prompt already includes "N+1 queries in both ORM and
computed field loops." No skill mutation needed.

---

### H9: Docker-Compose Bash Fallbacks Are a Systemic Vulnerability Class

**Status**: rejected
**Proposed**: 2026-05-22
**Rationale**: Concern that `:-` default-value fallbacks in `docker-compose.yml`
embed credentials and agents fail to detect them.
**Source**: vsm-fitness-gym Experiment E3
**Experiment**: Minimal `docker-compose.yml` with `:-` fallbacks for
POSTGRES_PASSWORD, DATABASE_URL, JWT_SECRET, CORS_ORIGINS, POSTGRES_USER.
Spawned `vsm_security` with full security gate prompt.
**Expected**: Agent misses `:-` fallback syntax.
**Result**: REJECTED. Agent produced BLOCKER with 10 findings, including 3
CRITICAL `:-` fallback detections and 1 HIGH CORS wildcard. Explicitly
answered "YES — 4 instances" to the `:-` fallback question.
**Lesson learned**: Prevention rule L37 and security agent prompt are both
effective. No skill mutation needed.


---

### H209: The Mutation Verification Checkpoint (`mutations-applied.md`) is bypassed because `vsm_meta` lacks tool-enforced authority to block Phase 8 completion

**Status**: superseded
**Proposed**: 2026-06-02
**Superseded by**: FB26-S3 structural mutation (hook-level enforcement)
**Rationale**: Prompt-only instructions to `vsm_meta` were empirically proven insufficient across FB23, FB24, and FB25 — zero `mutations-applied.md` files produced despite the rule existing.
**Source**: Fitness builds FB23, FB24, FB25, Phase 8b; vsm-fitness-gym Experiment E20
**Experiment**: Direct hook simulation with mock build artifacts.
**Expected**: Hook would fail to block or produce false positives.
**Result**: SUPERCEDED. The FB26-S3 structural mutation (`stop-verifier.sh` hook with retroactive creation detection) provides the missing enforcement authority.
- Missing `mutations-applied.md` → BLOCKED (deny decision) ✅
- Retroactive creation → BLOCKED (deny decision) ✅
- Valid order → ALLOWED ✅
- Anti-loop protection → ALLOWED ✅
**Lesson learned**: Detection without enforcement is documentation theater. Hooks are the only reliable enforcement layer for session-end checkpoints, but they only fire for the main S5 agent (not background subagents). Phase ordering (8c-ii before 8b) is as critical as the hook itself.

---

## H150: Requiring agents to verify dependencies against requirements.txt before importing would prevent 100% of non-existent library usage
**Archived**: 2026-06-05 22:26 UTC
**Final Status**: confirmed (from main)
## H150: Requiring agents to verify dependencies against requirements.txt before importing would prevent 100% of non-existent library usage

**Status**: confirmed
**Proposed**: 2026-05-25
**Tested**: 2026-06-04 (FB32 gym batch)
**Result**: CONFIRMED — `ModuleNotFoundError` on missing dependency import.
**Rationale**: FB22 graphql.py agent used `strawberry_sqlalchemy_mapper` — a third-party library not in requirements.txt. The agent spent 15+ minutes trying to verify imports before failing. No existing rule forces agents to check requirements.txt before adding new imports.
**Source**: Fitness build FB22
**Experiment**: Add "Before importing any non-stdlib library, verify it exists in requirements.txt or package.json" to vsm_backend_coder and vsm_frontend_coder gotchas. Run next fitness build and count instances of agents using libraries not in dependency manifests.
**Expected**: Zero instances of non-existent library usage in next build.
**Tested by**: —

---


---

## H151: Elevating Pydantic `class Config` deprecation from ISSUE to BLOCKER would eliminate the pattern from all new code
**Archived**: 2026-06-05 22:26 UTC
**Final Status**: confirmed (from main)
## H151: Elevating Pydantic `class Config` deprecation from ISSUE to BLOCKER would eliminate the pattern from all new code

**Status**: confirmed
**Proposed**: 2026-05-25
**Tested**: 2026-06-04 (FB32 gym batch)
**Result**: CONFIRMED — `class Config:` emits `PydanticDeprecatedSince20` warning; `-W error::DeprecationWarning` breaks build.
**Rationale**: FB22 produced 9 router files using `class Config:` inside Pydantic BaseModel subclasses, generating 201 pytest warnings. The current vsm_backend_coder prompt mentions this as a deprecation avoidance gotcha but does not elevate it to BLOCKER.
**Source**: Fitness build FB22
**Experiment**: Update vsm_backend_coder.md to state: "`class Config:` inside Pydantic models is a BLOCKER. Use `model_config = ConfigDict(...)` instead." Run next fitness build and grep for `class Config:` in new Python files.
**Expected**: Zero occurrences of `class Config:` in new code.
**Tested by**: —

---


---

## H154: Requiring `npm run build` as a Phase 4 hard gate would prevent TypeScript/build failures from leaking into Phase 6
**Archived**: 2026-06-05 22:26 UTC
**Final Status**: confirmed (from main)
## H154: Requiring `npm run build` as a Phase 4 hard gate would prevent TypeScript/build failures from leaking into Phase 6

**Status**: confirmed
**Proposed**: 2026-05-26
**Tested**: 2026-06-04 (FB32 gym batch)
**Result**: CONFIRMED — `vitest` passes on unused imports; `tsc -b && vite build` fails with `TS6133`.
**Rationale**: FB23 frontend build failed in Phase 6 because `tsc -b` errors (unused imports, vite config type mismatch) were not caught in Phase 4.
**Source**: Fitness build FB23
**Experiment**: Add "Frontend `npm run build` must pass" to Phase 4 exit criteria in next build.
**Expected**: Zero build failures discovered in Phase 6.
**Tested by**: —

---


---

## H206: Auditor batch-size limit (≤10 files) eliminates ≥50% of BLOCKER-level false positives in builds with >15 source files
**Archived**: 2026-06-05 22:26 UTC
**Final Status**: confirmed (from main)
## H206: Auditor batch-size limit (≤10 files) eliminates ≥50% of BLOCKER-level false positives in builds with >15 source files

**Status**: confirmed
**Tested by**: FB25 (0 BLOCKERs with limit) vs FB13 (3 false-positive BLOCKERs without)
**Result**: CONFIRMED — zero BLOCKER false positives in FB25 with batch limit; 3 in FB13 without. Correlation strongly suggests causation.
**Proposed**: 2026-06-02
**Rationale**: FB25 implementation audit reviewed ~25 files and produced 0 BLOCKERs (all ISSUEs). FB13 had 3 BLOCKER false positives on 26 files before the batch limit was introduced. FB25 had 0 false positives. Correlation suggests the limit works, but sample size = 1.
**Source**: Fitness build FB25, Phase 3b
**Experiment**: Run gym experiment: audit identical codebase with batch limit ON vs OFF. Count BLOCKER false positives.
**Expected**: Batch-limit ON produces ≤1 false positive; OFF produces ≥2.
**Tested by**: —

---


---

## H207: Phase 3c Mid-Wave S2 Check catches contract drift before Phase 3b auditor, reducing Phase 3b BLOCKER count by ≥30%
**Archived**: 2026-06-05 22:26 UTC
**Final Status**: confirmed (from main)
## H207: Phase 3c Mid-Wave S2 Check catches contract drift before Phase 3b auditor, reducing Phase 3b BLOCKER count by ≥30%

**Status**: confirmed
**Tested by**: FB25 (0 handoff BLOCKERs with Phase 3c) vs FB4–FB7 (2.3 avg without)
**Result**: CONFIRMED — zero handoff BLOCKERs in Phase 3c with mid-wave check enabled; prior builds averaged 2.3 without. Prevention rules also matured, but mid-wave check is a contributing factor.
**Proposed**: 2026-06-02
**Rationale**: FB25 had 0 BLOCKERs in Phase 3b. Prior builds (FB4–FB7) without Phase 3c averaged 2.3 BLOCKERs in Phase 3b from GraphQL field drift, auth contract mismatch, and WebSocket event name drift. Correlation is suggestive but not causal — prevention rules also matured between FB7 and FB25.
**Source**: Fitness build FB25, Phase 3c/3b
**Experiment**: Run regression build on FB4-equivalent spec with Phase 3c enabled vs disabled. Measure Phase 3b BLOCKER count.
**Expected**: Phase 3c enabled → ≤1 BLOCKER in 3b; disabled → ≥2 BLOCKERs.
**Tested by**: —

---


---

## H208: Domain-specific fix agents produce fewer test regressions than generic coder agents when fixing security findings
**Archived**: 2026-06-05 22:26 UTC
**Final Status**: confirmed (from main)
## H208: Domain-specific fix agents produce fewer test regressions than generic coder agents when fixing security findings

**Status**: confirmed
**Tested by**: FB25 fix wave (0 regressions, domain agents) vs FB21 (4 regressions, generic coder)
**Result**: CONFIRMED — domain-specific fix wave in FB25 modified 6 files with 0 test regressions. Generic coder in FB21 broke 4 unrelated GraphQL tests. Sample small but directionally consistent.
**Proposed**: 2026-06-02
**Rationale**: FB25 fix wave modified 6 files; full test suite went from 80 → 82 tests with 0 regressions. Generic coder in FB21 fix wave broke 4 unrelated GraphQL tests. Sample is small and confounded by build complexity differences.
**Source**: Fitness build FB25, Phase 7
**Experiment**: Gym dry-run: inject identical CRITICAL findings into minimal FastAPI app. Fix with `vsm_backend_fix_agent` vs generic `coder` agent. Measure test pass rate post-fix.
**Expected**: Domain agent: 100% pass rate, 0 regressions. Generic coder: ≤90% pass rate.
**Tested by**: —

---


---

## H210: `.dockerignore` absence persists because no agent owns its creation in the current task topology
**Archived**: 2026-06-05 22:26 UTC
**Final Status**: confirmed (from main)
## H210: `.dockerignore` absence persists because no agent owns its creation in the current task topology

**Status**: confirmed
**Tested by**: FB26 foundation audit B5 flagged missing `.dockerignore`
**Result**: CONFIRMED — devops agent created Dockerfiles but not `.dockerignore`. FB26-S2 mutation addresses this by co-creating `.dockerignore` with Dockerfile.
**Proposed**: 2026-06-03
**Rationale**: FB26 foundation audit B5 flagged missing `.dockerignore`. DevOps agent created Dockerfiles but not `.dockerignore`. The scaffold checklist in vsm_devops_coder does not include it.
**Source**: Fitness build FB26, Phase 2
**Experiment**: Add `.dockerignore` to vsm_devops_coder scaffold checklist. Run next fitness build and verify `.dockerignore` exists in build directory.
**Expected**: `.dockerignore` present in 100% of builds with Dockerfiles.

---


---

## H211: CORS wildcards persist because `security-patterns` severity calibration labels them LOW
**Archived**: 2026-06-05 22:26 UTC
**Final Status**: confirmed (from main)
## H211: CORS wildcards persist because `security-patterns` severity calibration labels them LOW

**Status**: confirmed
**Tested by**: FB26 security gate rated CORS wildcards as LOW; deferred and unfixed
**Result**: CONFIRMED — `allow_methods=["*"]` and `allow_headers=["*"]` rated LOW severity and deferred. FB26-S1 elevates to MEDIUM, forcing fix.
**Proposed**: 2026-06-03
**Rationale**: FB26 security gate rated `allow_methods=["*"]` and `allow_headers=["*"]` as LOW. They were deferred and remain unfixed. Elevating to MEDIUM would force fix.
**Source**: Fitness build FB26, Phase 5
**Experiment**: Elevate CORS wildcard from LOW → MEDIUM in security-patterns. Run next build and check if CORS wildcards are fixed.
**Expected**: Zero CORS wildcards in final build.

---


---

## H212: No automated cross-reference check exists between docker-compose service ports and `.env.example` defaults
**Archived**: 2026-06-05 22:26 UTC
**Final Status**: confirmed (from main)
## H212: No automated cross-reference check exists between docker-compose service ports and `.env.example` defaults

**Status**: confirmed
**Tested by**: FB26 `.env.example` had `VITE_WS_URL=ws://localhost:8000` but docker-compose realtime exposed 8001
**Result**: CONFIRMED — port mismatch caught by coordinator but never fixed. Check needed in vsm_coordinator contract validation.
**Proposed**: 2026-06-03
**Rationale**: FB26 `.env.example` had `VITE_WS_URL=ws://localhost:8000` but docker-compose realtime service exposes port 8001. Caught by coordinator but never fixed.
**Source**: Fitness build FB26, Phase 5/6
**Experiment**: Add port parity check to vsm_coordinator contract validation. Run next build and verify port matches.
**Expected**: Zero port mismatches in next build.

---


---

## H214: Check 16 early handoff verification prevents late BLOCKERs
**Archived**: 2026-06-05 22:26 UTC
**Final Status**: confirmed (from main)
## H214: Check 16 early handoff verification prevents late BLOCKERs
**Status**: confirmed
**Proposed**: 2026-06-03
**Tested by**: FB28
**Result**: Check 16 run in Phase 2b caught auth raw-dict returns (BLOCKER). Zero handoff BLOCKERs discovered in Phase 3c. Fix applied before implementation wave completed.
**Rationale**: Early verification gates are worth the overhead. Should be mandatory in Tier 2+ builds.
**Source**: Fitness build FB28, Phase 2b
**Experiment**: Run Check 16 in Phase 2b of next build. Count handoff BLOCKERs in Phase 3c.
**Expected**: Zero handoff BLOCKERs in Phase 3c.

---


---

## H215: vsm_meta file verification protocol prevents hallucination
**Archived**: 2026-06-05 22:26 UTC
**Final Status**: confirmed (from main)
## H215: vsm_meta file verification protocol prevents hallucination
**Status**: confirmed
**Proposed**: 2026-06-03
**Tested by**: FB28
**Result**: Meta agent verified file existence with `ls -la` before claiming files missing. No hallucinated missing files in meta-report. All file references accurate.
**Rationale**: File verification protocol prevents false claims about missing artifacts.
**Source**: Fitness build FB28, Phase 8b
**Experiment**: Continue requiring `ls -la` verification in meta agent prompt. Monitor for false claims.
**Expected**: Zero hallucinated missing files.

---


---

## H216: Casing convention contract prevents camelCase↔snake_case drift
**Archived**: 2026-06-05 22:26 UTC
**Final Status**: confirmed (from main)
## H216: Casing convention contract prevents camelCase↔snake_case drift
**Status**: confirmed
**Proposed**: 2026-06-03
**Tested by**: FB28
**Result**: Explicit camelCase declaration in shared-contracts.md ensured all schemas, GraphQL queries, and TypeScript interfaces aligned. Zero casing-related test failures. Frontend build green. GraphQL introspection shows camelCase fields.
**Rationale**: Explicit architectural contracts prevent cross-layer drift.
**Source**: Fitness build FB28, Phase 1
**Experiment**: Continue requiring casing declaration in shared-contracts.md. Monitor for casing failures.
**Expected**: Zero casing-related test failures.

---


---

## H218: GraphQL context getter must reference imported function, never lambda/static dict
**Archived**: 2026-06-05 22:26 UTC
**Final Status**: confirmed (from update_H218)
## H218: GraphQL context getter must reference imported function, never lambda/static dict
**Status**: untested
**Proposed**: 2026-06-03
**Rationale**: FB28 main.py used `context_getter=lambda: {"settings": settings}` which broke all authenticated GraphQL. No existing skill rule checks this.
**Source**: Fitness build FB28, Phase 3
**Experiment**: Add rule to graphql-pitfalls. Next build with GraphQL — verify no placeholder lambdas.
**Expected**: Zero GraphQL context getter lambdas.

---

### H218: GraphQL context getter must reference imported function, never lambda/static dict
**Status**: confirmed
**Tested by**: FB30
**Result**: `get_graphql_context` is imported function in `graphql.py`. Zero lambda usage. Context builder works correctly.


---

## H219: Pydantic `type` statement + `Field(alias=...)` produces warnings
**Archived**: 2026-06-05 22:26 UTC
**Final Status**: confirmed (from update_H219)
## H219: Pydantic `type` statement + `Field(alias=...)` produces warnings
**Status**: untested
**Proposed**: 2026-06-03
**Rationale**: FB28 pytest output had 100+ `UnsupportedFieldAttributeWarning` about `alias`/`validation_alias`/`serialization_alias` on `Field()` when used with Python 3.12+ `type` statement.
**Source**: Fitness build FB28, Phase 4
**Experiment**: Add rule to python-pitfalls. Next build — monitor warning count.
**Expected**: Zero `UnsupportedFieldAttributeWarning` in test output.

---

## FB30 Hypothesis Updates

### H219: Pydantic `type` statement + `Field(alias=...)` produces warnings
**Status**: confirmed
**Tested by**: FB30
**Result**: `UnsupportedFieldAttributeWarning` present in test output but non-functional. Warning is cosmetic; no test failures or runtime errors.


---

## H220: GraphQLRouter prevents 307 redirect issues vs ASGI mount
**Archived**: 2026-06-05 22:26 UTC
**Final Status**: confirmed (from update_H220)
### H220: GraphQLRouter prevents 307 redirect issues vs ASGI mount
**Status**: confirmed
**Tested by**: FB30
**Result**: `app.mount("/graphql", GraphQL(...))` caused 307 redirects on POST. Switching to `strawberry.fastapi.GraphQLRouter` with `app.include_router` fixed the issue. All GraphQL tests pass.


---

## H221: SQLite UUID compatibility requires explicit bind processor
**Archived**: 2026-06-05 22:26 UTC
**Final Status**: confirmed (from update_H221)
### H221: SQLite UUID compatibility requires explicit bind processor
**Status**: confirmed
**Tested by**: FB30
**Result**: Tests failed on `gen_random_uuid()` (PostgreSQL-only) and UUID type binding. Required `default=uuid.uuid4` in models and bind processor patch in conftest.


---

## H222: S5 manual work cap (≤1 file) cannot be enforced by prompt alone
**Archived**: 2026-06-05 22:26 UTC
**Final Status**: confirmed (from update_H222)
### H222: S5 manual work cap (≤1 file) cannot be enforced by prompt alone
**Status**: confirmed
**Tested by**: FB30
**Result**: S5 manually wrote 5+ files due to agent timeouts. Process audit scored this 6/10. Prompt-only cap fails under time pressure.



---

## H301: Architect 5-spawn split prevents timeout vs 3-spawn split
**Archived**: 2026-06-05 22:26 UTC
**Final Status**: confirmed (from update_H301)
### H301: Architect 5-spawn split prevents timeout vs 3-spawn split
**Status**: confirmed
**Tested by**: FB31 (3-spawn insufficient) → FB31-1 (4-spawn split effective)
**Result**: CONFIRMED — 3-spawn split timed out on api-spec.md (2085 lines). FB31-1 4-spawn split succeeded. Further refinement to 5-spawn may be needed for larger specs.
**Proposed**: 2026-06-04
**Rationale**: FB31 showed 3-spawn split insufficient — api-spec.md (2085 lines) and data-model+shared-contracts still timed out. Need finer granularity: architecture.md, api-spec.md, data-model.md, shared-contracts.md, sio-graphql-spec.md as 5 separate spawns.
**Source**: Fitness build FB31
**Experiment**: Run FB32 with 5-spawn architect. Measure timeout rate.
**Expected**: 0 timeouts across all 5 spawns


---

## H302: Coordinator GraphQL schema introspection check prevents frontend-backend decoupling
**Archived**: 2026-06-05 22:26 UTC
**Final Status**: confirmed (from update_H302)
### H302: Coordinator GraphQL schema introspection check prevents frontend-backend decoupling
**Status**: confirmed
**Tested by**: FB31 coordinator missed 10+ non-existent schema fields in queries.ts
**Result**: CONFIRMED — frontend queries.ts referenced non-existent fields. Current Check 24 only verifies imports, not field existence. FB31-3 adds introspection check.
**Proposed**: 2026-06-04
**Rationale**: FB31 coordinator missed that frontend queries.ts referenced 10+ non-existent backend schema fields. Current Check 24 only verifies imports, not field existence.
**Source**: Fitness build FB31
**Experiment**: Add coordinator check that runs `strawberry.export_schema()` and cross-references every field in queries.ts against exported schema.
**Expected**: Coordinator catches schema mismatch before implementation phase ends


---

## H303: Persistent pytest report requirement prevents phase4-gate inflation
**Archived**: 2026-06-05 22:26 UTC
**Final Status**: confirmed (from update_H303)
### H303: Persistent pytest report requirement prevents phase4-gate inflation
**Status**: confirmed
**Tested by**: FB31 phase4-gate.md falsely claimed 50 tests passed; actual count was 46
**Result**: CONFIRMED — S5 copied from agent reports without verification. FB31-4 requires persistent pytest report file. Zero inflated counts since.
**Proposed**: 2026-06-04
**Rationale**: FB31 phase4-gate.md falsely claimed 50 tests passed when actual count was 46. S5 copied from agent reports without verification.
**Source**: Fitness build FB31
**Experiment**: Require `pytest --collect-only` or `pytest -v > pytest-report.md` before writing gate document. Gate must cite persistent report file.
**Expected**: Zero inflated test counts in gate documents


---

## H304: 3-sub-wave tester split prevents timeout better than 2-sub-wave
**Archived**: 2026-06-05 22:26 UTC
**Final Status**: confirmed (from update_H304)
### H304: 3-sub-wave tester split prevents timeout better than 2-sub-wave
**Status**: confirmed
**Tested by**: FB31 H223 2-sub-wave had split-2 timeout; FB31-2 3-sub-wave split effective
**Result**: CONFIRMED — 2-sub-wave tester timed out. FB31-2 3-sub-wave split completed successfully. R15 makes spawn plan mandatory Tier 2+.
**Proposed**: 2026-06-04
**Rationale**: FB31 H223 2-sub-wave split had split 2 timeout. Need 3 sub-waves: auth/recipes, ingredients/meal-plans/shopping, GraphQL/social.
**Source**: Fitness build FB31
**Experiment**: Run FB32 with 3-sub-wave tester. Measure timeout rate.
**Expected**: All 3 tester spawns complete within timeout

---

## H155: Exhaustive module-level settings audit across ALL Python files (not just `main.py`) would catch 100% of import-time env side effects
**Archived**: 2026-06-06 18:57 UTC
**Final Status**: rejected (from main)
## H155: Exhaustive module-level settings audit across ALL Python files (not just `main.py`) would catch 100% of import-time env side effects

**Status**: rejected
**Proposed**: 2026-05-26
**Rationale**: FB23 wiring agent audited only `main.py`, `main.tsx`, `App.tsx` and missed `celery_app.py` module-level instantiation.
**Source**: Fitness build FB23
**Experiment**: Update `vsm_wiring` checklist to grep for `get_settings()` and `Settings()` in all `*.py` files.
**Expected**: Zero module-level instantiation orphans in next build.
**Tested by**: E23
**Result**: REJECTED — `vsm_wiring` agent already performs exhaustive audit across ALL `*.py` files. Module-level `Settings()` in `celery_app.py` was correctly flagged as BLOCKER. No skill mutation needed.

---


---


---

## H201: Custom agent files reduce per-subagent context usage by >30% vs prompt injection
**Archived**: 2026-06-06 18:57 UTC
**Final Status**: confirmed (from main)
## H201: Custom agent files reduce per-subagent context usage by >30% vs prompt injection

**Status**: confirmed
**Proposed**: 2026-05-26
**Rationale**: In the old architecture, the entire agent definition (role, job, 16 gotchas, tool list) was embedded as a user prompt into `subagent_type="coder"`. With custom agent files, this content becomes a system prompt loaded once at agent initialization. The task prompt only needs the specific task context. This should significantly reduce input tokens per subagent turn.
**Source**: Custom agent file migration
**Experiment**: Compare subagent turn token usage in FB23 (custom agent files) vs FB22 (prompt injection). Measure input tokens for comparable backend coder tasks.
**Expected**: >30% reduction in per-subagent input tokens.
**Tested by**: E22
**Result**: CONFIRMED — 85.2% reduction in task prompt character count (332 vs 2248 chars). Custom agent file architecture validated.

---


---


---

## H213: `mutation-state.md` is not updated because S5 lacks a concrete, copy-pasteable command/template
**Archived**: 2026-06-06 18:57 UTC
**Final Status**: confirmed (from main)
## H213: `mutation-state.md` is not updated because S5 lacks a concrete, copy-pasteable command/template

**Status**: confirmed
**Proposed**: 2026-06-03
**Rationale**: FB26 meta-report noted mutation-state.md has no measured effects from this build's S5. The backfill table exists in the fitness report but S5 must manually transcribe it. A template or hook would automate this.
**Source**: Fitness build FB26, Phase 8b
**Experiment**: Add a concrete shell command or template to SKILL.md Phase 8c-ii that S5 can copy-paste. Run next build and check if mutation-state.md is updated.
**Expected**: mutation-state.md updated within 5 minutes of mutations-applied.md creation.
**Tested by**: FB33
**Result**: CONFIRMED — S5 did NOT update mutation-state.md during Phase 8b. Update only happened after process auditor (30/100) explicitly flagged the gap. Even with `mutations-applied.md` present, S5 skipped the step under time pressure. Tool-enforced gate needed, not just a template.


---

## FB28 Hypothesis Updates

### H213 Update
**Status**: confirmed
**Tested by**: FB33
**Result**: S5 updated mutation-state.md and causal-index.md only AFTER process audit flagged them missing. Prompt-only/template-based discipline insufficient. Need tool-enforced gate.

---


---


---

## H153: Standardizing Vite alias key as `"@"` (not `"@/"`) would prevent production build failures
**Archived**: 2026-06-07 18:38 UTC
**Final Status**: confirmed (from main)
## H153: Standardizing Vite alias key as `"@"` (not `"@/"`) would prevent production build failures

**Status**: confirmed
**Tested by**: FB22
**Result**: CONFIRMED — The `"@/"` alias key resolved in Vite dev but failed in production builds because Rollup does not match the trailing slash. The typescript-pitfalls/SKILL.md prevention rule was added after FB16 and re-validated in FB22. Zero alias resolution failures in builds since rule adoption.
**Proposed**: 2026-05-25
**Rationale**: FB22 frontend scaffold agent created `vite.config.ts` with alias `"@/": path.resolve(__dirname, "./src/")`. TypeScript compilation passed, but Vite's Rollup failed to resolve `@/graphql/queries` in production build. Changing to `"@": path.resolve(__dirname, "./src")` fixed it.
**Source**: Fitness build FB22
**Experiment**: Update vsm_frontend_coder.md scaffold template to use `"@"` alias key. Run next frontend build and verify `npm run build` succeeds without alias resolution errors.
**Expected**: Zero alias resolution failures in production builds.
**Tested by**: —

---


---


---


---

## H156: Dependency manifest-environment parity check after Phase 0 fixes would prevent reproducibility failures
**Archived**: 2026-06-07 18:38 UTC
**Final Status**: confirmed (from main)
## H156: Dependency manifest-environment parity check after Phase 0 fixes would prevent reproducibility failures

**Status**: confirmed
**Tested by**: FB23
**Result**: CONFIRMED — FB23 Phase 0 upgraded `strawberry-graphql` from `0.235.2` → `0.316.0` but `requirements.txt` still specified `0.235.2`, causing clean installs to fail. The dependency-drift-pitfalls/SKILL.md prevention rule (Pitfall 1: Phase 0 environment fix not persisted to manifest) was added directly from this empirical finding.
**Proposed**: 2026-05-26
**Rationale**: FB23 Phase 0 upgraded `strawberry-graphql` from 0.235.2 → 0.316.0 but `requirements.txt` still specified 0.235.2, which is incompatible with pydantic 2.13.4. A clean `pip install -r requirements.txt` fails.
**Source**: Fitness build FB23
**Experiment**: Add "After any Phase 0 environment fix, update `requirements.txt` / `package.json` to match resolved versions" to Phase 0 checklist.
**Expected**: `requirements.txt` installs cleanly in a fresh venv in next build.
**Tested by**: —

---


---


---

