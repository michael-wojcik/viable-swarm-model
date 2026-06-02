# Cross-File Integration Verification Checklist

> **Mutation rules**: Append new checks discovered in the field. When adding a
> check, assign the next available number, include a severity label, and cite
> the source build/hypothesis. **If a check is a duplicate or near-duplicate of
> an existing check, MERGE it rather than append.** If a check applies only to
> a specific feature (GraphQL, WebSocket, etc.), add it to the relevant Tier 2
> group, NOT to Tier 1.

Run ALL Tier 1 checks before declaring integration complete.
Run ONLY the Tier 2 groups relevant to your build's features.

**Failure rule**: If ANY check fails, send back to responsible S1 for
correction BEFORE quality gates.

---

## Tier 1: Universal Checks (Run for ALL builds)

### Check 1: Export/Import Verification (ISSUE)
- [ ] Every exported utility/type is imported by at least one consumer file
- [ ] Every import statement resolves to an existing export
- [ ] No orphaned code — utilities that were created are actually used

### Check 2: Contract Consistency (BLOCKER)
- [ ] Shared contracts (types, interfaces) are consistently used across files
- [ ] No duplicate type definitions with different shapes

### Check 3: Entry Points (BLOCKER)
- [ ] Entry points (routes, main, index) import and register all middleware
- [ ] Every service has a verifiable entry point (Dockerfile CMD/ENTRYPOINT file exists)

### Check 4: Build Verification (BLOCKER)
- [ ] Codebase compiles/builds without errors
- [ ] No TypeScript/JavaScript syntax errors

### Check 5: Auth & Middleware (BLOCKER)
- [ ] Auth middleware raises HTTPException on failure, never returns `None` silently
- [ ] Document ownership filtering on ALL list endpoints
- [ ] Public DTOs omit answer/solution fields for game/quiz APIs
- [ ] Every REST list/detail endpoint has explicit auth guards or public documentation
- [ ] Unauthenticated REST endpoints do not expose draft/private data
- [ ] See also: `security-lessons.md` L38 (registration role elevation prevention).

### Check 6: File Structure (ISSUE)
- [ ] No orphaned utility files
- [ ] No empty files committed
- [ ] README has setup instructions

### Check 7: Parallel Agent Coordination (BLOCKER)
- [ ] Entry point files (main.py, App.tsx, server.ts) are modified by at most one agent per wave
- [ ] If multiple agents must contribute to entry points, a dedicated "wiring" agent runs last
- [ ] All imports in entry points resolve (no missing modules)

### Check 8: Auth Response Contract Documentation (BLOCKER)
- [ ] `api-spec.md` MUST include an explicit "Auth Contracts" section with:
  - Login response JSON shape (exact keys: `access_token`, `token_type`, `role?`, `expires_in?`)
  - Register request JSON shape (exact keys: `email`, `password`, `company_name`, `role`)
  - JWT payload claims (exact keys: `sub`, `role`, `exp`, `iat`)
- [ ] Backend implementation matches the documented contract exactly
- [ ] Frontend consumes only keys documented in the contract
- [ ] Any mismatch between frontend expectation and backend response is a BLOCKER

**Source**: FB18 LoginPage expected `role` in login response (backend returned only
`access_token` + `token_type`). RegisterPage sent `name` instead of `company_name`.
No auth contract existed in api-spec.md (H86).

### Check 9: Orphaned Exports / Dead Code Scan (ISSUE)
- [ ] Every exported function/class in backend is imported by at least one consumer file
- [ ] Every exported function/class in frontend is imported by at least one consumer file
- [ ] No duplicate implementations of the same utility in different files

### Check 10: Circular Import Prevention (BLOCKER)
- [ ] No router/module imports from `main.py` (or equivalent entry point)
- [ ] Shared singletons (limiter, config, database) live in dedicated modules, not in entry points
- [ ] After any fix agent adds cross-module imports, run `python -c "import app.main"` to verify
  no circular dependencies were introduced
- [ ] If fix introduces `from app.main import X` in a router, verify router is not imported by
  main.py at module level

**Source**: FB15 Fix Wave introduced circular import when wiring rate limiting (H70).

### Check 11: Post-Fix Security Re-Check (BLOCKER)
- [ ] After any fix wave that modified auth, GraphQL, or WebSocket files, re-run security
  checks on those specific files
- [ ] Verify auth middleware still raises on failure (never returns None)
- [ ] Verify GraphQL `get_context` still propagates exceptions (no broad `except` added)
- [ ] Verify WebSocket room handlers still verify session before room access
- [ ] If security regression is found, escalate to S5 immediately

### Check 12: Subprocess Import Verification (BLOCKER)
- [ ] After implementation wave and after fix wave, run
  `python -c "import app.main; import app.graphql; import app.sio"` (or equivalent
  entry points) in a subprocess
- [ ] If any module raises `NameError`, `ImportError`, or `ModuleNotFoundError`, treat as BLOCKER
- [ ] In-process code review (ReadFile) is insufficient — it does not catch missing imports
  that are only referenced at runtime

### Check 13: CORS Configuration Validation (HIGH)
- [ ] CORS origin is explicit allowlist, never `*` or `true` when `allow_credentials=True`
- [ ] `Settings.CORS_ORIGINS` has no default wildcard; app refuses to start if CORS_ORIGINS is unset
- [ ] FastAPI CORS middleware and Socket.io `cors_allowed_origins` use the same explicit allowlist
- [ ] `allow_methods` and `allow_headers` are not `"*"` when `allow_credentials=True`
- [ ] Explicit methods list and explicit headers list required when credentials are enabled
- [ ] See also: `security-lessons.md` L61 (CORS wildcard equivalence).

**Source**: FB21 `main.py:37-38` used `allow_methods=["*"]` and `allow_headers=["*"]` with
`allow_credentials=True`. Security gate Check #4 only verified origins, not method/header
wildcards (CORS coverage gap).

### Check 14: REST & GraphQL Auth RBAC Parity (BLOCKER)
- [ ] `api-spec.md` MUST include an explicit `RBAC: [roles]` array for every endpoint
  (e.g., `RBAC: ["admin", "auditor"]`). NEVER use ambiguous labels like
  "(owner-filtered)" without specifying which roles can access.
- [ ] GraphQL mutations enforce the SAME RBAC as REST endpoints
- [ ] GraphQL list queries apply the same ownership filtering as REST list endpoints
- [ ] GraphQL geo/spatial endpoints apply the same bounds caps as REST geo endpoints
- [ ] `viewer` cannot perform mutations that REST restricts to `admin` only
- [ ] If an endpoint has ownership filtering, the RBAC array shows WHO can access it,
  and a separate `Ownership: owner_id == current_user.id` note shows HOW results are filtered
- [ ] See also: `security-lessons.md` L38 (registration role elevation prevention).

**Source**: FB17 api-spec.md "(owner-filtered)" label caused GraphQL RBAC parity gap (H83).
FB24 GraphQL mutations lacked REST-equivalent role guards.

### Check 15: Runtime API Verification (BLOCKER)
- [ ] Before using framework-specific parameters (e.g., `strawberry.Schema(validation_rules=[...])`),
  verify with `help(Class.__init__)` or test invocation
- [ ] If parameter is not recognized, do NOT use it — find the correct API for the installed version
- [ ] This applies to Strawberry, FastAPI, SQLAlchemy, and any library with version drift

**Source**: FB15 agent used `validation_rules` parameter that doesn't exist in installed
strawberry-graphql (H72).

### Check 16: Cross-Layer Runtime Consistency (BLOCKER)
- [ ] **localStorage key parity**: grep ALL `localStorage.getItem/setItem/removeItem` calls.
  The token key name MUST match the auth router's response key exactly.
- [ ] **Celery broker URL**: grep ALL `Celery(` instantiations. The `broker=` parameter MUST use
  `get_settings().REDIS_URL` or equivalent settings reference. Hardcoded `redis://localhost:6379/0`
  is a BLOCKER.
- [ ] **Socket.IO namespace parity**: Backend `sio.py` namespace MUST match frontend
  `sio/client.ts` namespace.
- [ ] **JWT payload key parity**: If frontend destructures `role` from JWT payload, verify
  `create_access_token` includes `"role"` claim.

**Source**: FB17 integration found 3 BLOCKERs from cross-layer mismatches: localStorage key
mismatch, Celery broker hardcoded to localhost, orphaned queries.ts exports (H81).

### Check 17: Router Registration Completeness (BLOCKER)
- [ ] List ALL Python files in `app/routers/` that define an `APIRouter` instance
- [ ] Verify EVERY router is `include_router`-ed in `main.py` or the ASGI entry point
- [ ] Verify router prefixes match `api-spec.md` exactly (e.g., `/shipments` not `/shipment`)
- [ ] Verify the GraphQL router (`GraphQLRouter`) is included if `graphql.py` exists

**Source**: FB18 `main.py` only registered `auth_router`. Shipments, analytics, exceptions,
and uploads routers were created but never registered, causing 404 on all core REST endpoints (H85).

### Check 18: Zero Deprecation Warnings From Application Code (HIGH)
- [ ] Run `pytest tests/` and capture all warnings
- [ ] Filter for warnings originating from application code (not test frameworks, not dependencies)
- [ ] Pydantic class-based `Config` MUST NOT be used — use `ConfigDict` instead
- [ ] FastAPI `@app.on_event("startup")` / `@app.on_event("shutdown")` MUST NOT be used —
  use `lifespan` context managers instead
- [ ] Any deprecation warning from application code is an ISSUE
- [ ] Any deprecation warning that will break on next major version is a BLOCKER

**Source**: FB20 embedded Pydantic V2 class-based `Config` in 4 files and FastAPI `@app.on_event`
  in `main.py`. Neither foundation auditor nor security gate flagged these (H106-related).

### Check 19: Phase 4 Exit Gate — Zero Test Failures Before Security/Integration (BLOCKER)
- [ ] Run `pytest tests/` — verify **zero failures**
- [ ] Run `vitest run` or `npm test` — verify **zero failures**
- [ ] Run `npm run build` — verify **zero errors**
- [ ] If ANY of the above report failures, **STOP**. Route to Phase 7 (Fix Wave).
  Do not proceed to Phase 5 (Security Gate) or Phase 6 (Integration Verification).

**Affected**: S5 (main agent), vsm_backend_tester, vsm_frontend_tester.
**Source**: Gym E16 (H106), FB20/FB21 fitness builds.

### Check 20: Re-Audit Report Artifact Exists After Fix Wave (BLOCKER)
- [ ] After Phase 7 fix wave, a re-audit report MUST be written to the build directory
- [ ] The report lists every file modified during the fix wave
- [ ] For each modified file: PASS / ISSUE / BLOCKER with rationale
- [ ] The report explicitly states whether any regressions were introduced
- [ ] If no re-audit report exists, Phase 7 is NOT complete

**Source**: FB20 resolved 9 security findings in Phase 7, but no re-audit report file exists
in the build directory (H106-related).

### Check 21: Phase 8b Meta-Report Completeness (BLOCKER)
- [ ] `meta-report.md` exists in the build directory
- [ ] It was produced by `vsm_meta`, not written by S5 (verify "Agent Performance Scores"
  table exists)
- [ ] It contains a **Phase Audit** section with process violation analysis
- [ ] It contains **Hypotheses Generated** with at least one new falsifiable hypothesis
- [ ] It contains **Mutations Proposed** with tier classification
  (append-only / refinement / structural)
- [ ] All proposed mutations are tracked in `mutations-applied.md` with status
  (Applied / Deferred / Rejected / Overlooked)
- [ ] If any mutation status is `Overlooked`, STOP — apply the missed mutation before
  declaring build complete

**Affected**: S5 (main agent), vsm_meta.
**Source**: Gym E16 (H106), SKILL.md Phase 8b hard block.

### Check 22: Auth Role Parity Between data-model.md and auth.py (BLOCKER)
- [ ] Read `data-model.md` and identify the `Role` / `UserRole` enum values
- [ ] Read `auth.py` and identify `ALLOWED_ROLES` (or equivalent role-based access control list)
- [ ] Verify EVERY role in `ALLOWED_ROLES` exists in the `data-model.md` enum
- [ ] Verify no enum values are missing from `ALLOWED_ROLES` if they represent valid user roles
- [ ] Mismatched roles (e.g., `"editor"` in allowlist but `"responder"` in enum) are a BLOCKER

**Source**: FB22 `auth.py` had `ALLOWED_ROLES = ["viewer", "editor", "admin"]` but data model
defined `"viewer"`, `"responder"`, `"admin"`. `"editor"` did not exist; `"responder"` was missing (H151).

### Check 23: Dependency Verification Against requirements.txt (BLOCKER)
- [ ] Grep ALL backend Python files for `import` and `from ... import` statements
- [ ] For every third-party import (not `typing`, `datetime`, `os`, `json`, etc.), verify the
  package name appears in `requirements.txt`
- [ ] If a package is imported but NOT in `requirements.txt`, this is a BLOCKER
- [ ] Common trap packages to watch for: `strawberry_sqlalchemy_mapper`, `sqlalchemy_strawberry`,
  `fastapi_graphql_auto`
- [ ] If GraphQL is used, verify `strawberry-graphql` is in `requirements.txt` and imports cleanly

**Source**: FB22 `graphql.py` agent imported `strawberry_sqlalchemy_mapper` (not in requirements.txt),
causing ~15 min agent timeout before S5 intervention (H150).

### Check 24: Dependency Manifest-Environment Parity (BLOCKER)
- [ ] After any Phase 0 environment fix (e.g., upgrading a package to resolve an incompatibility),
  verify `requirements.txt` / `package.json` reflects the resolved version
- [ ] Run `pip install -r requirements.txt` (or `npm ci`) in a fresh environment and verify
  the app imports cleanly
- [ ] If the manifest specifies an incompatible version, treat as BLOCKER

**Source**: FB23 Phase 0 upgraded `strawberry-graphql` from 0.235.2 → 0.316.0 but `requirements.txt`
still specified 0.235.2, causing clean-install failures.

---

## Tier 2: Conditional Checks (Run only if feature exists)

> Read ONLY the sections relevant to your build. Skip all others.

### WebSocket (run if `sio.py` or Socket.IO exists)

#### Check 25: WebSocket Event Contracts (BLOCKER)
- [ ] Every backend `emit` has matching frontend listener (and vice versa)
- [ ] WebSocket message shape: `kind` field values match exactly between backend and frontend
- [ ] Shared event constants file exists and is imported by both sides
- [ ] `api-spec.md` WebSocket event names match `sio.py` emit/handler names
- [ ] `sio.py` emit names match `shared/sio-events.ts` constant values
- [ ] `shared/sio-events.ts` constants are imported by both backend and frontend
- [ ] For every event the frontend listens for, the backend emits it at least once
- [ ] Event name strings match exactly (case-sensitive)
- [ ] **Socket.IO server instance reuse**: The ASGI entry point (`realtime.py`) imports and
  reuses the SAME `sio` instance that event handlers are registered on in `sio.py`.
  Creating a new `AsyncServer` in `realtime.py` breaks all WS handlers.

#### Check 26: WebSocket Authentication & Authorization (BLOCKER)
- [ ] WebSocket room subscription handlers (`subscribe_patient`, etc.) verify the socket has
  authenticated BEFORE allowing room access
- [ ] WebSocket room unsubscription handlers verify the socket session before leaving a room
- [ ] Socket.io `cors_allowed_origins` uses the same explicit allowlist as HTTP CORS middleware,
  never `"*"`
- [ ] Backend `authenticate` event stores user session; all subsequent room operations read
  and validate that session
- [ ] WebSocket room handlers verify the user is ENROLLED in the target course (or is the
  instructor/admin) before allowing room access. Session auth alone is insufficient.
- [ ] Browser WebSocket auth uses path-based tokens (NOT query params) when headers are impossible
- [ ] Backend validates token from path parameter before accepting connection
- [ ] Token is short-lived (≤15 min) and scoped to the specific resource
- [ ] `api-spec.md` explicitly documents the WebSocket auth handshake: connect → auth event →
  payload shape → server response → room join
- [ ] Frontend and backend use the SAME auth mechanism (either Socket.IO `auth` option OR custom
  `authenticate` event, not both)
- [ ] Backend rejects all room operations until auth handshake completes

**Source**: FB17 `security-lessons.md` L57 (GraphQL subscription resolvers must verify resource
ownership before yielding) for the same underlying principle.

### GraphQL (run if `graphql.py` or Strawberry exists)

#### Check 27: GraphQL Schema Contracts (BLOCKER)
- [ ] SDL types match TypeScript payload types
- [ ] Every subscription has matching resolver with `subscribe` returning AsyncIterable
- [ ] @graphql-depth-limit installed (max 10) + complexity analysis
- [ ] Run `python -c "from app.graphql import schema; print(schema)"` to introspect the actual
  GraphQL schema
- [ ] GraphQL schema field names (after auto-camelCase from Strawberry) match frontend query
  field names exactly
- [ ] Frontend queries MUST use camelCase, not snake_case, when the backend uses Strawberry
- [ ] Every field queried by frontend exists in the backend schema
- [ ] No frontend queries reference fields that were renamed or removed in backend
- [ ] For EVERY frontend mutation, verify input argument types match the introspected schema
  EXACTLY (e.g., `DateTime` vs `String`, `Int` vs `Float`)
- [ ] Cross-check against api-spec.md: if spec says `String` but schema says `DateTime`, it is a BLOCKER
- [ ] GraphQL enum values returned to the client match the values expected by frontend TypeScript unions
- [ ] For Strawberry: `strawberry.enum` member names (which become GraphQL enum values) must match
  frontend enum literals exactly
- [ ] Changing GraphQL enum definitions must trigger synchronized updates to frontend queries,
  tests, and shared types
- [ ] `GraphQLRouter` is mounted with `context_getter=get_context` so auth context propagates
  to resolvers
- [ ] GraphQL `get_context` or equivalent context builders MUST propagate auth exceptions
  (JWT errors, missing tokens). Never silently catch auth exceptions and return an anonymous
  context. Auth failures MUST result in GraphQL errors or `AuthenticationError`, not `user = None`
- [ ] See also: `security-lessons.md` L63 (GraphQL context builders must be fail-closed).

**Source**: FB15 coordinator verified field names but missed String vs DateTime input type trap (H68).
FB17 field-name-only verification missed argument type mismatches.

#### Check 28: GraphQL Enum Runtime Safety (BLOCKER)
- [ ] Python enums used in GraphQL schemas use `str, enum.Enum` (or equivalent) when their
  values are strings
- [ ] Enum construction from database string values does not raise `ValueError`

#### Check 29: Apollo Client Usage Verification (ISSUE)
- [ ] If `main.tsx` wraps the app in `ApolloProvider`, verify at least ONE page component uses
  `useQuery` or `useMutation` from `@apollo/client`
- [ ] If ZERO pages use Apollo Client, either: (a) remove ApolloProvider and graphql dependencies,
  or (b) migrate data-fetching pages from REST `fetch()` to Apollo Client
- [ ] REST `fetch()` is acceptable for: file uploads (multipart/form-data), auth endpoints
  (login/register/refresh), and health checks
- [ ] GraphQL queries in `queries.ts` that are never imported by any page/component are dead code

**Source**: FB17 frontend initialized ApolloProvider but all pages used REST fetch();
queries.ts was completely orphaned (H84).

### Frontend (run if React/Vite/TypeScript frontend exists)

#### Check 30: Frontend Scaffolding (BLOCKER)
- [ ] `package.json` exists
- [ ] `vite.config.ts` exists (with path alias)
- [ ] `tsconfig.json` exists
- [ ] `index.html` exists
- [ ] `src/main.tsx` (or equivalent) exists
- [ ] `src/App.tsx` exists

#### Check 31: Frontend Paths & Config (ISSUE)
- [ ] Frontend relative path to shared types: `../../shared/` not `../shared/` in monorepos
- [ ] Vite/Webpack proxy config includes `/api`, `/graphql`, `/ws`, `/tiles` paths
- [ ] GraphQL subscriptions need `ws: true` in proxy config
- [ ] Vite path alias configured for shared types (e.g., `@flux/shared`)
- [ ] **Config key name parity**: Every `getattr(settings, "KEY_NAME")` or `settings.KEY_NAME`
  reference in the codebase must match an actual field defined in the Settings/Pydantic class.
  Name drift silently breaks functionality.

#### Check 32: Frontend Build Script Verification (BLOCKER)
- [ ] Run `npm run build` (or equivalent package.json script), not just the underlying tool
  (`vite build`, `next build`, etc.)
- [ ] Package.json scripts may include additional type-checking or linting steps that
  `vite build` alone does not exercise
- [ ] Verify `tsconfig.json` includes all necessary types (e.g., `@types/node` for `vite.config.ts`)

#### Check 33: Frontend Config Fallback Check (HIGH)
- [ ] No `||` fallbacks in frontend API/WS/GraphQL config files (`src/graphql/client.ts`,
  `src/sio/client.ts`, etc.)
- [ ] All API URLs are required build-time env vars with no localhost fallback
- [ ] Missing env vars cause build-time failure, not silent fallback to localhost
- [ ] See also: `security-lessons.md` L62 (frontend API URL fallback ban).

#### Check 34: Frontend Cross-File Import Resolution (BLOCKER)
- [ ] After all parallel frontend implementation agents complete, run `npx tsc --noEmit`
  (or `vite build`) to verify all cross-file imports resolve
- [ ] Every export from `queries.ts` MUST be imported by at least one page or component
- [ ] Every field destructured from Zustand stores MUST exist in the store's type definition
- [ ] Every type imported from `shared/types.ts` MUST be defined in that file

#### Check 35: Frontend `as any` Anti-Pattern (ISSUE)
- [ ] Scan all `.tsx` and `.ts` files for `as any` casts
- [ ] Every `as any` must have a comment explaining why type safety is intentionally bypassed
- [ ] `as any` used to destructure store fields is a BLOCKER — the store schema must be updated
  instead
- [ ] Run `tsc --noEmit` after removing `as any` to verify no hidden contract mismatches

**Source**: FB15 frontend agent used `useEventStore() as any` to hide missing `salesMetrics`
field (H71).

#### Check 36: Vite Proxy Port Verification (BLOCKER)
- [ ] Vite proxy target ports must match the actual exposed ports in docker-compose.yml
- [ ] `/api` and `/graphql` proxy targets must match the API service port (e.g., 8000)
- [ ] `/ws` proxy target must match the realtime service port (e.g., 8001)
- [ ] Never proxy to a default port (e.g., 4000) unless that port is explicitly exposed in docker-compose

#### Check 37: Vite Alias Key Verification (BLOCKER)
- [ ] Read `vite.config.ts` and inspect `resolve.alias`
- [ ] The alias key MUST be `"@"` mapping to `path.resolve(__dirname, "./src")`
- [ ] The alias key `"@/"` mapping to `./src/` is a BLOCKER — it works in dev but fails in
  production builds because Rollup does not match the trailing slash
- [ ] Verify `tsconfig.json` `paths` aligns with the Vite alias (e.g., `"@/*": ["src/*"]`)

**Source**: FB22 `vite.config.ts` used `"@/"` → `./src/`; `npm run build` failed with Rollup
resolution error (H153).

#### Check 38: Frontend Page Data Fetching Verification (BLOCKER)
- [ ] Every page component contains at least one live data fetch (GraphQL query, REST fetch,
  or store subscription) that renders actual data
- [ ] Stub pages (`<div>Label</div>` with void imports) are BLOCKERs

**Source**: FB24 stub pages detected — pages had import statements but no actual data fetching (H158).

#### Check 39: Frontend Dockerfile Build Args (ISSUE)
- [ ] `VITE_API_URL` and `VITE_WS_URL` passed as `ARG` in frontend Dockerfile
- [ ] Runtime env vars are not silently baked as `undefined` into static bundles

### ORM / Database (run if SQLAlchemy, Prisma, or pgvector exists)

#### Check 40: Prisma / ORM (BLOCKER)
- [ ] Relation names match on both sides (`@relation("Name")`)
- [ ] N+1 queries prevented (selectinload for relationships, batched GROUP BY for computed fields)

#### Check 41: SQLAlchemy Engine Configuration (BLOCKER)
- [ ] `models.py` does NOT hardcode database connection strings at module level
- [ ] Engine is created from `get_settings().DATABASE_URL` or uses a lazy factory pattern
- [ ] Engine creation does not trigger side effects at import time

#### Check 42: Model-Spec Alignment Check (BLOCKER)
- [ ] SQLAlchemy/model field names match `data-model.md` exactly
- [ ] SQLAlchemy/model field types match `data-model.md` exactly
- [ ] All entities in `data-model.md` are represented in the ORM models
- [ ] All relationships and constraints from `data-model.md` are implemented
- [ ] If `data-model.md` does not exist, skip this check

#### Check 43: pgvector Pipeline (ISSUE)
- [ ] PostgreSQL vector extension enabled
- [ ] VECTOR(N) column matches embedding dimensions
- [ ] ivfflat index with `vector_cosine_ops` exists
- [ ] Embeddings generated before INSERT/UPDATE

### Infrastructure & DevOps (run if Docker, Redis, Celery, or rate limiting exists)

#### Check 44: Docker Compose (BLOCKER)
- [ ] All services have verifiable entry points (CMD/ENTRYPOINT file exists)
- [ ] Environment variable names match exactly across docker-compose/.env/code
- [ ] No `||` fallbacks for SECRET/KEY/PASSWORD/TOKEN variables

#### Check 45: Docker-Compose Command Module Verification (BLOCKER)
- [ ] For every `command:` or `CMD` in `docker-compose.yml` that references a Python module
  (e.g., `celery -A app.celery_app`), verify the module path matches the actual file layout
  inside the container
- [ ] If the Dockerfile `WORKDIR` is `/app` and the module is `celery_app.py` at the root,
  the correct command is `celery -A celery_app`, NOT `celery -A app.celery_app`
- [ ] Mismatched module paths are a BLOCKER — the container crashes on startup

**Source**: FB23 `docker-compose.yml` referenced `celery -A app.celery_app` but the module was
`celery_app.py` with no `app/` package.

#### Check 46: Redis Queue (BLOCKER)
- [ ] Queue name consistent between API `lpush` and worker `brpop`
- [ ] Worker re-enqueues dependents after completion
- [ ] Redis pub/sub channel names match between producer and consumer

#### Check 47: Rate Limit Exception Handler (BLOCKER)
- [ ] If `SlowAPIMiddleware` is installed, verify `app.add_exception_handler(RateLimitExceeded, handler)`
  or equivalent `@app.exception_handler(RateLimitExceeded)` exists
- [ ] Without an exception handler, rate-limited requests crash with unhandled exception instead
  of returning HTTP 429
- [ ] The handler MUST return JSON with `{"error": "Rate limit exceeded"}` and status 429

**Source**: FB17 backend installed SlowAPIMiddleware but lacked exception handler for
RateLimitExceeded (active issue).
- [ ] See also: `security-lessons.md` L40 (rate limiting requires decorators, middleware, AND
  exception handler).

### Domain-Specific (run if feature exists)

#### Check 48: Server-Sent Events (SSE) (ISSUE)
- [ ] Backend uses `StreamingResponse(media_type="text/event-stream")`
- [ ] Backend yields `data: {json}\n\n` format
- [ ] Frontend uses `getReader()` + `TextDecoder`, not EventSource
- [ ] Frontend splits on `"\n\n"` to extract messages
- [ ] Short-lived SSE token exchange implemented (never long-lived JWT in URL)

#### Check 49: CRDT Persistence (ISSUE)
- [ ] Yjs PersistenceAdapter connected to doc `update` event
- [ ] BYTEA column exists in PostgreSQL
- [ ] Load path SELECTs + applies updates in chronological order (`ORDER BY created_at`)

#### Check 50: DAG Validation (BLOCKER)
- [ ] `validate()` called on every create/update/execute
- [ ] 3-color DFS (WHITE/GRAY/BLACK) for cycle detection
- [ ] Kahn's algorithm for topological sort determines execution order

#### Check 51: State Machine Domain Alignment (BLOCKER)
- [ ] Backend state machine enum values match frontend TypeScript union types exactly
- [ ] Every state value emitted by backend is handled by frontend switch/case
- [ ] No frontend-only states that backend never emits (causes unreachable code)

#### Check 52: Case-Sensitive Enum Alignment (BLOCKER)
- [ ] GraphQL enum values match TypeScript union types exactly (including case)
- [ ] Backend string literals match frontend string literals exactly
- [ ] Shared constants file is the single source of truth for enum values

#### Check 53: Mobile / Game UI (LOW)
- [ ] 60px minimum button height
- [ ] Dark theme (#0f172a) for OLED
- [ ] Tested at 375px viewport

### Language-Specific (run if language exists)

#### Check 54: Rust Workspace (ISSUE)
- [ ] Workspace `Cargo.toml` includes ALL member crates
- [ ] No duplicate imports between `lib.rs` and local paths in same file
- [ ] Integration tests in `tests/` import from library path, not local modules

#### Check 55: Go JSON Tags (ISSUE)
- [ ] All JSON tags are camelCase (`json:"camelCase"`)
- [ ] No snake_case leaking to frontend via struct tags
