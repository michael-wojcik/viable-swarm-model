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
