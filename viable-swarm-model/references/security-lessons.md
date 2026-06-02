# Security Lessons — Prevention Rule Format

> **Mutation rules**: Append new lessons as they are discovered. Mark lessons
> that are consistently false positives with `~~strikethrough~~` and rationale.
> If a prevention rule is proven ineffective after 3+ sessions, append a
> correction rather than deleting. The history of what was tried matters.
>
> **Organization**: Rules are grouped by TOPIC, not by build discovery date.
> Each rule includes ALL builds that discovered or validated it. This prevents
> duplicate rule proposals — scan the relevant topic before adding a new rule.
>
> **See also**: Mutation FB21-8 reorganized this file from chronological to topical.

---

## Core Workflow

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

### L6: Agent Ceiling is Host-Configured
**Prevention rule**: Wave size is limited by `background.max_running_tasks` in the
host's `~/.kimi/config.toml`. Beyond that: queue additional agents or use recursive
sub-VSMs. Do not invent arbitrary sub-limits.
**Affected**: S3 (main agent).

### L7: Gather vs. Stop for Security Findings
**Prevention rule**: Default: planned quality wave → gather all findings then
fix. Mid-build discovery → emergency stop. Never mix the two modes.
**Affected**: S3 (main agent), vsm_security.

### L10: Re-audit After Fixes is Mandatory
**Prevention rule**: Always re-audit fixed files. Exit criteria uses re-audit,
not original audit report. Stale reports mislead.
**Affected**: S3 (main agent), vsm_auditor.

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

## Auth & Registration

### L38: Self-Registration Must Never Accept User-Supplied Role Elevation
**Prevention rule**: Registration endpoints (REST and GraphQL) MUST validate the
`role` field against an explicit allowlist. The allowlist MUST NOT include
`"admin"`, `"superuser"`, or equivalent elevated roles. Unknown roles MUST
default to the least-privileged role or be rejected. Admin elevation requires a
separate privileged operation (admin-only endpoint, invitation, or manual
approval). The security gate must verify BOTH that an allowlist exists AND that
the allowlist excludes superuser roles.
**Affected**: vsm_security, vsm_architect, all backend S1 agents.
**Source**: FB10 (self-registration role elevation), FB14 (allowlist validation),
FB21 (allowlist composition Check #13 false negative).

### L48: SECRET_KEY Must Have Minimum Length Validation
**Prevention rule**: `SECRET_KEY` (or `JWT_SECRET`) MUST have a `min_length`
validator (e.g., Pydantic `Field(..., min_length=32)`). Empty strings or short
secrets are CRITICAL vulnerabilities enabling JWT forgery. A default value of
`""` is NOT sufficient mitigation.
**Affected**: vsm_security, foundation wave agents.
**Source**: FB14, Phase 5.

### L59: Refresh Token Endpoint Must Verify User Still Exists and Is Active
**Prevention rule**: `POST /auth/refresh` (or GraphQL `refreshToken`) MUST query
the database for the user identified by the refresh token's `sub` claim BEFORE
minting new tokens. If the user has been deleted or deactivated
(`is_active=False`), the endpoint MUST return 401. Decoding a valid JWT is NOT
sufficient — the user record is the source of truth.
**Affected**: vsm_security, S1-Backend.
**Source**: FB20, Phase 5.
**See also**: `integration-checklist.md` Check 32 (post-fix security re-check).

---

## JWT & Token Security

### L11: Hardcoded Secrets are the #1 Critical Finding
**Prevention rule**: JWT_SECRET required (no default), minimum 32 chars, app
refuses to start without it. Ban default secret values in ALL config.
**Affected**: All S1 agents, vsm_security.

### L18: Fake JWT Parsers for Development Are Never Removed
**Prevention rule**: Complete rewrite with proper library (jsonwebtoken::decode,
HMAC-SHA256). No bypass path. App panics at startup if JWT_SECRET missing.
**Affected**: S1-Backend, vsm_security.

### L28: JWT Signature Verification is Non-Negotiable
**Prevention rule**: Any code that calls `jwt.decode` with
`options={"verify_signature": False}` or equivalent is a CRITICAL security
vulnerability. This includes "convenience" helpers like `decode_token` that
bypass verification. All JWT decoding MUST use the secret key and verify the
signature. If the secret is "unavailable" in a context (e.g., Socket.IO), pass
`settings.secret_key` explicitly.
**Affected**: S1-Backend, vsm_security.

### L36: Silent None Returns in Middleware Bypass Security Controls
**Prevention rule**: Auth middleware raises HTTPException on failure. Never
return None for auth context.
**Affected**: S1-Backend, vsm_security.

### L50: JWT Payload Must Include Role Claim
**Prevention rule**: `create_access_token` MUST include `"role": user.role` in
the JWT payload. The `get_current_user` dependency can then enforce RBAC at the
edge without an extra database lookup. Without the role claim, middleware cannot
perform role-based access control efficiently.
**Affected**: vsm_security, backend coder agents, fix agents.
**Source**: FB16, FB17 (re-validated).

---

## Rate Limiting

### L26: Rate Limiting on Auth Endpoints Is Not Optional
**Prevention rule**: Auth endpoints (register, login, refresh) without rate
limiting are brute-force vulnerable. Add rate limiting requirement to foundation
wave for any build with auth.
**Affected**: S1 coders in Phase 2, vsm_security.
**Source**: FB1, FB3, FB10.

### L39: Rate Limiting Must Be in Foundation Wave for Auth Builds
**Prevention rule**: Any build with authentication MUST include rate limiting
scaffolding in the foundation wave (Phase 2), not just the security gate (Phase
5). Auth endpoints (`/register`, `/login`, `/refresh`) are brute-force vectors
from day one.
**Affected**: S1 coders in Phase 2, vsm_security.
**Source**: FB3, FB10.

### L40: Rate Limiting Requires Decorators, Middleware, AND Exception Handler
**Prevention rule**: Rate limiting is a three-component system:
1. Endpoint decorators (`@limiter.limit(...)`) on auth routes
2. Middleware `app.add_middleware(SlowAPIMiddleware)`
3. `@app.exception_handler(RateLimitExceeded)` returning HTTP 429 with JSON error body
All three are mandatory. Without the exception handler, rate-limited requests
crash with HTTP 500 instead of 429.
**Affected**: S1-Backend, vsm_security, vsm_wiring.
**Source**: FB3 (middleware missing), FB17 (handler missing), FB21 (handler missed by all gates).
**See also**: `integration-checklist.md` Check 53 (rate-limit exception handler verification).

### L58: Rate Limiting Must Be Distributed-Safe
**Prevention rule**: In-memory rate limiting (`defaultdict` + `asyncio.Lock`) is
NOT acceptable for production deployments. Under multi-process uvicorn workers,
each process has isolated memory, allowing `limit × N_workers` requests before
any 429 is returned. Rate limiting MUST use a shared store (Redis, memcached) or
be documented as a known limitation with explicit TODO comment.
**Affected**: vsm_security, S1-Backend.
**Source**: FB20, Phase 3/6.

---

## GraphQL Security

### L25: GraphQL Depth Limiting + Complexity Analysis Is Mandatory
**Prevention rule**: GraphQL schemas without depth/complexity limiting are a DoS
vector. Every GraphQL-enabled build MUST include `QueryDepthLimiter(max_depth=10)`
(or similar) in the schema. The architect MUST specify this in design docs; the
security gate MUST verify it is installed. Also add `MaxAliasesLimiter` and
`MaxTokensLimiter` where available.
**Affected**: vsm_architect, vsm_auditor, vsm_security, vsm_wiring.
**Source**: FB1, FB18, FB20.

### L63: GraphQL Context Builders Must Be Fail-Closed
**Prevention rule**: GraphQL `get_context` or equivalent context builders MUST
NOT catch all exceptions from authentication and set `user = None`. This creates
a fail-open auth bypass: if a resolver forgets to check `user is None`,
unauthenticated requests proceed silently. Let `get_current_user` raise its
`HTTPException` (or `AuthenticationError`) so Strawberry/FastAPI can translate it
to a GraphQL error. Auth failures MUST propagate as GraphQL errors or raise
`AuthenticationError`. Fail-closed, never fail-open.
**Affected**: vsm_security, backend implementation agents, vsm_auditor.
**Source**: FB6, FB10, FB12, FB21.

### L42: GraphQL RBAC Must Be Explicitly Verified Against REST
**Prevention rule**: When a project has BOTH REST and GraphQL endpoints, the
security gate MUST verify that GraphQL mutations enforce the SAME role-based
access control as REST endpoints. GraphQL mutations are not exempt from
authorization. Check every mutation: `create_*`, `update_*`, `delete_*` against
REST `require_role()` constraints.
**Affected**: vsm_security, vsm_auditor.
**Source**: FB5, FB8.

### L44: Strawberry Auto-CamelCase Requires Explicit Verification
**Prevention rule**: When using Strawberry GraphQL, ALWAYS verify frontend
queries use camelCase field names matching the auto-generated schema. Run
`python -c "from app.graphql import schema; print(schema)"` and cross-check
against frontend `gql` documents. Snake_case in frontend queries is a BLOCKER
when Strawberry is configured for auto-camelCase.
**Affected**: vsm_coordinator, vsm_auditor, S1-Frontend.
**Source**: FB12, Phase 3b/5.

### L51: GraphQL-REST RBAC Parity Requires Explicit Role Arrays in api-spec.md
**Prevention rule**: Every endpoint in `api-spec.md` MUST include an explicit
`RBAC: [roles]` array. Ambiguous labels like "(owner-filtered)" or "(public)"
MUST be forbidden — they cause downstream implementation agents to make
inconsistent assumptions about which roles can access which endpoints. GraphQL
resolvers MUST enforce the same RBAC as their REST equivalents.
**Affected**: vsm_architect, S1-Backend, vsm_security, vsm_coordinator.
**Source**: FB17, Phase 1/5.

### L57: GraphQL Subscription Resolvers Must Verify Resource Ownership Before Yielding
**Prevention rule**: Any GraphQL subscription resolver that filters by
`resource_id` (e.g., `property_id`, `room_id`, `project_id`) MUST verify that
`current_user` has access to that specific resource BEFORE yielding events.
Role checks (`_ensure_role`) are NOT sufficient — a tenant with role="tenant"
could subscribe to `property_id=None` and receive ALL events, or subscribe to
another tenant's `property_id` and receive cross-tenant data.
**Checklist addition**:
- [ ] Every subscription resolver with a `resource_id` parameter queries the database to verify ownership/lease/membership
- [ ] `property_id=None` subscriptions are REJECTED with 403 unless the user is a super-admin
- [ ] The verification happens BEFORE entering the `while True` generator loop
**Affected**: vsm_security, S1-Backend, vsm_backend_tester.
**Source**: FB20, Phase 5/8b.

---

## WebSocket Security

### L16: WebSocket Auth Must Be In-Band, Never in URL
**Prevention rule**: Frontend sends auth as first WS message after connection:
`{"msg_type":"auth","token":"..."}`. NEVER `?token=...` in WebSocket URL.
**Affected**: S1-Backend, S1-Frontend, vsm_security.

### L43: WebSocket Room Handlers Must Verify Course Enrollment
**Prevention rule**: WebSocket `join_room` / `subscribe_*` handlers must verify
BOTH authentication (valid session) AND authorization (user is enrolled in the
target course / is the instructor). Session-only verification allows any
authenticated user to access any room.
**Affected**: vsm_security, S1 backend coders.
**Source**: FB8. `join_classroom` verified socket session but not course enrollment.
**See also**: `integration-checklist.md` Check 30 (WebSocket room handlers verify enrollment before allowing room access).

---

## CORS & Infrastructure

### L61: CORS origin: true is Equivalent to Wildcard
**Prevention rule**: Explicit allowlist from config. Never `origin: true` or
`origin: "*"` with `credentials: true`. Also verify `allow_methods` and
`allow_headers` are explicit lists, not `"*"`, when `allow_credentials=True`.
**Affected**: S1-Backend, vsm_security.
**Related**: Check 58 (integration-checklist.md).

### L33: SSE JWT in URL is Unavoidable Architectural Vulnerability
**Prevention rule**: Short-lived SSE token exchange. Client POSTs JWT to
`/auth/sse-token` → receives 5-minute token → connects with `?sse_token=...`.
**Affected**: S1-Backend, S1-Frontend, vsm_security.

### L37: Docker-Compose Bash Fallbacks Embed Secrets Silently
**Prevention rule**: Ban `:-` default-value fallbacks in `docker-compose.yml` for
ALL variables, especially `DATABASE_URL`, `REDIS_URL`, `POSTGRES_PASSWORD`, and
`CORS_ORIGINS`. Services must fail to start if required environment variables are
missing. Fallbacks silently embed credentials and bypass fail-safe configuration.
Also ban hardcoded literal passwords in docker-compose (e.g.,
`POSTGRES_PASSWORD: devpassword`).
**Affected**: S1-DevOps, vsm_security.
**Source**: FB2, FB18 (rule persisted despite prior mutation).
**See also**: `integration-checklist.md` Check 37 (CORS configuration validation).

### L66: Infrastructure Security Is as Critical as Application Security
**Prevention rule**: Security gate must inspect docker-compose.yml, Dockerfile,
.env.example, and nginx config with the same rigor as application code. Check for
hardcoded passwords, `:-` fallbacks, wildcard CORS in compose, and missing
security headers in nginx.
**Affected**: vsm_security, S1-DevOps.

---

## Data Exposure & Frontend Security

### L19: Game API Answer Exposure Enables Cheating
**Prevention rule**: Public DTOs omit `correct_answer_index` and solution
fields. Never expose answers in public endpoints.
**Affected**: S1-Backend, vsm_security.

### L62: Frontend API URL Fallback is Deployment Risk
**Prevention rule**: Fail-fast throw Error if `VITE_API_URL` missing. `||
'http://localhost:8000'` silently routes API calls to localhost in production.
**Affected**: S1-Frontend, vsm_security.
**See also**: `integration-checklist.md` Check 36 (frontend config fallback check).

### L41: JWT Storage in localStorage is a MEDIUM Security Risk
**Prevention rule**: Flag JWT persisted to `localStorage` as MEDIUM severity.
Prefer httpOnly, `SameSite=strict`, secure cookies. If Bearer tokens are
required, recommend short-lived access tokens with refresh-token rotation.
**Affected**: vsm_security.
**Source**: FB5.

### L49: Frontend Cross-File Contract Mismatches Require Automated Check
**Prevention rule**: Parallel frontend agents independently produce queries.ts,
stores, and page components that may have incompatible contracts. A lightweight
automated check (`tsc --noEmit` or import grep) MUST run before the auditor to
catch missing exports, missing store fields, and type mismatches.
**Affected**: vsm_coordinator, S3 (main agent), vsm_auditor.
**Source**: FB14, Phase 3b.

---

## N+1 & Performance

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

## Integration & Cross-Service

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

### L54: Celery Broker URL Must Use Settings, Never Hardcoded Localhost
**Prevention rule**: ALL `Celery()` instantiations MUST use
`broker=get_settings().REDIS_URL` (or equivalent settings reference). Hardcoded
`redis://localhost:6379/0` breaks containerized deployments and is a HIGH
severity configuration error.
**Affected**: S1-Backend, vsm_security, vsm_coordinator.
**Source**: FB17, Phase 3/6.

---

## Testing & Verification

### ~~L12: Tester Bug-Fix Inline is Highly Valued~~ (SUPERSEDED by L67)
**Prevention rule**: vsm_tester prompt includes: "Fix bugs inline during test
writing. Document each under 'Bugs Found and Fixed'."
**Affected**: vsm_tester.

### L64: Every Service Must Have a Verifiable Entry Point
**Prevention rule**: After each build wave, verify every Dockerfile's CMD
points to a file that exists. Report generator had no src/index.ts but
Dockerfile referenced it.
**Affected**: vsm_coordinator, vsm_auditor.

---

## Meta-Learning

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

---

## Security Operations

### L5: Security Engineer Non-Negotiable for Production
**Prevention rule**: Always spawn vsm_security before delivery. Without it,
CORS reflection attacks, hardcoded secrets, SSRF go undetected.
**Affected**: S3 (main agent).

### L65: Fix Agents Can Introduce Vulnerabilities
**Prevention rule**: Fix agents (especially generic coders fixing
security-related code) can accidentally introduce vulnerabilities while trying to
be helpful. The security gate MUST re-audit ALL files modified during any fix
wave, not just the originally flagged files.
**Affected**: S3 (main agent), vsm_security.

---

## Severity Calibration

### L46: Connection String Defaults Are Not CRITICAL Secrets
**Prevention rule**: `DATABASE_URL` and `REDIS_URL` defaults (e.g.,
`postgresql+asyncpg://user:pass@localhost/db`, `redis://localhost:6379`) are
LOW severity unless they contain production credentials. Distinguish between:
(1) secret fallbacks (JWT_SECRET, POSTGRES_PASSWORD) = CRITICAL, and
(2) connection string defaults = LOW/MEDIUM.
**Affected**: vsm_security.
**Source**: FB12, Phase 5.

### L47: CORS Method and Header Wildcards with Credentials
**Prevention rule**: When `allow_credentials=True`, `allow_methods` and `allow_headers` MUST use explicit allowlists, not `"*"` wildcards. Most security checklists only verify `allow_origins`, but method/header wildcards are equally dangerous: they allow arbitrary cross-origin requests with authenticated cookies.
**Verification**: `grep -r 'allow_methods.*\*' --include='*.py' .` and `grep -r 'allow_headers.*\*' --include='*.py' .`
**Affected**: vsm_security, vsm_backend_coder.
**Source**: Gym E16 (H106), FB20-Test security report.

### L67: Tester Bug-Fix Inline is Deprecated — Route ALL Fixes to Phase 7
**Prevention rule**: The `vsm_tester` legacy agent has been removed. ALL testing is now performed by domain-specific testers (`vsm_backend_tester`, `vsm_frontend_tester`). Neither tester is permitted to fix bugs inline. Test failures MUST be reported to S5, who routes them to Phase 7 (Fix Wave) with the appropriate domain-specific fix agent (`vsm_backend_fix_agent` or `vsm_frontend_fix_agent`). Inline fixes bypass re-audit, post-fix security re-check, and mandatory `re-audit-report.md` production. This applies to ALL tiers, including Tier 1 (<1000 lines).
**Supersedes**: L12 (Tester Bug-Fix Inline is Highly Valued)
**Affected**: S5 (main agent), vsm_backend_tester, vsm_frontend_tester, vsm_backend_fix_agent, vsm_frontend_fix_agent.
**Source**: Gym E15 (H105), FB20/FB21 fitness builds.

## IDOR vs Missing Ownership Checks (Refined FB23)

When auditing detail endpoints (`GET /resource/{id}`), distinguish carefully:

- **Missing authorization** = ANY authenticated user can read ANY resource.
  This is pure IDOR. Severity: HIGH/BLOCKER.

- **Missing ownership checks** = The endpoint HAS role-based filtering
  (e.g., non-privileged users see only `published` jobs, or interviewers see
  only their assigned candidates) but lacks per-resource ownership verification.
  This is NOT pure IDOR — it is an authorization gap. Severity: MEDIUM/HIGH.

**Do NOT** label role-filtered endpoints as "IDOR" when the actual issue is
missing ownership. Misclassification reduces signal-to-noise ratio and misleads
fix agents about the required remediation (ownership check vs full auth rewrite).

**Verification question**: If User A (role: interviewer) can read User B's
interview record despite not being assigned to it, is that because:
(a) there is NO auth check at all (IDOR), or
(b) there IS a role check but no ownership check (auth gap)?

Answer (b) → classify as "missing ownership check", not "IDOR".

**Source**: FB23 security report labeled `jobs.py:get_job()` and
`candidates.py:get_candidate()` as IDOR when both had role-based access
controls. The real gap was lack of resource ownership verification.

---

## File Upload Size Limits (FB25)

File upload endpoints using `UploadFile` (or language-equivalent) MUST enforce a
`max_bytes` limit or stream to disk. Loading entire files into memory with
`await file.read()` is a **MEDIUM** severity DoS vector, not LOW.

Pattern:
```python
MAX_UPLOAD_BYTES = 10 * 1024 * 1024  # 10 MB

@router.post("/upload")
async def upload(file: UploadFile):
    contents = await file.read()
    if len(contents) > MAX_UPLOAD_BYTES:
        raise HTTPException(413, "File too large")
```

**Source**: FB25 `uploads.py` read entire uploaded files into memory with no
size cap. Security auditor rated it LOW/pre-existing; should be MEDIUM.

## Rate Limiting Applied (FB25)

If rate-limiting middleware is installed (e.g., `SlowAPIMiddleware`), at least
two high-risk endpoints MUST have `@limiter.limit()` decorators. Middleware
installation without endpoint decoration is a configuration gap.

Minimum decorated endpoints:
- `/auth/login` or `/auth/token`
- `/auth/register`
- `/graphql` (if exposed)

**Source**: FB25 `app/main.py` registered `SlowAPIMiddleware` and a
`RateLimitExceeded` handler, but zero endpoints applied `@limiter.limit()`.
