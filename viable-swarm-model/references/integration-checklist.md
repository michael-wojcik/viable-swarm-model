# Cross-File Integration Verification Checklist

> **Mutation rules**: Append new checks discovered in the field. Mark checks
> that are consistently irrelevant for certain project types with a note.
> Never delete — a check that seems irrelevant for one project type may be
> critical for another.

Run ALL of these before declaring integration complete.

**Failure rule**: If ANY check fails, send back to responsible S1 for
correction BEFORE quality gates.

---

## 1. (ISSUE) Export/Import Verification
- [ ] Every exported utility/type is imported by at least one consumer file
- [ ] Every import statement resolves to an existing export
- [ ] No orphaned code — utilities that were created are actually used

## 2. (BLOCKER) Contract Consistency
- [ ] Shared contracts (types, interfaces) are consistently used across files
- [ ] No duplicate type definitions with different shapes

## 3. (BLOCKER) Entry Points
- [ ] Entry points (routes, main, index) import and register all middleware
- [ ] Every service has a verifiable entry point (Dockerfile CMD/ENTRYPOINT file exists)

## 4. (BLOCKER) Build Verification
- [ ] Codebase compiles/builds without errors
- [ ] No TypeScript/JavaScript syntax errors

## 5. (BLOCKER) WebSocket Event Contracts
- [ ] Every backend `emit` has matching frontend listener (and vice versa)
- [ ] WebSocket message shape: `kind` field values match exactly between backend and frontend
- [ ] Shared event constants file exists and is imported by both sides
- [ ] **Socket.IO server instance reuse**: The ASGI entry point (`realtime.py`) imports and reuses the SAME `sio` instance that event handlers are registered on in `sio.py`. Creating a new `AsyncServer` in `realtime.py` breaks all WS handlers.

## 6. (BLOCKER) GraphQL Contracts
- [ ] SDL types match TypeScript payload types
- [ ] Every subscription has matching resolver with `subscribe` returning AsyncIterable
- [ ] @graphql-depth-limit installed (max 10) + complexity analysis
- [ ] **Schema introspection verification**: Run `python -c "from app.graphql import schema; print(schema)"` and verify EVERY frontend query field name matches the introspected schema EXACTLY (Strawberry auto-camelCases snake_case Python fields to camelCase GraphQL fields)
- [ ] **GraphQLRouter wiring**: Verify `GraphQLRouter` is mounted with `context_getter=get_context` so auth context propagates to resolvers
- [ ] **GraphQL argument type parity**: Verify every frontend mutation's input argument types match the introspected schema input types (not just field names)

## 7. (ISSUE) Frontend Paths & Config
- [ ] Frontend relative path to shared types: `../../shared/` not `../shared/` in monorepos
- [ ] Vite/Webpack proxy config includes `/api`, `/graphql`, `/ws`, `/tiles` paths
- [ ] GraphQL subscriptions need `ws: true` in proxy config
- [ ] Vite path alias configured for shared types (e.g., `@flux/shared`)
- [ ] **Config key name parity**: Every `getattr(settings, "KEY_NAME")` or `settings.KEY_NAME` reference in the codebase must match an actual field defined in the Settings/Pydantic class. Name drift (e.g., `CORS_ORIGINS` vs `CORS_ALLOWED_ORIGINS`) silently breaks functionality.

## 8. (ISSUE) pgvector Pipeline
- [ ] PostgreSQL vector extension enabled
- [ ] VECTOR(N) column matches embedding dimensions
- [ ] ivfflat index with `vector_cosine_ops` exists
- [ ] Embeddings generated before INSERT/UPDATE

## 9. (ISSUE) Server-Sent Events (SSE)
- [ ] Backend uses `StreamingResponse(media_type="text/event-stream")`
- [ ] Backend yields `data: {json}\n\n` format
- [ ] Frontend uses `getReader()` + `TextDecoder`, not EventSource
- [ ] Frontend splits on `"\n\n"` to extract messages
- [ ] Short-lived SSE token exchange implemented (never long-lived JWT in URL)

## 10. (ISSUE) CRDT Persistence
- [ ] Yjs PersistenceAdapter connected to doc `update` event
- [ ] BYTEA column exists in PostgreSQL
- [ ] Load path SELECTs + applies updates in chronological order (`ORDER BY created_at`)

## 11. (BLOCKER) DAG Validation
- [ ] `validate()` called on every create/update/execute
- [ ] 3-color DFS (WHITE/GRAY/BLACK) for cycle detection
- [ ] Kahn's algorithm for topological sort determines execution order

## 12. (BLOCKER) Redis Queue
- [ ] Queue name consistent between API `lpush` and worker `brpop`
- [ ] Worker re-enqueues dependents after completion
- [ ] Redis pub/sub channel names match between producer and consumer

## 13. (BLOCKER) Frontend Scaffolding
- [ ] `package.json` exists
- [ ] `vite.config.ts` exists (with path alias)
- [ ] `tsconfig.json` exists
- [ ] `index.html` exists
- [ ] `src/main.tsx` (or equivalent) exists
- [ ] `src/App.tsx` exists

## 14. (ISSUE) Rust Workspace
- [ ] Workspace `Cargo.toml` includes ALL member crates
- [ ] No duplicate imports between `lib.rs` and local paths in same file
- [ ] Integration tests in `tests/` import from library path, not local modules

## 15. (ISSUE) Go JSON Tags
- [ ] All JSON tags are camelCase (`json:"camelCase"`)
- [ ] No snake_case leaking to frontend via struct tags

## 16. (BLOCKER) Docker Compose
- [ ] All services have verifiable entry points (CMD/ENTRYPOINT file exists)
- [ ] Environment variable names match exactly across docker-compose/.env/code
- [ ] No `||` fallbacks for SECRET/KEY/PASSWORD/TOKEN variables

## 17. (BLOCKER) Prisma / ORM
- [ ] Relation names match on both sides (`@relation("Name")`)
- [ ] N+1 queries prevented (selectinload for relationships, batched GROUP BY for computed fields)

## 18. (BLOCKER) Auth & Middleware
- [ ] Auth middleware raises HTTPException on failure, never returns None silently
- [ ] Document ownership filtering on ALL list endpoints
- [ ] Public DTOs omit answer/solution fields for game/quiz APIs

## 19. (LOW) Mobile / Game UI (if applicable)
- [ ] 60px minimum button height
- [ ] Dark theme (#0f172a) for OLED
- [ ] Tested at 375px viewport

## 20. (ISSUE) File Structure
- [ ] No orphaned utility files
- [ ] No empty files committed
- [ ] README has setup instructions

## 21. (BLOCKER) Parallel Agent Coordination
- [ ] Entry point files (main.py, App.tsx, server.ts) are modified by at most one agent per wave
- [ ] If multiple agents must contribute to entry points, a dedicated "wiring" agent runs last
- [ ] All imports in entry points resolve (no missing modules)

## 22. (BLOCKER) WebSocket Auth Contracts
- [ ] Browser WebSocket auth uses path-based tokens (NOT query params) when headers are impossible
- [ ] Backend validates token from path parameter before accepting connection
- [ ] Token is short-lived (≤15 min) and scoped to the specific resource

## 23. (BLOCKER) State Machine Domain Alignment
- [ ] Backend state machine enum values match frontend TypeScript union types exactly
- [ ] Every state value emitted by backend is handled by frontend switch/case
- [ ] No frontend-only states that backend never emits (causes unreachable code)

## 24. (BLOCKER) Case-Sensitive Enum Alignment
- [ ] GraphQL enum values match TypeScript union types exactly (including case)
- [ ] Backend string literals match frontend string literals exactly
- [ ] Shared constants file is the single source of truth for enum values

## 25. (ISSUE) Frontend Dockerfile Build Args
- [ ] `VITE_API_URL` and `VITE_WS_URL` passed as `ARG` in frontend Dockerfile
- [ ] Runtime env vars are not silently baked as `undefined` into static bundles

## 26. (BLOCKER) GraphQL Field Name Alignment
- [ ] Run `python -c "from app.graphql import schema; print(schema)"` to inspect the actual GraphQL schema
- [ ] GraphQL schema field names (after auto-camelCase) match frontend query field names exactly
- [ ] For Strawberry: verify that `snake_case` backend fields produce the expected `camelCase` frontend fields
- [ ] Frontend queries MUST use camelCase, not snake_case, when the backend uses Strawberry
- [ ] Every field queried by frontend exists in the backend schema
- [ ] No frontend queries reference fields that were renamed or removed in backend
- [ ] See also: `security-lessons.md` L63 (GraphQL context fail-closed)

## 27. (BLOCKER) Auth Response Contract Documentation
- [ ] Auth endpoints (`/register`, `/login`, `/refresh`) have documented exact response JSON keys in api-spec.md
- [ ] Backend implementation matches the documented contract exactly
- [ ] Frontend consumes the exact keys documented in the contract

## 28. (ISSUE) Orphaned Exports / Dead Code Scan
- [ ] Every exported function/class in backend is imported by at least one consumer file
- [ ] Every exported function/class in frontend is imported by at least one consumer file
- [ ] No duplicate implementations of the same utility in different files

## 29. (BLOCKER) WebSocket Event Name Dictionary Cross-Check
- [ ] `api-spec.md` WebSocket event names match `sio.py` emit/handler names
- [ ] `sio.py` emit names match `shared/sio-events.ts` constant values
- [ ] `shared/sio-events.ts` constants are imported by both backend and frontend
- [ ] Every backend `emit` has a matching frontend `socket.on` listener

## 42. (BLOCKER) GraphQL Enum Runtime Safety
- [ ] Python enums used in GraphQL schemas use `str, enum.Enum` (or equivalent) when their values are strings
- [ ] Enum construction from database string values does not raise `ValueError`

## 43. (BLOCKER) Circular Import Prevention
- [ ] No router/module imports from `main.py` (or equivalent entry point)
- [ ] Shared singletons (limiter, config, database) live in dedicated modules, not in entry points

## 20. GraphQL-REST Contract Parity
- [ ] GraphQL mutations enforce the same RBAC as REST endpoints
- [ ] GraphQL list queries apply the same ownership filtering as REST list endpoints
- [ ] GraphQL geo/spatial endpoints apply the same bounds caps as REST geo endpoints

## 30. (BLOCKER) WebSocket Authentication & Authorization
- [ ] WebSocket room subscription handlers (`subscribe_patient`, etc.) verify the socket has authenticated BEFORE allowing room access
- [ ] WebSocket room unsubscription handlers verify the socket session before leaving a room
- [ ] Socket.io `cors_allowed_origins` uses the same explicit allowlist as HTTP CORS middleware, never `"*"`
- [ ] Backend `authenticate` event stores user session; all subsequent room operations read and validate that session
- [ ] WebSocket room handlers verify the user is ENROLLED in the target course (or is the instructor/admin) before allowing room access. Session auth alone is insufficient.
- [ ] See also: `security-lessons.md` L57 (GraphQL subscription resolvers must verify resource ownership before yielding) for the same underlying principle applied to GraphQL.

## 31. (BLOCKER) Model-Spec Alignment Check
- [ ] SQLAlchemy/model field names match `data-model.md` exactly
- [ ] SQLAlchemy/model field types match `data-model.md` exactly
- [ ] All entities in `data-model.md` are represented in the ORM models
- [ ] All relationships and constraints from `data-model.md` are implemented
- [ ] If `data-model.md` does not exist, skip this check

## 32. (BLOCKER) Post-Fix Security Re-Check
- [ ] After any fix wave that modified auth, GraphQL, or WebSocket files, re-run security checks on those specific files
- [ ] Verify auth middleware still raises on failure (never returns None)
- [ ] Verify GraphQL `get_context` still propagates exceptions (no broad `except` added)
- [ ] Verify WebSocket room handlers still verify session before room access
- [ ] If security regression is found, escalate to S5 immediately

## 33. (BLOCKER) Subprocess Import Verification
- [ ] After implementation wave and after fix wave, run `python -c "import app.main; import app.graphql; import app.sio"` (or equivalent entry points) in a subprocess
- [ ] If any module raises `NameError`, `ImportError`, or `ModuleNotFoundError`, treat as BLOCKER
- [ ] In-process code review (ReadFile) is insufficient — it does not catch missing imports that are only referenced at runtime

## 34. (BLOCKER) Frontend Build Script Verification
- [ ] Run `npm run build` (or equivalent package.json script), not just the underlying tool (`vite build`, `next build`, etc.)
- [ ] Package.json scripts may include additional type-checking or linting steps that `vite build` alone does not exercise
- [ ] Verify `tsconfig.json` includes all necessary types (e.g., `@types/node` for `vite.config.ts`)

## 35. (BLOCKER) GraphQL Enum Serialization Alignment
- [ ] GraphQL enum values returned to the client match the values expected by frontend TypeScript unions and REST API contracts
- [ ] For Strawberry: `strawberry.enum` member names (which become GraphQL enum values) must match frontend enum literals exactly
- [ ] Changing GraphQL enum definitions must trigger synchronized updates to frontend queries, tests, and shared types

## 36. (HIGH) Frontend Config Fallback Check
- [ ] No `||` fallbacks in frontend API/WS/GraphQL config files (`src/graphql/client.ts`, `src/sio/client.ts`, etc.)
- [ ] All API URLs are required build-time env vars with no localhost fallback
- [ ] Missing env vars cause build-time failure, not silent fallback to localhost
- [ ] See also: `security-lessons.md` L62 (frontend API URL fallback ban).

## 37. (HIGH) CORS Configuration Validation
- [ ] CORS origin is explicit allowlist, never `*` or `true` when `allow_credentials=True`
- [ ] `Settings.CORS_ORIGINS` has no default wildcard; app refuses to start if CORS_ORIGINS is unset
- [ ] FastAPI CORS middleware and Socket.io `cors_allowed_origins` use the same explicit allowlist
- [ ] See also: `security-lessons.md` L61 (CORS wildcard equivalence).

## 38. (BLOCKER) REST Endpoint Auth Guard Check
- [ ] All REST list endpoints (`GET /`) have explicit auth guards or public documentation
- [ ] All REST detail endpoints (`GET /{id}`) have explicit auth guards or public documentation
- [ ] Unauthenticated REST endpoints do not expose draft/private data
- [ ] GraphQL RBAC parity: every GraphQL mutation enforces the same role requirements as its REST equivalent
- [ ] See also: `security-lessons.md` L38 (registration role elevation prevention).


---



## 45. GraphQL Context Fail-Closed
- [ ] GraphQL `get_context` or equivalent context builders MUST propagate auth exceptions (JWT errors, missing tokens)
- [ ] Never silently catch auth exceptions and return an anonymous/unauthenticated context
- [ ] Auth failures MUST result in GraphQL errors or `AuthenticationError`, not `user = None`
- [ ] See also: `security-lessons.md` L63 (GraphQL context builders must be fail-closed).

## 39. (BLOCKER) Vite Proxy Port Verification
- [ ] Vite proxy target ports must match the actual exposed ports in docker-compose.yml
- [ ] `/api` and `/graphql` proxy targets must match the API service port (e.g., 8000)
- [ ] `/ws` proxy target must match the realtime service port (e.g., 8001)
- [ ] Never proxy to a default port (e.g., 4000) unless that port is explicitly exposed in docker-compose

## 40. (BLOCKER) WebSocket Auth Handshake Sequence
- [ ] `api-spec.md` explicitly documents the WebSocket auth handshake: connect → auth event → payload shape → server response → room join
- [ ] Frontend and backend use the SAME auth mechanism (either Socket.IO `auth` option OR custom `authenticate` event, not both)
- [ ] Backend rejects all room operations until auth handshake completes

## 41. (BLOCKER) SQLAlchemy Engine Configuration
- [ ] `models.py` does NOT hardcode database connection strings at module level
- [ ] Engine is created from `get_settings().DATABASE_URL` or uses a lazy factory pattern
- [ ] Engine creation does not trigger side effects at import time

## 42. GraphQL Schema Introspection Verification
- [ ] Run `python -c "from app.graphql import schema; print(schema)"` (or equivalent) to introspect the actual GraphQL schema
- [ ] Verify EVERY frontend query in `queries.ts` matches the schema's argument types exactly (e.g., `DateTime` vs `String`, `Int` vs `Float`)
- [ ] Verify EVERY frontend mutation's expected return type matches the schema's actual return type (e.g., `Boolean` vs object type)
- [ ] Verify frontend query field names match schema field names exactly (case-sensitive, including auto-camelCase from Strawberry)
- [ ] ANY mismatch is a BLOCKER: send to frontend or backend agent for correction

## 43. Frontend Cross-File Import Resolution
- [ ] After all parallel frontend implementation agents complete, run `npx tsc --noEmit` (or `vite build`, or manual grep of all imports) to verify all cross-file imports resolve
- [ ] Every export from `queries.ts` MUST be imported by at least one page or component
- [ ] Every field destructured from Zustand stores MUST exist in the store's type definition
- [ ] Every type imported from `shared/types.ts` MUST be defined in that file
- [ ] ANY unresolved import or missing field is a BLOCKER before the auditor runs

## Check 46: Circular Import Prevention (Fix Wave)
- [ ] After any fix agent adds cross-module imports, run `python -c "import app.main"` to verify no circular dependencies
- [ ] If fix introduces `from app.main import X` in a router, verify router is not imported by main.py at module level
- [ ] Extract shared dependencies (limiter, settings, db) to dedicated modules rather than importing from main.py

**Source**: FB15 Fix Wave introduced circular import when wiring rate limiting (H70)

## Check 47: Frontend `as any` Anti-Pattern
- [ ] Scan all `.tsx` and `.ts` files for `as any` casts
- [ ] Every `as any` must have a comment explaining why type safety is intentionally bypassed
- [ ] `as any` used to destructure store fields is a BLOCKER — the store schema must be updated instead
- [ ] Run `tsc --noEmit` after removing `as any` to verify no hidden contract mismatches

**Source**: FB15 frontend agent used `useEventStore() as any` to hide missing `salesMetrics` field (H71)

## Check 48: GraphQL Argument Type Parity
- [ ] Run schema introspection (`python -c "from app.graphql import schema; print(schema)"`)
- [ ] For EVERY frontend mutation, verify input argument types match the introspected schema EXACTLY
- [ ] Cross-check against api-spec.md: if spec says `String` but schema says `DateTime`, it is a BLOCKER
- [ ] Field-name alignment is necessary but NOT sufficient — argument types must also match

**Source**: FB15 coordinator verified field names but missed String vs DateTime input type trap (H68)

## Check 49: Runtime API Verification
- [ ] Before using framework-specific parameters (e.g., `strawberry.Schema(validation_rules=[...])`), verify with `help(Class.__init__)` or test invocation
- [ ] If parameter is not recognized, do NOT use it — find the correct API for the installed version
- [ ] This applies to Strawberry, FastAPI, SQLAlchemy, and any library with version drift

**Source**: FB15 agent used `validation_rules` parameter that doesn't exist in installed strawberry-graphql (H72)

## Check 50: Cross-Layer Runtime Consistency
- [ ] **localStorage key parity**: grep ALL `localStorage.getItem/setItem/removeItem` calls in frontend. The token key name MUST match the auth router's response key exactly (e.g., if auth router returns `{ token: "..." }`, frontend MUST use `localStorage.getItem("token")`, NOT `localStorage.getItem("access_token")`)
- [ ] **Celery broker URL**: grep ALL `Celery(` instantiations. The `broker=` parameter MUST use `get_settings().REDIS_URL` or equivalent settings reference. Hardcoded `redis://localhost:6379/0` is a BLOCKER
- [ ] **Socket.IO namespace parity**: Backend `sio.py` namespace MUST match frontend `sio/client.ts` namespace. Default namespace (`/`) on both sides is acceptable, but a mismatch is a BLOCKER
- [ ] **JWT payload key parity**: If frontend destructures `role` from JWT payload, verify `create_access_token` includes `"role"` claim. If frontend expects `userId`, verify token includes it

**Source**: FB17 integration found 3 BLOCKERs from cross-layer mismatches: localStorage key mismatch (`access_token` vs `token`), Celery broker hardcoded to localhost, orphaned queries.ts exports (H81)

## Check 51: api-spec.md RBAC Explicit Arrays
- [ ] Every endpoint in `api-spec.md` MUST include an explicit `RBAC: [roles]` array (e.g., `RBAC: ["admin", "adjuster", "auditor"]`)
- [ ] NEVER use ambiguous natural-language labels like "(owner-filtered)" or "(public)" without specifying which roles can access
- [ ] GraphQL resolvers MUST have the same RBAC array as their REST equivalent endpoints
- [ ] If an endpoint has ownership filtering, the RBAC array shows WHO can access it, and a separate `Ownership: owner_id == current_user.id` note shows HOW results are filtered

**Source**: FB17 api-spec.md "(owner-filtered)" label caused GraphQL RBAC parity gap (H83)
- [ ] See also: `security-lessons.md` L38 (registration role allowlist composition).

## Check 52: Apollo Client Usage Verification
- [ ] If `main.tsx` wraps the app in `ApolloProvider`, verify at least ONE page component uses `useQuery` or `useMutation` from `@apollo/client`
- [ ] If ZERO pages use Apollo Client, either: (a) remove ApolloProvider and graphql dependencies, or (b) migrate data-fetching pages from REST `fetch()` to Apollo Client
- [ ] REST `fetch()` is acceptable for: file uploads (multipart/form-data), auth endpoints (login/register/refresh), and health checks
- [ ] GraphQL queries in `queries.ts` that are never imported by any page/component are dead code — treat as ISSUE

**Source**: FB17 frontend initialized ApolloProvider but all pages used REST fetch(); queries.ts was completely orphaned (H84)

## Check 53: Rate Limit Exception Handler
- [ ] If `SlowAPIMiddleware` is installed, verify `app.add_exception_handler(RateLimitExceeded, handler)` or equivalent `@app.exception_handler(RateLimitExceeded)` exists
- [ ] Without an exception handler, rate-limited requests crash with unhandled exception instead of returning HTTP 429
- [ ] The handler MUST return JSON with `{"error": "Rate limit exceeded"}` and status 429

**Source**: FB17 backend installed SlowAPIMiddleware but lacked exception handler for RateLimitExceeded (active issue)
- [ ] See also: `security-lessons.md` L40 (rate limiting requires decorators, middleware, AND exception handler).

## Check 54: Router Registration Completeness
- [ ] List ALL Python files in `app/routers/` that define a `APIRouter` instance
- [ ] Verify EVERY router is `include_router`-ed in `main.py` or the ASGI entry point
- [ ] If a router exists in `app/routers/` but is NOT included in `main.py`, this is a BLOCKER
- [ ] Verify router prefixes match `api-spec.md` exactly (e.g., `/shipments` not `/shipment`)
- [ ] Verify the GraphQL router (`GraphQLRouter`) is included if `graphql.py` exists

**Source**: FB18 `main.py` only registered `auth_router`. Shipments, analytics, exceptions, and uploads routers were created but never registered, causing 404 on all core REST endpoints (H85)

## Check 55: Auth Response Contract Documentation
- [ ] `api-spec.md` MUST include an explicit "Auth Contracts" section with:
  - Login response JSON shape (exact keys: `access_token`, `token_type`, `role?`, `expires_in?`)
  - Register request JSON shape (exact keys: `email`, `password`, `company_name`, `role`)
  - JWT payload claims (exact keys: `sub`, `role`, `exp`, `iat`)
- [ ] Frontend login page MUST destructure only keys documented in the login response contract
- [ ] Frontend register page MUST send only keys documented in the register request contract
- [ ] Any mismatch between frontend expectation and backend response is a BLOCKER

**Source**: FB18 LoginPage expected `role` in login response (backend returned only `access_token` + `token_type`). RegisterPage sent `name` instead of `company_name`. No auth contract existed in api-spec.md (H86)

## Check 56: Zero Deprecation Warnings From Application Code
- [ ] Run `pytest tests/` and capture all warnings
- [ ] Filter for warnings originating from application code (not test frameworks, not dependencies)
- [ ] Pydantic class-based `Config` MUST NOT be used — use `ConfigDict` instead
- [ ] FastAPI `@app.on_event("startup")` / `@app.on_event("shutdown")` MUST NOT be used — use `lifespan` context managers instead
- [ ] Any deprecation warning from application code is an ISSUE (moderate severity)
- [ ] Any deprecation warning that will break on next major version is a BLOCKER

**Source**: FB20 embedded Pydantic V2 class-based `Config` in 4 files (`config.py`, `properties.py`, `leases.py`, `tenants.py`) and FastAPI `@app.on_event` in `main.py`. Neither foundation auditor nor security gate flagged these. They will break on Pydantic V3 / next FastAPI major.

## Check 57: Re-Audit Report Artifact Exists After Fix Wave
- [ ] After Phase 7 fix wave, a re-audit report MUST be written to the build directory
- [ ] The report lists every file modified during the fix wave
- [ ] For each modified file: PASS / ISSUE / BLOCKER with rationale
- [ ] The report explicitly states whether any regressions were introduced
- [ ] If no re-audit report exists, Phase 7 is NOT complete

**Source**: FB20 resolved 9 security findings in Phase 7, but no re-audit report file exists in the build directory. `meta-report.md` notes: "no re-audit report file exists... implying re-audit occurred, but no re-audit report file exists."

## Check 58: CORS Method and Header Wildcards
- [ ] Verify `allow_methods` and `allow_headers` in CORS middleware are not `"*"` when `allow_credentials=True`
- [ ] Explicit methods list (e.g., `["GET", "POST", "PUT", "DELETE", "PATCH"]` ) and explicit headers list required when credentials are enabled
- [ ] Socket.IO `cors_allowed_origins` must also use the same explicit allowlist, never `"*"`
- [ ] `Settings.CORS_ORIGINS` has no default wildcard; app refuses to start if CORS_ORIGINS is unset

**Source**: FB21 `main.py:37-38` used `allow_methods=["*"]` and `allow_headers=["*"]` with `allow_credentials=True`. Security gate Check #4 only verified origins, not method/header wildcards. Low severity but systemic coverage gap.


---

## Check 57: Phase 4 Exit Gate — Zero Test Failures Before Security/Integration
**Rationale**: Gym E16 (H106) found builds proceeding to Phase 5/6 with failing pytest tests. This wastes security and integration effort on broken code. The Phase 4 exit gate is now a HARD BLOCK in SKILL.md.

- [ ] Run `pytest tests/` — verify **zero failures**
- [ ] Run `vitest run` or `npm test` — verify **zero failures**
- [ ] Run `npm run build` — verify **zero errors**
- [ ] If ANY of the above report failures, **STOP**. Route to Phase 7 (Fix Wave). Do not proceed to Phase 5 (Security Gate) or Phase 6 (Integration Verification).

**Affected**: S5 (main agent), vsm_backend_tester, vsm_frontend_tester.
**Source**: Gym E16 (H106), FB20/FB21 fitness builds.

---

## Check 58: Phase 8b Verification — Meta-Report Completeness
**Rationale**: Gym E16 (H106) confirmed that skipping Phase 8b means process violations go undetected. But even when Phase 8b runs, S5 might accept an incomplete meta-report or write one manually. This check ensures the meta-reflection is genuine and actionable.

- [ ] `meta-report.md` exists in the build directory
- [ ] It was produced by `vsm_meta`, not written by S5 (verify "Agent Performance Scores" table exists)
- [ ] It contains a **Phase Audit** section with process violation analysis
- [ ] It contains **Hypotheses Generated** with at least one new falsifiable hypothesis
- [ ] It contains **Mutations Proposed** with tier classification (append-only / refinement / structural)
- [ ] All proposed mutations are tracked in `mutations-applied.md` with status (Applied / Deferred / Rejected / Overlooked)
- [ ] If any mutation status is `Overlooked`, STOP — apply the missed mutation before declaring build complete

**Affected**: S5 (main agent), vsm_meta.
**Source**: Gym E16 (H106), SKILL.md Phase 8b hard block.
