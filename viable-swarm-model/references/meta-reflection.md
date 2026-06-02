# Meta-Reflection — Skill-Level Performance Learning

> **Purpose**: Cross-build reflections on the viable-swarm-model skill's own
> performance. Synthesized from individual `meta-report.md` artifacts.
> **Location**: `~/vsm/viable-swarm-model/references/meta-reflection.md`
> **Read by**: `vsm_meta` at startup (if present)
> **Written by**: S5 during Phase 8, after reviewing `meta-report.md`

---

## Entry [N] — YYYY-MM-DD

**Builds**: [Which builds contributed this insight]
**Pattern**: [What systemic behavior was observed across multiple builds]
**Evidence**: [Specific scores, findings, or quotes from meta-reports]
**Implication**: [What this means for skill design]
**Action taken**: [What was changed in the skill as a result]

---

## Example

## Entry 1 — 2026-05-26

**Builds**: FB17, FB22, FB23
**Pattern**: Frontend build failures (`tsc -b`, `npm run build`) consistently leak
from Phase 4 into Phase 6 because the Phase 4 exit gate only checks test counts,
not build success.
**Evidence**: FB23 meta-report: "frontend `npm run build` was NOT run during
Phase 4 — it was deferred to Phase 6, where it failed."
**Implication**: The Phase 4 hard gate is incomplete. It must include frontend
production build verification alongside test counts.
**Action taken**: Added `npm run build` / `tsc -b` as mandatory Phase 4 gate in
`SKILL.md` (H154).


---

## Entry 2 — 2026-06-02

**Builds**: FB24
**Pattern**: Phase 4 hard gate (Pattern 46 / Test-First Exit Gate) is bypassed when exactly 1 test fails, especially if the failure is an exception rather than an assertion error. Additionally, SQLAlchemy `Mapped[Enum] = mapped_column(sa.String)` type mismatches are an entirely undetected bug class across all audit agents.
**Evidence**:
- FB24 independent test verification: 84 passed, 1 failed (`test_stock.py::test_update_transfer_status_invalid_transition` — `AttributeError: 'str' object has no attribute 'value'` at `stock.py:338`).
- Build proceeded through Phases 5, 6, 7, 8 without fixing this test.
- Foundation audit: 2 BLOCKERs, 11 ISSUEs — no enum type safety check.
- Implementation audit: 5 BLOCKERs, 8 ISSUEs — no enum type safety check.
- Security gate: 0 BLOCKERs, 2 MEDIUM, 4 LOW — missed the runtime-crash bug entirely.
- Re-audit: 0 BLOCKERs, 3 ISSUEs — checked 6 fix-wave items, missed the enum bug.
- No `mutations-applied.md` produced — Mutation Orphan failure mode (FB18-10 not enforced).
**Implication**:
1. The Test-First Exit Gate needs an explicit S5 verification command (not just a pattern in pattern-library.md).
2. A new anti-pattern is needed for SQLAlchemy String-mapped enum columns.
3. The Mutation Verification Checkpoint (FB18-10) must become a hard block, not a soft recommendation.
**Action taken**:
- Proposed 3 new hypotheses (H203, H204, H205) in `references/hypotheses.md`.
- Proposed append-only mutations to `anti-patterns.md`, `integration-checklist.md`, `security-lessons.md`.
- Proposed refinement mutations to `agents/vsm_auditor.md` and `SKILL.md` Phase 7.
- Proposed structural mutations to `SKILL.md` Phase 4 (hard gate enforcement) and Phase 8b (mutation checkpoint hard block).
