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


## Mutation Gym-1 — 2026-05-25

**Session**: vsm-fitness-gym batch experiment run (E6–E14)
**File**: `~/vsm/vsm-fitness-gym/references/experiments.md`
**Type**: append-only
**Rationale**: The gym had no experiment log. Running 10 experiments (8 untested + 2 inconclusive hypotheses) produced structured evidence for all hypotheses. A centralized log prevents re-running the same experiments and provides empirical justification for mutations.
**Expected effect**: Future gym sessions can reference past experiments by ID. No duplicate work.

---

## Mutation Gym-2 — 2026-05-25

**Session**: vsm-fitness-gym batch experiment run (E6–E14)
**File**: `~/vsm/viable-swarm-model/references/pattern-library.md`
**Type**: append-only
**Rationale**: Three new patterns discovered via gym experiments:
1. Auth Response Contract Template (H20) — prevents login/register contract mismatches
2. Frontend Build Script Verification (H48) — catches `tsc -b` failures that `vite build` misses
3. Domain-Specific Coder Prompts (H59) — reduces systematic false negatives by embedding stack gotchas in agent prompts
**Expected effect**: Future architects and S5 agents reference these patterns during builds.

---

## Mutation Gym-3 — 2026-05-25

**Session**: vsm-fitness-gym batch experiment run (E6–E14)
**File**: `~/vsm/viable-swarm-model/agents/vsm_auditor.md`
**Type**: refinement
**Rationale**: H46 confirmed that re-auditing changed files only misses regressions introduced by fixes. A minimal experiment showed fixing `test_get_user` broke `test_get_post`. The auditor prompt previously said "After fixes: re-audit changed files only." Updated to require full test suite re-run and `re-audit-report.md` artifact.
**Expected effect**: Future fix waves run full test suites. Regressions are caught before delivery.

---

## Mutation Gym-4 — 2026-05-25

**Session**: Gym experiments E15–E17 — H105, H106, H107
**File**: `~/vsm/vsm-fitness-gym/references/experiments.md`, `~/vsm/viable-swarm-model/references/hypotheses.md`
**Type**: append-only
**Rationale**:
1. E15 (H105): Process audit + prompt efficacy test. Confirmed that generic coder simulating S5 inline fix bypasses re-audit. vsm_backend_fix_agent enforces full protocol.
2. E16 (H106): Proxy experiment with fictional build artifacts. vsm_meta caught all process violations and generated 8 hypotheses + mutations. Phase 8b mechanism validated.
3. E17 (H107): Controlled experiment with 3 backend + 2 frontend BLOCKERs. Domain fix agents outperformed generic coder on security invariant enforcement (admin exclusion) and re-audit artifact production (100% vs 0%).
4. H108 and H109 added to main skill backlog from vsm_meta output.
**Expected effect**: Main skill hypothesis backlog has zero original untested items. Gym experiment log documents all three experiments with full methodology and results.

---
