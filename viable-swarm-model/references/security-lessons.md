# Security Lessons — Prevention Rule Format

> **Mutation rules**: Append new lessons as they are discovered. Mark lessons
> that are consistently false positives with `~~strikethrough~~` and rationale.
> If a prevention rule is proven ineffective after 3+ sessions, append a
> correction rather than deleting. The history of what was tried matters.

All 37 empirical lessons from cybernetic-dev-swarm, organized as prevention
rules for agent prompts. Each lesson: category, prevention rule, affected
agents.

---

## Core Workflow Lessons

### L1: Agent Prompts Need Read-Before-Write Enforcement
**Prevention rule**: Add "Read all input files BEFORE writing any code" to
every agent prompt. Without this, agents guess at interfaces rather than
reading the spec.
**Affected**: All S1 agents, vsm_architect.

### L2: Fix Wave Protocol Essential
**Prevention rule**: Phase 7 exists with fix task template, file-conflict
detection, re-audit protocol. Orchestrator must not invent fix flow ad-hoc.
**Affected**: S3 (main agent), vsm_auditor.

### L3: Internal Framework Must Stay Internal
**Prevention rule**: "NEVER output VSM diagrams to the user." 80/20 rule:
80% code/configs, 20% process docs max. Users get software, VSM stays in
agent context.
**Affected**: All agents.

### L4: Coordinator Essential for Multi-Service
**Prevention rule**: Any project with >1 service MUST spawn vsm_coordinator
after implementation wave. Without it, solver->API integration mismatches go
undetected.
**Affected**: S3 (main agent).

### L6: 5 Parallel Agents is Practical Maximum
**Prevention rule**: Wave size ≤5 agents. Beyond 5: use recursive sub-VSMs.
Orchestrator bandwidth is the limiting factor.
**Affected**: S3 (main agent).

### L7: Gather vs. Stop for Security Findings
**Prevention rule**: Default: planned quality wave → gather all findings then
fix. Mid-build discovery → emergency stop. Never mix the two modes.
**Affected**: S3 (main agent), vsm_security.

### L10: Re-audit After Fixes is Mandatory
**Prevention rule**: Always re-audit fixed files. Exit criteria uses re-audit,
not original audit report. Stale reports mislead.
**Affected**: S3 (main agent), vsm_auditor.

### L12: Tester Bug-Fix Inline is Highly Valued
**Prevention rule**: vsm_tester prompt includes: "Fix bugs inline during test
writing. Document each under 'Bugs Found and Fixed'."
**Affected**: vsm_tester.

### L13: Filesystem is the Only Reliable Communication Channel
**Prevention rule**: Every prompt has explicit Input/Output/CRITICAL sections
with exact file paths. Agents cannot see each other's task results.
**Affected**: S3 (main agent).

### L14: Status Reports are Orchestrator's Lifeline
**Prevention rule**: With 5+ parallel agents, require status reports. This is
the only way to track what happened without reading every output file.
**Affected**: All S1 agents.

### L15: Wave Verification Checklist Prevents Blind Dispatch
**Prevention rule**: Run wave verification checklist after every wave before
dispatching next wave.
**Affected**: S3 (main agent).

---

## Security Lessons (Critical)

### L5: Security Engineer Non-Negotiable for Production
**Prevention rule**: Always spawn vsm_security before delivery. Without it,
CORS reflection attacks, hardcoded secrets, SSRF go undetected.
**Affected**: S3 (main agent).

### L11: Hardcoded Secrets are the #1 Critical Finding
**Prevention rule**: JWT_SECRET required (no default), minimum 32 chars, app
refuses to start without it. Ban default secret values in ALL config.
**Affected**: All S1 agents, vsm_security.

### L16: WebSocket Auth Must Be In-Band, Never in URL
**Prevention rule**: Frontend sends auth as first WS message after connection:
`{"msg_type":"auth","token":"..."}`. NEVER `?token=...` in WebSocket URL.
**Affected**: S1-Backend, S1-Frontend, vsm_security.

### L18: Fake JWT Parsers for Development Are Never Removed
**Prevention rule**: Complete rewrite with proper library (jsonwebtoken::decode,
HMAC-SHA256). No bypass path. App panics at startup if JWT_SECRET missing.
**Affected**: S1-Backend, vsm_security.

### L27: || Fallback for Secrets is as Dangerous as Hardcoding
**Prevention rule**: `if (!process.env.JWT_SECRET) { process.exit(1) }`.
Never use `||` for SECRET/KEY/PASSWORD/TOKEN vars.
**Affected**: All S1 agents, vsm_security.

### L28: CORS origin: true is Equivalent to Wildcard
**Prevention rule**: Explicit allowlist from config. Never `origin: true` or
`origin: "*"` with `credentials: true`.
**Affected**: S1-Backend, vsm_security.

### L33: SSE JWT in URL is Unavoidable Architectural Vulnerability
**Prevention rule**: Short-lived SSE token exchange. Client POSTs JWT to
`/auth/sse-token` → receives 5-minute token → connects with `?sse_token=...`.
**Affected**: S1-Backend, S1-Frontend, vsm_security.

### L36: Silent None Returns in Middleware Bypass Security Controls
**Prevention rule**: Auth middleware raises HTTPException on failure. Never
return None for auth context.
**Affected**: S1-Backend, vsm_security.

### L9: Document Ownership Filtering Easy to Miss
**Prevention rule**: Security + auditor both check ownership filtering on every
list endpoint. List endpoints must return ONLY records belonging to the
authenticated user/organization.
**Affected**: S1-Backend, vsm_security, vsm_auditor.

### L19: Game API Answer Exposure Enables Cheating
**Prevention rule**: Public DTOs omit `correct_answer_index` and solution
fields. Never expose answers in public endpoints.
**Affected**: S1-Backend, vsm_security.

### L25: GraphQL Depth Limiting is Essential
**Prevention rule**: Install @graphql-depth-limit (max 10) + complexity analysis.
Deeply nested queries can cause DoS.
**Affected**: S1-Backend, vsm_security.

### L34: N+1 Queries in Computed Field Loops
**Prevention rule**: Batched GROUP BY queries for all computed fields (COUNT,
SUM) in list endpoints. Existing prevention focuses on ORM relationship loading
(selectinload) but NOT computed field queries.
**Affected**: S1-Backend, vsm_auditor.

### L35: O(n) Patterns in Auth Flows are Scalability Time Bombs
**Prevention rule**: Use indexed queries for token lookups. Password reset
token lookup must use indexed JSONB query with GIN index, not `select().all()`
followed by Python iteration.
**Affected**: S1-Backend, vsm_security.

---

## Integration Lessons

### L8: Multi-Service Projects Need Explicit Contract Validation
**Prevention rule**: vsm_coordinator validates Celery task names, signatures,
routing across all services. Silent mismatches cause all async ops to fail.
**Affected**: vsm_coordinator.

### L17: Frontend/Backend Auth Changes Must Be Coordinated
**Prevention rule**: Both sides must change simultaneously. vsm_coordinator
checks WebSocket auth contract matches on both sides.
**Affected**: vsm_coordinator.

### L23: Processor Model Drift Between Services
**Prevention rule**: Shared models package or vsm_coordinator validation of
column names. Alert processor had `sp_o2` vs `spO2` — BLOCKER.
**Affected**: vsm_coordinator.

### L29: Same Bug Pattern Propagates Across Multiple Files
**Prevention rule**: After fixing a field mapping bug, grep same pattern across
ALL files. `restSeconds` mapped from `rpe` existed in 3 files; fix wave only
fixed 1.
**Affected**: All S1 agents, vsm_auditor.

### L30: Prisma Relation Name Mismatch Blocks Client Generation
**Prevention rule**: vsm_coordinator validates relation names match on both
sides (`@relation("Requester")` vs `@relation("Follower")`).
**Affected**: vsm_coordinator.

### L31: Standalone Worker Cannot Be Imported as Library
**Prevention rule**: Communication via DB or API, never direct import. Push
service was standalone worker, backend tried to import it → MODULE_NOT_FOUND.
**Affected**: vsm_coordinator, S1-Backend.

### L32: Environment Variable Naming Drift
**Prevention rule**: vsm_coordinator validates env var names match exactly
across docker-compose/.env/code. `POLL_INTERVAL_MS` vs `POLL_MS` = silent
configuration failure.
**Affected**: vsm_coordinator.

### L37: Frontend API URL Fallback is Deployment Risk
**Prevention rule**: Fail-fast throw Error if `VITE_API_URL` missing. `||
'http://localhost:8000'` silently routes API calls to localhost in production.
**Affected**: S1-Frontend, vsm_security.

### L26: Every Service Must Have a Verifiable Entry Point
**Prevention rule**: After each build wave, verify every Dockerfile's CMD
points to a file that exists. Report generator had no src/index.ts but
Dockerfile referenced it.
**Affected**: vsm_coordinator, vsm_auditor.

---

## Meta-Learning Lessons

### L20: Re-Audit is the Highest-Value Quality Gate
**Prevention rule**: Security engineer, coordinator, tester, and auditor all
missed frontend/backend auth mismatch. Only the re-audit caught it. Re-audit
validates the system AS A WHOLE after fixes.
**Affected**: S3 (main agent), vsm_auditor.

### L21: Prevention Outperforms Detection
**Prevention rule**: Across 5 builds: 49 security findings detected. After
encoding 20 lessons as prevention rules: only 3 findings (87.5% reduction).
Strategy: detect early → encode prevention → prevent future → discover NEW
vulnerability classes.
**Affected**: All agents.

### L22: Vulnerability Prevention Rules in Agent Prompts Work
**Prevention rule**: 7 explicit security rules in agent prompt produced code
passing 12 targeted security checks. Agent prompts are the delivery mechanism
for accumulated wisdom.
**Affected**: All S1 agents.

### L24: Prevention Works for Known Patterns, Not Novel Ones
**Prevention rule**: Need TWO tracks: security (mature, prevention-based) AND
completeness (emerging, detection-based). 23 security lessons prevented 100%
of known anti-patterns but revealed new failure modes.
**Affected**: S3 (main agent), vsm_auditor.

### L25: GraphQL Depth Limiting Must Be in Design Checklist
**Prevention rule**: GraphQL schemas without depth/complexity limiting are a DoS vector. In FB1,
`strawberry.Schema` was created with no `max_depth` or `max_complexity`. Security gate caught it
as HIGH severity. Add "GraphQL depth limit (max 10) + complexity analysis" to architect design
checklist and integration checklist.
**Affected**: vsm_architect, vsm_auditor, vsm_security.

### L26: Rate Limiting on Auth Endpoints Is Not Optional
**Prevention rule**: Auth endpoints (register, login, refresh) without rate limiting are brute-force
vulnerable. In FB1, 8-character password minimum + no rate limiting = credential stuffing risk.
Add rate limiting requirement to foundation wave for any build with auth.
**Affected**: S1 coders in Phase 2, vsm_security.

### L37: Docker-Compose Bash Fallbacks Embed Secrets Silently
**Prevention rule**: Ban `:-` default-value fallbacks in `docker-compose.yml` for ALL
variables, especially `DATABASE_URL`, `REDIS_URL`, `POSTGRES_PASSWORD`, and `CORS_ORIGINS`.
Services must fail to start if required environment variables are missing. Fallbacks
silently embed credentials and bypass fail-safe configuration.
**Affected**: S1-DevOps, vsm_security.

### L38: Infrastructure Security Is as Critical as Application Security
**Prevention rule**: Security gate must inspect docker-compose.yml, Dockerfile, .env.example,
and nginx config with the same rigor as application code. Check for hardcoded passwords,
`:-` fallbacks, wildcard CORS in compose, and missing security headers in nginx.
**Affected**: vsm_security, S1-DevOps.

### L39: Rate Limiting Must Be in Foundation Wave for Auth Builds
**Prevention rule**: Any build with authentication MUST include rate limiting scaffolding
in the foundation wave (Phase 2), not just the security gate (Phase 6). Auth endpoints
(`/register`, `/login`, `/refresh`) are brute-force vectors from day one.
**Affected**: S1 coders in Phase 2, vsm_security.

### L40: Rate Limiting Requires Both Decorators AND Middleware
**Prevention rule**: Rate limiting is incomplete without `SlowAPIMiddleware` installed in
`main.py`. Endpoint decorators (`@limiter.limit(...)`) raise `RateLimitExceeded`, but without
the middleware the exception propagates to the generic handler and returns HTTP 500 instead
of 429. Both components are mandatory: (1) endpoint decorators on auth routes, (2) middleware
`app.add_middleware(SlowAPIMiddleware)`, (3) `@app.exception_handler(RateLimitExceeded)` returning 429.
**Affected**: S1-Backend, vsm_security.
**Source**: FB3 security gate MEDIUM-4 — decorators present in foundation wave but middleware
missing until Phase 6.

---

### L38: GraphQL RBAC Must Match REST RBAC
**Prevention rule**: When a project has BOTH REST and GraphQL endpoints, the security gate MUST verify that GraphQL resolvers enforce the SAME role-based access control as REST endpoints. GraphQL mutations are not exempt from authorization.
**Affected**: vsm_security, vsm_auditor.
**Source**: Fitness build FB5. GraphQL `createIncident` allowed any authenticated user while REST required `commander`/`dispatcher`.

### L39: GraphQL List Endpoints Require Ownership Filtering
**Prevention rule**: All GraphQL list queries (`incidents`, `resources`, `evidence`, etc.) MUST apply the same ownership/role scoping as their REST equivalents. A `responder` must not be able to enumerate all entities via GraphQL.
**Affected**: vsm_security, vsm_auditor.
**Source**: Fitness build FB5. GraphQL list queries returned unscoped data; REST endpoints were correctly scoped.

### L40: Upload Filename Sanitization Prevents Stored XSS
**Prevention rule**: Any user-provided filename stored in the database and rendered in the UI MUST be sanitized (strip HTML/JS characters) or replaced with a safe generated name before persistence.
**Affected**: vsm_security, S1 backend coders.
**Source**: Fitness build FB5. `uploads.py` stored `file.filename` verbatim without sanitization.

### L41: JWT Storage in localStorage is a MEDIUM Security Risk
**Prevention rule**: Flag JWT persisted to `localStorage` as MEDIUM severity. Prefer httpOnly, `SameSite=strict`, secure cookies. If Bearer tokens are required, recommend short-lived access tokens with refresh-token rotation.
**Affected**: vsm_security.
**Source**: Fitness build FB5. `authStore.ts` used Zustand `persist` middleware → token in `localStorage`.

---

### L42: GraphQL RBAC Must Be Explicitly Verified Against REST
**Prevention rule**: When a project has BOTH REST and GraphQL endpoints, the security gate MUST verify that GraphQL mutations enforce the SAME role-based access control as REST endpoints. GraphQL mutations are not exempt from authorization. Check every mutation: `create_*`, `update_*`, `delete_*` against REST `require_role()` constraints.
**Affected**: vsm_security, vsm_auditor.
**Source**: Fitness build FB8. GraphQL `update_course`/`delete_course` allowed any authenticated user while REST required `admin`/`instructor`.

### L43: WebSocket Room Handlers Must Verify Course Enrollment
**Prevention rule**: WebSocket `join_room` / `subscribe_*` handlers must verify BOTH authentication (valid session) AND authorization (user is enrolled in the target course / is the instructor). Session-only verification allows any authenticated user to access any room.
**Affected**: vsm_security, S1 backend coders.
**Source**: Fitness build FB8. `join_classroom` verified socket session but not course enrollment.

### L38: GraphQL Context Builders Must Be Fail-Closed
**Prevention rule**: GraphQL `get_context` or equivalent context builders MUST NOT catch all exceptions from authentication and set `user = None`. This creates a fail-open auth bypass: if a resolver forgets to check `user is None`, unauthenticated requests proceed silently. Let `get_current_user` raise its `HTTPException` (or `AuthenticationError`) so Strawberry/FastAPI can translate it to a GraphQL error.
**Affected**: vsm_security, backend implementation agents.
**Evidence**: FB6 security gate found `graphql.py` catching `Exception` and setting `user = None`, rated MEDIUM but is actually HIGH severity.

### L39: httpOnly Cookie Auth Requires Backend Cookie Setting
**Prevention rule**: If the spec requires "frontend uses httpOnly cookies (not localStorage)", the foundation wave MUST implement backend cookie setting (`response.set_cookie`) in the login endpoint. Returning the JWT in JSON body and storing it in Zustand memory does NOT satisfy the httpOnly requirement — the token is still accessible to JavaScript via the response body.
**Affected**: vsm_security, foundation wave agents.
**Evidence**: FB6 frontend stored token in Zustand (not localStorage), but backend still returned it in JSON. Security gate noted as MEDIUM but is actually HIGH.

### L28: JWT Signature Verification is Non-Negotiable
**Prevention rule**: Any code that calls `jwt.decode` with `options={"verify_signature": False}` or equivalent is a CRITICAL security vulnerability. This includes "convenience" helpers like `decode_token` that bypass verification. All JWT decoding MUST use the secret key and verify the signature. If the secret is "unavailable" in a context (e.g., Socket.IO), pass `settings.secret_key` explicitly.
**Affected**: S1-Backend, vsm_security.

### L29: Fix Agents Can Introduce Vulnerabilities
**Prevention rule**: Fix agents (especially generic coders fixing security-related code) can accidentally introduce vulnerabilities while trying to be helpful. The security gate MUST re-audit ALL files modified during any fix wave, not just the originally flagged files.
**Affected**: S3 (main agent), vsm_security.

---

## FB10 Discoveries

### L38: Self-Registration Must Never Accept User-Supplied Role Elevation
**Prevention rule**: Registration endpoints (REST and GraphQL) MUST NOT accept a `role` field from the client. All self-registered users MUST default to the lowest-privilege role (e.g., `customer`). Admin or seller elevation MUST require a separate privileged operation (admin-only endpoint, email verification, or manual approval).
**Affected**: vsm_architect, vsm_security, all backend S1 agents.
**Rationale**: FB10 security gate found that both REST `POST /auth/register` and GraphQL `register` mutation accepted a user-supplied `role`, allowing immediate privilege escalation to `admin`.

### L39: GraphQL Context Builders Must Propagate Auth Exceptions
**Prevention rule**: GraphQL `get_context` or equivalent context builders MUST NOT silently catch auth exceptions (e.g., `jwt.PyJWTError`) and fall back to an anonymous context. Auth failures MUST propagate as GraphQL errors or raise `AuthenticationError`. Fail-closed, not fail-open.
**Affected**: vsm_security, backend S1 agents.
**Rationale**: FB10 security gate found that `get_context` caught `jwt.PyJWTError` and set `user = None`, creating a fail-open pattern where malformed tokens were treated as anonymous requests.

### L40: Rate Limiting Must Be Explicit on Auth Endpoints
**Prevention rule**: Auth endpoints (`/register`, `/login`, password reset) MUST have explicit `@limiter.limit(...)` decorators, even if global `SlowAPIMiddleware` is installed. Global middleware alone is insufficient for per-endpoint control.
**Affected**: vsm_security, backend S1 agents.
**Rationale**: FB10 security gate found that `/register` and `/login` had no per-endpoint rate limits despite `SlowAPIMiddleware` being wired globally.
