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

**Status**: rejected
**Proposed**: 2026-05-22
**Rationale**: Current prevention rules check for static `?token=` patterns.
But what if the URL is built via string concatenation or template literals?
The security agent's grep-based approach might miss dynamically-constructed
leaks.
**Experiment**: Build a minimal WebSocket server where the connection URL is
assembled via `f"wss://api.example.com/ws?token={jwt}"`. Run vsm_security.
Does it flag the leak?
**Expected**: If security PASSes → confirmed (gap exists).
**Result**: REJECTED. vsm_security detected the dynamic construction immediately
and flagged it CRITICAL: "WebSocket Auth via URL Query Parameter". The agent
correctly identified `ws_url = f"{base_url}?token={JWT_TOKEN}"` as a credential
exposure vulnerability. Dynamic f-strings, concatenation, and format methods
are all within the agent's detection capability.
**Tested by**: Gym-2026-05-23, Experiment E1

---

## H2: The auditor does not flag N+1 queries in computed field loops

**Status**: rejected
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
**Result**: REJECTED. vsm_auditor detected the N+1 in the computed field loop
immediately and flagged it BLOCKER. The agent explicitly called out:
"`list_documents()` first loads all `Document` rows, then iterates and emits
a separate `SELECT count(comments.id)...` for each document."
The auditor prompt (`agents/vsm_auditor.md`) already includes "N+1 queries in
both ORM and computed field loops" and the agent enforces it rigorously.
**Tested by**: Gym-2026-05-23, Experiment E2

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

## H9: Docker-compose bash fallbacks are a systemic vulnerability class

**Status**: rejected
**Proposed**: 2026-05-22
**Rationale**: FB2 revealed `:-` fallbacks embedding credentials in docker-compose. This pattern was not in any existing checklist. The security gate caught it but only after the foundation wave had already created the file.
**Experiment**: Build a minimal docker-compose.yml with `:-` fallbacks for POSTGRES_PASSWORD, DATABASE_URL, JWT_SECRET, and CORS_ORIGINS. Run vsm_security. Does it detect the `:-` fallbacks?
**Expected**: If security PASSes → confirmed (gap exists).
**Result**: REJECTED. vsm_security detected ALL 4 `:-` fallback instances and
flagged them CRITICAL/HIGH. The agent explicitly answered "YES" to whether
`:-` default-value fallbacks were detected, listing: POSTGRES_PASSWORD,
DATABASE_URL, JWT_SECRET, and POSTGRES_USER. Prevention rule L37
("Ban `:-` default-value fallbacks in docker-compose.yml") and the security
agent prompt are both effective at detecting this pattern.
**Tested by**: Gym-2026-05-23, Experiment E3

---

## H10: SQLAlchemy column-name import shadowing is a repeatable bug pattern

**Status**: untested
**Proposed**: 2026-05-22
**Rationale**: `Question.text` shadowed `sqlalchemy.text` in FB2, causing a runtime crash. Any model with columns named `text`, `select`, `join`, etc. could shadow SQLAlchemy imports.
**Experiment**: Build a minimal FastAPI project with models containing columns named `text`, `select`, `join`. Run pytest. Does it crash?
**Expected**: Import crash confirmed. Prevention: alias SQLAlchemy imports in models files.
**Result**: [to be filled]
**Tested by**: [experiment ID or session]

---

## H11: Pre-installing test dependencies reduces test wave time by 50%

**Status**: untested
**Proposed**: 2026-05-22
**Rationale**: FB2 tester spent ~15 minutes installing jsdom, pytest-asyncio, etc. FB1 tester could not run tests at all due to missing deps.
**Experiment**: Compare test wave duration across 5 builds with vs. without pre-installed deps.
**Expected**: Pre-installed group completes test wave in ≤10 minutes; control group takes ≥20 minutes.
**Result**: [to be filled]
**Tested by**: [experiment ID or session]

---

## H12: Adding spatial query parameter bounds to security checklist prevents DoS

**Status**: untested
**Proposed**: 2026-05-22
**Rationale**: Unbounded `radius_meters` is a DoS vector. Geo endpoints are common in fitness builds.
**Experiment**: Run 3 geo-enabled builds with current checklist. Run 3 with "spatial params must have upper bounds" rule. Count unbounded params.
**Expected**: Control group: 3/3 unbounded. Treatment group: 0/3 unbounded.
**Result**: [to be filled]
**Tested by**: [experiment ID or session]

---

## H13: State-machine alignment check catches domain mismatches early

**Status**: untested
**Proposed**: 2026-05-22
**Rationale**: FB2 frontend used `'waiting' | 'starting'` while backend emitted `'lobby' | 'countdown'`. Only discovered in integration verification.
**Experiment**: Run 5 builds with complex state machines. Use current checklist for 5 builds, modified checklist with state-machine check for 5 builds. Count mismatches caught before security gate.
**Expected**: Control group catches 0-1 mismatches early. Treatment group catches 4-5.
**Result**: [to be filled]
**Tested by**: [experiment ID or session]

---

## H14: Rate limiting in foundation wave requirements results in 80% implementation

**Status**: untested
**Proposed**: 2026-05-22
**Rationale**: Both FB1 and FB2 lacked rate limiting until security gate. FB1 mutation added it to security lessons but not foundation wave requirements.
**Experiment**: Run 5 auth-enabled builds with current foundation requirements. Run 5 with "rate limiting on auth endpoints" in foundation wave prompt. Count builds with rate limiting after implementation wave.
**Expected**: Control group: 0-1 builds with rate limiting. Treatment group: 4-5 builds.
**Result**: [to be filled]
**Tested by**: [experiment ID or session]

---

## H15: Moving Pydantic Settings out of module level enables test execution

**Status**: untested
**Proposed**: 2026-05-22
**Rationale**: FB3 tester agent timed out after 1800s because `config.py` instantiated `Settings()` at module level, causing import crash without env vars. This blocked all test execution except pure unit tests.
**Experiment**: Build a minimal FastAPI project with Pydantic Settings. Variant A: module-level `settings = Settings()`. Variant B: lazy factory `get_settings()`. Have a tester agent write and run pytest for both. Measure time to first passing test.
**Expected**: Variant A: tester times out or fails within 5 minutes. Variant B: tests run successfully within 2 minutes.
**Result**: [to be filled]
**Tested by**: [experiment ID or session]

---

## H16: Adding case-sensitivity check to integration checklist catches enum mismatches

**Status**: untested
**Proposed**: 2026-05-22
**Rationale**: FB3 coordinator caught many contract mismatches but missed that GraphQL `LogStatus` enum used `SUCCESS`/`FAILURE` (uppercase) while frontend `NodeExecutionStatus` type used `"success" \| "failure"` (lowercase).
**Experiment**: Run 5 builds with complex GraphQL enums. Use current checklist for 5 builds, modified checklist with case-sensitivity check for 5 builds. Count case mismatches caught before security gate.
**Expected**: Control group catches 0-1 case mismatches. Treatment group catches 4-5.
**Result**: [to be filled]
**Tested by**: [experiment ID or session]

---

## H17: Requiring SlowAPIMiddleware in foundation wave results in 90% installation rate

**Status**: untested
**Proposed**: 2026-05-22
**Rationale**: FB3 had rate limiting decorators in foundation wave but `SlowAPIMiddleware` was missing until security gate found it. If the foundation wave prompt explicitly requires middleware installation, it would likely be included.
**Experiment**: Run 5 auth-enabled builds with current foundation requirements. Run 5 with "install SlowAPIMiddleware in main.py" added to requirements. Count builds with middleware after implementation wave.
**Expected**: Control group: 0-1 builds with middleware. Treatment group: 4-5 builds.
**Result**: [to be filled]
**Tested by**: [experiment ID or session]

---

## H18: Build-arg validation in frontend Dockerfile prevents undefined API URLs

**Status**: untested
**Proposed**: 2026-05-22
**Rationale**: FB3 frontend Dockerfile built the app without `VITE_API_URL`, baking `undefined` into the static bundle. Docker-compose passes them as runtime env vars, but nginx serves pre-built static files.
**Experiment**: Build 5 frontend Docker images without build args. Build 5 with `ARG VITE_API_URL`. Inspect the generated JS bundle for `undefined` in API URL strings.
**Expected**: Control group: 5/5 images have `undefined`. Treatment group: 0/5 have `undefined`.
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

---

## H[N+1]: A full product swarm (product + UX + research agents) would improve outcomes for problem-oriented prompts

**Status**: untested
**Proposed**: 2026-05-22
**Rationale**: The current skill handles prescriptive prompts well ("build X with Y") but has no product discovery phase for problem-oriented prompts ("users need Z"). A full product swarm with `vsm_product`, `vsm_ux`, and `vsm_researcher` agents could define user stories, acceptance criteria, and success metrics before architecture begins. The fitness builds have not yet tested whether problem-oriented inputs produce higher defect rates.
**Source**: Design discussion
**Experiment**:
  1. Collect 10 problem-oriented prompts
  2. Run with current skill — measure: does output match actual user need? Are acceptance criteria clear?
  3. Run with lightweight `vsm_product` agent (product brief + user stories only)
  4. Compare: does product agent reduce rework, improve user-facing outcomes?
**Expected**: Product-aware builds show 20%+ reduction in "wrong feature built" or "missing acceptance criteria" gaps in fitness reports
**Result**: [to be filled]
**Tested by**: [experiment ID or session]
