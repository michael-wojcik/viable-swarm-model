# VSM Mutation Cemetery — Removed Rules Archive
> Updated by: S5 when removal gate triggers (≥2 ineffective mutations)
> Auto-maintained by: session-end hook (updates "Builds since removal" counters)

This file archives mutations that were removed for ineffectiveness.
The history of what was tried and rejected is valuable — it prevents
re-adding the same broken rules.

## Removal Rules
1. A mutation is moved here (not deleted) when:
   - Its target failure mode recurred in 3+ builds despite the mutation
   - Coach scores it 1–2 on effectiveness scale
   - The removal gate (≥2 ineffective mutations) triggers
2. The original rule text is preserved exactly.
3. The replacement (if any) is documented.
4. "Builds since removal" and "Recurrence since removal" are auto-updated.

## Cemetery Entries

### R-1 — FB19-7: Cross-skill mutation log review
**Removed**: 2026-06-02 (comprehensive audit)
**Type**: append-only
**Target failure**: Main skill mutation log recording gym/coach mutations
**Applied**: 2026-05-25
**Ineffective in builds**: FB19–FB25 (7 builds)
**Original rule text**: "Main skill mutation-log.md should NOT record gym or coach mutations. Each skill maintains its own log."
**Rationale for removal**: The three skills share a single git repository at `~/vsm/`. Separating logs by skill creates artificial boundaries where none exist in the filesystem. The cross-skill integration is a feature, not a bug.
**Replacement**: None — remove the constraint entirely.
**Builds since removal**: 0
**Recurrence since removal**: N/A (constraint removed, not replaced)

### R-2 — FB23-3: Inline fix prevention (prompt-only layer)
**Removed**: 2026-06-02 (comprehensive audit)
**Type**: refinement
**Target failure**: S5 performing inline fixes during Phase 6/7 boundary
**Applied**: 2026-06-01
**Ineffective in builds**: FB23, FB24 (2 builds)
**Original rule text**: "S5 MUST NOT perform inline fixes during Phase 6/7 boundary. Route to Phase 7 fix agents."
**Rationale for removal**: Prompt-only instructions cannot prevent S5 from bypassing boundaries under time pressure. The boundary-guardian.sh hook already provides tool-level enforcement for S5, and prompt-hardened rules in vsm-main.md provide Layer 1 for all agents. A third redundant prompt rule adds zero marginal enforcement.
**Replacement**: Strengthen boundary-guardian.sh to block ALL source file writes (not just .py/.ts/.js) when synthesis-integration.md exists without re-audit-report.md.
**Builds since removal**: 0
**Recurrence since removal**: —

### R-3 — FB25-S2: Mutation checkpoint hard gate (prompt-only)
**Removed**: 2026-06-04 (comprehensive audit)
**Type**: structural
**Target failure**: Mutation Verification Checkpoint (`mutations-applied.md`) bypassed
**Applied**: 2026-06-02
**Ineffective in builds**: FB26 (1 build — 4th consecutive bypass overall)
**Original rule text**: "Phase 8c-ii completion explicitly depends on three verifiable criteria: (1) file exists, (2) all measured effects non-empty, (3) S5 explicitly states completion."
**Rationale for removal**: Prompt-only instructions are insufficient to prevent S5 from bypassing checkpoints under session-end time pressure. The mutation was empirically ineffective (Score: 1) — `mutations-applied.md` was still missing in FB26. Superseded by FB26-S3 structural hard gate (tool-enforced, retroactive creation detection, Phase 8c-ii moved BEFORE Phase 8b).
**Replacement**: FB26-S3 — `stop-verifier.sh` hook blocks session end if checkpoint missing; Phase 8c-ii runs BEFORE Phase 8b.
**Builds since removal**: 0
**Recurrence since removal**: —

> **Previous state**: No entries. This organism had never removed a mutation before the 2026-06-02 audit. The removal gate (Phase 8c-ii, Step 8c-6) had never triggered despite 5 ineffective mutations sitting in the Active Mutation Portfolio.
> **Audit action**: Pre-emptively moved 2 clearly obsolete mutations to cemetery. Remaining 3 ineffective mutations (FB22-2, FB18-10, FB9/P46) await redesign in FB26.


### R-4 — FB26-S5: Session-start hook auto-injection
**Removed**: 2026-06-04 (comprehensive audit)
**Type**: structural
**Target failure**: Session-start hook failed to fire in 3 consecutive builds, leaving S5 without skill-state initialization
**Applied**: 2026-06-03
**Ineffective in builds**: FB28, FB29 (3 consecutive failures)
**Original rule text**: "Auto-inject skill-state.md read into S5 context at session start via session-start.sh hook."
**Rationale for removal**: The kimi-cli hook engine does not reliably fire session-start hooks. Empirical testing confirmed 0/3 successful firings. The replacement is explicit S5 manual checklist in Phase 0 (see SKILL.md Step 0b).
**Replacement**: Explicit Phase 0 manual checklist — S5 reads skill-state.md, mutation-state.md, and hypotheses.md manually before spawning any agents.
**Builds since removal**: 0
**Recurrence since removal**: —
