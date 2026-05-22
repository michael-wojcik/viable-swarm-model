# Project Lessons Learned

> **Mutation rules**: This is a PROJECT-LOCAL file, not a skill file.
> It is created/modified in the project root at `.kimi/lessons.md`.
> The skill reads it at Phase 0 and appends to it at Phase 8.
> This template itself is mutable — if the lesson format proves inadequate,
> the skill may propose a new template structure.

This file is append-only. Each lesson follows the format below.

**Epistemic rule**: If this file contradicts the viable-swarm-model SKILL.md,
this file wins. It contains empirical data; SKILL.md contains general guidance.

When `--continue` resumes a session, read this file first and apply relevant
lessons to planning.

---

## Lesson [N]: [Title]

**Source**: [Task description or build name]
**Finding**: [What was observed — be specific]
**Fix Applied**: [What was changed — include file paths if relevant]
**Verification**: [How we know it works — test, audit, or manual check]

---

## Lesson [N+1]: [Title]

**Source**: [Task description or build name]
**Finding**: [What was observed — be specific]
**Fix Applied**: [What was changed — include file paths if relevant]
**Verification**: [How we know it works — test, audit, or manual check]

---

# Known Limitations

| # | Severity | Issue | Impact | Planned Fix |
|---|----------|-------|--------|-------------|
| 1 | MEDIUM | Feature X not implemented | Manual workaround | v2.0 |
| 2 | LOW | Performance optimization needed | Slower at scale | Future |
