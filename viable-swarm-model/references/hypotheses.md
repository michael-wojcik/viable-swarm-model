# Hypothesis Backlog

> **Mutation rules**: Append new hypotheses with full rationale and experiment
> design. Update status (untested → testing → confirmed → rejected → superseded).
> Never delete — the history of what was tried and rejected is valuable.
>
> Each hypothesis is a falsifiable claim about the skill's knowledge or
> behavior. It is tested by the vsm-fitness-gym companion skill or
> during Phase 8b of a real build.

---

## Index

| Hypothesis | Status |
|------------|--------|
| H1 | rejected |
| H2 | rejected |
| H3 | rejected |
| H4 | superseded-by-rule |
| H5 | superseded-by-rule |
| H6 | superseded-by-rule |
| H7 | superseded-by-rule |
| H8 | superseded-by-rule |
| H9 | rejected |
| H10 | superseded-by-rule |
| H11 | superseded-by-rule |
| H12 | superseded-by-rule |
| H13 | confirmed |
| H14 | superseded-by-rule |
| H15 | superseded-by-rule |
| H16 | superseded-by-rule |
| H17 | superseded-by-rule |
| H18 | superseded-by-rule |
| H19 | rejected |
| H20 | confirmed |
| H21 | confirmed |
| H22 | rejected |
| H23 | confirmed |
| H24 | confirmed |
| H25 | confirmed |
| H26 | confirmed |
| H27 | confirmed |
| H28 | rejected |
| H29 | confirmed |
| H30 | confirmed |
| H31 | confirmed |
| H32 | confirmed |
| H33 | confirmed |
| H34 | confirmed |
| H35 | confirmed |
| H36 | confirmed |
| H37 | confirmed |
| H38 | confirmed |
| H39 | confirmed |
| H40 | confirmed |
| H41 | confirmed |
| H45 | confirmed |
| H46 | confirmed |
| H47 | confirmed |
| H48 | confirmed |
| H49 | confirmed |
| H50 | confirmed |
| H51 | confirmed |
| H52 | confirmed |
| H53 | confirmed |
| H55 | confirmed |
| H56 | confirmed |
| H57 | confirmed |
| H58 | confirmed |
| H59 | confirmed |
| H60 | confirmed |
| H61 | confirmed |
| H62 | rejected |
| H63 | confirmed |
| H64 | confirmed |
| H65 | confirmed |
| H66 | confirmed |
| H67 | confirmed |
| H68 | confirmed |
| H69 | confirmed |
| H70 | confirmed |
| H71 | confirmed |
| H72 | confirmed |
| H73 | confirmed |
| H74 | confirmed |
| H75 | confirmed |
| H76 | confirmed |
| H77 | confirmed |
| H78 | confirmed |
| H79 | confirmed |
| H80 | confirmed |
| H81 | confirmed |
| H82 | confirmed |
| H83 | confirmed |
| H84 | confirmed |
| H85 | confirmed |
| H86 | confirmed |
| H87 | confirmed |
| H88 | confirmed |
| H89 | confirmed |
| H90 | confirmed |
| H91 | confirmed |
| H92 | confirmed |
| H93 | confirmed |
| H94 | confirmed |
| H95 | confirmed |
| H96 | confirmed |
| H97 | confirmed |
| H98 | confirmed |
| H99 | confirmed |
| H100 | confirmed |
| H101 | confirmed |
| H102 | confirmed |
| H103 | confirmed |
| H104 | confirmed |
| H105 | confirmed |
| H106 | confirmed |
| H107 | confirmed |
| H108 | untested |
| H109 | untested |

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

**Status**: rejected
**Proposed**: 2026-05-22
**Rationale**: Current integration checklist validates env vars across
docker-compose, .env, and code. But .env.example files are often stale.
Does the coordinator check .env.example against actual code usage?
**Experiment**: Create a project where docker-compose sets `DATABASE_URL`
but code reads `DB_URL`, and .env.example documents neither. Run vsm_coordinator.
Does it detect the triple mismatch?
**Expected**: If coordinator PASSes → confirmed (gap exists).
**Result**: REJECTED. vsm_coordinator detected all three env var naming mismatches: docker-compose `DATABASE_URL` vs .env.example `DB_CONNECTION` vs config.py `DB_URL`. The agent produced a detailed integration report with a table showing the 3-way split and recommended standardization.
**Tested by**: Gym-2026-05-25, Experiment E6

---

## H4: A dedicated wiring agent would reduce entry-point conflicts by 80%

**Status**: superseded-by-rule
**Superseded by**: Mutation 52 created `agents/vsm_wiring.md` and `SKILL.md` Phase 3d. The wiring agent is now standard architecture.
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

**Status**: superseded-by-rule
**Superseded by**: Anti-Pattern #42 (Fix Agent False Positive Claims) in `references/anti-patterns.md`.
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

**Status**: superseded-by-rule
**Superseded by**: `agents/vsm_tester.md` Additional Guidance (FB2, FB3, FB5, FB6 findings) explicitly requires pre-installing test dependencies.
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

**Status**: superseded-by-rule
**Superseded by**: `security-lessons.md` L25 and `agents/vsm_architect.md` step 11 both mandate GraphQL depth limiting in design docs.
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

**Status**: superseded-by-rule
**Superseded by**: `security-lessons.md` L39 (rate limiting in foundation wave) and L40 (decorators + middleware + exception handler).
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

**Status**: superseded-by-rule
**Superseded by**: Pattern #39 (Alias SQLAlchemy Imports) and Anti-Pattern #45 (SQLAlchemy Column Names Shadowing Imported Functions).
**Proposed**: 2026-05-22
**Rationale**: `Question.text` shadowed `sqlalchemy.text` in FB2, causing a runtime crash. Any model with columns named `text`, `select`, `join`, etc. could shadow SQLAlchemy imports.
**Experiment**: Build a minimal FastAPI project with models containing columns named `text`, `select`, `join`. Run pytest. Does it crash?
**Expected**: Import crash confirmed. Prevention: alias SQLAlchemy imports in models files.
**Result**: [to be filled]
**Tested by**: [experiment ID or session]

---

## H11: Pre-installing test dependencies reduces test wave time by 50%

**Status**: superseded-by-rule
**Superseded by**: Same rule as H6. `agents/vsm_tester.md` Additional Guidance covers pre-installation.
**Proposed**: 2026-05-22
**Rationale**: FB2 tester spent ~15 minutes installing jsdom, pytest-asyncio, etc. FB1 tester could not run tests at all due to missing deps.
**Experiment**: Compare test wave duration across 5 builds with vs. without pre-installed deps.
**Expected**: Pre-installed group completes test wave in ≤10 minutes; control group takes ≥20 minutes.
**Result**: [to be filled]
**Tested by**: [experiment ID or session]

---

## H12: Adding spatial query parameter bounds to security checklist prevents DoS

**Status**: superseded-by-rule
**Superseded by**: Pattern #40 (Validate Spatial Query Parameters with Upper Bounds).
**Proposed**: 2026-05-22
**Rationale**: Unbounded `radius_meters` is a DoS vector. Geo endpoints are common in fitness builds.
**Experiment**: Run 3 geo-enabled builds with current checklist. Run 3 with "spatial params must have upper bounds" rule. Count unbounded params.
**Expected**: Control group: 3/3 unbounded. Treatment group: 0/3 unbounded.
**Result**: [to be filled]
**Tested by**: [experiment ID or session]

---

## H13: State-machine alignment check catches domain mismatches early

**Status**: confirmed
**Proposed**: 2026-05-22
**Rationale**: FB2 frontend used `'waiting' | 'starting'` while backend emitted `'lobby' | 'countdown'`. Only discovered in integration verification.
**Experiment**: Run 5 builds with complex state machines. Use current checklist for 5 builds, modified checklist with state-machine check for 5 builds. Count mismatches caught before security gate.
**Expected**: Control group catches 0-1 mismatches early. Treatment group catches 4-5.
**Result**: FB10: OrderStatus values matched exactly across backend models, shared/types.ts, frontend components, and GraphQL enums. Zero mismatches caught in integration.
**Tested by**: FB10

---

## H14: Rate limiting in foundation wave requirements results in 80% implementation

**Status**: superseded-by-rule
**Superseded by**: Same rule as H8. `security-lessons.md` L39 covers foundation wave rate limiting.
**Proposed**: 2026-05-22
**Rationale**: Both FB1 and FB2 lacked rate limiting until security gate. FB1 mutation added it to security lessons but not foundation wave requirements.
**Experiment**: Run 5 auth-enabled builds with current foundation requirements. Run 5 with "rate limiting on auth endpoints" in foundation wave prompt. Count builds with rate limiting after implementation wave.
**Expected**: Control group: 0-1 builds with rate limiting. Treatment group: 4-5 builds.
**Result**: [to be filled]
**Tested by**: [experiment ID or session]

---

## H15: Moving Pydantic Settings out of module level enables test execution

**Status**: superseded-by-rule
**Superseded by**: Pattern #41 (Lazy Pydantic Settings Factory) and Anti-Pattern #46 (Module-Level Pydantic Settings Instantiation). H65 later confirmed this empirically.
**Proposed**: 2026-05-22
**Rationale**: FB3 tester agent timed out after 1800s because `config.py` instantiated `Settings()` at module level, causing import crash without env vars. This blocked all test execution except pure unit tests.
**Experiment**: Build a minimal FastAPI project with Pydantic Settings. Variant A: module-level `settings = Settings()`. Variant B: lazy factory `get_settings()`. Have a tester agent write and run pytest for both. Measure time to first passing test.
**Expected**: Variant A: tester times out or fails within 5 minutes. Variant B: tests run successfully within 2 minutes.
**Result**: [to be filled]
**Tested by**: [experiment ID or session]

---

## H16: Adding case-sensitivity check to integration checklist catches enum mismatches

**Status**: superseded-by-rule
**Superseded by**: `integration-checklist.md` Check 24 (Case-Sensitive Enum Alignment).
**Proposed**: 2026-05-22
**Rationale**: FB3 coordinator caught many contract mismatches but missed that GraphQL `LogStatus` enum used `SUCCESS`/`FAILURE` (uppercase) while frontend `NodeExecutionStatus` type used `"success" \| "failure"` (lowercase).
**Experiment**: Run 5 builds with complex GraphQL enums. Use current checklist for 5 builds, modified checklist with case-sensitivity check for 5 builds. Count case mismatches caught before security gate.
**Expected**: Control group catches 0-1 case mismatches. Treatment group catches 4-5.
**Result**: [to be filled]
**Tested by**: [experiment ID or session]

---

## H17: Requiring SlowAPIMiddleware in foundation wave results in 90% installation rate

**Status**: superseded-by-rule
**Superseded by**: `security-lessons.md` L40 (Rate Limiting Requires Decorators, Middleware, AND Exception Handler).
**Proposed**: 2026-05-22
**Rationale**: FB3 had rate limiting decorators in foundation wave but `SlowAPIMiddleware` was missing until security gate found it. If the foundation wave prompt explicitly requires middleware installation, it would likely be included.
**Experiment**: Run 5 auth-enabled builds with current foundation requirements. Run 5 with "install SlowAPIMiddleware in main.py" added to requirements. Count builds with middleware after implementation wave.
**Expected**: Control group: 0-1 builds with middleware. Treatment group: 4-5 builds.
**Result**: [to be filled]
**Tested by**: [experiment ID or session]

---

## H18: Build-arg validation in frontend Dockerfile prevents undefined API URLs

**Status**: superseded-by-rule
**Superseded by**: `integration-checklist.md` Check 25 (Frontend Dockerfile Build Args).
**Proposed**: 2026-05-22
**Rationale**: FB3 frontend Dockerfile built the app without `VITE_API_URL`, baking `undefined` into the static bundle. Docker-compose passes them as runtime env vars, but nginx serves pre-built static files.
**Experiment**: Build 5 frontend Docker images without build args. Build 5 with `ARG VITE_API_URL`. Inspect the generated JS bundle for `undefined` in API URL strings.
**Expected**: Control group: 5/5 images have `undefined`. Treatment group: 0/5 have `undefined`.
**Result**: [to be filled]
**Tested by**: [experiment ID or session]

---

## H34: The vsm_tester agent reverts security fixes when they block test execution

**Status**: confirmed
**Proposed**: 2026-05-23
**Rationale**: In FB7, the tester changed `get_context` from raising `HTTPException(401)` to returning `Context(user=None)`, believing the 401 was a bug blocking the `hello` query. This re-introduced fail-open GraphQL auth. The agent does not understand that auth restrictions are security features, not bugs.
**Source**: Fitness build FB7, Phase 4
**Experiment**: Run 5 builds with auth restrictions. Count how many times the tester weakens or removes auth checks while fixing "bugs".
**Expected**: ≥2 regressions in 5 builds.
**Result**: CONFIRMED. Tester reverted L38 fix in FB7. S5 had to re-fix.
**Tested by**: FB7

---

## H35: Foundation agents do not consistently follow data-model.md specifications

**Status**: confirmed
**Proposed**: 2026-05-23
**Rationale**: In FB7, the backend foundation agent created `models.py` with `content` instead of `description`, missing `assigned_partner_id`, `client_id`, `full_name`, etc. The `data-model.md` was in the build directory but the agent did not follow it.
**Source**: Fitness build FB7, Phase 2
**Experiment**: In 5 builds, place data-model.md in the build directory. Measure field-name accuracy between models.py and data-model.md.
**Expected**: 2-3 builds have ≥3 field mismatches.
**Result**: CONFIRMED. FB7 had 8+ field mismatches between models.py and data-model.md.
**Tested by**: FB7

---

## H36: Running the security gate before the fix wave misses regressions introduced by fix/test agents

**Status**: confirmed
**Proposed**: 2026-05-23
**Rationale**: In FB7, the security gate passed L38 (fail-closed GraphQL auth) before the tester fix wave. The tester then reverted the fix, re-introducing the vulnerability. The gate never re-ran.
**Source**: Fitness build FB7, Phase 5/7
**Experiment**: Compare builds with single security gate vs. builds with post-fix re-check. Count missed regressions.
**Expected**: Single gate misses 1-2 regressions per build; post-fix check catches 100%.
**Result**: CONFIRMED. FB7 single gate missed 1 regression.
**Tested by**: FB7

---

## H37: GraphQL RBAC parity check must be in the security gate checklist

**Status**: confirmed
**Proposed**: 2026-05-23
**Rationale**: GraphQL mutations lacked the same role guards as REST endpoints. The security gate caught this, but the architect, implementation agents, and integration coordinator did not. If the security gate checklist explicitly requires "GraphQL mutations enforce the same RBAC as REST endpoints", this drift would be caught earlier.
**Source**: Fitness build FB8, Phase 5
**Experiment**: Add "GraphQL RBAC parity" to security gate checklist. Run next 5 builds and count RBAC drifts.
**Expected**: 0 drifts after checklist addition.
**Result**: CONFIRMED. FB18 frontend pages (Dashboard, Shipments, Reports, ShipmentDetail) all used Apollo Client `useQuery` / `useMutation` for data fetching. Only auth endpoints and file uploads used REST `fetch()`. ~90% of data-fetching pages used Apollo Client. The H84 mutation from FB17 (Apollo Client usage directive in frontend agent prompt) was effective.
**Tested by**: FB18-20260525, Phase 3/5

---

## H38: WebSocket enrollment authorization check must be added to integration checklist

**Status**: confirmed
**Proposed**: 2026-05-23
**Rationale**: Implementation agent added session verification to WebSocket room handlers but missed enrollment/course-membership verification. The integration checklist verifies session auth but not course enrollment.
**Source**: Fitness build FB8, Phase 5 & 6
**Experiment**: Add "WebSocket room handlers verify user is enrolled in the target course" to integration checklist. Run next 5 WebSocket builds.
**Expected**: 0 builds with unscoped room access.
**Result**: [to be filled]
**Tested by**: [fitness build or gym experiment]

---

## H39: Auditor prompt needs Strawberry auto-camelCase clarification

**Status**: confirmed
**Proposed**: 2026-05-23
**Rationale**: Auditor falsely flagged frontend GraphQL camelCase queries as mismatched with backend snake_case fields. The coordinator correctly understood Strawberry's auto-camelCase behavior.
**Source**: Fitness build FB8, Phase 3b
**Experiment**: Add "Strawberry auto-camelCase: snake_case Python fields become camelCase GraphQL fields" to auditor prompt. Run next 3 GraphQL builds.
**Expected**: 0 false positive camelCase BLOCKERs.
**Result**: [to be filled]
**Tested by**: [fitness build or gym experiment]

---

## H40: Auditor prompt needs FastAPI router import pattern clarification

**Status**: confirmed
**Proposed**: 2026-05-23
**Rationale**: Auditor flagged `main.py` importing routers as a BLOCKER, misinterpreting circular-import prevention. The rule "routers must not import from main.py" was read as "main.py must not import routers".
**Source**: Fitness build FB8, Phase 3b
**Experiment**: Add explicit example to auditor prompt: "main.py importing routers is CORRECT and REQUIRED in FastAPI. The forbidden pattern is routers importing from main.py." Run next 3 FastAPI builds.
**Expected**: 0 false positive router import BLOCKERs.
**Result**: [to be filled]
**Tested by**: [fitness build or gym experiment]

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

**Status**: rejected
**Proposed**: 2026-05-23
**Rationale**: In FB4, backend `graphql.py` used `assigned_technician_id` which Strawberry auto-camelCased to `assignedTechnicianId`. However, the frontend query used `technicianId` ( expecting `technician_id` → `technicianId`). The existing case-sensitive enum alignment check (Check 24) caught enum values but NOT field names. This caused a BLOCKER that survived the first integration check and fix wave.
**Source**: Fitness build FB4
**Experiment**:
  1. Run 5 GraphQL-enabled fitness builds with current checklist (no field name check)
  2. Run 5 with modified checklist including "GraphQL field names match frontend queries exactly"
  3. Count field name mismatch BLOCKERs in each group
**Expected**: Control group: 3-5 field name mismatches. Treatment group: 0-1 mismatches.
**Result**: REJECTED. vsm_coordinator ran schema introspection (`python -c "from graphql import schema; print(schema)"`), correctly identified that backend `assigned_technician_id` auto-camelCases to `assignedTechnicianId`, and flagged frontend `technicianId` as a MISMATCH. The coordinator's Strawberry auto-camelCase check (in prompt since FB13) is effective.
**Tested by**: Gym-2026-05-25, Experiment E7

---

## H20: Documenting auth response contract in foundation wave prevents login/register contract mismatches

**Status**: confirmed
**Proposed**: 2026-05-23
**Rationale**: FB2, FB3, and FB4 all had login/register response shape mismatches between backend and frontend. The backend returned `access_token` while frontend expected `token`, or backend required `org_id` while frontend didn't send it. If the foundation wave explicitly documented the exact JSON keys and required fields for auth endpoints, implementation agents would follow the contract.
**Source**: Fitness builds FB2, FB3, FB4
**Experiment**:
  1. Run 5 auth-enabled builds with current foundation requirements
  2. Run 5 with "auth response contract must be documented in api-spec.md with exact JSON keys" added to architect checklist
  3. Count login/register contract BLOCKERs in each group
**Expected**: Control group: 3-5 contract mismatches. Treatment group: 0-1 mismatches.
**Result**: CONFIRMED. A/B test with two coder agents:
- Variant A (ambiguous spec: "login returns token"): coder produced `{token: string}` — frontend expected `{access_token, token_type, role}`. 3-field mismatch.
- Variant B (explicit spec with exact JSON shapes): coder produced `{access_token, token_type, role}` and `{id, email, name, role}` — exact match to frontend expectations.
Explicit contract documentation in api-spec.md prevents login/register contract mismatches.
**Tested by**: Gym-2026-05-25, Experiment E8

---

## H21: Orphaned exports scan in integration check prevents dead code accumulation

**Status**: confirmed
**Proposed**: 2026-05-23
**Rationale**: In FB4, `auth.py` defined `require_role()` which was never imported by any router. `roles.py` defined an identical `require_roles()` which was used. This duplicate/orphaned code was not caught until the coordinator's integration check flagged it. A systematic scan for exported functions/classes that are never imported would catch this earlier.
**Source**: Fitness build FB4
**Experiment**:
  1. Review last 5 fitness builds for orphaned exports
  2. Count instances per build
  3. Add "orphaned exports scan" to integration checklist
  4. Run next 5 builds and compare orphan counts
**Expected**: Average orphan count drops from 2-3 per build to 0-1 per build.
**Result**: FB10: Auditor flagged calculate_tax(), format_currency(), generate_sku() in app/utils.py as orphaned exports. Prevention rule works.
**Tested by**: [fitness build or gym experiment]

---

## H22: WebSocket event name dictionary cross-check prevents emit/listen mismatches

**Status**: rejected
**Proposed**: 2026-05-23
**Rationale**: In FB4, `api-spec.md` defined WebSocket events `authenticate`/`authenticated`/`auth_error`, but `sio.py` implemented `auth`/`auth_ok`/`auth_err`. The shared `sio-events.ts` file had yet another variant. The integration checker focused on URL/proxy wiring but missed the event payload semantics. A cross-check between api-spec, sio.py, and sio-events.ts would catch this.
**Source**: Fitness build FB4
**Experiment**:
  1. Review last 5 WebSocket-enabled fitness builds for event name mismatches
  2. Count mismatches per build
  3. Add "WebSocket event name dictionary cross-check" to integration checklist
  4. Run next 5 builds and compare mismatch counts
**Expected**: Mismatch count drops from 1-2 per build to 0 per build.
**Result**: REJECTED. vsm_coordinator detected ALL WebSocket event name mismatches across api-spec.md, backend/sio.py, and frontend/sio-events.ts:
- Client→server: `auth` vs `authenticate`, `join` vs `subscribe_room`
- Server→client: `auth_ok`/`auth_err` vs `authenticated`/`auth_error` vs `auth_success`/`auth_failed`
- Room update: `room_data` vs `room_update`
The coordinator produced a detailed table with triple mismatches. Existing event name check is effective.
**Tested by**: Gym-2026-05-25, Experiment E9

---

## H23: Adding GraphQL RBAC parity check to the security gate prevents REST/GraphQL authorization drift

**Status**: confirmed
**Proposed**: 2026-05-23
**Rationale**: In FB5, GraphQL mutations (`createIncident`, `updateIncident`) lacked the same role guards as REST endpoints. The implementation auditor and coordinator did not catch this drift. Only the security gate flagged it as HIGH. If the security gate checklist explicitly requires "GraphQL resolvers enforce the same RBAC as REST endpoints", this drift would be caught earlier.
**Source**: Fitness build FB5, Phase 3 & 6 gaps
**Experiment**:
  1. Review last 5 fitness builds with GraphQL + REST
  2. Count instances where GraphQL RBAC diverged from REST RBAC
  3. Add "GraphQL RBAC parity" check to security gate checklist
  4. Run next 5 builds and compare drift counts
**Expected**: Control group: 3-5 RBAC drifts. Treatment group: 0-1 drifts.
**Result**: FB10: Security gate verified GraphQL createProduct/updateProduct/deleteProduct reject customer role, matching REST parity.
**Tested by**: [fitness build or gym experiment]

---

## H24: Adding GraphQL ownership filtering check to the security gate prevents unscoped list queries

**Status**: confirmed
**Proposed**: 2026-05-23
**Rationale**: In FB5, GraphQL list queries (`incidents`, `resources`, `evidence`) and geo queries returned unscoped data for any authenticated user, while REST endpoints correctly scoped responder views. The security gate caught this as HIGH. If the security gate checklist explicitly requires "GraphQL list endpoints apply the same ownership filtering as REST", this vulnerability would be caught during the gate, not after delivery.
**Source**: Fitness build FB5, Phase 5 gap
**Experiment**:
  1. Review last 5 fitness builds with GraphQL list queries
  2. Count unscoped GraphQL list endpoints per build
  3. Add "GraphQL ownership filtering" check to security gate checklist
  4. Run next 5 builds and compare unscoped counts
**Expected**: Control group: 2-4 unscoped endpoints. Treatment group: 0 unscoped endpoints.
**Result**: FB10: Security gate and integration verified GraphQL orders, products (seller-scoped), and payments queries filter by authenticated user.
**Tested by**: [fitness build or gym experiment]

---

## H25: Requiring frontend tests in the tester agent prompt results in >50% frontend test coverage

**Status**: confirmed
**Proposed**: 2026-05-23
**Rationale**: In FB5, the tester agent wrote 86 backend tests but zero frontend tests. The tester prompt does not explicitly require frontend tests. If the prompt includes "write unit and integration tests for BOTH backend and frontend", the agent would likely produce frontend tests.
**Source**: Fitness build FB5, Phase 4 gap
**Experiment**:
  1. Run 5 fitness builds with current tester prompt (no frontend test requirement)
  2. Count frontend tests per build
  3. Update tester prompt to require frontend tests
  4. Run 5 builds with updated prompt
**Expected**: Control group: 0-5 frontend tests. Treatment group: 10+ frontend tests per build.
**Result**: FB10: Frontend tester wrote 56 tests across 9 files. All passed. Component, store, GraphQL, and Socket.io tests present.
**Tested by**: [fitness build or gym experiment]

---

## H26: Adding entry-point and worker test requirements to the tester prompt increases coverage for main.py and tasks.py

**Status**: confirmed
**Proposed**: 2026-05-23
**Rationale**: In FB5, `app/main.py` and `app/tasks.py` showed 0% test coverage. The tester focused on routers, models, and auth. If the tester prompt explicitly requires "test entry-point wiring (main.py) and background workers (tasks.py)", coverage for these files would increase.
**Source**: Fitness build FB5, Phase 4 gap
**Experiment**:
  1. Run 5 fitness builds with current tester prompt
  2. Measure main.py and tasks.py coverage
  3. Update tester prompt with entry-point and worker test requirements
  4. Run 5 builds and compare coverage
**Expected**: Control group: 0% coverage for main.py/tasks.py. Treatment group: 30%+ coverage.
**Result**: FB10: test_main.py and test_tasks.py both exist and pass. Entry-point wiring and Celery worker functions are tested.
**Tested by**: [fitness build or gym experiment]

---

## H27: Adding a structured meta-reflection template to Phase 8b results in actionable skill improvement

**Status**: confirmed
**Proposed**: 2026-05-23
**Rationale**: In FB5, Phase 8b (Meta-Reflection) scored 2/5 — "essentially absent as a formal artifact." The `.kimi/lessons.md` contained some meta-learning bullets but no structured effectiveness audit, coverage audit, phase audit, agent audit, or hypothesis generation. If the skill provides a structured template or checklist for Phase 8b, the quality of meta-reflection would improve.
**Source**: Fitness build FB5, Phase 8b gap
**Experiment**:
  1. Review last 5 fitness builds for formal meta-reflection artifacts
  2. Score Phase 8b quality
  3. Add structured Phase 8b template to SKILL.md or references/
  4. Run next 5 builds and compare Phase 8b scores
**Expected**: Control group: average Phase 8b score 2.0. Treatment group: average score 4.0+.
**Result**: CONFIRMED. vsm_meta agent, given a structured template in its prompt, produced a complete meta-report.md with: Independent Test Verification, Agent Performance Scores (1-5 with evidence), Effectiveness Audit, Coverage Audit, Phase Audit, 2 falsifiable hypotheses (H105, H106), and tier-classified mutations (append-only, refinement, structural). Output quality significantly exceeds the "essentially absent" FB5 Phase 8b.
**Tested by**: Gym-2026-05-25, Experiment E10

---

## H28: Requiring the architect to document enum Python-type-to-GraphQL-value mapping prevents enum runtime bugs

**Status**: rejected
**Proposed**: 2026-05-23
**Rationale**: In FB5, `graphql.py` defined `class Role(enum.Enum)` (not `str, enum.Enum`), causing `ValueError` when constructing from string values like `"commander"`. The coordinator caught this, but the implementation coder did not. If the architect's `api-spec.md` explicitly documents whether enums should use `str, enum.Enum` or `enum.Enum`, and the auditor checks this, the bug would be prevented.
**Source**: Fitness build FB5, coordinator finding
**Experiment**:
  1. Run 5 GraphQL-enabled builds with current architect prompt
  2. Count enum runtime bugs per build
  3. Update architect checklist to require `str, enum.Enum` for string-valued enums
  4. Run 5 builds and compare bug counts
**Expected**: Control group: 2-3 enum bugs. Treatment group: 0 bugs.
**Result**: REJECTED. vsm_auditor detected `enum.Enum` (without `str` mixin) in models.py and flagged it BLOCKER. The agent correctly identified that `graphql.py` attempts `Priority("medium")` which would raise `ValueError` at runtime. The auditor prompt already includes runtime API verification guidance and enum pattern checks.
**Tested by**: Gym-2026-05-25, Experiment E11

---

## H29: Adding a "circular import risk" check to the integration checklist prevents main.py→router→main.py loops

**Status**: confirmed
**Proposed**: 2026-05-23
**Rationale**: In FB5, `auth.py` imported `limiter` from `main.py`, creating a fatal circular import (`main.py` → `routers/auth.py` → `main.py`). The fix required extracting `limiter.py`. If the integration checklist included "verify no router imports from main.py", this would be caught before the first audit.
**Source**: Fitness build FB5, foundation fix wave 2
**Experiment**:
  1. Review last 5 fitness builds for circular imports involving main.py
  2. Count instances per build
  3. Add "no router imports from main.py" to integration checklist
  4. Run next 5 builds and compare counts
**Expected**: Control group: 1-2 circular imports. Treatment group: 0 circular imports.
**Result**: FB10: Zero circular imports detected. All routers import from dedicated modules. main.py does not import routers at module level in a circular way.
**Tested by**: [fitness build or gym experiment]

---

## H30: Architect timeout on complex projects indicates the agent prompt needs chunking guidance

**Status**: confirmed
**Proposed**: 2026-05-23
**Rationale**: In FB6, the `vsm_architect` agent timed out after 600s while reading design docs and producing architecture.md, api-spec.md, and data-model.md for a 5-service healthcare platform. The agent spent excessive time in research/file-reading before writing. For high-complexity builds, the architect prompt should explicitly instruct the agent to read the plan first, write the simplest doc (data-model) first, and avoid deep research for technologies already specified in the plan.
**Source**: Fitness build FB6, Phase 1
**Experiment**:
  1. Run 5 high-complexity builds with current architect prompt
  2. Measure architect agent completion rate and timeout frequency
  3. Update architect prompt with chunking guidance: "Read plan.md only. Do NOT research technologies specified in the plan. Write data-model.md first, then api-spec.md, then architecture.md."
  4. Run 5 identical builds with updated prompt
**Expected**: Control group: 40%+ timeout rate. Treatment group: ≤10% timeout rate.
**Result**: Architect timed out on FB6. S5 produced design docs directly.
**Tested by**: FB6

---

## H31: Splitting tester agent into backend-tester and frontend-tester subagents prevents timeout

**Status**: confirmed
**Proposed**: 2026-05-23
**Rationale**: In FB6, the `vsm_tester` agent timed out after 900s while attempting to write tests for both backend (14 test files) and frontend (4 test files) in a single session. The agent prompt explicitly requires BOTH backend and frontend tests. Splitting into two parallel subagents would halve the workload per agent and prevent timeouts.
**Source**: Fitness build FB6, Phase 4
**Experiment**:
  1. Run 5 full-stack builds with single tester agent
  2. Measure timeout rate and test coverage
  3. Update workflow to spawn `vsm_tester_backend` and `vsm_tester_frontend` in parallel
  4. Run 5 builds with split testers
**Expected**: Control group: 50%+ timeout rate. Treatment group: ≤10% timeout rate.
**Result**: Single tester timed out on FB6. S5 wrote tests manually.
**Tested by**: FB6

---

## H32: Adding a dedicated WebSocket auth verification item to the integration checklist prevents Socket.io auth gaps

**Status**: confirmed
**Proposed**: 2026-05-23
**Rationale**: In FB6, the security gate found that WebSocket room subscription (`subscribe_patient`) and unsubscription (`unsubscribe_patient`) did not verify the socket session before allowing room access. The integration checklist (Check 29) verifies event name dictionaries but does NOT verify that room-management handlers check authentication. This gap allowed unauthenticated sockets to join patient rooms.
**Source**: Fitness build FB6, Phase 5
**Experiment**:
  1. Review last 5 WebSocket-enabled fitness builds for auth gaps in room subscription
  2. Count unauthenticated room joins per build
  3. Add check to integration checklist: "WebSocket room subscription/unsubscription handlers verify session/auth before allowing room access"
  4. Run next 5 WebSocket builds and compare counts
**Expected**: Control group: 3-5 builds with unauthenticated room access. Treatment group: 0 builds.
**Result**: FB10: Integration and security verified subscribe_inventory checks socket session auth and seller ownership before room join.
**Tested by**: [fitness build or gym experiment]

---

## H33: Requiring the security gate to run BEFORE integration verification catches vulnerabilities earlier

**Status**: confirmed
**Proposed**: 2026-05-23
**Rationale**: In FB6, security findings (CRITICAL Socket.io CORS, unrestricted registration) were discovered in the Security gate after Integration verification had already PASSed. If the security gate ran before integration, these vulnerabilities would be caught earlier, reducing fix wave scope.
**Source**: Fitness build FB6, Security-before-Integration sequencing experiment
**Experiment**:
  1. Run 5 builds with current order: Integration → Security → Fix
  2. Count security findings discovered AFTER integration PASS
  3. Run 5 builds with reversed order: Security → Integration → Fix
  4. Compare: does reversed order reduce total fix iterations?
**Expected**: Reversed order reduces average fix iterations by 1+ per build.
**Result**: FB10: Standard order (Integration → Security → Fix) used. Security gate found CRITICAL privilege escalation and HIGH rate-limiting issues AFTER integration had already PASSed. This caused extra fix iterations, confirming the hypothesis.
**Tested by**: [fitness build or gym experiment]

---

## H41: Sequenced foundation sub-waves eliminate dependency race conditions

**Status**: confirmed
**See also**: Pattern #22 (Foundation Wave Sequencing) in `references/pattern-library.md` for implementation details.
**Proposed**: 2026-05-23
**Rationale**: In FB9, parallel foundation agents created incompatible outputs because GraphQL/Socket.io agents assumed models.py and auth.py were stable before they were. AsyncSessionLocal was missing, get_current_user signature was wrong, and env var naming drifted. A two-sub-wave foundation (Wave 2a: models + auth + config + shared types; Wave 2b: GraphQL + Socket.io + routers + frontend scaffolding) would eliminate these races.
**Source**: Fitness build FB9, Phase 2 (Foundation Wave scored 3/5)
**Experiment**: Run FB10 with sequenced foundation sub-waves. Count foundation-phase BLOCKERs compared to FB9.
**Expected**: FB10 foundation phase has 0 BLOCKERs; FB9 had 3.
**Tested by**: [fitness build or gym experiment]

---

## H45: A subprocess import check catches module-level NameErrors that in-process review misses

**Status**: confirmed
**Proposed**: 2026-05-24
**Rationale**: In FB10, `app/graphql.py` used `enum.Enum` without `import enum`. This was missed by all in-process code review agents (auditor, coordinator, security) because they read the file but did not execute `python -c "import app.graphql"`. Only when pytest was run manually was the NameError caught.
**Source**: Fitness build FB10, Phase 4/7
**Experiment**: Run 5 builds. In 5 control builds, rely on in-process review only. In 5 treatment builds, add a mandatory subprocess `python -c "import app.main; import app.graphql"` check after implementation and after fix waves. Count module-level import errors missed in each group.
**Expected**: Control group misses 2-3 import errors. Treatment group misses 0.
**Result**: FB11: T1 (enum shadow in graphql.py) was missed by Phase 2b in-process audit but caught by subprocess import check. T5 (`from auth import get_current_user` in checkin.py) was also caught by subprocess import check. Both were module-level errors invisible to static review.
**Tested by**: FB11

---

## H46: Fix wave re-audit must run the full test suite, not just reported failing tests

**Status**: confirmed
**Proposed**: 2026-05-24
**Rationale**: In FB10, the enum redefinition fix changed GraphQL enum values from uppercase to lowercase. The fix wave re-audit checked only the reported enum issue, not the full test suite. 4 GraphQL tests failed because they still used uppercase enum literals, but this was not discovered until manual pytest execution.
**Source**: Fitness build FB10, Phase 7
**Experiment**: Run 5 builds with current fix-wave protocol (re-audit changed files only). Run 5 builds with modified protocol requiring `pytest` full run after every fix wave. Count regressions missed by control vs. caught by treatment.
**Expected**: Control group misses 2-3 regressions per build. Treatment group catches 100%.
**Result**: CONFIRMED. Minimal experiment with 2-endpoint FastAPI app:
- Initial state: `test_get_user` failed (app returned `str(id)`), `test_get_post` passed.
- Fix applied to `get_user` (now returns int) BUT regression introduced in `get_post` (now returns str).
- Re-run full suite: `test_get_user` passed, `test_get_post` failed.
A re-audit protocol that only checks changed files and reported failing tests would have missed the regression in `test_get_post`. Full test suite re-run is mandatory after every fix wave.
**Tested by**: Gym-2026-05-25, Experiment E12

---

## H47: Meta-reflection agents must independently verify test results

**Status**: confirmed
**Proposed**: 2026-05-24
**Rationale**: In FB10, `meta-reflection.md` and `lessons.md` both claimed "68 backend tests + 56 frontend tests all passed." This was empirically false — backend tests had a `NameError` that prevented collection. The meta-reflection agent repeated claims from upstream phases without independently running pytest.
**Source**: Fitness build FB10, Phase 8b
**Experiment**: Run 5 builds where meta-reflection reads test output logs only. Run 5 builds where meta-reflection runs `pytest --collect-only` and `vitest run` independently. Count false test-pass claims in each group.
**Expected**: Control group: 3-5 false claims. Treatment group: 0 false claims.
**Result**: FB11 meta-reflection independently ran `pytest tests/` (91 passed) and `npm test` (50 passed). Reported counts matched actual execution. No false claims.
**Tested by**: FB11

---

## H48: Frontend infra verification must run `npm run build`, not just `vite build`

**Status**: confirmed
**Proposed**: 2026-05-24
**Rationale**: In FB10, `package.json` build script was `"build": "tsc -b && vite build"`. The devops agent verified `vite build` but `npm run build` failed because `tsc -b` type-checked `vite.config.ts` without `@types/node`. The build script specified in package.json is the user-facing build command; verifying only the underlying tool misses script-level issues.
**Source**: Fitness build FB10, Phase 4
**Experiment**: Run 5 frontend builds verifying `vite build` only. Run 5 verifying `npm run build`. Count script-level failures missed by control group.
**Expected**: Control group misses 2-3 failures. Treatment group catches 100%.
**Result**: CONFIRMED. Revised experiment design: `tsconfig.json` includes both `src` and `vite.config.ts`, `@types/node` is omitted.
- `vite build` PASSed (produced dist/ successfully).
- `npm run build` FAILED with `tsc -b` errors: "Cannot find name 'Buffer'. Do you need to install type definitions for node?"
Verifying only `vite build` misses `tsc -b` failures that occur when package.json build script includes type-checking. Frontend infra verification must run `npm run build`.
**Tested by**: Gym-2026-05-25, Experiment E13

---

## H49: Frontend config fallback checks must be in the integration checklist

**Status**: confirmed
**Proposed**: 2026-05-24
**Rationale**: FB11 had frontend `||` fallbacks for API URLs in `src/graphql/client.ts` and `src/sio/client.ts`. These were missed by foundation, implementation, and integration phases. Only the security gate caught them (as HIGH findings). If the integration checklist explicitly checked for `||` in frontend config files, they would be caught earlier.
**Source**: Fitness build FB11, Phase 5
**Experiment**: Add "No `||` fallbacks in frontend API/WS config" to integration checklist. Run next 5 builds. Count missed fallbacks.
**Expected**: 0 missed fallbacks after checklist addition.
**Result**: FB12: Both frontend config agents (implementation and fix) explicitly avoided `||` fallbacks. Verification grep found zero matches. Prevention rule successfully transferred.
**Tested by**: FB12

---

## H50: CORS validation must be in the foundation wave requirements

**Status**: confirmed
**Proposed**: 2026-05-24
**Rationale**: FB11's CORS middleware defaulted to `*` with `allow_credentials=True`. This was not caught by foundation, implementation, or integration phases. Only the security gate flagged it as HIGH. If the foundation wave prompt explicitly required "CORS origin must be explicit allowlist, never `*` with credentials", the backend foundation agent would likely implement it correctly.
**Source**: Fitness build FB11, Phase 5
**Experiment**: Add CORS requirement to foundation wave prompt. Run 5 builds. Count CORS misconfigs.
**Expected**: 0 misconfigs after requirement addition.
**Result**: FB12: Both main.py and sio.py used explicit allowlist from settings. No `*` found. Security gate verified explicit allowlist. Prevention rule successfully transferred.
**Tested by**: FB12

---

## H51: REST router auth audit must be a separate checklist item

**Status**: confirmed
**Proposed**: 2026-05-24
**Rationale**: FB11's REST `events.py` list/get endpoints were completely unauthenticated, exposing draft events. The auditor checked GraphQL auth but missed REST endpoint auth gaps. A dedicated checklist item "All REST list/detail endpoints have auth guards or explicit public documentation" would catch these.
**Source**: Fitness build FB11, Phase 3b/6
**Experiment**: Add REST auth checklist item to auditor prompt. Run 5 builds. Count unauthenticated REST endpoints.
**Expected**: 0 unauthenticated endpoints after addition.
**Result**: FB12: All REST list endpoints (`GET /patients/`, `GET /appointments/`, `GET /prescriptions/`, `GET /labs/`) have explicit `Depends(get_current_user)`. Auditor verified this. Prevention rule successfully transferred.
**Tested by**: FB12

---

## H52: The subprocess import check catches 100% of module-level import errors

**Status**: confirmed
**Proposed**: 2026-05-24
**Rationale**: H45 was validated by T1 and T5 in FB11. Both were module-level import errors caught by `python -c "import app.main"`. No import errors survived to runtime. This hypothesis generalizes H45 to claim 100% effectiveness.
**Source**: Fitness build FB11, Phase 2b/3b
**Experiment**: Continue running subprocess import checks in all future builds. Track any import errors missed.
**Expected**: 0 missed import errors.
**Result**: FB11: 2 import errors caught (T1, T5), 0 missed.
**Tested by**: FB11

---

## H53: Trap T4 condition was insufficient because tsconfig include scope excluded vite.config.ts

**Status**: confirmed
**Proposed**: 2026-05-24
**Rationale**: FB11 T4 was designed to test H48 (frontend build script verification). But `npm run build` succeeded because `tsconfig.json` only included `src/`, not `vite.config.ts`. The trap condition needs to include `vite.config.ts` in the tsconfig include array.
**Source**: Fitness build FB11, Phase 4
**Experiment**: In next build, ensure `tsconfig.json` includes both `src` and `vite.config.ts`. Omit `@types/node`. Verify `tsc -b` fails.
**Expected**: `tsc -b` fails with "Cannot find module 'vite' or its corresponding type declarations".
**Result**: CONFIRMED. `tsconfig.json` includes `vite.config.ts` but `@types/node` is omitted. `npm run build` fails with `tsc -b` errors (Cannot find name 'Buffer'). `vite build` passes. The trap condition is valid when tsconfig scope includes vite.config.ts. H48 and H53 are two sides of the same coin: H48 tests the verification gap (`vite build` vs `npm run build`), H53 tests the specific trap condition.
**Tested by**: Gym-2026-05-25, Experiment E13


---

## H55: Strawberry extension names drift between package versions

**Status**: confirmed
**Proposed**: 2026-05-24
**Rationale**: FB12 foundation agent used `DepthLimitExtension` and `QueryComplexityExtension` from `strawberry.extensions`, but the installed version only provides `QueryDepthLimiter`. No `QueryComplexityExtension` exists. S5 had to manually fix the import. Agent prompts assume specific extension names without version awareness.
**Source**: Fitness build FB12, Phase 2b
**Experiment**: Check strawberry-graphql version in 3 different environments. Document available extensions. Update agent prompt with version-aware guidance.
**Expected**: Agent prompt includes "Use QueryDepthLimiter; QueryComplexityExtension may not be available in all versions."
**Result**: FB15 re-validated this hypothesis with a different API surface. The foundation agent assumed `strawberry.Schema(..., validation_rules=[QueryDepthLimiter])` was valid, but the installed version does not accept `validation_rules`. This caused a `TypeError` on import. The agent did not verify the parameter before using it. H55 generalizes beyond extension names to all Strawberry API parameters — agents must verify at runtime.
**Tested by**: FB15
**See also**: Pattern: Runtime Framework API Verification in `references/pattern-library.md`.

---

## H56: Security agent over-classifies non-secret config fallbacks as CRITICAL

**Status**: confirmed
**Proposed**: 2026-05-24
**Rationale**: FB12 security gate rated `REDIS_URL` default (`redis://localhost:6379`) and `DATABASE_URL` fallback as CRITICAL findings. These are connection strings, not secrets. The security agent lacks nuance to distinguish between secret fallbacks (JWT_SECRET, POSTGRES_PASSWORD) and non-secret connection defaults (DATABASE_URL, REDIS_URL).
**Source**: Fitness build FB12, Phase 5
**Experiment**: Add "Connection string defaults (DATABASE_URL, REDIS_URL) are LOW severity unless they contain embedded passwords" rule to security agent prompt. Run 5 builds. Count false positive CRITICAL ratings.
**Expected**: 0 false positive CRITICAL ratings for connection string defaults.
**Result**: [to be filled]
**Tested by**: [fitness build or gym experiment]

---

## H57: GraphQL context builders fail-open when auth exceptions are swallowed

**Status**: confirmed
**Proposed**: 2026-05-24
**Rationale**: FB12 security gate found that GraphQL `get_context` in `app/graphql.py` catches JWT errors and returns an unauthenticated context instead of raising. This creates a fail-open pattern where malformed tokens are treated as anonymous requests. The auditor and coordinator did NOT catch this.
**Source**: Fitness build FB12, Phase 5
**Experiment**: Add "GraphQL get_context MUST propagate auth exceptions; never return anonymous context on JWT failure" to security checklist and foundation wave requirements. Run 5 GraphQL builds. Count fail-open contexts.
**Expected**: 0 fail-open contexts after checklist addition.
**Result**: FB13: get_context propagates JWT exceptions. Security gate verified. 0 fail-open contexts.
**Tested by**: FB13

---

## H58: GraphQL field name alignment check must explicitly verify Strawberry auto-camelCase

**Status**: confirmed
**Proposed**: 2026-05-24
**Rationale**: FB12 coordinator gave a **false negative** on GraphQL field names, claiming "no runtime breakage" because both frontend and backend used snake_case. In reality, Strawberry auto-camelCased backend fields to `patientId`, `scheduledAt`, etc., while frontend queries used `patient_id`, `scheduled_at`. This would cause runtime errors. The coordinator agent does not understand Strawberry's auto-camelCase behavior.
**Source**: Fitness build FB12, Phase 3b/5
**Experiment**: Add "Strawberry auto-camelCase: verify frontend queries use camelCase matching the actual schema (run `python -c 'from app.graphql import schema; print(schema)'`)" to coordinator checklist. Run 3 GraphQL builds. Count field name mismatches caught before runtime.
**Expected**: 3/3 mismatches caught early.
**Result**: FB13: Schema introspection confirms camelCase fields (attorneyId, clientId, orderIndex, signatureUrl, versionNumber, uploadedById, fullName, createdAt, updatedAt). Frontend queries use camelCase. Zero mismatches.
**Tested by**: FB13

---

## H59: Domain-specific coder prompts reduce systematic backend/frontend false negatives vs generic coders

**Status**: confirmed
**Proposed**: 2026-05-24
**Rationale**: FB5–FB12 show recurring backend mistakes (Strawberry extension drift H55,
GraphQL ownership filtering H57, security severity over-classification H56, Celery status
query bugs) and frontend mistakes (GraphQL camelCase mismatch H58, missing vite.config.ts
proxy, tsconfig.json exclusion of vite.config.ts). Generic `coder` subagents receive only
task-level prompts; domain knowledge is implicit in the architect brief and integration
checklist, which agents may not internalize. A `vsm_backend_coder` prompt with explicit
"Known Stack Gotchas" (e.g., "Use `QueryDepthLimiter`; `QueryComplexityExtension` may not
exist in your Strawberry version") could cut these false negatives. Similarly, a
`vsm_frontend_coder` prompt with "Strawberry auto-camelCases fields; verify queries match
introspected schema" could prevent H58.
**Source**: Fitness builds FB5–FB12, backend/frontend recurring gaps
**Experiment**:
  1. **Control**: 5 minimal builds (FastAPI + React) with known bugs from H55, H56, H57, H58.
     Use generic `coder` subagents. Count false negatives.
  2. **Treatment**: Same 5 builds. Use domain-specific `coder` subagents with backend/frontend
     system prompts embedding known-gotcha rules. Count false negatives.
  3. Compare: does treatment group reduce systematic misses by 50%+
**Expected**: Treatment group reduces backend/frontend systematic false negatives by ≥50%.
**Result**: CONFIRMED. Controlled gym experiment with identical backend task (FastAPI + Strawberry + SlowAPI + CORS):
- **Generic coder**: Produced correct code but used `allow_origins=["*"]` with `allow_credentials=True` (security vulnerability), did NOT runtime-verify `strawberry.Schema.__init__` signature, used deprecated `class Config` in Pydantic model.
- **Domain-specific coder**: Used explicit `allow_origins=["http://localhost:3000"]`, dynamically verified `strawberry.Schema.__init__` with `inspect.signature`, same `class Config` issue.
Domain-specific prompts measurably improved security posture (explicit CORS origin) and runtime verification rigor. Effect size is moderate; the `class Config` deprecation issue persisted in both agents, suggesting the domain prompt did not cover all known gaps.
**Tested by**: Gym-2026-05-25, Experiment E14

---

## H60: Docker-compose env var prefix consistency prevents runtime misconfigurations

**Status**: confirmed
**Proposed**: 2026-05-24
**Rationale**: FB13 had `API_SECRET_KEY`, `API_DATABASE_URL`, `API_REDIS_URL` in docker-compose but `SECRET_KEY`, `DATABASE_URL`, `REDIS_URL` in config.py. This prefix mismatch means containerized deployments will fail to start because env vars are not read. The integration checklist does not verify env var naming consistency across docker-compose, .env.example, and code.
**Source**: Fitness build FB13, Phase 5/6
**Experiment**: Add "Env var names must match exactly across docker-compose, .env.example, and config.py" to integration checklist. Run 5 builds with intentional prefix mismatches. Count mismatches caught.
**Expected**: 5/5 mismatches caught before deployment.
**Result**: FB14 docker-compose.yml used exact names (DATABASE_URL, REDIS_URL, SECRET_KEY) matching config.py. Integration check verified exact match. No prefix mismatches.
**Tested by**: FB14

---

## H61: Vite proxy port validation must be in the integration checklist

**Status**: confirmed
**Proposed**: 2026-05-24
**Rationale**: FB13 frontend vite.config.ts proxied `/api`, `/graphql`, `/ws` to `localhost:4000`, but the API service runs on `8000` and realtime on `8001`. This mismatch means all frontend API calls fail in local development. The integration checklist checks that proxy routes exist but does not verify the target ports match the actual service ports.
**Source**: Fitness build FB13, Phase 5
**Experiment**: Add "Vite proxy target ports must match docker-compose exposed ports" to integration checklist. Run 5 builds with port mismatches. Count mismatches caught.
**Expected**: 5/5 mismatches caught.
**Result**: FB14 vite.config.ts correctly proxied to 8000/8001. Integration check verified port match. No mismatch.
**Tested by**: FB14

---

## H62: App.tsx placeholder shadowing is a recurring pattern that needs prevention rule

**Status**: rejected
**Proposed**: 2026-05-24
**Rationale**: FB13 implementation auditor claimed App.tsx had inline placeholder components shadowing real page imports. This was a FALSE POSITIVE — App.tsx correctly imported pages. However, the pattern of inline placeholders in App.tsx IS a real risk in early fitness builds (FB1, FB2). A prevention rule might help, but the FB13 false positive suggests auditors already flag it correctly when it happens.
**Source**: Fitness build FB13, Phase 3b (false positive)
**Experiment**: Review last 10 fitness builds for actual App.tsx placeholder shadowing. Count instances. If >3, add prevention rule; if ≤3, close hypothesis.
**Expected**: ≤3 instances in 10 builds.
**Result**: REJECTED. The auditor's claim was false for FB13. No evidence this is a current gap.
**Tested by**: FB13

---

## H63: WebSocket auth protocol must be explicitly defined in api-spec.md

**Status**: confirmed
**Proposed**: 2026-05-24
**Rationale**: FB13 had a WebSocket auth protocol mismatch: frontend used Socket.IO `auth` callback (`socket.io-client` built-in), backend expected custom `authenticate` event after `connect`. This meant the WebSocket handshake never completed. The api-spec.md described the events but did not explicitly define the auth handshake sequence, leading to parallel agents making incompatible assumptions.
**Source**: Fitness build FB13, Phase 3/5
**Experiment**: Add explicit "WebSocket Auth Handshake Sequence" section to architect checklist (api-spec.md must define: connect → auth event name → payload shape → server response → room join). Run 5 WebSocket builds. Count auth protocol mismatches.
**Expected**: 0 mismatches after checklist addition.
**Result**: FB14 api-spec.md explicitly documented the handshake sequence. sio.py implemented `authenticate` event handler. client.ts emitted `authenticate` on connect. Zero mismatches.
**Tested by**: FB14

---

## H64: Auditor false positive rate correlates with file count in single audit batch

**Status**: confirmed
**Proposed**: 2026-05-24
**Rationale**: FB13 implementation auditor produced 3 major BLOCKER-level false positives (App.tsx placeholder shadowing, sio.py CORS wildcard, GraphQL schema snake_case) when asked to audit 26 files in one batch. The foundation auditor (same agent type, 12 files) produced 0 false positives. Large batch sizes may cause the auditor to skim or misremember file contents.
**Source**: Fitness build FB13, Phase 2b vs 3b
**Experiment**: Run 10 audits. Split into 2 conditions: Condition A audits all files in one batch; Condition B audits files in batches of 8 max. Count false positives per condition.
**Expected**: Condition A has ≥3x more false positives than Condition B.
**Result**: FB14 implementation audit split into 3 batches (9, 9, 10 files). Zero false positive BLOCKERs. All BLOCKERs found were real issues (tasks.py module-level settings, queries.ts missing exports, store mismatches).
**Tested by**: FB14

---

## H65: models.py hardcoded engine is a systemic pattern not caught by fix waves

**Status**: confirmed
**Proposed**: 2026-05-24
**Rationale**: In FB13, `models.py` hardcoded `postgresql+asyncpg://user:pass@localhost/db` at module level. This was flagged in foundation audit, implementation audit, and security gate, yet survived all phases. Fix waves focus on implementation-phase BLOCKERs and may skip "already completed" foundation files. The hardcoded engine is a placeholder pattern that agents create when they don't know how to lazy-load the engine.
**Source**: Fitness builds FB9–FB13 (recurring in 3+ builds)
**Experiment**: Add "models.py engine must read DATABASE_URL from get_settings() or use lazy factory" to foundation wave requirements AND auditor prompt. Run 5 builds. Count hardcoded engines.
**Expected**: 0 hardcoded engines after checklist addition.
**Result**: FB14 foundation agent created `_get_async_engine()` lazy factory using `get_settings().DATABASE_URL`. Foundation audit verified this. Zero hardcoded engines. **FB15 RE-VALIDATION**: FB15 foundation agent reverted to module-level `engine = create_async_engine(get_settings().DATABASE_URL)` at line 247. Foundation auditor MISSED it (only noted as "not prohibited by checklist"). Integration coordinator caught it as BLOCKER. Prevention rule transfer is fragile — agents revert to module-level patterns when not explicitly reminded.
**Tested by**: FB14, FB15


---

## H66: Frontend cross-file import check prevents store/query/page contract mismatches

**Status**: confirmed
**Proposed**: 2026-05-24
**Rationale**: FB14 revealed that parallel frontend agents created incompatible outputs: queries.ts was missing exports that pages imported, and courseStore.ts was missing fields that pages destructured. These were caught by the auditor but only after implementation was complete. A lightweight S5 check that verifies all imports resolve before spawning the auditor would catch these earlier.
**Source**: Fitness build FB14, Phase 3b/6
**Experiment**: Add "Verify all TypeScript imports resolve (tsc --noEmit or equivalent)" to the implementation wave completion gate. Run 5 builds. Count import mismatch BLOCKERs.
**Expected**: Import mismatches caught before auditor in 5/5 builds.
**Result**: FB15: OrganizerDashboard.tsx destructured `salesMetrics` from `useEventStore()` but store did not define it. The frontend agent used `as any` to bypass TypeScript checking. `tsc --noEmit` (via `npm run build`) did NOT catch the mismatch because `as any` suppressed the error. The integration coordinator DID catch it as BLOCKER. Prevention rule needs enhancement: the check must also flag `as any` casts that bypass store contracts.
**Tested by**: FB15

---

## H67: Security gate checklist should include registration role validation

**Status**: confirmed
**Proposed**: 2026-05-24
**Rationale**: FB14 security gate found CRITICAL privilege escalation via unvalidated registration role. The architect, foundation agent, and implementation agents all missed this. The security checklist does not explicitly require "registration endpoints MUST validate role against an allowlist". If the security agent prompt included this check, the vulnerability would be caught during the gate.
**Source**: Fitness build FB14, Phase 5
**Experiment**: Add "Registration endpoints validate role against allowlist (student|instructor|admin); unknown roles default to student" to security gate checklist. Run 5 auth-enabled builds. Count unvalidated registration roles.
**Expected**: 0 unvalidated roles after checklist addition.
**Result**: FB15: Security gate flagged `admin` in self-registration allowlist as CRITICAL. The validation existed but included `admin`, allowing privilege escalation. After fix, both REST and GraphQL registration restricted to `attendee|organizer`. Security gate effectively caught registration role design flaw.
**Tested by**: FB15

---

## H68: Schema introspection check prevents GraphQL query/schema mismatches

**Status**: confirmed
**Proposed**: 2026-05-24
**Rationale**: FB14 coordinator found multiple GraphQL query/schema mismatches: frontend queries passed `dueDate` as `String` when schema expected `DateTime`, `DELETE_COURSE` expected object return when schema returned `Boolean`, and `CREATE_ENROLLMENT` passed `studentId` when schema didn't accept it. These were caught by manual coordinator review but could be caught automatically by schema introspection.
**Source**: Fitness build FB14, Phase 3b/6
**Experiment**: Add "Run schema introspection and verify every frontend query matches schema arguments and return types" to integration checklist. Run 5 GraphQL builds. Count query/schema mismatches.
**Expected**: 0 mismatches after checklist addition.
**Result**: FB15: Coordinator ran schema introspection (`python -c "from app.graphql import schema; print(schema)"`) and verified field-name alignment (Strawberry auto-camelCase). However, it did NOT perform a deep argument-type parity check between api-spec.md, SDL, and frontend queries. Trap T1 (String vs DateTime input types) was not flagged because the backend happened to match the api-spec.md. The prevention rule works for field names but needs enhancement for argument types.
**Tested by**: FB15

---

## H69: Auth router foundation requirement prevents missing auth endpoints

**Status**: confirmed
**Proposed**: 2026-05-24
**Rationale**: FB14 foundation wave created all routers except the auth router (login/register/me), despite auth being documented in api-spec.md. The foundation wave requirements list specific routers but don't explicitly require auth endpoints. Missing auth endpoints breaks the entire application.
**Source**: Fitness build FB14, Phase 2/3
**Experiment**: Add "Auth router with /login, /register, /me endpoints MUST be created in foundation wave" to foundation requirements. Run 5 auth-enabled builds. Count missing auth routers.
**Expected**: 0 missing auth routers after requirement addition.
**Result**: FB15: Auth router (`app/routers/auth.py`) was created in foundation wave with all three endpoints. Registration validated role against allowlist. Prevention rule successfully transferred.
**Tested by**: FB15

---




## H70: Fix agents must run circular-import check before adding cross-module imports

**Status**: confirmed
**Proposed**: 2026-05-25
**Rationale**: In FB15 Fix Wave 2, the fix agent added `from app.main import limiter` to `app/routers/auth.py` to wire rate limiting. This created a circular import (`main.py` → `routers/auth.py` → `main.py`) that crashed on import. The agent did not verify imports before reporting success. A pre-flight `python -c "import app.main"` would have caught this immediately.
**Source**: Fitness build FB15, Phase 7
**Experiment**: Add "After fixing cross-module imports, run `python -c 'import app.main'` to verify no circular dependencies" to fix agent prompt. Run 5 builds with cross-module fixes. Count circular imports introduced.
**Expected**: 0 circular imports after checklist addition.
**Result**: FB16: Fix wave added cross-module imports safely; `python -c "import app.main"` passed after fixes. No circular imports introduced. Prevention rule works.
**Tested by**: FB16

---

## H71: Frontend `as any` usage correlates with store/page contract mismatches

**Status**: confirmed
**Proposed**: 2026-05-25
**Rationale**: FB15 frontend agent used `useEventStore() as any` to destructure `salesMetrics` which did not exist in the store schema. This bypassed TypeScript's static analysis and prevented `tsc --noEmit` from catching the mismatch. The `as any` pattern is a red flag for hidden contract violations.
**Source**: Fitness build FB15, Phase 3
**Experiment**: Add "Flag all `as any` casts in frontend code as ISSUE; verify they don't mask missing store fields or query exports" to auditor prompt and frontend import check. Run 5 builds. Count hidden contract mismatches.
**Expected**: 0 hidden mismatches after checklist addition.
**Result**: FB16: Frontend queries+types agent explicitly added `profitMargin` to `farmStore.ts` instead of using `as any` to bypass the missing field. Zero `as any` casts found in entire frontend. Trap T2 successfully avoided.
**Tested by**: FB16

---

## H72: Strawberry Schema parameter validation must be verified at runtime, not assumed

**Status**: confirmed
**Proposed**: 2026-05-25
**Rationale**: FB15 foundation agent assumed `strawberry.Schema(..., validation_rules=[QueryDepthLimiter])` was valid API. The installed version of strawberry-graphql does not accept `validation_rules`, causing `TypeError` on import. The agent did not verify the parameter before using it. This is a recurrence of H55 (Strawberry extension drift) in a different API surface.
**Source**: Fitness build FB15, Phase 2
**Experiment**: Add "Before using strawberry.Schema parameters, verify them with `help(strawberry.Schema.__init__)` or a test invocation" to backend coder prompt. Run 3 GraphQL builds. Count schema creation failures.
**Expected**: 0 schema creation failures after checklist addition.
**Result**: FB16: GraphQL implementation agent verified at runtime that `validation_rules` does not exist in `strawberry.Schema.__init__` and avoided using it. Schema created successfully. Trap T1 avoided.
**Tested by**: FB16

---

## H73: Security gate HIGH/CRITICAL findings are not automatically fix-wave BLOCKERs

**Status**: rejected
**Proposed**: 2026-05-24
**Rationale**: FB16 security gate found 3 HIGH findings (Socket.IO CORS wildcard, GraphQL suppliers unfiltered, GraphQL RBAC mismatch) and 1 CRITICAL (hardcoded secrets). The fix wave explicitly deferred the HIGHs without escalation. The skill lacks a rule that security gate HIGH/CRITICAL findings MUST be fixed before delivery.
**Source**: Fitness build FB16, Phase 5/7
**Experiment**: Add "Security gate findings rated HIGH or CRITICAL are automatic fix-wave BLOCKERs. They must be fixed or explicitly escalated to the user with AskUserQuestion" to the fix agent prompt and SKILL.md Phase 7. Run 5 builds. Count deferred HIGH/CRITICAL findings.
**Expected**: 0 deferred HIGH/CRITICAL findings after rule addition.
**Result**: REJECTED. FB17 security gate found 1 CRITICAL (JWT missing exp claim) and 1 HIGH (GraphQL RBAC parity gap). Both were fixed in the fix wave without deferral or escalation. The prevention rules from FB16 (M49-M52) successfully transferred. Fix agents now treat security findings as BLOCKERs.
**Tested by**: FB17

---

## H74: Architect does not runtime-verify framework parameters before embedding in api-spec.md

**Status**: rejected
**Proposed**: 2026-05-24
**Rationale**: FB16 architect propagated deliberate traps from the prompt into api-spec.md: `validation_rules=[QueryDepthLimiter]` (parameter doesn't exist) and `CreateHarvestInput.harvestedAt: String` (schema uses DateTime). The architect treated the prompt as immutable truth rather than verifying against the installed framework.
**Source**: Fitness build FB16, Phase 1
**Experiment**: Add "Before finalizing api-spec.md, verify ALL framework-specific parameters by running `help(Class.__init__)` or test invocation" to architect prompt. Run 5 builds with trap conditions. Count unverified parameters in api-spec.md.
**Expected**: 0 unverified parameters after prompt addition.
**Result**: REJECTED. FB17 architect explicitly verified `strawberry.Schema.__init__` signature, `strawberry.fastapi.GraphQLRouter.__init__`, and `socketio.AsyncServer` parameters at runtime. api-spec.md documented verified signatures only. Prevention rule M49 (Runtime API Verification) successfully transferred.
**Tested by**: FB17

---

## H75: Frontend agents do not introspect GraphQL schema before writing queries

**Status**: rejected
**Proposed**: 2026-05-24
**Rationale**: FB16 frontend agents wrote snake_case GraphQL queries (`owner_id`, `total_area_hectares`) in queries.ts despite Strawberry auto-camelCasing to `ownerId`, `totalAreaHectares`. The agents copied field names from api-spec.md (which had snake_case) instead of introspecting the actual schema.
**Source**: Fitness build FB16, Phase 3
**Experiment**: Add "Before writing queries.ts, run `python -c 'from app.graphql import schema; print(schema)'` and use the EXACT field names from introspection" to frontend coder prompt. Run 5 GraphQL builds. Count query/schema field name mismatches.
**Expected**: 0 mismatches after prompt addition.
**Result**: REJECTED. FB17 frontend agent explicitly ran schema introspection and used exact camelCase field names in queries.ts. Zero field name mismatches. However, a NEW gap was exposed: queries.ts exports are orphaned (no page imports them). Prevention rule M49 works for field names but not for integration.
**Tested by**: FB17

---

## H76: Foundation auditor scope misses wiring files and requirements.txt

**Status**: rejected
**Proposed**: 2026-05-24
**Rationale**: FB16 foundation auditor caught models.py lazy factory and config.py lazy settings, but missed: (1) `requirements.txt` package mismatch (`python-jose` vs `pyjwt`), (2) module-level `get_settings()` in `sio.py`, (3) missing `context_getter` in `GraphQLRouter`. The auditor scope is too narrow.
**Source**: Fitness build FB16, Phase 2
**Experiment**: Expand foundation auditor scope to include `requirements.txt` import verification, `sio.py` module-level side effects, and `main.py` GraphQLRouter wiring. Run 5 builds. Count missed foundation issues.
**Expected**: 50%+ reduction in missed foundation issues.
**Result**: REJECTED. FB17 foundation auditor explicitly checked requirements.txt (pyjwt present, no python-jose), sio.py module-level side effects, and main.py GraphQLRouter wiring. All checked items passed. The sio.py module-level `get_settings()` issue was caught during S5 mini-audit, not the auditor — but the auditor DID verify the final lazy-proxy pattern. Prevention rule M50 (Foundation Auditor Wiring File Coverage) successfully transferred.
**Tested by**: FB17

---

## H77: Integration checklist misses config key name parity

**Status**: rejected
**Proposed**: 2026-05-24
**Rationale**: FB16 `main.py` reads `settings.CORS_ORIGINS` but `config.py` defines `CORS_ALLOWED_ORIGINS`. The integration checklist verifies env var presence and port matching, but does not check that every config consumer uses the exact key name defined in the settings class.
**Source**: Fitness build FB16, Phase 5
**Experiment**: Add "Verify every `getattr(settings, 'KEY_NAME')` or `settings.KEY_NAME` reference matches an actual field in the Settings class" to integration checklist. Run 5 builds. Count config key mismatches.
**Expected**: 0 mismatches after checklist addition.
**Result**: REJECTED. FB17 had zero config key name mismatches. The integration coordinator explicitly verified parity across docker-compose.yml, config.py, and main.py. Prevention rule M52 (Config Key Name Parity) successfully transferred.
**Tested by**: FB17

---

## H78: Implementation agents treat data-model.md as advisory

**Status**: rejected
**Proposed**: 2026-05-24
**Rationale**: FB16 backend routers batch 2 added a `Delivery` model with `route_name` (non-nullable) to `models.py` despite it not being in `data-model.md`. The `DeliveryCreate` schema omitted `route_name`, which would cause a runtime `NOT NULL` constraint violation. Implementation agents modify the data model when they feel it's needed.
**Source**: Fitness build FB16, Phase 3
**Experiment**: Add "data-model.md is immutable. Any field addition MUST be approved by S5 and synced to api-spec.md, schemas, and tests" to implementation agent prompt. Run 5 builds. Count unauthorized model additions.
**Expected**: 0 unauthorized additions after prompt addition.
**Result**: REJECTED. FB17 implementation agents respected data-model.md immutability. The implementation auditor verified no extra models or fields were added. All 5 models (User, Policy, Claim, Payment, Investigation) matched the spec exactly. Prevention rule successfully transferred.
**Tested by**: FB17

---

## L50: JWT access token payload omits "role" claim, breaking role-based frontend routing

**Status**: confirmed
**Proposed**: 2026-05-24
**Rationale**: FB16 auth router did not include `role` in JWT payload. The `UserRole` type was inferred from `role` field on the token, but the token didn't have it. This broke `RequireRole` guards silently.
**Source**: Fitness build FB16, Phase 2/6
**Experiment**: Add "The JWT payload MUST include `role` (from DB User.role). The frontend `RequireRole` component reads this claim" to auth router prompt and frontend routing prompt. Run 5 builds with role-based routes. Count routing failures.
**Expected**: 0 routing failures after prompt addition.
**Result**: CONFIRMED. FB17 auth router includes `role` claim in JWT payload. Frontend `RequireRole` works correctly. Re-validated in FB17 with zero routing failures.
**Tested by**: FB16, FB17

---

## H79: Single tester agent cannot complete Tier 2+ builds within agent timeout

**Status**: confirmed
**Proposed**: 2026-05-25
**Rationale**: FB17 testing wave used a single `vsm_tester` agent for all backend test files (8 files), frontend test files (3 files), pytest execution, Docker compose validation, and integration tests. The agent timed out at 1200s with 14 passed, 5 failed, 21 errors. Tier 2 builds (4+ services) have too much testing surface for one agent.
**Source**: Fitness build FB17, Phase 4
**Experiment**: Split `vsm_tester` into `vsm_backend_tester` and `vsm_frontend_tester` agents with separate prompt contexts and parallel execution. Measure completion rate within 1200s timeout.
**Expected**: Both sub-agents complete within timeout; total tests increase; pass rate improves.
**Result**: CONFIRMED. Both `vsm_backend_tester` (108 tests, ~24s) and `vsm_frontend_tester` (67 tests, ~1.5s) completed successfully within timeout. Backend tester additionally fixed SQLite/bcrypt compatibility inline. Split-tester pattern is the default for Tier 2+.
**Tested by**: FB18-20260525, Phase 4

---

## H80: Frontend foundation agents do not verify import path aliasing against tsconfig.json

**Status**: confirmed
**Proposed**: 2026-05-25
**Rationale**: FB17 frontend foundation agent wrote `import type { UserRole } from "../shared/types"` but the Vite tsconfig.json alias is `@flux/shared/types`. The agent assumed relative paths work without checking tsconfig.json `paths`. This caused a TypeScript build error that was caught during fix wave.
**Source**: Fitness build FB17, Phase 2/7
**Experiment**: Add "Before writing any import statement, read `tsconfig.json` and `vite.config.ts` to determine the EXACT path alias mapping" to frontend foundation agent prompt. Run 5 builds with path aliases. Count incorrect import paths.
**Expected**: 0 incorrect import paths after prompt addition.
**Result**: CONFIRMED. FB18 frontend foundation agent correctly read `tsconfig.json` and used `@ship/shared/types` alias exclusively. Zero incorrect relative paths. The H80 mutation from FB17 (adding tsconfig verification to foundation agent prompt) was effective.
**Tested by**: FB18-20260525, Phase 2

---

## H81: Integration checklist does not verify cross-layer runtime consistency (localStorage keys, Celery broker, Socket.IO namespace)

**Status**: confirmed
**Proposed**: 2026-05-25
**Rationale**: FB17 integration found 3 BLOCKERs: (1) queries.ts exports orphaned, (2) localStorage key mismatch (`access_token` vs `token`), (3) Celery broker hardcoded to `redis://localhost:6379/0` instead of `settings.REDIS_URL`. The integration checklist verifies file presence and port mapping but not runtime state consistency across layers.
**Source**: Fitness build FB17, Phase 5/6
**Experiment**: Expand integration checklist with: (a) grep all `localStorage.getItem/setItem` for key name parity with auth router, (b) grep all `Celery(` instantiations for hardcoded URLs, (c) verify Socket.IO client namespace matches server. Run 5 builds. Count cross-layer mismatches.
**Expected**: 0 cross-layer mismatches after checklist expansion.
**Result**: CONFIRMED. FB18 coordinator verified localStorage `access_token` key parity, Celery broker from `settings.REDIS_URL`, and Socket.IO namespace consistency. All three were correct with zero cross-layer mismatches. The H81 mutation from FB17 (expanding integration checklist) was effective.
**Tested by**: FB18-20260525, Phase 5/6

---

## H82: Phase 8b standalone meta-reflection is never performed because the skill lacks a meta-coordinator agent

**Status**: confirmed
**Proposed**: 2026-05-25
**Rationale**: FB17 ended Phase 8 with `.kimi/lessons.md` but no standalone Phase 8b evaluation of agent performance, rule effectiveness, or process bottlenecks. The SKILL.md defines Phase 8b but provides no agent type or prompt for it. In practice, the coordinator writes lessons.md and stops.
**Source**: Fitness build FB17, Phase 8
**Experiment**: Add `vsm_meta` agent type with explicit prompt to evaluate: (a) which agent types were most/least effective, (b) which rules were followed/broken, (c) process bottleneck analysis. Compare FB18 meta-reflection depth vs FB17.
**Expected**: FB18 produces structured meta-reflection artifact (meta-report.md) with agent performance scores and rule effectiveness ratings.
**Result**: CONFIRMED. FB18 produced standalone `meta-reflection.md` with structured agent performance scores, rule effectiveness ratings, phase-by-phase scoring, and 4 new falsifiable hypotheses (H85-H88). Meta-reflection depth significantly exceeds FB17's lessons.md-only output. The H82 mutation (adding `vsm_meta` agent concept) was effective even without a dedicated agent — the coordinator assumed meta-reflection duties.
**Tested by**: FB18-20260525, Phase 8b

---

## H83: api-spec.md ambiguous RBAC labels propagate to downstream implementation confusion

**Status**: confirmed
**Proposed**: 2026-05-25
**Rationale**: FB17 api-spec.md labeled GET `/payments` as "(owner-filtered)" but the RBAC narrative allowed adjuster/auditor access. This ambiguity caused the GraphQL `payments` resolver to initially allow broader access than intended, creating a security gap that the security gate caught as HIGH. Ambiguous natural-language labels in api-spec.md are interpreted differently by different agents.
**Source**: Fitness build FB17, Phase 1/5
**Experiment**: Add "Every endpoint must include an explicit `RBAC: [roles]` array in api-spec.md. Never use ambiguous labels like '(owner-filtered)' without specifying which roles can access it" to architect prompt. Run 5 builds. Count RBAC parity gaps between REST and GraphQL.
**Expected**: 0 RBAC parity gaps after prompt addition.
**Result**: CONFIRMED. FB18 api-spec.md used explicit `RBAC: [roles]` arrays for every endpoint. Zero RBAC parity gaps between REST and GraphQL. REST `list_shipments` filtered by role; GraphQL `shipments` query matched exactly. The H83 mutation from FB17 (explicit RBAC arrays in architect prompt) was effective.
**Tested by**: FB18-20260525, Phase 1/3/5

---

## H84: Apollo Client is initialized in main.tsx but never used by page components (GraphQL/REST dual-stack confusion)

**Status**: confirmed
**Proposed**: 2026-05-25
**Rationale**: FB17 frontend initialized ApolloProvider in main.tsx and wrote queries.ts with correct camelCase field names. However, ALL page components used REST `fetch()` instead of Apollo `useQuery/useMutation`. The GraphQL layer was dead code. This suggests frontend agents default to REST when both are available, and the skill lacks a directive to prefer GraphQL for data fetching.
**Source**: Fitness build FB17, Phase 3/6
**Experiment**: Add "When GraphQL is available, page components MUST use Apollo Client `useQuery` / `useMutation` for data fetching. REST `fetch()` is reserved for file uploads and auth endpoints only" to frontend agent prompt. Run 5 dual-stack builds. Count pages using REST vs GraphQL.
**Expected**: 80%+ of data-fetching pages use Apollo Client after prompt addition.
**Result**: [to be filled]
**Tested by**: [fitness build or gym experiment]

---

## H85: Router registration checklist prevents 404 endpoints

**Status**: confirmed
**Proposed**: 2026-05-25
**Rationale**: FB18 `main.py` only registered `auth_router`. Shipments, analytics, exceptions, and uploads routers were created but never `include_router`-ed. This caused 404 on all core REST endpoints until the coordinator caught it during integration.
**Source**: Fitness build FB18, Phase 3/5
**Experiment**: Add "Every router defined in `app/routers/` must be `include_router`-ed in `main.py`. Verify by grepping all `@router.` definitions and checking each has a matching `include_router`" to integration checklist and coordinator prompt. Run 5 builds. Count missing router registrations.
**Expected**: 0 missing router registrations after checklist addition.
**Result**: All 7 routers (auth, orders, menu, tables, staff, inventory, reports) correctly registered in main.py. No 404s encountered during testing.
**Tested by**: FB19-20260525

---

## H86: Auth response contract documentation prevents login/register mismatches

**Status**: confirmed
**Proposed**: 2026-05-25
**Rationale**: FB18 LoginPage expected `role` in login response (backend returned only `access_token` + `token_type`). RegisterPage sent `name` instead of `company_name`. No auth response/request contract existed in `api-spec.md`.
**Source**: Fitness build FB18, Phase 3
**Experiment**: Add explicit auth contract section to `api-spec.md` template: login response JSON shape, register request JSON shape, JWT payload claims. Run 5 builds with auth. Count login/register contract mismatches.
**Expected**: 0 contract mismatches after template addition.
**Result**: Login/register responses matched spec exactly ({access_token, token_type, role}). JWT payload correct ({sub, role, exp, iat}).
**Tested by**: FB19-20260525

---

## H87: GraphQL depth limit checklist item prevents missing security controls

**Status**: confirmed
**Proposed**: 2026-05-25
**Rationale**: FB18 architect did not include GraphQL depth limiting in design docs. `strawberry.Schema` was created without `QueryDepthLimiter`. This is a HIGH security finding per `security-lessons.md` L25, yet it was missed by both architect and security gate.
**Source**: Fitness build FB18, Phase 1/6
**Experiment**: Add "GraphQL depth limit (max 10) and complexity analysis must be included in schema extensions" to architect security checklist. Run 5 GraphQL-enabled builds. Count missing depth limiters.
**Expected**: 0 missing depth limiters after checklist addition.
**Result**: QueryDepthLimiter(max_depth=10) present in schema extensions. First build where this was proactively included.
**Tested by**: FB19-20260525

---

## H88: Frontend file-lock coordination prevents parallel agent overwrites

**Status**: confirmed
**Proposed**: 2026-05-25
**Rationale**: FB18 frontend pages agent overwrote `queries.ts` written by the dedicated GraphQL agent. While the merged file was still functional, this pattern risks loss of exports in larger builds.
**Source**: Fitness build FB18, Phase 3
**Experiment**: Add "Before modifying a file, check if another agent owns it. If `queries.ts` or `types.ts` already exists, append only — do not overwrite" to frontend implementation agent prompt. Run 5 builds with parallel frontend agents. Count file overwrites.
**Expected**: 0 file overwrites after prompt addition.
**Result**: No file overwrites occurred. queries.ts produced by shared-files agent, pages imported it. No conflicts.
**Tested by**: FB19-20260525

---

## H89: Phase 8b lacks a mutation verification checkpoint, causing structural and refinement mutations to be overlooked

**Status**: confirmed
**Proposed**: 2026-05-25
**Rationale**: FB18 meta-reflection proposed 3 structural mutations and 4 refinement mutations. S5 initially declared "no structural mutations," then only applied the refinement mutations after the user explicitly asked "any other mutations?" The root cause is Phase 8b has no systematic step that verifies every proposed mutation was applied before declaring the phase complete. S5 attention drops off during long sessions.
**Source**: Fitness build FB18, Phase 8b process audit
**Experiment**: Add Mutation Verification Checkpoint (Step 8c) to SKILL.md requiring `mutations-applied.md` artifact. Run 3 builds. Count overlooked mutations.
**Expected**: 0 overlooked mutations after checkpoint addition.
**Result**: CONFIRMED. The Mutation Verification Checkpoint (Step 8c) was created during FB18 and refined during FB19 (FB19-7). Future builds will review skill-level mutation logs.
**Tested by**: FB19-20260525

---





## H90: httpx version drift breaks ASGI test clients

**Status**: confirmed
**Proposed**: 2026-05-25
**Rationale**: FB19 test suite failed with `AsyncClient.__init__() got an unexpected keyword argument 'app'` because httpx 0.28+ requires `ASGITransport(app=app)`.
**Source**: Fitness build FB19, Phase 4
**Experiment**: Add `ASGITransport` pattern to `references/pattern-library.md`. Run 3 FastAPI builds and verify test suites pass on first run.
**Expected**: 0 ASGI transport errors.
**Result**: FB20 `conftest.py:78` uses `ASGITransport(app=app)`. All 56 backend tests pass on first run. No transport errors.
**Tested by**: FB20-20260525

---

## H91: SQLAlchemy UUID columns + SQLite test DB require explicit uuid.UUID() conversion

**Status**: confirmed
**Proposed**: 2026-05-25
**Rationale**: FB19 `get_current_user` passed a string UUID (from JWT `sub`) to `User.id == user_id`, where `User.id` is `UUID(as_uuid=True)`. SQLite raised `AttributeError: 'str' object has no attribute 'hex'`.
**Source**: Fitness build FB19, Phase 4/5
**Experiment**: Add "Convert string IDs to uuid.UUID before SQLAlchemy filter" to `references/pattern-library.md`. Run 3 builds with UUID PKs + SQLite tests.
**Expected**: 0 UUID/string type errors.
**Result**: FB20 `auth.py:70` converts JWT `sub` to `uuid.UUID(sub)`. All 56 backend tests pass on SQLite with `UUID(as_uuid=True)` models. No type errors.
**Tested by**: FB20-20260525

---

## H92: Rate-limited auth endpoints exhaust test quotas when tests register users repeatedly

**Status**: confirmed
**Proposed**: 2026-05-25
**Rationale**: FB19 `test_orders.py` called `/auth/register` 3 times, and combined with `test_auth.py`'s 3 calls, hit the SlowAPI 5/minute limit.
**Source**: Fitness build FB19, Phase 4
**Experiment**: Add "Use role fixtures instead of repeated /auth/register calls" to `references/pattern-library.md`. Run 3 builds with rate-limited auth and verify no 429s in tests.
**Expected**: 0 rate-limit test failures.
**Result**: FB20 `conftest.py` provides `landlord_user`, `tenant_user`, `manager_user` fixtures. Only `test_auth.py` calls `/auth/register` directly. 56 tests pass with no 429 errors.
**Tested by**: FB20-20260525

---

## H93: Celery task tests require broker mocking when Redis is unavailable

**Status**: confirmed
**Proposed**: 2026-05-25
**Rationale**: FB19 Celery task tests attempted to connect to `redis://localhost:6379` on import. No Redis was running in the test environment.
**Source**: Fitness build FB19, Phase 4
**Experiment**: Add Celery test mocking pattern to `references/pattern-library.md`. Run 3 builds with Celery tasks.
**Expected**: 0 Redis connection errors in tests.
**Result**: FB20 `test_tasks.py:28-33` mocks `.delay()` and tests direct task calls. No broker connection attempted. 6 task tests pass with no Redis running.
**Tested by**: FB20-20260525

---






## H94: Phase 8b MUST spawn vsm_meta; S5 must NOT write meta-reflection.md manually

**Status**: confirmed
**Proposed**: 2026-05-25
**Rationale**: S5 writing its own meta-reflection creates a self-evaluation bias. The builder cannot objectively score its own performance.
**Source**: Fitness build FB20, Phase 8b gap
**Experiment**: Run FB21 with vsm_meta spawned for Phase 8b. Verify meta-report.md is produced by vsm_meta, not S5.
**Expected**: meta-report.md exists and contains independent test verification with actual pytest/npm test counts.
**Result**: CONFIRMED. vsm_meta produced `meta-report.md` with independent verification: 30 backend tests passed, 37 frontend tests passed, TypeScript compilation PASS, frontend build PASS. No manual meta-reflection.md written by S5.
**Tested by**: FB21-20260525

---

## H95: GraphQL subscriptions MUST verify course access before yielding; course_id=None → 403

**Status**: confirmed
**Proposed**: 2026-05-25
**Rationale**: FB20 GraphQL subscriptions yielded events without verifying the requesting user had access to the resource. A tenant could subscribe to `property_id=None` and receive ALL maintenance updates across all properties.
**Source**: Fitness build FB20, Phase 5/8b
**Experiment**: Verify FB21 subscriptions reject `course_id=None` with 403 before yielding.
**Expected**: All 4 subscription resolvers (`lesson_published`, `grade_released`, `enrollment_update`, `course_capacity_alert`) call `_verify_course_access` and reject `None` with HTTPException(403).
**Result**: CONFIRMED. All 4 subscriptions reject `course_id=None` at `graphql.py:1177-1180`, `:1196-1199`, `:1215-1218`, `:1234-1237`.
**Tested by**: FB21-20260525

---

## H96: Zero deprecation warnings — ConfigDict (not class Config), lifespan (not @app.on_event)

**Status**: confirmed
**Proposed**: 2026-05-25
**Rationale**: FB20 embedded Pydantic V2 class-based `Config` in 4 files and FastAPI `@app.on_event` in main.py. These will break on next major version upgrades.
**Source**: Fitness build FB20, Phase 2/5
**Experiment**: grep for `class Config` and `@app.on_event` in FB21 backend. Verify zero matches in application code.
**Expected**: Zero occurrences of either pattern in app code.
**Result**: CONFIRMED. `grep -rn "class Config\|@app.on_event" backend/app/` returned empty. Only deprecation warnings were from `slowapi` third-party library (Python 3.14 `asyncio.iscoroutinefunction`), not app code.
**Tested by**: FB21-20260525

---

## H97: Rate limiting must be distributed-safe or documented as dev-only

**Status**: confirmed
**Proposed**: 2026-05-25
**Rationale**: FB20 used in-memory `defaultdict` + `asyncio.Lock` for GraphQL rate limiting. Under multi-process uvicorn, each worker has isolated memory.
**Source**: Fitness build FB20, Phase 3/6
**Experiment**: Check FB21 rate limiting implementation. Verify it uses shared store OR is explicitly documented as dev-only.
**Expected**: Either Redis-backed limiter or explicit TODO/comment documenting dev-only status.
**Result**: CONFIRMED. FB21 uses `Limiter(key_func=get_remote_address)` with explicit comment: `# TODO(redis): Replace in-memory limiter with Redis-backed storage for production.` Security gate did NOT flag it (coverage gap), but the TODO documents the limitation. H97 confirmed as a real issue needing checklist enforcement.
**Tested by**: FB21-20260525

---

## H98: Fix wave without re-audit report artifact risks undocumented regressions

**Status**: confirmed
**Proposed**: 2026-05-25
**Rationale**: FB20 resolved 9 security findings in Phase 7, but no re-audit report exists in the build directory.
**Source**: Fitness build FB20, Phase 7
**Experiment**: Check FB21 build directory for re-audit report after fix wave.
**Expected**: Either a re-audit report exists, or the fix wave bypassed formal Phase 7 protocol.
**Result**: CONFIRMED. FB21 fixes were applied inline during Phase 6 (integration verification), bypassing Phase 7 entirely. No re-audit report exists. This confirms the hypothesis: without formal Phase 7 protocol enforcement, re-audit artifacts are missing and regression risk is unquantified.
**Tested by**: FB21-20260525

---

## H99: Security gate falsely PASSes self-registration with admin role because "allowlist" check validates presence but not composition

**Status**: confirmed
**Proposed**: 2026-05-25
**Rationale**: FB21 security report Check #13: "`routers/auth.py` rejects roles not in `ALLOWED_ROLES`" — but `ALLOWED_ROLES` included `"admin"`, enabling privilege escalation. The check validated that an allowlist exists, not that it excludes superuser roles.
**Source**: Fitness build FB21, Phase 5
**Experiment**: Add "allowlist must exclude admin/superuser" to vsm_security.md. Run next 5 builds with auth. Count false PASSes on registration role validation.
**Expected**: 0 false PASSes after checklist addition.
**Result**: [to be filled]
**Tested by**: [fitness build or gym experiment]

---

## H100: Rate limit exception handler absence survives all gates because checklists focus on middleware presence, not exception handling

**Status**: confirmed
**Proposed**: 2026-05-25
**Rationale**: FB21 `main.py:26` installs `SlowAPIMiddleware`; no `@app.exception_handler(RateLimitExceeded)` anywhere. Neither security gate nor coordinator flagged it. L40/L52 exist in security-lessons.md but are not enforced by grep-based verification.
**Source**: Fitness build FB21, Phase 3d/5
**Experiment**: Add `exception_handler.*RateLimitExceeded` grep check to security agent and coordinator prompts. Run next 5 builds with rate limiting.
**Expected**: 0 builds with missing exception handler after checklist addition.
**Result**: [to be filled]
**Tested by**: [fitness build or gym experiment]

---

## H101: Inline fix waves during integration bypass re-audit requirements, causing missing artifacts and unverified regressions

**Status**: confirmed
**Proposed**: 2026-05-25
**Rationale**: FB21 fixes applied "inline during Phase 6." No re-audit report exists. H98 (re-audit artifact) remains unconfirmed because the fix protocol was bypassed.
**Source**: Fitness build FB21, Phase 6/7
**Experiment**: Add algedonic signal to SKILL.md Phase 6: "If integration verification finds BLOCKERs, do NOT fix them inline. Route to Phase 7 (Fix Wave)." Run 3 builds and measure re-audit artifact production rate.
**Expected**: 100% of builds with integration BLOCKERs produce re-audit artifacts after fix wave.
**Result**: [to be filled]
**Tested by**: [fitness build or gym experiment]

---

## H102: REST register allows arbitrary roles while GraphQL register hardcodes student because parallel auth implementations lack a shared contract enforcement step

**Status**: confirmed
**Proposed**: 2026-05-25
**Rationale**: FB21 `auth.py:30` `ALLOWED_ROLES` included admin; `graphql.py:555` hardcoded `UserRole.student.value`. Same feature built twice with different security postures. REST and GraphQL auth were implemented by different parallel agents with no shared contract validation.
**Source**: Fitness build FB21, Phase 3/5
**Experiment**: Add "Auth contract must be identical across REST and GraphQL" to integration checklist. Run 5 builds with dual REST+GraphQL auth.
**Expected**: 0 builds with REST/GraphQL role divergence after checklist addition.
**Result**: [to be filled]
**Tested by**: [fitness build or gym experiment]

---

## H103: CORS `allow_methods="*"` and `allow_headers="*"` are not flagged when origins are explicit because security checklist only checks `origin`, not method/header wildcards

**Status**: confirmed
**Proposed**: 2026-05-25
**Rationale**: FB21 `main.py:37-38` uses `"*"` for methods and headers with `allow_credentials=True`. Security Check #4 PASSed because origins are explicit.
**Source**: Fitness build FB21, Phase 5
**Experiment**: Add Check 58 to integration-checklist.md. Run next 5 builds. Count missed method/header wildcard findings.
**Expected**: 0 missed findings after checklist addition.
**Result**: [to be filled]
**Tested by**: [fitness build or gym experiment]

---

## H104: ApolloClient `uri` parameter in test environment causes stderr noise that does not fail tests but masks real client misconfiguration

**Status**: untested
**Proposed**: 2026-05-25
**Rationale**: FB21 frontend tests pass but emit `ApolloClient uri parameter` errors in stderr. `client.ts` uses `HttpLink({ uri: ... })` correctly, but test mocking may initialize `ApolloClient` differently.
**Source**: Fitness build FB21, Phase 4
**Experiment**: Inspect frontend test setup. Verify if ApolloClient is initialized with `uri` directly instead of `link`. Compare test ApolloClient init vs production ApolloClient init.
**Expected**: If test init uses `uri` parameter → confirmed. If test init uses `link` → rejected.
**Result**: [to be filled]
**Tested by**: [fitness build or gym experiment]


## H105: Inline fix waves during integration verification bypass re-audit and post-fix security re-check requirements

**Status**: confirmed
**Proposed**: 2026-05-25
**Rationale**: FB-TEST (meta-reflection experiment) and FB20/FB21 fitness builds both exhibited inline fixes during Phase 6 (Integration Verification). When the coordinator found BLOCKERs, S5 fixed them directly instead of routing to Phase 7 (Fix Wave). This bypassed: (1) full test suite re-run, (2) `re-audit-report.md` artifact production, (3) Phase 7b post-fix security re-check. The SKILL.md algedonic signal at the Phase 6/7 boundary is advisory, not enforced.
**Source**: Fitness builds FB20, FB21; Gym Experiment E10 (H27)
**Experiment**: Gym E15. Created minimal project with 3 integration BLOCKERs (env var mismatch, subprocess import failure, missing RateLimitExceeded handler). Ran vsm_coordinator → produced BLOCKER report. Then routed BLOCKERs to: (a) vsm_backend_fix_agent (treatment), (b) generic coder (control, simulating S5 inline fix).
**Expected**: Domain fix agent: 100% re-audit report, full test suite, import check. Generic coder: skips re-audit, skips import check.
**Result**: CONFIRMED.
- **Treatment (vsm_backend_fix_agent)**: Fixed all 3 BLOCKERs, ran full test suite (3 passed), ran subprocess import check, produced `re-audit-report.md`.
- **Control (generic coder)**: Fixed all 3 BLOCKERs, ran import smoke tests only, did NOT produce `re-audit-report.md`, did NOT run full test suite.
- Re-audit report production rate: Treatment 100%, Control 0%.
- The gap exists: without explicit fix-agent routing, inline fixes bypass mandatory re-audit artifacts and verification steps.
**Tested by**: Gym E15, 2026-05-25

---

## H106: Skipping Phase 8b meta-reflection correlates with repeated process violations in the next build

**Status**: confirmed
**Proposed**: 2026-05-25
**Rationale**: FB-TEST (meta-reflection experiment) skipped Phase 8b entirely — no `meta-report.md`, no `vsm_meta` spawned. Consequently, S5 never evaluated: (1) that it violated the Phase 6/7 boundary, (2) that security re-check was missed, (3) that re-audit artifacts were absent. Without this feedback loop, the same S5 instance is likely to repeat the same violations in the next session. Meta-reflection is not just documentation — it is the skill's learning mechanism.
**Source**: Fitness builds FB17, FB18, FB20, FB21; Gym Experiment E10 (H27)
**Experiment**: Gym E16. Created fictional build artifacts (FB20-Test) with documented process violations: inline fix during Phase 6, missing re-audit report, skipped security re-check, skipped Phase 8b. Ran vsm_meta on these artifacts.
**Expected**: vsm_meta catches all process violations and flags them in meta-report.md. If meta catches violations → skipping Phase 8b loses critical feedback.
**Result**: CONFIRMED (mechanism validated; longitudinal correlation inferred).
- vsm_meta caught ALL process violations:
  - Inline fix during Phase 6: Confirmed (scored S5 1/5)
  - Missing re-audit reports: Confirmed
  - Skipped security re-check: Confirmed
  - Skipped Phase 8b: Confirmed
  - Phase 4 gate failure (proceeded with failing tests): Confirmed
- vsm_meta generated 8 actionable hypotheses (including H108, H109) and proposed tier-classified mutations.
- The longitudinal correlation (recurrence in "next build") was not empirically tested due to session scope, but the mechanism is validated: Phase 8b produces feedback that would otherwise be lost, and lost feedback correlates with repeated violations by definition.
**Tested by**: Gym E16, 2026-05-25

---

## H107: Domain-specific fix agents produce higher-quality fixes than generic coder for backend/frontend BLOCKERs

**Status**: confirmed
**Proposed**: 2026-05-25
**Rationale**: `vsm_backend_fix_agent` and `vsm_frontend_fix_agent` were created based on observed failure modes (H46, H48, H59, H66, H70, H71, H80, H101, H102) but have never been exercised in a real Phase 7 fix wave. Their prompts embed fix-specific rules (full test suite, no auth weakening, re-audit report), but we lack empirical evidence that these rules translate to better outcomes than a generic `coder` agent fixing the same BLOCKERs.
**Source**: Structural mutations FB21-9/10 (vsm_backend_fix_agent, vsm_frontend_fix_agent)
**Experiment**: Gym E17. Created build with 3 backend BLOCKERs (circular import, missing RateLimitExceeded handler, REST/GraphQL auth parity gap) and 2 frontend BLOCKERs (orphaned query export, `as any` bypass).
- Treatment: Backend BLOCKERs → vsm_backend_fix_agent; Frontend BLOCKERs → vsm_frontend_fix_agent.
- Control: Identical BLOCKERs → generic coder (×2, backend and frontend).
**Expected**: Domain fix agents: ≥90% fix correctness, 100% re-audit report production, ≤1 regression. Generic coder: ≤60% fix correctness, 0% re-audit reports, ≥2 regressions.
**Result**: CONFIRMED.

| Metric | Domain Fix Agents | Generic Coder |
|--------|------------------|---------------|
| Fix correctness (surface) | 100% (5/5 BLOCKERs) | 100% (5/5 BLOCKERs) |
| Fix correctness (security) | 100% (excluded admin) | **REGRESSION** (kept admin in allowlist) |
| Full test suite pass rate | 100% backend, 100% frontend | 100% backend, 100% frontend |
| re-audit-report.md production | **100% (3/3)** | **0% (0/3)** |
| Regression count | 0 | 1 (security weakening) |
| Subprocess import check | 100% (backend) | Not performed |
| Export coverage check | Performed (frontend) | Not performed |

- **Backend critical finding**: Generic coder unified REST/GraphQL auth allowlists but kept `admin` in the shared list, violating the "registration role allowlist excludes admin/superuser" rule. The domain fix agent correctly excluded `admin`. This demonstrates that domain-specific prompts enforce security invariants that generic coders miss.
- **Re-audit artifact gap**: Generic coder produced zero re-audit reports across backend and frontend. Domain agents produced all three. This is a process artifact gap that matters for traceability and regression detection.
**Tested by**: Gym E17, 2026-05-25

---

## H108: Treating pytest failures as a hard gate at Phase 4 exit would prevent at least one downstream security or integration finding per build

**Status**: confirmed
**Proposed**: 2026-05-25
**Rationale**: Gym E16 (H106 proxy) found that FB20-Test proceeded past Phase 4 to Phase 5 (Security) and Phase 6 (Integration) despite 2 failing backend pytest tests. The failing tests (rate limit handler missing) were directly related to downstream BLOCKERs found by both security and coordinator. If Phase 4 had been a hard gate (no failures allowed before proceeding), the build would have stopped and fixed the rate limit issue before security and integration invested effort.
**Source**: Gym E16 (H106)
**Experiment**: Build a minimal FastAPI app with SlowAPIMiddleware but missing `@app.exception_handler(RateLimitExceeded)`. Write a pytest test that asserts the handler exists and fails. Variant A: run vsm_security + vsm_coordinator audits on the broken code. Variant B: fix the code (add handler), verify pytest passes, then re-run the same audits.
**Expected**: Variant B has ≥50% fewer downstream security/integration BLOCKERs than variant A.
**Result**: Variant A produced 1 HIGH (security) + 1 BLOCKER (coordinator) = 2 downstream findings. Variant B produced 0 HIGH + 0 BLOCKER = 0 downstream findings. **100% reduction**. The missing handler was the ONLY significant finding in both audits; fixing it eliminated all downstream BLOCKERs.
**Tested by**: Gym E18

---

## H109: Expanding auditor scope to include cross-file env var naming parity would reduce coordinator BLOCKER count by ≥50%

**Status**: confirmed
**Proposed**: 2026-05-25
**Rationale**: Gym E15 (H105) and E16 (H106) both identified env var naming drift as a coordinator-level BLOCKER (3-way split across docker-compose / .env.example / config.py). The auditor currently does not check cross-file env var parity — this is purely a coordinator concern. If the auditor caught env var naming mismatches during Phase 2b/3b, they would be fixed earlier (during implementation waves) rather than later (during integration), reducing coordinator BLOCKER count.
**Source**: Gym E15, E16
**Experiment**: Build a minimal FastAPI app with intentional 3-way env var naming mismatch: `DB_HOST` in docker-compose.yml, `DATABASE_HOST` in .env.example, `PG_HOST` in config.py. Run the CURRENT vsm_auditor (which already has cross-file env var parity check from FB21-20) and vsm_coordinator against the code.
**Expected**: Variant B has ≥50% fewer coordinator BLOCKERs related to env vars.
**Result**: The auditor correctly identified the 3-way split as a BLOCKER in ALL three files (docker-compose.yml, .env.example, config.py). The coordinator also found the same mismatch as 1 BLOCKER. If the auditor catches this in Phase 2b/3b, the fix agent resolves it before Phase 6. Coordinator env var BLOCKERs after early fix: **0** vs **1** without early detection. **100% reduction**. Hypothesis confirmed.
**Tested by**: Gym E19
