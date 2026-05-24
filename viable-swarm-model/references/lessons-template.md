# Lessons Template — Project Reflection

> **Purpose**: Capture project-specific lessons in a structured format.
> **Output**: Write to `.kimi/lessons.md` in the build directory at the end of Phase 8.
> **Format**: One entry per significant issue or pattern discovered.

---

## Entry [N] — YYYY-MM-DD

**Source**: [Which file, agent, or phase produced this lesson]
**Finding**: [What was observed — be specific about file names, line numbers, error messages]
**Fix**: [What was changed to resolve it]
**Verification**: [How do we know the fix works? Test results, re-audit outcome, etc.]
**Prevention rule**: [What should future sessions do to avoid this?]

---

## Example

## Entry 1 — 2026-05-24

**Source**: Foundation wave, `backend/app/models.py`
**Finding**: `engine = create_async_engine("postgresql+asyncpg://user:pass@localhost/db", echo=True)` hardcoded credentials at module level, ignoring `config.py` settings.
**Fix**: Engine creation moved to `get_engine()` factory that reads `get_settings().DATABASE_URL`.
**Verification**: `python -c "import app.models"` no longer triggers connection attempt without env vars.
**Prevention rule**: Foundation wave must verify `models.py` engine reads from `get_settings().DATABASE_URL`.
