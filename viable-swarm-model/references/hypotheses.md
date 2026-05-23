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
**Result**: CONFIRMED. A minimal experiment with one ambiguous prompt ("Users need a way to share grocery lists...") showed dramatic scope-creep reduction. The control architect (raw prompt) added an entire auth subsystem (JWT/bcrypt/register/login), multiple lists per household, and quantity/unit fields — all explicitly out of scope. The treatment architect (with product brief) produced a design with only 3 core features, 12+ explicit scope boundaries, and no auth. The product brief's 'Out of Scope' list acted as effective guardrails.
**Tested by**: Gym-2026-05-23, Experiment E4

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

## H[N+1]: The vsm_product subagent reduces implementation defects for problem-oriented prompts

**Status**: confirmed
**Proposed**: 2026-05-22
**Rationale**: The `vsm_product` agent was added to handle problem-oriented prompts ("Users need Z") by producing structured product briefs before architecture begins. Without it, the architect receives ambiguous input, which may lead to scope creep, missing acceptance criteria, and misaligned implementation.
**Source**: Agent addition — `vsm_product`
**Experiment**:
  1. Design 5 problem-oriented prompts (e.g., "Users need to collaborate on documents in real-time")
  2. **Build A** (control): Pass raw prompt directly to `vsm_architect`, run full workflow
  3. **Build B** (test): Spawn `vsm_product` first, pass product brief to `vsm_architect`, run full workflow
  4. Compare using `vsm_fitness_coach` / `vsm_trainer`:
     - Phase 1 (Intelligence) scores: does Build B produce clearer architecture docs?
     - Phase 3 (Implementation) BLOCKER counts
     - "Scope creep" or "unclear requirements" gap frequency
     - Fix iteration count in Phase 7
**Expected**: Build B shows 20%+ fewer implementation-phase BLOCKERs and 30%+ fewer "unclear requirements" gaps. If no significant difference → `vsm_product` may be redundant; consider merging into architect prompt.
**Result**: [to be filled]
**Tested by**: [experiment ID or session]

---

## H[N+2]: vsm_security with Security Fix Mode reduces security regressions compared to read-only audit

**Status**: rejected
**Proposed**: 2026-05-22
**Rationale**: `vsm_security` was updated from read-only audit to include Security Fix Mode — writing security tests and surgical fixes for CRITICAL/HIGH findings. Previously, security findings were reported to generic `coder` agents who might implement fixes incorrectly or miss edge cases. The hypothesis is that security-specific tests and fixes written by the security agent itself are more correct and complete.
**Source**: Agent update — `vsm_security` Security Fix Mode
**Experiment**:
  1. Design 3 projects with known security vulnerabilities (auth bypass, injection, CORS misconfig)
  2. **Build A** (control): `vsm_security` reads-only, reports findings, generic `coder` fixes them
  3. **Build B** (test): `vsm_security` writes security tests + surgical fixes inline
  4. Re-run `vsm_security` audit on both builds after fixes
  5. Compare: does Build B have fewer remaining vulnerabilities? Are security tests more comprehensive?
**Expected**: Build B shows 30%+ fewer remaining CRITICAL/HIGH findings in re-audit. Security tests in Build B cover more attack vectors.
**Result**: REJECTED. In a minimal experiment with a single vulnerable FastAPI app, the generic coder (control) fixed all 4 CRITICAL/HIGH findings including sensitive-field stripping in response DTOs. The vsm_security Security Fix Mode agent (treatment) missed Finding 4 (HIGH: public DTO exposes sensitive fields) and left `secret`/`owner` exposed. The treatment also used overly broad `except Exception:` instead of specific `jwt.PyJWTError`. The generic coder produced cleaner, more complete fixes.
**Tested by**: Gym-2026-05-23, Experiment E5

---

## H[N+3]: Native YAML custom subagents (via --agent-file) would improve agent consistency vs markdown prompts

**Status**: untested  
**Proposed**: 2026-05-22  
**Rationale**: Currently, custom agents (`vsm_architect`, `vsm_auditor`, etc.) are defined as markdown prompt files spawned via the `Agent` tool using built-in `subagent_type` values (`coder`, `explore`, `plan`). Kimi CLI supports native custom subagent definitions in YAML agent files with `--agent-file`, including tool restrictions (`exclude_tools`), inheritance (`extend`), and template variables (`system_prompt_args`). This could reduce prompt drift, enforce tool boundaries at the CLI level, and simplify maintenance. However, this requires session-level agent configuration, making it incompatible with the current skill-loading model (`extra_skill_dirs`). This hypothesis is **low priority** — only test if prompt drift or tool misuse becomes a measurable problem in fitness builds.
**Source**: CLI docs exploration
**Experiment**:
  1. Create `vsm-agent.yaml` defining all custom subagents with tool restrictions and inheritance
  2. Start session with `kimi --agent-file vsm-agent.yaml`
  3. Run 5 fitness builds with the YAML agent configuration
  4. Run 5 fitness builds with the current markdown prompt approach
  5. Compare: agent tool misuse rates, prompt consistency, build quality scores
**Expected**: YAML approach shows measurable reduction in agent tool misuse (e.g., auditor writing files, architect coding) and more consistent outputs. If no difference → markdown approach is sufficient; close hypothesis.
**Result**: [to be filled]
**Tested by**: [experiment ID or session]

---

## H[N+4]: A full product swarm (product + UX + research agents) would improve outcomes for problem-oriented prompts

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

---

## H19: Adding GraphQL field name alignment to integration checklist prevents Strawberry auto-camelCase drift

**Status**: untested
**Proposed**: 2026-05-23
**Rationale**: In FB4, backend `graphql.py` used `assigned_technician_id` which Strawberry auto-camelCased to `assignedTechnicianId`. However, the frontend query used `technicianId` ( expecting `technician_id` → `technicianId`). The existing case-sensitive enum alignment check (Check 24) caught enum values but NOT field names. This caused a BLOCKER that survived the first integration check and fix wave.
**Source**: Fitness build FB4
**Experiment**:
  1. Run 5 GraphQL-enabled fitness builds with current checklist (no field name check)
  2. Run 5 with modified checklist including "GraphQL field names match frontend queries exactly"
  3. Count field name mismatch BLOCKERs in each group
**Expected**: Control group: 3-5 field name mismatches. Treatment group: 0-1 mismatches.
**Result**: [to be filled]
**Tested by**: [fitness build or gym experiment]

---

## H20: Documenting auth response contract in foundation wave prevents login/register contract mismatches

**Status**: untested
**Proposed**: 2026-05-23
**Rationale**: FB2, FB3, and FB4 all had login/register response shape mismatches between backend and frontend. The backend returned `access_token` while frontend expected `token`, or backend required `org_id` while frontend didn't send it. If the foundation wave explicitly documented the exact JSON keys and required fields for auth endpoints, implementation agents would follow the contract.
**Source**: Fitness builds FB2, FB3, FB4
**Experiment**:
  1. Run 5 auth-enabled builds with current foundation requirements
  2. Run 5 with "auth response contract must be documented in api-spec.md with exact JSON keys" added to architect checklist
  3. Count login/register contract BLOCKERs in each group
**Expected**: Control group: 3-5 contract mismatches. Treatment group: 0-1 mismatches.
**Result**: [to be filled]
**Tested by**: [fitness build or gym experiment]

---

## H21: Orphaned exports scan in integration check prevents dead code accumulation

**Status**: untested
**Proposed**: 2026-05-23
**Rationale**: In FB4, `auth.py` defined `require_role()` which was never imported by any router. `roles.py` defined an identical `require_roles()` which was used. This duplicate/orphaned code was not caught until the coordinator's integration check flagged it. A systematic scan for exported functions/classes that are never imported would catch this earlier.
**Source**: Fitness build FB4
**Experiment**:
  1. Review last 5 fitness builds for orphaned exports
  2. Count instances per build
  3. Add "orphaned exports scan" to integration checklist
  4. Run next 5 builds and compare orphan counts
**Expected**: Average orphan count drops from 2-3 per build to 0-1 per build.
**Result**: [to be filled]
**Tested by**: [fitness build or gym experiment]

---

## H22: WebSocket event name dictionary cross-check prevents emit/listen mismatches

**Status**: untested
**Proposed**: 2026-05-23
**Rationale**: In FB4, `api-spec.md` defined WebSocket events `authenticate`/`authenticated`/`auth_error`, but `sio.py` implemented `auth`/`auth_ok`/`auth_err`. The shared `sio-events.ts` file had yet another variant. The integration checker focused on URL/proxy wiring but missed the event payload semantics. A cross-check between api-spec, sio.py, and sio-events.ts would catch this.
**Source**: Fitness build FB4
**Experiment**:
  1. Review last 5 WebSocket-enabled fitness builds for event name mismatches
  2. Count mismatches per build
  3. Add "WebSocket event name dictionary cross-check" to integration checklist
  4. Run next 5 builds and compare mismatch counts
**Expected**: Mismatch count drops from 1-2 per build to 0 per build.
**Result**: [to be filled]
**Tested by**: [fitness build or gym experiment]

---

## H23: Adding GraphQL RBAC parity check to the security gate prevents REST/GraphQL authorization drift

**Status**: untested
**Proposed**: 2026-05-23
**Rationale**: In FB5, GraphQL mutations (`createIncident`, `updateIncident`) lacked the same role guards as REST endpoints. The implementation auditor and coordinator did not catch this drift. Only the security gate flagged it as HIGH. If the security gate checklist explicitly requires "GraphQL resolvers enforce the same RBAC as REST endpoints", this drift would be caught earlier.
**Source**: Fitness build FB5, Phase 3 & 6 gaps
**Experiment**:
  1. Review last 5 fitness builds with GraphQL + REST
  2. Count instances where GraphQL RBAC diverged from REST RBAC
  3. Add "GraphQL RBAC parity" check to security gate checklist
  4. Run next 5 builds and compare drift counts
**Expected**: Control group: 3-5 RBAC drifts. Treatment group: 0-1 drifts.
**Result**: [to be filled]
**Tested by**: [fitness build or gym experiment]

---

## H24: Adding GraphQL ownership filtering check to the security gate prevents unscoped list queries

**Status**: untested
**Proposed**: 2026-05-23
**Rationale**: In FB5, GraphQL list queries (`incidents`, `resources`, `evidence`) and geo queries returned unscoped data for any authenticated user, while REST endpoints correctly scoped responder views. The security gate caught this as HIGH. If the security gate checklist explicitly requires "GraphQL list endpoints apply the same ownership filtering as REST", this vulnerability would be caught during the gate, not after delivery.
**Source**: Fitness build FB5, Phase 6 gap
**Experiment**:
  1. Review last 5 fitness builds with GraphQL list queries
  2. Count unscoped GraphQL list endpoints per build
  3. Add "GraphQL ownership filtering" check to security gate checklist
  4. Run next 5 builds and compare unscoped counts
**Expected**: Control group: 2-4 unscoped endpoints. Treatment group: 0 unscoped endpoints.
**Result**: [to be filled]
**Tested by**: [fitness build or gym experiment]

---

## H25: Requiring frontend tests in the tester agent prompt results in >50% frontend test coverage

**Status**: untested
**Proposed**: 2026-05-23
**Rationale**: In FB5, the tester agent wrote 86 backend tests but zero frontend tests. The tester prompt does not explicitly require frontend tests. If the prompt includes "write unit and integration tests for BOTH backend and frontend", the agent would likely produce frontend tests.
**Source**: Fitness build FB5, Phase 4 gap
**Experiment**:
  1. Run 5 fitness builds with current tester prompt (no frontend test requirement)
  2. Count frontend tests per build
  3. Update tester prompt to require frontend tests
  4. Run 5 builds with updated prompt
**Expected**: Control group: 0-5 frontend tests. Treatment group: 10+ frontend tests per build.
**Result**: [to be filled]
**Tested by**: [fitness build or gym experiment]

---

## H26: Adding entry-point and worker test requirements to the tester prompt increases coverage for main.py and tasks.py

**Status**: untested
**Proposed**: 2026-05-23
**Rationale**: In FB5, `app/main.py` and `app/tasks.py` showed 0% test coverage. The tester focused on routers, models, and auth. If the tester prompt explicitly requires "test entry-point wiring (main.py) and background workers (tasks.py)", coverage for these files would increase.
**Source**: Fitness build FB5, Phase 4 gap
**Experiment**:
  1. Run 5 fitness builds with current tester prompt
  2. Measure main.py and tasks.py coverage
  3. Update tester prompt with entry-point and worker test requirements
  4. Run 5 builds and compare coverage
**Expected**: Control group: 0% coverage for main.py/tasks.py. Treatment group: 30%+ coverage.
**Result**: [to be filled]
**Tested by**: [fitness build or gym experiment]

---

## H27: Adding a structured meta-reflection template to Phase 8b results in actionable skill improvement

**Status**: untested
**Proposed**: 2026-05-23
**Rationale**: In FB5, Phase 8b (Meta-Reflection) scored 2/5 — "essentially absent as a formal artifact." The `.kimi/lessons.md` contained some meta-learning bullets but no structured effectiveness audit, coverage audit, phase audit, agent audit, or hypothesis generation. If the skill provides a structured template or checklist for Phase 8b, the quality of meta-reflection would improve.
**Source**: Fitness build FB5, Phase 8b gap
**Experiment**:
  1. Review last 5 fitness builds for formal meta-reflection artifacts
  2. Score Phase 8b quality
  3. Add structured Phase 8b template to SKILL.md or references/
  4. Run next 5 builds and compare Phase 8b scores
**Expected**: Control group: average Phase 8b score 2.0. Treatment group: average score 4.0+.
**Result**: [to be filled]
**Tested by**: [fitness build or gym experiment]

---

## H28: Requiring the architect to document enum Python-type-to-GraphQL-value mapping prevents enum runtime bugs

**Status**: untested
**Proposed**: 2026-05-23
**Rationale**: In FB5, `graphql.py` defined `class Role(enum.Enum)` (not `str, enum.Enum`), causing `ValueError` when constructing from string values like `"commander"`. The coordinator caught this, but the implementation coder did not. If the architect's `api-spec.md` explicitly documents whether enums should use `str, enum.Enum` or `enum.Enum`, and the auditor checks this, the bug would be prevented.
**Source**: Fitness build FB5, coordinator finding
**Experiment**:
  1. Run 5 GraphQL-enabled builds with current architect prompt
  2. Count enum runtime bugs per build
  3. Update architect checklist to require `str, enum.Enum` for string-valued enums
  4. Run 5 builds and compare bug counts
**Expected**: Control group: 2-3 enum bugs. Treatment group: 0 bugs.
**Result**: [to be filled]
**Tested by**: [fitness build or gym experiment]

---

## H29: Adding a "circular import risk" check to the integration checklist prevents main.py→router→main.py loops

**Status**: untested
**Proposed**: 2026-05-23
**Rationale**: In FB5, `auth.py` imported `limiter` from `main.py`, creating a fatal circular import (`main.py` → `routers/auth.py` → `main.py`). The fix required extracting `limiter.py`. If the integration checklist included "verify no router imports from main.py", this would be caught before the first audit.
**Source**: Fitness build FB5, foundation fix wave 2
**Experiment**:
  1. Review last 5 fitness builds for circular imports involving main.py
  2. Count instances per build
  3. Add "no router imports from main.py" to integration checklist
  4. Run next 5 builds and compare counts
**Expected**: Control group: 1-2 circular imports. Treatment group: 0 circular imports.
**Result**: [to be filled]
**Tested by**: [fitness build or gym experiment]
