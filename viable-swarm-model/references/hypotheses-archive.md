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

## Rejected

> No hypotheses have been formally rejected. When a hypothesis is rejected,
> append it here with the rationale for rejection and any lessons learned.

