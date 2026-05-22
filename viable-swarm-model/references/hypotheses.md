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

## H4: A dedicated wiring agent would reduce entry-point conflicts by 80%

**Status**: untested
**Proposed**: 2026-05-22
**Rationale**: In FB1, the backend implementation agent and worker agent both modified
`main.py` and `worker.py`. The later agent overwrote the earlier agent's changes,
causing integration failures. If a single "wiring" agent ran after all implementation
agents to handle entry-point imports and registrations, these conflicts would not occur.
**Experiment**: Run two fitness builds identical in scope. Build A uses current parallel
approach. Build B adds a dedicated wiring agent that runs after implementation agents
and is the ONLY agent allowed to modify main.py/App.tsx. Count entry-point conflicts.
**Expected**: Build B has ≤1 entry-point conflict; Build A has ≥3.
**Result**: [to be filled]
**Tested by**: [experiment ID or session]

---

## H5: Requiring fix agents to run verification commands would reduce false positives by 90%

**Status**: untested
**Proposed**: 2026-05-22
**Rationale**: In FB1 Fix Wave 2, the fix agent claimed to update `useYjs.ts` to include
the JWT token in the URL path. In reality, the token was still passed as the `room`
parameter to `WebsocketProvider` — the fix was a false positive. If fix agents were
required to run a shell verification command (e.g., `grep` for the expected change)
before reporting success, false positives would be caught.
**Experiment**: Run 10 fix tasks with the current prompt (no verification requirement).
Run 10 identical fix tasks with a modified prompt requiring a verification shell command.
Count false positive fixes in each group.
**Expected**: Control group (no verification): ≥3 false positives. Treatment group
(verification required): ≤1 false positive.
**Result**: [to be filled]
**Tested by**: [experiment ID or session]

---

## H6: Pre-installing test dependencies would enable test execution for 70% of Python builds

**Status**: untested
**Proposed**: 2026-05-22
**Rationale**: In FB1 Phase 4, the tester agent could not write or execute tests because
the environment lacked pytest, pytest-asyncio, httpx, and PostgreSQL/Redis. The agent
spent most of its time failing shell commands instead of writing tests. If common test
dependencies were pre-installed, the agent could focus on test logic.
**Experiment**: Compare test wave outcomes across 5 Python fitness builds with current
environment vs. 5 builds with pytest/pytest-asyncio/httpx pre-installed.
**Expected**: Pre-installed deps group produces executable test files in 70%+ of builds;
current group produces executable tests in ≤20%.
**Result**: [to be filled]
**Tested by**: [experiment ID or session]

---

## H7: Adding GraphQL depth limit to architect checklist would result in 95% implementation rate

**Status**: untested
**Proposed**: 2026-05-22
**Rationale**: FB1's GraphQL schema had no depth limiting — a HIGH security finding.
Neither the architect nor the backend coder included it. If the architect's design
checklist explicitly required "GraphQL depth limit (max 10) + complexity analysis",
the backend coder would likely implement it.
**Experiment**: Run 5 GraphQL-enabled fitness builds with current checklist. Run 5 with
modified checklist including GraphQL depth limit requirement. Count builds with depth
limiting implemented.
**Expected**: Current checklist: 0-1 builds with depth limiting. Modified checklist: 4-5 builds.
**Result**: [to be filled]
**Tested by**: [experiment ID or session]

---

## H8: Adding rate limiting to foundation requirements would result in 80% implementation rate

**Status**: untested
**Proposed**: 2026-05-22
**Rationale**: FB1 had no rate limiting on auth endpoints — a HIGH security finding.
The foundation wave created auth scaffolding but did not include rate limiting. If the
foundation wave requirements explicitly included "rate limiting on auth endpoints",
the backend foundation agent would implement it early.
**Experiment**: Run 5 auth-enabled fitness builds with current foundation requirements.
Run 5 with modified requirements including rate limiting. Count builds with rate limiting.
**Expected**: Current: 0-1 builds with rate limiting. Modified: 3-4 builds.
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
