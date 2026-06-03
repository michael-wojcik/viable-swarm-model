# Anti-Pattern Registry

> **Mutation rules**: Append new anti-patterns with full what/when/prevention.
> Mark false positives with `~~strikethrough~~` and empirical rationale.
> Never delete — the history of what was tried and rejected is valuable.
>
> **See also**: `references/security-lessons.md` for prevention rules by topic,
> `references/pattern-library.md` for proven solutions.

---

## Security Anti-Patterns

### 1. Hardcoded secrets
**What**: Default secret values in config files (e.g., `JWT_SECRET = "dev-secret"`).  
**When**: Developer uses placeholder secrets for local development that survive to production.  
**Prevention**: Required env vars, min 32 chars, app refuses to start without. No defaults.  
**See also**: `security-lessons.md` L11 (Hardcoded Secrets are the #1 Critical Finding)

### 2. `||` fallback for secrets
**What**: `process.env.JWT_SECRET || 'jwt_secret'` silently bypasses required-secret checks.  
**When**: Developer thinks fallback is "convenient for local dev."  
**Prevention**: Explicit validation, `process.exit(1)` if missing. Ban `||` for SECRET/KEY/PASSWORD/TOKEN.

### 3. Fake JWT parsers for development
**What**: Base64-decode without signature verification, generate random UUID on failure.
**See also**: `security-lessons.md` L18, L28  
**When**: "Temporary" bypass for easier local testing.  
**Prevention**: jsonwebtoken::decode with HMAC-SHA256, no bypass path, app panics at startup if JWT_SECRET missing.

### 4. CORS wildcard with credentials
**What**: `origin: "*"` or `origin: true` with `credentials: true`.
**See also**: `security-lessons.md` L61  
**When**: Developer enables CORS broadly to "fix" a frontend connection issue.  
**Prevention**: Explicit allowlist from config. Functionally identical to wildcard.

### 5. JWT in WebSocket URL
**What**: `?token=...` in WebSocket URL leaks to logs/history/Referer.
**See also**: `security-lessons.md` L16  
**When**: Developer passes auth the easiest way they can find.  
**Prevention**: In-band auth as first message after connection.

### 6. Document ownership filtering missing
**What**: List endpoints return ALL records without user-scoped filters.  
**When**: CRUD scaffold generated without auth integration.  
**Prevention**: Security + auditor both check ownership filtering on every list endpoint.

### 7. Game API returns answers
**What**: Public endpoints return correct_answer_index or solution data.  
**When**: Same DTO used for admin and player endpoints.  
**Prevention**: Public DTO omitting answer fields.

### 8. GraphQL without depth limiting
**What**: No @graphql-depth-limit or complexity analysis installed.  
**When**: GraphQL API built without security review.  
**Prevention**: Depth limit max 10 + complexity analysis.

### 9. Passwords in plaintext or weak hashing
**What**: MD5/SHA1 for passwords, or stored plaintext.  
**When**: Developer underestimates password security importance.  
**Prevention**: bcrypt via passlib, HTTPS, httpOnly cookies for refresh tokens.

### 10. Auth middleware returns None
**What**: Silent failure disables security controls. `get_organization_id()` returned None on failure.
**See also**: `security-lessons.md` L36  
**When**: Developer prefers graceful degradation over explicit failures.  
**Prevention**: Raise HTTPException on failure, never return None for auth context.

### 11. Frontend API URL localhost fallback
**What**: `|| 'http://localhost:8000'` silently routes API calls to localhost in production.
**See also**: `security-lessons.md` L62  
**When**: Developer adds fallback to make local dev easier.  
**Prevention**: Fail-fast throw Error if VITE_API_URL missing.

---

## Integration Anti-Patterns

### 12. Celery task name mismatch
**What**: Different conventions per service ("docuflow.processor.*" vs "processor.*").  
**When**: Services built by different agents without contract validation.  
**Prevention**: Coordinator validates task names, signatures, routing.

### 13. Processor model drift
**What**: Each service defines own models with different column names (sp_o2 vs spO2).  
**When**: Shared schema not enforced across services.  
**Prevention**: Shared models package or coordinator validation.

### 14. Bug propagation across files
**What**: Same bug pattern in multiple files, fix wave only fixes one.  
**When**: Field mapping bug exists in 3 files, agent only sees one.  
**Prevention**: After fixing, grep same pattern across ALL files.

### 15. Prisma relation name mismatch
**What**: `@relation("Requester")` vs `@relation("Follower")`.  
**When**: Schema written by different agents or in different waves.  
**Prevention**: Coordinator validates relation names match on both sides.

### 16. Standalone worker imported as library
**What**: Service structured as worker but imported directly. MODULE_NOT_FOUND crash.  
**When**: Backend tries to reuse worker code via import.  
**Prevention**: Communication via DB or API, never direct import.

### 17. Environment variable naming drift
**What**: docker-compose sets `POLL_INTERVAL_MS` but code reads `POLL_MS`.  
**When**: Config and code written separately.  
**Prevention**: Coordinator validates env var names match across docker-compose/.env/code.

### 18. Orphaned utility code
**What**: S1 agents create shared utilities but consumer files never import them.  
**When**: Agent writes utility assuming another agent will use it.  
**Prevention**: S1 agents verify exports are consumed; S2 verifies wiring.

### 19. Duplicate imports (Rust)
**What**: Mixing `use crate_name::mod::Item` and `use mod::Item` in same file.  
**When**: Code written by agent unfamiliar with Rust workspace conventions.  
**Prevention**: Choose ONE style per file. main.rs imports ONLY from library path.

### 20. Frontend wrong relative path to shared
**What**: Using `../shared/` instead of `../../shared/` in monorepos.  
**When**: Agent copies path from one file to another without checking depth.  
**Prevention**: Verify with grep. Prefer Vite path aliases.

### 21. Missing Cell import (React)
**What**: Copy-paste from docs without checking.  
**When**: Agent copies example code incompletely.  
**Prevention**: Code review catches. Build verification.

---

## Process Anti-Patterns

### 22. Sequential everything
**What**: Dispatching one agent at a time wastes swarm power.  
**When**: Orchestrator unsure about dependencies.  
**Prevention**: Parallelize aggressively.

### 23. Vague prompts
**What**: Prompts without specific input/output file paths.  
**When**: Orchestrator rushes to dispatch without planning.  
**Prevention**: Every prompt has Input/Output/CRITICAL sections with exact paths.

### 24. No shared workspace
**What**: Agents produce output in wrong locations.  
**When**: Project structure not established before dispatch.  
**Prevention**: Establish shared workspace with exact paths.

### 25. Skipping review
**What**: Never deliver without audit pass.  
**When**: Time pressure or overconfidence.  
**Prevention**: Dispatch reviewers in parallel with next build wave.

### 26. Agents as documentation generators
**What**: Agents write process docs instead of code.  
**When**: Agent confused about its role.  
**Prevention**: 80/20 rule — 80% code/configs, 20% docs max.

### 27. Nested orchestration for simple tasks
**What**: Sub-orchestrators for small agent swarms.  
**When**: Over-application of VSM recursion.  
**Prevention**: Main agent handles directly; use sub-orchestrators only when recursion is warranted.

### 28. Not reading outputs between waves
**What**: Dispatching Wave N+1 before Wave N outputs ready.  
**When**: Orchestrator skips verification checklist.  
**Prevention**: Wave Verification Checklist after every wave.

### 29. S1 proliferation
**What**: More S1 agents than task justifies.  
**When**: Orchestrator thinks more agents = faster.  
**Prevention**: Prefer focused agents over general ones.

### 30. Ignoring algedonic signals
**What**: Suppressing pain signals.  
**When**: Orchestrator wants to maintain momentum.  
**Prevention**: Always investigate. CRITICAL bypasses to S5.

### 31. Skipping learning phase
**What**: Not running Phase 8 (reflection).  
**When**: Session declared "done" after delivery.  
**Prevention**: Session is NOT COMPLETE without learning.

### 32. Ignoring loaded session memory
**What**: Memory exists but not applied.  
**When**: Orchestrator forgets to read `.kimi/lessons.md`.  
**Prevention**: Memory check is FIRST action. Algedonic PAIN if ignored.

### 33. Session context loss destroys files
**What**: Continued sessions lose sub-agent file writes.  
**When**: `--continue` used but file state not verified.  
**Prevention**: Verify expected files exist at start of continued session.

### 34. Flat-only structure
**What**: Not using recursion when warranted.  
**When**: Complex subsystem built by generalists instead of specialists.  
**Prevention**: Many agents or many tightly-coupled files → consider recursion.

### 35. Spawning S2/S3 for small sessions
**What**: Standalone Coordination/Control agents for small sessions.  
**When**: Over-formal application of VSM.  
**Prevention**: Main agent performs S2/S3 directly when the task does not warrant standalone agents.

### 36. Using unmaintained react-beautiful-dnd
**What**: Unmaintained since 2022, critical React 18 bugs.  
**When**: Developer copies old tutorial.  
**Prevention**: Use `@hello-pangea/dnd` (community fork, drop-in replacement).

### 37. Flooding awareness updates without debouncing
**What**: mousemove events saturate network.  
**When**: Real-time cursor sharing or presence implemented naively.  
**Prevention**: Debounce to 10/sec max, deduplicate unchanged payloads, clear on mouse leave.

---

## Data/Architecture Anti-Patterns

### 39. Frontend components without project scaffolding
**What**: Config files forgotten when scope split across agents.  
**When**: Multiple agents each assume another handled config.  
**Prevention**: Active creation requirement + Phase 4 verification.

---

## Additional Anti-Patterns (Discovered in Field)

### 40. Synchronous file I/O in request handlers
**What**: `fs.readFileSync()` or equivalent blocks the event loop.  
**When**: Developer uses sync API for convenience.  
**Prevention**: Use async I/O or worker threads in request handlers.

### 41. Missing request payload validation
**What**: API endpoints accept arbitrary JSON without schema validation.  
**When**: Developer trusts client input.  
**Prevention**: Zod/Joi/class-validator on ALL inputs. Fail closed.

### 42. Fix Agent False Positive Claims
**What**: Fix agent reports "fixed" but the code change does not actually resolve the issue.  
**When**: Agent misreads code, applies change to wrong location, or claims success before verification.  
**Prevention**: Require fix agents to run a verification shell command (e.g., `grep`) before reporting completion. Example: FB1 Fix Wave 2 claimed Yjs token in URL path but token was still passed as `room` parameter.  
**Affected**: vsm_fix agents, S1 coders in Phase 7.

### 43. Parallel Agents Overwriting Shared Entry Points
**What**: Multiple implementation agents modify the same entry-point file (main.py, App.tsx). Later agent overwrites earlier agent's imports/registrations.  
**When**: Backend and worker agents both wire routers into `main.py`.  
**Prevention**: Either (a) serialize entry-point wiring to a single agent, or (b) have a dedicated "wiring" agent run after all implementation agents.  
**Affected**: S1 coders in Phase 3.
**See also**: Pattern #22 (Foundation Wave Sequencing) for the broader parallel-agent coordination strategy; Mutation 52 (`agents/vsm_wiring.md`) for the dedicated wiring agent solution.

### 44. Docker-Compose Default-Value Fallbacks Embedding Secrets
**What**: `docker-compose.yml` uses `${DATABASE_URL:-postgresql://user:pass@db/db}` or `POSTGRES_PASSWORD: geoquiz` as defaults.
**See also**: `security-lessons.md` L37  
**When**: Developer adds fallbacks to make local dev easier.  
**Prevention**: Ban `:-` fallbacks in docker-compose entirely. Use `.env` files for local dev. Services must fail to start if required vars are missing. Grep for `:-` in docker-compose as a BLOCKER.  
**Affected**: S1-DevOps, vsm_security.

### 45. SQLAlchemy Column Names Shadowing Imported Functions
**What**: A model column named `text` shadows `sqlalchemy.text`, causing `TypeError` at import time.  
**When**: Model designer chooses intuitive column names without checking SQLAlchemy imports.  
**Prevention**: Alias SQLAlchemy imports in model files (`sa_text`, `sa_select`). Add this to foundation wave checklist for SQLAlchemy projects.  
**Affected**: S1-Backend, vsm_auditor.

### 46. Module-Level Pydantic Settings Instantiation
**What**: `settings = Settings()` at module scope crashes on import when env vars are missing.  
**When**: Developer follows Pydantic docs example without considering testability.  
**Prevention**: Use lazy factory (`get_settings()`) or dependency injection. Never instantiate at module level. This prevents test discovery, CI execution, and agent-based testing.  
**Example**: FB3 `backend/app/config.py` had `settings = Settings()` at bottom. Tester agent could not import any backend module for 1800s until timeout.  
**Affected**: S1-Backend, vsm_tester, vsm_auditor.

### 47. JWT Signature Verification Bypass
**What**: A `decode_token` helper or similar function uses `jwt.decode(token, options={"verify_signature": False}, ...)`
**See also**: `security-lessons.md` L28 (JWT Signature Verification is Non-Negotiable) to "conveniently" read the payload without verifying the signature.  
**When**: Developer thinks they need to decode the token in a context where the secret is "unavailable" (e.g., WebSocket auth, logging, debugging).  
**Prevention**: NEVER disable JWT signature verification. If the secret is needed, pass it explicitly. Ban any function that sets `verify_signature=False`. The security gate must flag this as CRITICAL.

## Implementation Anti-Patterns

### Anti-Pattern #50: Module-Level Engine Instantiation
**What**: `engine = create_async_engine(get_settings().DATABASE_URL)` at module level in `models.py`.  
**When**: Agent doesn't know how to create a lazy factory and defaults to the simplest pattern.  
**Prevention**: models.py MUST use `_get_async_engine()` lazy factory or similar. Auditor must flag module-level engine as BLOCKER.

**Source**: FB15 foundation agent reverted to module-level engine despite FB14 prevention rule (H65)

### Anti-Pattern #51: `as any` Type Safety Bypass
**What**: Using `as any` to destructure fields that don't exist in the type definition.  
**When**: Frontend agent needs a field that wasn't created in the store/schema and uses `as any` to silence TypeScript instead of fixing the source.  
**Prevention**: Frontend import check (`tsc --noEmit`) must be combined with an explicit scan for `as any` casts. Any `as any` that masks a missing field is a BLOCKER.

**Source**: FB15 frontend agent used `useEventStore() as any` to access missing `salesMetrics` (H71)

### Anti-Pattern #52: GraphQL queries.ts Orphaned Exports
**What**: `queries.ts` contains well-formed GraphQL queries with correct camelCase field names, but NO page or component imports them. The queries are dead code.
**When**: Frontend agent introspects the schema and writes queries correctly, but page components independently use REST `fetch()` instead.
**Prevention**: Integration checklist must verify every export from `queries.ts` is imported by at least one consumer. If queries are orphaned, either migrate pages to Apollo Client or remove the GraphQL layer.
**Affected**: S1-Frontend, vsm_coordinator.
**Source**: FB17 queries.ts had correct introspected field names but was never imported by any page (H84)

### Anti-Pattern #53: Apollo Client Initialized but Unused
**What**: `main.tsx` wraps the app in `ApolloProvider` with a configured `apolloClient`, but ALL page components use REST `fetch()` for data fetching. The GraphQL infrastructure is initialized but never exercised.
**When**: Frontend agents default to REST when both REST and GraphQL are available, or they don't know which data-fetching pattern to prefer.
**Prevention**: Frontend agent prompt must state: "When GraphQL is available, use Apollo Client `useQuery` / `useMutation` for data fetching. REST `fetch()` is reserved for file uploads and auth endpoints." Integration checklist verifies Apollo Client is actually used.
**Affected**: S1-Frontend, vsm_coordinator.
**Source**: FB17 frontend had ApolloProvider but zero Apollo usage across 10 pages (H84)

### Anti-Pattern #54: api-spec.md Ambiguous RBAC Labels
**What**: api-spec.md uses natural-language labels like "(owner-filtered)" or "(public)" instead of explicit `RBAC: [roles]` arrays. Different agents interpret these labels differently.
**When**: Architect writes concise endpoint descriptions without formalizing access control. Downstream implementation agents (REST routers, GraphQL resolvers) make inconsistent assumptions.
**Prevention**: Architect prompt must require explicit `RBAC: [roles]` arrays for every endpoint. Security gate must flag ambiguous labels as HIGH. Integration checklist verifies GraphQL resolvers match the explicit RBAC arrays.
**Affected**: vsm_architect, S1-Backend, vsm_security, vsm_coordinator.
**Source**: FB17 "(owner-filtered)" label caused GraphQL RBAC parity gap between REST and GraphQL (H83)

### Anti-Pattern #55: Frontend Import Path Guessing
**What**: Frontend agent writes relative imports (`../shared/types`) without checking `tsconfig.json` `paths` or `vite.config.ts` aliases. The import fails at build time because the alias is different (e.g., `@flux/shared/types`).
**When**: Agent assumes relative paths work in all project configurations, or copies import patterns from previous builds without verifying the current project's alias setup.
**Prevention**: Frontend foundation agent MUST read `tsconfig.json` and `vite.config.ts` before writing ANY import statement. Use the project's configured alias, not relative paths, for shared types and cross-package imports.
**Affected**: S1-Frontend, foundation wave agents.
**Source**: FB17 frontend agent wrote `../shared/types` but tsconfig.json alias was `@flux/shared/types` (H80)

### Anti-Pattern #56: S5 Inline Fix During Integration Verification
**What**: S5 fixes coordinator BLOCKERs directly during Phase 6 (Integration Verification) instead of routing to Phase 7 (Fix Wave).
**See also**: `security-lessons.md` L67 This bypasses: (1) full test suite re-run, (2) `re-audit-report.md` artifact production, (3) Phase 7b post-fix security re-check.
**When**: Coordinator finds BLOCKERs; S5 interprets them as "quick fixes" and applies them immediately to keep the build moving. The algedonic signal at the Phase 6/7 boundary is advisory, not enforced.
**Prevention**: Coordinator output template MUST include a mandatory footer: "If BLOCKERs exist, route to Phase 7. Do NOT fix inline." SKILL.md Phase 4 must be a hard gate (zero test failures before Phase 5/6). S5 must treat integration BLOCKERs as Phase 7 spawn triggers, not inline to-do items.
**Affected**: S5 (main agent), vsm_coordinator.
**Source**: Gym E15 (H105), FB20/FB21 fitness builds.

### Anti-Pattern #57: `strawberry_sqlalchemy_mapper` and Other Non-Existent Package Imports
**What**: Agent imports a package name that sounds plausible (`strawberry_sqlalchemy_mapper`, `sqlalchemy_strawberry`, `fastapi_graphql_auto`) but is not in `requirements.txt` and may not even exist on PyPI. The agent then enters an infinite loop trying to verify the import in a subprocess.
**When**: Developer (or agent) assumes a popular framework must have an "official" ORM mapper plugin and imports it without checking. In FB22, this consumed ~15 minutes of agent time before S5 killed the task.
**Prevention**: Dependency Verification BLOCKER (vsm_backend_coder gotcha #14). Before importing ANY third-party package not already used in the codebase, verify it is listed in `requirements.txt`. If the package is NOT listed, STOP and use standard library/framework types instead.
**Affected**: `vsm_backend_coder`, S1 backend agents, `vsm_auditor`.
**Source**: FB22 `graphql.py` agent imported `from strawberry_sqlalchemy_mapper import StrawberrySQLAlchemyMapper` (H150).

### Anti-Pattern #58: Vite Alias Key `"@/"` with Trailing Slash
**What**: `vite.config.ts` uses `"@/"` as the alias key instead of `"@"`. Development builds work because Vite's dev server is lenient, but production builds fail because Rollup does not match the trailing slash.
**When**: Developer copies an alias pattern from a different project or tutorial without checking Vite/Rollup resolution semantics.
**Prevention**: Vite Alias Key BLOCKER (vsm_frontend_coder gotcha #8). The alias key MUST be `"@"` mapping to `path.resolve(__dirname, "./src")`. The alias `"@/"` mapping to `./src/` is a BLOCKER.
**Affected**: `vsm_frontend_coder`, S1 frontend agents.
**Source**: FB22 `vite.config.ts` used `"@/"` → `./src/`; `npm run build` failed with Rollup resolution error (H153).

### Anti-Pattern #59: Invoking `/flow:viable-swarm-model` Without `--agent-file`

**What**: The user launches Kimi CLI with the default agent and types `/flow:viable-swarm-model`. The skill loads, S5 begins Phase 0, and eventually calls `Agent(subagent_type="vsm_architect")`. The call fails because custom subagent types are only available when `--agent-file agents/vsm-main.yaml` was used at launch.
**When**: User forgets the `--agent-file` flag, or launches a new session without it, or resumes a session that was started with the default agent.
**Prevention**: Phase 0 step 6b smoke test. Before dispatching any implementation agents, spawn a trivial `vsm_meta` subagent. If it fails with unknown subagent type, STOP and emit algedonic with the correct launch command.
**Affected**: S5 (main agent), all builds.
**Source**: Custom agent file migration (2026-05-26).
