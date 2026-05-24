# Mutation Log

> This file is append-only. Every modification the gym skill makes to its own
> files is recorded here with full rationale. If the skill becomes corrupted,
> this log is the audit trail for `git revert`.
>
> **Mutation rules**: Append only. Each entry includes: session context,
> file changed, type of change, rationale, expected effect.

---

## Mutation 1 — 2026-05-23

**Session**: Creation of gym mutation-log infrastructure
**File**: `references/mutation-log.md`, `SKILL.md`
**Type**: structural
**Rationale**: The gym skill referenced self-modification and the three-tier
mutation system but lacked the supporting infrastructure: no mutation-log.md,
no format template, and no rollback procedure. Gym mutations (experiment designer
prompt refinements, template updates, phase logic changes) had no designated
audit trail.

**Expected effect**: Future gym mutations will be logged here. The gym is now
a fully self-documenting learning organism with its own epistemic infrastructure.

---

## Mutation [N] — YYYY-MM-DD

**Session**: [Brief description of the experiment or gym self-evaluation]
**File**: [Which file was modified]
**Type**: [append | refinement | structural]
**Rationale**: [What empirical finding motivated this change. Be specific:
which experiment, which hypothesis, which result.]
**Expected effect**: [How the next experiment should behave differently
because of this mutation.]

**Before**:
```
[content or summary of what existed]
```

**After**:
```
[content or summary of what replaced it]
```
