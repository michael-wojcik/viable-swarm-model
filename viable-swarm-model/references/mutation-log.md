# Mutation Log

> This file is append-only. Every modification the skill makes to its own
> files is recorded here with full rationale. If the skill becomes corrupted,
> this log is the audit trail for `git revert`.
>
> **Mutation rules**: Append only. Each entry includes: session context,
> file changed, type of change, rationale, expected effect.

---

## Mutation 1 — 2026-05-22

**Session**: Initial creation of viable-swarm-model skill
**File**: `SKILL.md`, `references/*`, `assets/*`
**Type**: create
**Rationale**: The skill was originally designed as a static instruction set.
A learning organism cannot have immutable DNA. All files must be mutable,
with regulated mutation rules, self-test at Phase 0, and a mutation log.
**Expected effect**: Future sessions will load a skill that can evaluate its
own performance and append new prevention rules, patterns, and anti-patterns
based on empirical results. The skill evolves between sessions.

---

## Mutation [N] — YYYY-MM-DD

**Session**: [Brief description of the task/session]
**File**: [Which file was modified]
**Type**: [append | edit | strikethrough | structural]
**Rationale**: [What empirical finding motivated this change. Be specific:
which build, which bug, which false positive, which missed vulnerability.]
**Expected effect**: [How the next session should behave differently because
of this mutation. What should be caught that wasn't? What should pass that
was falsely flagged?]

**Before**:
```
[content or summary of what existed]
```

**After**:
```
[content or summary of what replaced it]
```

## Mutation [2] — 2026-05-22

**Session**: Fitness build FB1 (DocuFlow)
**File**: Multiple references files
**Type**: append
**Rationale**: FB1 revealed 5 systemic gaps: (1) parallel agents overwrite entry points,
(2) fix agents claim false positives, (3) tester agent cannot function without runtime deps,
(4) GraphQL depth limiting missing from design checklist, (5) rate limiting missing from
foundation requirements. These are empirical findings from a 3500+ line multi-service build.
**Expected effect**: Next session with GraphQL will include depth limiting in design.
Next fix wave will require verification commands. Entry point conflicts will be reduced.
Tester agent environment awareness will improve.

**Files modified**:
- `references/hypotheses.md` — Added H4-H8
- `references/pattern-library.md` — Added Pattern #38 (WebSocket path token auth)
- `references/anti-patterns.md` — Added Anti-Patterns #42-43 (fix false positives, entry point overwrites)
- `references/security-lessons.md` — Added L25-L26 (GraphQL depth limit, rate limiting)
- `references/integration-checklist.md` — Added checks #21-22 (parallel coordination, WebSocket auth)
