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

> **Previous state**: No entries. This organism had never removed a mutation before the 2026-06-02 audit. The removal gate (Phase 8c-ii, Step 8c-6) had never triggered despite 5 ineffective mutations sitting in the Active Mutation Portfolio.
> **Audit action**: Pre-emptively moved 2 clearly obsolete mutations to cemetery. Remaining 3 ineffective mutations (FB22-2, FB18-10, FB9/P46) await redesign in FB26.

