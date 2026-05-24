# Mutation Log

> This file is append-only. Every modification the coach skill makes to its own
> files is recorded here with full rationale. If the skill becomes corrupted,
> this log is the audit trail for `git revert`.
>
> **Mutation rules**: Append only. Each entry includes: session context,
> file changed, type of change, rationale, expected effect.

---

## Mutation 1 — 2026-05-23

**Session**: Creation of coach mutation-log infrastructure
**File**: `references/mutation-log.md`, `SKILL.md`
**Type**: structural
**Rationale**: The coach skill referenced self-modification and the three-tier
mutation system but lacked the supporting infrastructure: no mutation-log.md,
no format template, no epistemic rules, and no rollback procedure. All coach
mutations were being logged in the main skill's mutation-log.md, which violated
the principle that each skill in the ecosystem should maintain its own audit trail.

**Expected effect**: Future coach mutations (prompt refinements, rubric updates,
fitness project additions, phase logic changes) will be logged here. The coach
is now a fully self-documenting learning organism.

---

## Mutation 2 — 2026-05-23

**Session**: Coach skill refinement — hypothesis status tracking gap
**File**: `SKILL.md`
**Type**: refinement
**Rationale**: The coach generated new hypotheses from fitness build gaps but
never explicitly updated the status of existing hypotheses tested by the build.
This left the hypothesis backlog with stale "untested" items.

**Expected effect**: After every fitness build, the coach will explicitly check
which hypotheses were tested, update their status (confirmed / rejected /
inconclusive), fill in the Result field with build evidence, and record the
build ID in the Tested by field.

**Files modified**:
- `SKILL.md` — Added Phase 2b: Update Hypothesis Statuses between Phase 2
  (Evaluate Performance) and Phase 3 (Generate Hypotheses). Updated Mermaid
  flow diagram to include P2H node.

---

## Mutation [N] — YYYY-MM-DD

**Session**: [Brief description of the fitness build or coach self-evaluation]
**File**: [Which file was modified]
**Type**: [append | refinement | structural]
**Rationale**: [What empirical finding motivated this change. Be specific:
which build, which phase score, which trainer gap.]
**Expected effect**: [How the next fitness build should behave differently
because of this mutation.]

**Before**:
```
[content or summary of what existed]
```

**After**:
```
[content or summary of what replaced it]
```
