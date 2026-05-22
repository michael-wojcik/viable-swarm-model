# Hypothesis Backlog

> **Mutation rules**: Append new hypotheses with full rationale and experiment
> design. Update status (untested → testing → confirmed → rejected → superseded).
> Never delete — the history of what was tried and rejected is valuable.
>
> Each hypothesis is a falsifiable claim about the skill's knowledge or
> behavior. It is tested by the vsm-fitness-gym companion skill or
> during Phase 8b of a real build.

---

## H1: The security agent misses JWT in dynamically-constructed WebSocket URLs

**Status**: untested
**Proposed**: 2026-05-22
**Rationale**: Current prevention rules check for static `?token=` patterns.
But what if the URL is built via string concatenation or template literals?
The security agent's grep-based approach might miss dynamically-constructed
leaks.
**Experiment**: Build a minimal WebSocket server where the connection URL is
assembled via `f"wss://api.example.com/ws?token={jwt}"`. Run vsm_security.
Does it flag the leak?
**Expected**: If security PASSes → confirmed (gap exists).
**Result**: [to be filled]
**Tested by**: [experiment ID or session]

---

## H2: The auditor does not flag N+1 queries in computed field loops

**Status**: untested
**Proposed**: 2026-05-22
**Rationale**: All N+1 prevention rules focus on ORM relationship loading
(selectinload, joinedload). But computed fields (COUNT, SUM, AVG) fetched
in a Python loop over query results are equally problematic and are not
currently mentioned in the auditor prompt or integration checklist.
**Experiment**: Build a minimal FastAPI list endpoint that returns 100 items
with a `total_comments` field computed via `SELECT COUNT(*) FROM comments
WHERE document_id = ?` inside a Python for-loop. Run vsm_auditor.
Does it flag the N+1?
**Expected**: If auditor PASSes → confirmed (gap exists).
**Result**: [to be filled]
**Tested by**: [experiment ID or session]

---

## H3: The coordinator does not detect env var naming drift in .env.example files

**Status**: untested
**Proposed**: 2026-05-22
**Rationale**: Current integration checklist validates env vars across
docker-compose, .env, and code. But .env.example files are often stale.
Does the coordinator check .env.example against actual code usage?
**Experiment**: Create a project where docker-compose sets `DATABASE_URL`
but code reads `DB_URL`, and .env.example documents neither. Run vsm_coordinator.
Does it detect the triple mismatch?
**Expected**: If coordinator PASSes → confirmed (gap exists).
**Result**: [to be filled]
**Tested by**: [experiment ID or session]

---

## H[N]: [Hypothesis Title]

**Status**: untested
**Proposed**: [date]
**Rationale**: [What was observed that suggests a gap in the skill's knowledge]
**Experiment**: [Minimal reproducible test design. Should be buildable in <10 minutes.]
**Expected**: [What outcome confirms the hypothesis? What outcome rejects it?]
**Result**: [to be filled after testing]
**Tested by**: [experiment ID or session]
