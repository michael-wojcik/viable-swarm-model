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
