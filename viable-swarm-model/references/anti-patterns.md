# Anti-Pattern Registry

> **Mutation rules**: Append new anti-patterns with full what/when/prevention.
> Mark false positives with `~~strikethrough~~` and empirical rationale.
> Never delete — the history of what was tried and rejected is valuable.

---

## Security Anti-Patterns

### 1. Hardcoded secrets
**What**: Default secret values in config files (e.g., `JWT_SECRET = "dev-secret"`).  
**When**: Developer uses placeholder secrets for local development that survive to production.  
**Prevention**: Required env vars, min 32 chars, app refuses to start without. No defaults.

### 2. `||` fallback for secrets
**What**: `process.env.JWT_SECRET || 'jwt_secret'` silently bypasses required-secret checks.  
**When**: Developer thinks fallback is "convenient for local dev."  
**Prevention**: Explicit validation, `process.exit(1)` if missing. Ban `||` for SECRET/KEY/PASSWORD/TOKEN.

### 3. Fake JWT parsers for development
**What**: Base64-decode without signature verification, generate random UUID on failure.  
**When**: "Temporary" bypass for easier local testing.  
**Prevention**: jsonwebtoken::decode with HMAC-SHA256, no bypass path, app panics at startup if JWT_SECRET missing.

### 4. CORS wildcard with credentials
**What**: `origin: "*"` or `origin: true` with `credentials: true`.  
**When**: Developer enables CORS broadly to "fix" a frontend connection issue.  
**Prevention**: Explicit allowlist from config. Functionally identical to wildcard.

### 5. JWT in WebSocket URL
**What**: `?token=...` in WebSocket URL leaks to logs/history/Referer.  
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
**When**: Developer prefers graceful degradation over explicit failures.  
**Prevention**: Raise HTTPException on failure, never return None for auth context.

### 11. Frontend API URL localhost fallback
**What**: `|| 'http://localhost:8000'` silently routes API calls to localhost in production.  
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
**Prevention**: Parallelize aggressively, max 5 per wave.

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
**What**: Sub-orchestrators for <10 agent swarms.  
**When**: Over-application of VSM recursion.  
**Prevention**: Main agent handles directly up to 10 agents.

### 28. Not reading outputs between waves
**What**: Dispatching Wave N+1 before Wave N outputs ready.  
**When**: Orchestrator skips verification checklist.  
**Prevention**: Wave Verification Checklist after every wave.

### 29. S1 proliferation
**What**: More S1 agents than task justifies.  
**When**: Orchestrator thinks more agents = faster.  
**Prevention**: Prefer 3-5 focused agents over 10+ general ones.

### 30. Ignoring algedonic signals
**What**: Suppressing pain signals.  
**When**: Orchestrator wants to maintain momentum.  
**Prevention**: Always investigate. CRITICAL bypasses to S5.

### 31. Skipping learning phase
**What**: Not running Phase 5 (reflection).  
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
**Prevention**: >3 agents or >3 tightly-coupled files → consider recursion.

### 35. Spawning S2/S3 for small sessions
**What**: Standalone Coordination/Control agents for <10 agents.  
**When**: Over-formal application of VSM.  
**Prevention**: Main agent performs S2/S3 directly for small sessions.

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

### 38. Storing passwords in plaintext or with weak hashing
**What**: MD5/SHA1 for passwords.  
**When**: Legacy code or inexperienced developer.  
**Prevention**: bcrypt, strong JWT secrets, HTTPS, httpOnly cookies.

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

### 44. Docker-Compose Default-Value Fallbacks Embedding Secrets
**What**: `docker-compose.yml` uses `${DATABASE_URL:-postgresql://user:pass@db/db}` or `POSTGRES_PASSWORD: geoquiz` as defaults.  
**When**: Developer adds fallbacks to make local dev easier.  
**Prevention**: Ban `:-` fallbacks in docker-compose entirely. Use `.env` files for local dev. Services must fail to start if required vars are missing. Grep for `:-` in docker-compose as a BLOCKER.  
**Affected**: S1-DevOps, vsm_security.

### 45. SQLAlchemy Column Names Shadowing Imported Functions
**What**: A model column named `text` shadows `sqlalchemy.text`, causing `TypeError` at import time.  
**When**: Model designer chooses intuitive column names without checking SQLAlchemy imports.  
**Prevention**: Alias SQLAlchemy imports in model files (`sa_text`, `sa_select`). Add this to foundation wave checklist for SQLAlchemy projects.  
**Affected**: S1-Backend, vsm_auditor.
