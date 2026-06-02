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

---

## Entry 3 — 2026-06-02

**Builds**: FB4–FB24 (comprehensive)
**Pattern**: Fitness build scores have remained flat (3.2–4.0) for 24 builds and
80+ mutations. The peak was FB9 at 4.0 (2026-05-23). No sustained upward
trajectory exists despite continuous mutation.
**Evidence**:
- Score series: 3.6, 3.7, 3.6, 3.5, 3.9, **4.0**, 3.3, 3.7, 3.2, 3.6, 3.7,
  3.4, —, 3.6, 3.2, 3.4, 3.7, 3.8, 3.2, 3.2.
- Zero mutations have ever been removed for ineffectiveness.
- "Measured effect" field in mutation log is almost universally empty.
- Persistent failure modes: Phase 4 gate bypass (FB20, FB21, FB24), inline fixes
  (FB20, FB21, FB23), frontend stubs (FB23, FB24), architect trap propagation
  (FB16–FB18), security gate misses (FB20, FB21).
**Implication**:
1. **Detection ≠ Enforcement**. The skill has excellent detection (checklists,
   audits, tests catch issues) but poor enforcement at the S5 level. Process
   boundaries rely on S5 self-discipline, which degrades under time pressure.
2. **Mutation bloat without removal**. Rules accumulate but are never pruned.
   Fragile transfer (H65 reverted in FB15) indicates rules work once but don't stick.
3. **Effectiveness tracking is template-only**. The infrastructure exists
   (evaluation-rubric.md, fitness-report-template.md) but is not structurally
   enforced in agent output.
**Action taken**:
- Added Mutation Effectiveness Scoring to coach rubric (Phase 2a, 1–5 scale).
- Added regression build mode every 5 builds (Coach Phase 6).
- Added process auditor agent (`vsm_process_auditor`) for Phase 8b compliance.
- Added "mutation removal gate" concept: ineffective mutations should be removed.
- Added this meta-reflection entry to track the stagnation pattern.


---

## Entry 4 — 2026-06-02

**Builds**: FB25
**Pattern**: All 5 hypotheses under test (H203–H205, H40, H157) were validated successfully in a single build for the first time. The prevention-rule stack is maturing — no enum `.value` crash, no stub pages, no Phase 4 gate bypass, no inline fixes. However, the Mutation Verification Checkpoint (FB18-10) continues to be bypassed in practice despite being a structural mutation.
**Evidence**:
- FB25 meta-report: "No `mutations-applied.md` exists in `.kimi/` despite FB18-10 structural mutation mandating it."
- Agent scores: minimum 4/5 across all 8 agent types — highest since FB9.
- Independent test verification: 82 backend + 53 frontend passed, 0 failures. Phase 4 gate was legitimate.
- H203 (sa.Enum trap): All enum columns used `sa.Enum(...)`; no `.value` crash.
- H204 (hard gate): `.kimi/phase4-gate.md` written before Phase 5.
- H205 (ISSUE sweep): `issue-sweep.md` categorizes all unfixed issues.
- H40 (router imports): Consistent `APIRouter` usage verified.
- H157 (stub prevention): All 5 pages have live data fetching.
**Implication**:
1. Prevention rules work when they are specific and stack-skill-enforced.
2. Process-level mutations (like FB18-10) fail without tool-enforced or hook-level backing. Prompt-only instructions degrade under session-end time pressure.
3. The skill's detection capability is now stronger than its enforcement capability at the S5 level.
**Action taken**:
- Proposed structural mutation to enforce `mutations-applied.md` as hard block in Phase 8c.
- Proposed refinement mutation to `vsm_meta.md` to explicitly check for `mutations-applied.md`.
- Added 4 new hypotheses (H206–H209) to backlog for gym testing.
