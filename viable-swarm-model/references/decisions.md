# VSM Decision Provenance Log
> Updated by: S5 after key decisions (Phase 0 plan approval, structural mutation approval, etc.)
> Read by: vsm_meta (Phase 8b) for causal analysis

This file tracks high-stakes decisions so the skill can later ask
"Was that decision correct?" and learn from the outcome.

## Decision Template
```markdown
## D[N] — YYYY-MM-DD HH:MM:SS
**Session**: [session_id]
**Decision**: [what was decided]
**Rationale**: [why S5 decided this]
**Predicted outcome**: [what S5 expected]
**Actual outcome**: [filled in post-build by vsm_meta]
**Correct?**: [yes/no/partially — filled in by meta-reflection]
**Lessons**: [what this teaches about S5's decision-making]
```

## Decisions Log

> **AUDIT FINDING (2026-06-03)**: This file has been empty for 25+ builds despite being
> referenced in SKILL.md and agent prompts. This is **documentation theater** — a process
> that exists on paper but is never executed. The root cause is that S5 has no
> tool-enforced reminder to log decisions, and the file is not checked by any gate.
>
> **Decision**: Rather than accumulate empty template entries, this file is now
> **deprecated as a manual log** and replaced with automated decision extraction.
> The `decision-enforcer.sh` hook already captures plan.md writes and warns if
> decisions.md is missing — but it does not block. For true decision provenance,
> see `.kimi/decisions-auto.md` in each build directory (extracted by session-end hook
> from plan.md structural mutation approval sections).
>
> **If this file remains empty after FB30**: Remove it entirely and update all
> references to point to `.kimi/decisions-auto.md`.

---

## D1 — 2026-06-03 04:15:00
**Session**: Comprehensive ecosystem audit (S5 orchestrator)
**Decision**: Deprecate manual decisions.md in favor of automated extraction
**Rationale**: 25 builds with zero manual entries proves the honor-system approach fails. The hook captures plan.md writes; decisions should be extracted automatically, not rely on S5 memory.
**Predicted outcome**: Decision provenance improves without adding S5 cognitive load
**Actual outcome**: [to be filled after FB27]
**Correct?**: [pending]
**Lessons**: Honor-system processes that are not checked by gates become theater

