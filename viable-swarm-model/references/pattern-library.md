# Proven Pattern Library

> **Mutation rules**: Append new patterns; mark obsolete patterns with
> `~~strikethrough~~` and rationale. Never delete — the log of what stopped
> working is as valuable as what currently works.

---


## Table of Contents

- [Foundation](#foundation)
- [Backend](#backend)
- [Frontend](#frontend)
- [Real-Time](#real-time)
- [Cross-Language](#cross-language)
- [Testing](#testing)
- [Game](#game)
- [GraphQL](#graphql)
- [Full-Stack](#full-stack)
- [Infrastructure](#infrastructure)
- [GraphQL & Real-Time](#graphql-&-real-time)
- [Process Patterns](#process-patterns)
  - [Pattern 22: Foundation Wave Sequencing](#pattern-22-foundation-wave-sequencing-for-multi-service-projects)
  - [Pattern 44: Pseudo-Recursion](#pattern-44-pseudo-recursion--internal-agent-self-regulation)
  - [FB17 Patterns](#fb17-patterns)

---
## Foundation

### 1. Foundation-First Wave Execution
**Trigger**: Starting any multi-file implementation.  
**Solves**: Downstream agents guessing at interfaces because types/config don't exist.  
**Implementation**: Spawn types, models, config, utils in Wave 1 before implementation in Wave 2. Creates stable contracts.

### 2. Entry Point Wiring (MANDATORY)
**Trigger**: After Wave 2 (foundation), before Wave 3 (features).  
**Solves**: Services that compile but have no runnable entry point.  
**Implementation**: Create main.go/server.ts and App.tsx with full routing. Entry points are NOT optional.

### 3. Frontend Scaffolding as Creation Requirement (ACTIVE)
**Trigger**: Any frontend agent creates components.  
**Solves**: Missing config files discovered during verification.  
**Implementation**: Agent MUST also create package.json, vite.config.ts (with path alias), tsconfig.json, tsconfig.node.json, index.html. Verification is too late — creation is required.

---

## Backend

### 4. asyncHandler Pattern B (Controllers Self-Wrap)
**Trigger**: Express/Fastify route handlers use async functions.  
**Solves**: Unhandled promise rejections crashing the server.  
**Implementation**: Controllers wrap exported functions: `export const getAll = asyncHandler(async (req, res) => {...})`. Route files pass controller functions directly.

### 5. PostGIS Stored Procedures for Geospatial API
**Trigger**: API serves spatial data.  
**Solves**: Repeated complex spatial queries in application code.  
**Implementation**: Define SQL functions for insert (ST_GeomFromGeoJSON), radius search (ST_DWithin), bounding box (&&), MVT tiles (ST_AsMVT), full-text search (to_tsvector + ts_rank), aggregate stats.

### 6. Dynamic MVT Tile Generation from PostGIS
**Trigger**: Map frontend needs vector tiles.  
**Solves**: Serving pre-generated tiles is storage-expensive; on-the-fly generation is CPU-expensive without optimization.  
**Implementation**: `mvt_tile(z, x, y, layer_name)` with ST_TileEnvelope, ST_AsMVTGeom, ST_AsMVT. Endpoint: `application/x-protobuf`, 204 for empty tiles, Cache-Control max-age=3600.

### 7. Python dataclasses-json with CamelCase for TypeScript Interop
**Trigger**: Python backend serves TypeScript frontend.  
**Solves**: snake_case Python leaking into camelCase frontend.  
**Implementation**: `@dataclass_json(letter_case=LetterCase.CAMEL)` auto-serializes. Lighter than Pydantic for simple DTOs.

### 8. Apollo Server v4 with graphql-ws for Subscriptions
**Trigger**: GraphQL subscriptions needed.  
**Solves**: subscriptions-transport-ws is deprecated and buggy.  
**Implementation**: Use graphql-ws. Split link: HTTP for queries, GraphQLWsLink for subscriptions. Redis pub/sub for scaling.

### 9. pgvector for Semantic Document Search with OpenAI Embeddings
**Trigger**: Document search needs semantic similarity.  
**Solves**: Keyword search misses conceptual matches.  
**Implementation**: text-embedding-3-small (1536 dims) in VECTOR(1536). ivfflat index with vector_cosine_ops. Similarity: `1 - (embedding <=> query_embedding)`. Hybrid: 70% semantic + 30% ts_rank.

### 10. Server-Sent Events (SSE) for AI Response Streaming
**Trigger**: Streaming LLM responses to frontend.  
**Solves**: WebSocket is overkill for one-way server→client streams.  
**Implementation**: FastAPI StreamingResponse with `media_type="text/event-stream"`, yield `data: {json}\n\n`. Frontend: fetch + response.body.getReader + TextDecoder, split on `"\n\n"`. Use POST (not EventSource which only supports GET).

### 11. Redis Task Queue with Async Worker and Dependent Enqueuing
**Trigger**: Background job processing with DAG dependencies.  
**Solves**: Simple queues don't handle "start job B only after job A finishes."  
**Implementation**: Redis lists as queue. API lpush, worker brpop. After task completes, load DAG, check prerequisites with _can_run(), enqueue dependents. Redis pub/sub for SSE progress.

### 12. DAG Stored as JSONB in PostgreSQL with Validation
**Trigger**: Workflow/pipeline execution with dependencies.  
**Solves**: Cycles and invalid topologies cause infinite loops or incorrect execution order.  
**Implementation**: Store nodes/edges arrays. Validate with 3-color DFS (WHITE/GRAY/BLACK) for cycle detection, Kahn's algorithm for topological sort. validate() returns (is_valid, error_messages).

### 13. Rust lib.rs + main.rs for Testable Binaries
**Trigger**: Rust CLI or service with integration tests.  
**Solves**: Integration tests cannot import from binary crates.  
**Implementation**: lib.rs re-exports all modules (`pub mod`). main.rs imports from crate library name. Integration tests in `tests/` import from same library path. Never mix local module imports with library imports in same file.

---

## Frontend

### 14. Canvas Rendering with React
**Trigger**: Game, chart, or image editor in React.  
**Solves**: React state updates are too slow for 60fps rendering.  
**Implementation**: Ref-based approach. Game state via refs (not React state). Canvas runs own requestAnimationFrame loop imperatively. React components provide UI shell only. Separate Canvas renderer from React UI components.

### 15. Vite Path Alias for Shared Types (Preferred over Relative)
**Trigger**: Monorepo with shared types package.  
**Solves**: `../../shared/` breaks when files move.  
**Implementation**: `resolve: { alias: { '@flux/shared': path.resolve(__dirname, '../shared/src') } }`. Verify: `grep -r "from.*\.\./.*shared"` returns nothing.

### 16. TipTap v2 Rich Text Editor with AI Integration
**Trigger**: Rich text editing with AI-assisted features.  
**Solves**: Building a rich text editor from scratch is error-prone.  
**Implementation**: `@tiptap/react`, `@tiptap/starter-kit`, `@tiptap/extension-placeholder`. useEditor() hook. `editor.getJSON()` for PostgreSQL JSONB persistence. BubbleMenu for inline AI actions.

### 17. D3.js v7 Interactive DAG Visualization with Drag and Connect
**Trigger**: Visual workflow editor or node graph.  
**Solves**: Complex graph visualization from scratch.  
**Implementation**: SVG nodes as colored rectangles, cubic bezier edges with arrowhead markers. d3-drag for dragging. Click-to-connect: first click source, second click target creates edge. d3.zoom for pan/zoom. Context menu on right-click.

### 18. Mobile-First Real-Time Game UI
**Trigger**: Game or real-time app with mobile users.  
**Solves**: Desktop-first designs fail on mobile.  
**Implementation**: 60px minimum button height, 160px+ countdown font, dark theme (#0f172a) for OLED, 375px test viewport. Player interfaces mobile-native; admin dashboards desktop-optimized.

---

## Real-Time

### 19. Raw WebSocket Event Constants (Non-Socket.io)
**Trigger**: Custom WebSocket implementation (not Socket.io).  
**Solves**: Single-character event name mismatch = silent failure.  
**Implementation**: Shared file with ALL event names as typed constants. Both backend (emit) and frontend (onmessage) MUST import. Manual JSON parsing means single-char mismatch = silent failure.

### 20. Socket.io v4 Rooms for Game Session Isolation
**Trigger**: Multiplayer game or session-based real-time app.  
**Solves**: Broadcasts leak across sessions.  
**Implementation**: One room per game session via `socket.join(join_code)`. Broadcasts target room only. Room cleanup on disconnect prevents memory leaks.

### 21. Server-Authoritative Countdown Timer as Asyncio Task
**Trigger**: Game or timed quiz needs synchronized countdown.  
**Solves**: Client clocks drift; client-side countdowns desync.  
**Implementation**: Timer runs server-side via `asyncio.create_task`, sleeps 1-second increments, broadcasts `countdown_tick`. Cancel via `asyncio.Event` or `task.cancel()`. Server time is sole truth.

### 22. FeedMessage Discriminated Union for WebSocket Contract
**Trigger**: Multiple message types over same WebSocket connection.  
**Solves**: Message parsing without type safety leads to runtime errors.  
**Implementation**: Envelope with `kind` field (TELEMETRY, ALERT, etc.). Both sides share `FeedMessage` type. Backend serializes as JSON text frames, frontend parses and switches on `kind`.

### 23. Yjs CRDT Persistence via PostgreSQL BYTEA
**Trigger**: Collaborative editing with offline support.  
**Solves**: Conflict resolution in concurrent document editing.  
**Implementation**: Store Uint8Array updates in BYTEA column. `yjs_updates` table: (doc_id, update_data, created_at). Reconstruct: SELECT all ORDER BY created_at, then Y.applyUpdate(). Provides conflict resolution, offline support, incremental sync.

### 24. Optimistic Update Engine with Rollback
**Trigger**: UI needs immediate feedback on user actions.  
**Solves**: Network latency makes UI feel sluggish.  
**Implementation**: Apply changes to Apollo cache immediately before server responds. Capture original state for rollback. Track pending operations. Clear all pending on disconnect.

---

## Cross-Language

### 25. Go JSON Tags for Cross-Language Alignment
**Trigger**: Go backend serves TypeScript frontend.  
**Solves**: Go's default snake_case leaks into frontend's camelCase.  
**Implementation**: Always camelCase JSON tags: `json:"camelCase"`. Verify Phase 4 by comparing Go struct tags against TypeScript interfaces.

### 26. Python dataclasses-json CamelCase
**Trigger**: Python backend serves TypeScript frontend.  
**Solves**: Python snake_case leaks into frontend.  
**Implementation**: `@dataclass_json(letter_case=LetterCase.CAMEL)` for Python backends serving TypeScript frontends.

---

## Testing

### 27. Deterministic Mock Embeddings for Testing Without API Keys
**Trigger**: Testing vector search or semantic similarity.  
**Solves**: Tests require OpenAI API keys and make real network calls.  
**Implementation**: Pseudo-random embeddings seeded by hash of input text. `hashlib.md5(text.encode())` seeds deterministic function. Tests run without API keys, identical text = identical vectors.

---

## Game

### 28. Game Engine as Foundation
**Trigger**: Building a multiplayer or real-time game.  
**Solves**: Game logic scattered across API/WebSocket layers.  
**Implementation**: Game engine (tick loop, physics, state management) built in Wave 1 as foundation. All other components (WebSocket hub, matchmaking, API) depend on engine types/interfaces.

### 29. FeedMessage Discriminated Union
**Trigger**: Game server sends multiple event types.  
**Solves**: Type-unsafe message handling.  
**Implementation**: See Pattern #22.

---

## GraphQL

### 30. Apollo Server v4 with graphql-ws
**Trigger**: GraphQL API with subscriptions.  
**Solves**: Deprecated subscription transport.  
**Implementation**: See Pattern #8.

### Pattern: Runtime Framework API Verification
**When**: Any agent documents or uses framework-specific parameters (e.g., `strawberry.Schema(validation_rules=[...])`, `socketio.AsyncServer(...)`).
**What**: Before embedding a parameter in design docs or code, verify it exists in the installed version via `python -c "help(Class.__init__)"` or test invocation.
**Why**: Framework versions drift. `DepthLimitExtension` becomes `QueryDepthLimiter`; `validation_rules` parameter disappears; `@app.on_event` becomes `lifespan`. Agents that copy parameters from documentation or prompts without runtime verification produce `TypeError` on import.
**How**:
1. Before documenting framework-specific parameters in `api-spec.md`, run `python -c "import module; help(Class.__init__)"`
2. If the parameter is not recognized, do NOT use it — find the correct API for the installed version
3. This applies to Strawberry, FastAPI, SQLAlchemy, Socket.IO, and any library with version drift
**Source**: FB12 agent assumed `DepthLimitExtension` and `QueryComplexityExtension` existed; installed version only had `QueryDepthLimiter` (H55). FB15 agent used `validation_rules` parameter that doesn't exist in installed strawberry-graphql (H72). FB20 embedded Pydantic class-based `Config` and FastAPI `@app.on_event` that will break on next major version (H96).
**See also**: `references/hypotheses.md` H55, H72, H96.

---

## Full-Stack

### 31. Frontend Scaffolding Active Creation
**Trigger**: Any frontend work begins.  
**Solves**: Missing config files discovered too late.  
**Implementation**: See Pattern #3.

### 32. Verify Frontend Scaffolding in Phase 4
**Trigger**: After frontend implementation wave.  
**Solves**: Config files missing despite active creation.  
**Implementation**: Even with active creation, Phase 4 MUST verify: package.json, vite.config.ts (with path alias), tsconfig.json, index.html, src/main.tsx, src/App.tsx exist.

---

## Infrastructure

### 33. PostGIS Dynamic MVT
**Trigger**: Map tiles from spatial database.  
**Solves**: Pre-rendering tiles is inflexible.  
**Implementation**: See Pattern #6.

### 34. Redis Dependent Enqueuing
**Trigger**: Job workflows with prerequisites.  
**Solves**: Race conditions in multi-step background jobs.  
**Implementation**: See Pattern #11.

### 35. D3.js Interactive DAG
**Trigger**: Visual node editor.  
**Solves**: Building graph visualization from scratch.  
**Implementation**: See Pattern #17.

### 36. Mobile-First Game UI
**Trigger**: Real-time game with mobile players.  
**Solves**: Desktop-first design fails on phones.  
**Implementation**: See Pattern #18.

### 37. Rust Testable Binaries
**Trigger**: Rust project needs integration tests.  
**Solves**: Binary crates cannot be imported by tests.  
**Implementation**: See Pattern #13.

### 38. Browser WebSocket Auth via URL Path Token
**Trigger**: WebSocket endpoint needs auth but browser `WebSocket` API cannot set custom headers.  
**Solves**: JWT leakage in URL query params (security anti-pattern) vs. impossible header auth.  
**Implementation**: Use route `/ws/resource/{id}/{token}` where `{token}` is a short-lived JWT. Backend validates token from path param. NOT a query param — query params are logged by proxies; path segments are less commonly logged.  
**Example**: `backend/app/websockets/yjs.py` + `frontend/src/hooks/useYjs.ts` in FB1.  
**Caveat**: Token may still appear in server access logs. Ensure log sanitization for WS endpoints.

### 39. Alias SQLAlchemy Imports in Model Files
**Trigger**: SQLAlchemy models define columns whose names shadow imported functions (`text`, `select`, `join`).  
**Solves**: `TypeError: 'MappedColumn' object is not callable` when `sqlalchemy.text` is shadowed by a column named `text`.  
**Implementation**: Alias imports at the top of model files: `from sqlalchemy import text as sa_text, select as sa_select`. Use `sa_text("...")` throughout the file.  
**Example**: FB2 `backend/app/models.py` — `Question.text` shadowed `sqlalchemy.text`, crashing imports.

### 40. Validate Spatial Query Parameters with Upper Bounds
**Trigger**: API accepts geospatial query parameters (`radius_meters`, `bbox`).  
**Solves**: Unbounded spatial queries are a DoS vector — scanning an entire PostGIS table with `ST_DWithin(..., 99999999)`.  
**Implementation**: Enforce `_MAX_RADIUS_METERS = 50_000` (50km) and return HTTP 400 if exceeded. For bbox, reject areas exceeding a threshold (e.g., 10,000 km²).  
**Example**: FB2 `backend/app/routers/geo.py` initially accepted arbitrary `radius_meters`.

### 41. Lazy Pydantic Settings Factory for Testability
**Trigger**: Backend uses Pydantic Settings for configuration.  
**Solves**: Module-level `settings = Settings()` crashes on import without env vars, blocking test discovery and CI execution.  
**Implementation**: Use a lazy factory pattern:
```python
_settings: Settings | None = None

def get_settings() -> Settings:
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
```
Never instantiate at module level. This allows tests to import modules and mock config.
**Example**: FB3 tester agent timed out after 1800s because `config.py` crashed on import.
**Affected**: S1-Backend, vsm_tester.

---

## GraphQL & Real-Time

### 42. Strawberry `str, enum.Enum` for String-Valued GraphQL Enums
**Trigger**: Backend defines GraphQL enums that map to database string columns.  
**Solves**: `ValueError` when constructing `enum.Enum` from a string value (e.g., `Role("commander")` fails on `enum.Enum` but works on `str, enum.Enum`).  
**Implementation**: Define enums as `class Role(str, enum.Enum): COMMANDER = "commander"`. Document this requirement in `api-spec.md` so implementation agents follow it.
**Source**: Fitness build FB5. Coordinator caught `enum.Enum` runtime bug in `graphql.py`.

### 43. Extract Shared Singletons to Dedicated Modules
**Trigger**: Multiple modules need access to the same stateful singleton (limiter, config, event bus).  
**Solves**: Circular imports when routers import from `main.py` to access the singleton.  
**Implementation**: Create `app/limiter.py`, `app/events.py`, etc. Entry point (`main.py`) imports from these modules; routers also import from these modules. Never import from the entry point.
**Source**: Fitness build FB5. `auth.py` imported `limiter` from `main.py`, causing circular import.

## Process Patterns

### Pattern 22: Foundation Wave Sequencing for Multi-Service Projects

**Problem**: In FB9, parallel foundation agents raced on shared dependencies. The GraphQL/Socket.io agent imported `AsyncSessionLocal` from `app.models` before the models agent defined it, and called `get_current_user(db=db)` with a non-existent signature. This produced 3 BLOCKERs in Phase 2b audit.

**Solution**: Split the foundation wave into two sequential sub-waves for projects with >1 service or complex backend/frontend split:

**Sub-Wave 2a — Core Contracts (run first, verify before 2b)**:
- `models.py` (with engine + session factory)
- `config.py` (with lazy factory, NO secret defaults)
- `auth.py` (with `get_current_user`, `require_role`)
- `roles.py`
- `shared/types.ts` and `shared/sio-events.ts`
- `requirements.txt`, `package.json`
- `.env.example` (naming contract established HERE)

**Sub-Wave 2b — Dependent Infrastructure (runs only after 2a passes audit)**:
- `graphql.py` (imports from models, auth)
- `sio.py` (imports from models, auth)
- `main.py` scaffolding (imports from config)
- Frontend scaffolding (imports shared types)
- `docker-compose.yml`

**Verification gate**: Run a mini-audit on 2a outputs before dispatching 2b. Check:
- `AsyncSessionLocal` is defined
- `get_current_user` signature is stable
- `.env.example` names are finalized

**Trade-off**: Adds ~5-10 minutes to foundation phase. Eliminates dependency race BLOCKERs.
**Tested by**: FB9 meta-reflection hypothesis H41 (validated in FB10). See also `references/hypotheses.md` H41.
**See also**: Anti-Pattern #43 (Parallel Agents Overwriting Shared Entry Points) for the related entry-point conflict problem.

---

### Pattern 44: Pseudo-Recursion — Internal Agent Self-Regulation

**Context**: True VSM recursion (every S1 contains its own S1-S5) is impossible in Kimi CLI because subagents cannot spawn their own sub-agent hierarchies.

**Workaround**: Embed a lightweight self-regulation checklist inside each S1 agent prompt so the agent performs internal coordination, audit, and policy checks before returning output.

**Template** (add to any S1 agent prompt):
```
Before returning your final output, verify:
- [S2] Does your output conform to the shared contracts (types, naming, interfaces)?
- [S3*] Have you checked for the most common errors in your domain (see anti-patterns)?
- [S4] Does your output match the architecture spec? If the spec is ambiguous, did you escalate?
- [S5] If you found a conflict between speed and correctness, which did you choose and why?
```

**Effect**: Distributed metasystem function. Not true recursion, but prevents S1 units from emitting unregulated output.

---

### FB17 Patterns

### Pattern: Frontend Import Path Verification Against tsconfig.json
**When**: Any frontend agent writes an import statement.
**What**: Before writing imports, read `tsconfig.json` `compilerOptions.paths` and `vite.config.ts` `resolve.alias`. Use the project's configured aliases for cross-package imports, NOT relative paths.
**Why**: Relative paths (`../shared/types`) fail when tsconfig.json defines a path alias (`@flux/shared/types`). Build errors discovered during fix wave waste iterations.
**How**:
1. Read `tsconfig.json` — extract `paths` mapping
2. Read `vite.config.ts` — extract `resolve.alias`
3. Use the alias for all imports from shared packages
4. Only use relative paths for imports within the same directory tree
**Source**: FB17 frontend agent wrote `../shared/types` but alias was `@flux/shared/types` (H80)

### Pattern: Split Tester Agents for Tier 2+ Builds
**When**: Project has 4+ services, 8+ test files, or >2000 lines of code.
**What**: Split `vsm_tester` into `vsm_backend_tester` and `vsm_frontend_tester` running in parallel. Backend tester focuses on pytest, database fixtures, and API integration tests. Frontend tester focuses on vitest, component tests, and build verification.
**Why**: A single tester agent times out under Tier 2+ load (1200s limit in FB17 with 14 passed, 5 failed, 21 errors). Splitting doubles effective testing capacity and prevents timeout collapse.
**How**:
1. Spawn `vsm_backend_tester` with scope: backend tests, pytest, docker-compose validation
2. Spawn `vsm_frontend_tester` with scope: frontend tests, vitest, npm run build
3. Both run in parallel with `run_in_background=true`
4. S5 aggregates results after both complete
**Expected outcome**: Both sub-agents complete within timeout; higher test pass rate.
**Source**: FB17 single tester agent collapsed under Tier 2 load (H79)

### Pattern: Explicit RBAC Arrays in api-spec.md
**When**: Architect writes api-spec.md for any project with authentication.
**What**: Every endpoint MUST include `RBAC: ["role1", "role2", ...]` array. Ownership filtering is documented separately as `Ownership: owner_id == current_user.id`. Never use ambiguous labels.
**Why**: Natural-language labels like "(owner-filtered)" are interpreted differently by REST router agents vs GraphQL resolver agents. Explicit arrays eliminate ambiguity.
**Example**:
```markdown
GET /claims
RBAC: ["admin", "adjuster", "auditor"]
Ownership: owner_id == current_user.id (ignored for admin)
```
**Source**: FB17 ambiguous "(owner-filtered)" label caused GraphQL RBAC parity gap (H83)

### Pattern: Verify Apollo Client Is Actually Used
**When**: Frontend project includes GraphQL dependencies.
**What**: After all frontend implementation agents complete, verify at least one page uses `useQuery` or `useMutation`. If zero pages use Apollo Client, either remove the GraphQL layer or migrate REST pages to GraphQL.
**Why**: Initializing ApolloProvider with unused dead code adds bundle size, build time, and confusion. Pages that should use GraphQL fallback to REST due to agent uncertainty.
**How**:
1. grep `src/pages/` for `useQuery\|useMutation\|useSubscription`
2. If zero matches → ISSUE: either migrate pages or remove ApolloProvider
3. grep `src/graphql/queries.ts` exports against `src/pages/` imports
4. If queries are orphaned → ISSUE: queries exist but no consumer
**Source**: FB17 ApolloProvider initialized but all 10 pages used REST fetch() (H84)

### Pattern: Auth Request/Response Contract Documentation
**When**: Any build with authentication (login, register, JWT).
**What**: The `api-spec.md` MUST include an explicit "Auth Contracts" section documenting:
1. **Login Response**: exact JSON keys returned by `POST /auth/login` (e.g., `access_token`, `token_type`, `role`, `expires_in`)
2. **Register Request**: exact JSON keys expected by `POST /auth/register` (e.g., `email`, `password`, `company_name`, `role`)
3. **JWT Payload**: exact claims in the token payload (e.g., `sub`, `role`, `exp`, `iat`)
4. **Refresh Response**: exact JSON keys returned by `POST /auth/refresh` (if applicable)
**Why**: Frontend and backend agents independently implement auth code. Without an explicit contract, frontend agents assume response shapes that backend agents don't return, causing login/register failures that are only caught during integration.
**How**:
1. Architect includes Auth Contracts section in `api-spec.md` before any implementation begins
2. Foundation auditor verifies Auth Contracts section exists and is complete
3. Frontend tester verifies login/register pages use ONLY keys documented in the contract
4. Backend tester verifies auth router returns EXACTLY the keys documented in the contract
**Source**: FB18 LoginPage expected `role` in login response (backend returned only `access_token` + `token_type`). RegisterPage sent `name` instead of `company_name`. No auth contract existed (H86)

### Pattern: Mutation Orphan Prevention
**When**: Any Phase 8b meta-reflection that proposes mutations.
**What**: Before declaring Phase 8 complete, produce a `mutations-applied.md`
tracking artifact that lists every proposed mutation with its tier, target file,
and status (`applied` / `deferred` / `rejected` / `overlooked`).
**Why**: S5 attention drops off during long sessions. Without a forced checkpoint,
structural mutations are miscategorized as append-only, refinement mutations are
forgotten, and typos survive for multiple builds. FB18 revealed this failure mode:
3 structural mutations were initially declared "none," and 4 refinement mutations
were only caught when the user asked "any other mutations?"
**How**:
1. `vsm_meta` MUST classify every mutation by tier with exact file paths
2. S5 MUST produce `mutations-applied.md` before git commit
3. S5 MUST verify every row in the table has status `applied`, `deferred`, or `rejected`
4. If any row is `overlooked`, STOP — apply the mutation, update the table, re-verify
5. Process-level gaps (e.g., "mutation tracking missing") must themselves be addressed
**Source**: FB18 Phase 8b mutation orphan failure — structural and refinement mutations were proposed but not applied systematically (H89)

### Pattern: ASGITransport for FastAPI Test Clients
**When**: Writing pytest integration tests for FastAPI with `httpx>=0.28.0`.
**What**: Use `httpx.ASGITransport(app=app)` instead of the deprecated `AsyncClient(app=app)` keyword argument.
**Why**: `httpx` 0.28+ removed the `app=` parameter from `AsyncClient.__init__`. Tests using the old pattern fail with `TypeError: AsyncClient.__init__() got an unexpected keyword argument 'app'`.
**How**:
```python
from httpx import ASGITransport, AsyncClient

async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
    response = await client.get("/health")
```
**Source**: FB19 test suite failed with `AsyncClient.__init__() got an unexpected keyword argument 'app'`. FB20 `conftest.py:78` uses `ASGITransport(app=app)`. All 56 backend tests pass. (H90)

### Pattern: UUID String-to-Object Conversion Before SQLAlchemy Filter
**When**: Using `UUID(as_uuid=True)` primary keys with SQLite test databases.
**What**: Convert string UUIDs (e.g., from JWT `sub` claim) to `uuid.UUID` objects before using them in SQLAlchemy `where()` clauses.
**Why**: SQLite with `UUID(as_uuid=True)` expects `uuid.UUID` objects. Passing a string raises `AttributeError: 'str' object has no attribute 'hex'`.
**How**:
```python
import uuid
from jwt.exceptions import InvalidTokenError

payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
user_id = uuid.UUID(payload["sub"])  # convert BEFORE filter
result = await db.execute(select(User).where(User.id == user_id))
```
**Source**: FB19 `get_current_user` passed string `sub` to `User.id == user_id`, causing SQLite `AttributeError`. FB20 `auth.py:70` converts to `uuid.UUID(sub)`. (H91)

### Pattern: Role Fixtures to Bypass Rate-Limited Auth Endpoints
**When**: Writing tests for applications with SlowAPI rate limits on `/auth/register`.
**What**: Seed users directly into the test database via fixtures instead of calling rate-limited registration endpoints repeatedly.
**Why**: SlowAPI's `5/minute` limit on `/auth/register` causes 429 errors when multiple test files each register users. Direct DB insertion bypasses the endpoint and the rate limit entirely.
**How**:
```python
@pytest.fixture
async def landlord_user(db):
    user = User(email="landlord@test.com", password_hash=hash_password("password"), role="landlord")
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user
```
**Source**: FB19 `test_orders.py` + `test_auth.py` combined for 6 `/auth/register` calls, hitting the 5/minute limit. FB20 `conftest.py` provides `landlord_user`, `tenant_user`, `manager_user` fixtures. 56 tests pass with zero 429s. (H92)

### Pattern: Celery Task Test Mocking Without Redis Broker
**When**: Writing tests for Celery tasks when Redis is not running in the test environment.
**What**: Mock `.delay()` calls and test the direct task function. Do not let Celery attempt broker connections during test collection or execution.
**Why**: Module-level `celery_app = Celery("app")` triggers broker connection on import if `broker_url` points to `redis://localhost:6379`. Without a running Redis, tests fail with `ConnectionRefusedError`.
**How**:
```python
from unittest.mock import patch
from app.tasks import send_notification

def test_send_notification_direct():
    result = send_notification("user-123", "Hello")
    assert result["sent"] is True

@patch("app.tasks.send_notification.delay")
def test_send_notification_delayed(mock_delay):
    send_notification.delay("user-123", "Hello")
    mock_delay.assert_called_once_with("user-123", "Hello")
```
**Source**: FB19 Celery tests failed with `ConnectionRefusedError` on `redis://localhost:6379`. FB20 `test_tasks.py:28-33` mocks `.delay()` and tests direct calls. 6 task tests pass with no Redis running. (H93)


### Pattern: Auth Response Contract Template
**When**: Writing api-spec.md for builds with authentication.
**What**: Document the EXACT JSON response shapes for login, register, refresh, and me endpoints, including every field name and type.
**Why**: Ambiguous specs ("returns a token") cause frontend/backend contract mismatches. In a gym experiment, an ambiguous spec produced `{token: string}` while the frontend expected `{access_token, token_type, role}`.
**How**:
```markdown
## Auth Endpoints

### POST /auth/login
**Request:** `{"email": "string", "password": "string"}`
**Response (200):** `{"access_token": "string", "token_type": "bearer", "role": "string"}`

### POST /auth/register
**Request:** `{"email": "string", "password": "string", "name": "string"}`
**Response (201):** `{"id": int, "email": "string", "name": "string", "role": "string"}`

### GET /auth/me
**Response (200):** `{"id": int, "email": "string", "name": "string", "role": "string"}`

### JWT Payload Claims
`{"sub": "user-id", "role": "string", "exp": unix_timestamp, "iat": unix_timestamp}`
```
**Source**: Gym-2026-05-25 Experiment E8 (H20). Variant A (ambiguous spec) caused 3-field mismatch. Variant B (explicit spec) matched perfectly.

### Pattern: Frontend Build Script Verification
**When**: Verifying frontend infrastructure in any build with a Vite/React frontend.
**What**: Run `npm run build` (the package.json script), NOT just `vite build`.
**Why**: `package.json` build scripts often include `tsc -b && vite build`. Verifying only `vite build` misses TypeScript compilation errors that `tsc -b` catches. In a gym experiment, `vite build` passed while `npm run build` failed with `tsc -b` errors (missing `@types/node`).
**How**:
```bash
# In the frontend directory:
npm run build
# Do NOT rely solely on:
# npx vite build
```
**Source**: Gym-2026-05-25 Experiment E13 (H48 + H53). `vite build` PASS, `npm run build` FAIL due to `tsc -b` type-checking `vite.config.ts` without `@types/node`.

### Pattern: Domain-Specific Coder Prompts with Known Stack Gotchas
**When**: Spawning implementation agents for complex stacks (FastAPI + Strawberry + SlowAPI + Celery + React + Apollo).
**What**: Embed a "Known Stack Gotchas" section directly in the coder agent prompt, not just in the architect brief or integration checklist.
**Why**: Generic `coder` subagents receive only task-level prompts. Domain knowledge in the architect brief may be ignored. A gym experiment showed domain-specific prompts measurably improved security posture (explicit CORS origins instead of wildcard) and runtime verification rigor (dynamic `inspect.signature` check on `strawberry.Schema.__init__`).
**How**: Add to backend coder prompt:
```
Known Stack Gotchas — verify these explicitly:
1. NEVER instantiate Pydantic Settings at module level. Use lazy factory.
2. ALWAYS use `str, enum.Enum` for string-valued enums.
3. NEVER assume `strawberry.Schema` accepts `validation_rules`. Verify with `help()` or `inspect.signature`.
4. ALWAYS install `@app.exception_handler(RateLimitExceeded)` when using SlowAPIMiddleware.
5. NEVER use CORS `allow_origins="*"` with `allow_credentials=True`.
6. NEVER use module-level `engine = create_async_engine(...)` in models.py.
```
**Source**: Gym-2026-05-25 Experiment E14 (H59). Generic coder used `allow_origins=["*"]` and skipped runtime API verification. Domain-specific coder used explicit origins and dynamic signature checks.

### Pattern 45: Fix Agent Dry-Run Validation

**When**: A new domain-specific fix agent (e.g., `vsm_backend_fix_agent`, `vsm_frontend_fix_agent`) is created or its prompt undergoes significant structural changes.

**What**: Before trusting the new fix agent in a production build, run a controlled "dry run" build with intentionally injected BLOCKERs that match the agent's domain.

**Why**: Fix agents are created based on observed failure modes, but their prompts have never been exercised in a real Phase 7 fix wave. A prompt that looks correct on paper may fail to produce the expected `re-audit-report.md`, may introduce regressions, or may miss subtle variants of the BLOCKERs it was designed to catch.

**How**:
1. Create a minimal build in the target stack (FastAPI/SQLAlchemy for backend, React/Vite for frontend).
2. Inject 2-3 known BLOCKERs from the agent's domain:
   - Backend: circular import, missing exception handler, auth parity gap
   - Frontend: orphaned query export, `as any` bypass, missing tsconfig include
3. Route BLOCKERs through the new fix agent in a proper Phase 7 flow.
4. Measure:
   - Fix correctness (does the code actually work?)
   - Full test suite pass rate post-fix
   - `re-audit-report.md` production rate
   - Regression count (did fixing one thing break another?)
5. Compare against a control: fix identical BLOCKERs with a generic `coder` agent.
6. If the domain-specific agent underperforms the generic agent → reject the prompt and iterate.

**Acceptance criteria**:
- ≥90% fix correctness
- 100% re-audit report production
- ≤1 regression per fix wave
- Full test suite passes after fix

**Source**: Structural mutations FB21-9/10 created `vsm_backend_fix_agent` and `vsm_frontend_fix_agent` without empirical validation. H107 formalizes the gap.
**Empirical validation**: Gym E17 (2026-05-25) confirmed both agents meet all acceptance criteria.
- Fix correctness: 100% (5/5 BLOCKERs fixed)
- Re-audit report production: 100% (3/3) vs generic coder 0% (0/3)
- Security invariant enforcement: Domain agents excluded `admin` from registration allowlist; generic coder kept `admin` (regression)
- Full test suite passes: 100% after fix
**See also**: `references/hypotheses.md` H107.

### Pattern 46: Test-First Exit Gate

**When**: Any build where Phase 4 (Testing) produces test failures, deprecation warnings, or build errors.

**What**: Before proceeding to Phase 5 (Security Gate) or Phase 6 (Integration Verification), verify **zero failures** across all test suites and build scripts. If any failure exists, STOP and route to Phase 7 (Fix Wave).

**Why**: Gym E16 (H106) and fitness builds FB20/FB21 both found builds proceeding past Phase 4 with failing pytest tests. This wastes security and integration effort on broken code. Security agents scan code that doesn't even pass basic tests. Integration coordinators validate contracts on top of failing foundations.

**How**:
1. After Phase 4 testers complete, S5 MUST read test output directly (not trust upstream claims).
2. Verify:
   - `pytest tests/` — zero failures
   - `vitest run` / `npm test` — zero failures
   - `npm run build` — zero errors
   - `tsc --noEmit` — zero type errors (TypeScript projects)
3. If ANY check fails → emit algedonic, route to Phase 7. Do not proceed.
4. After fixes clear, re-run Phase 4 → Phase 5 → Phase 6 in sequence.

**Empirical validation** (E18, H108): A minimal FastAPI app with a missing `RateLimitExceeded` exception handler produced 1 HIGH (security) + 1 BLOCKER (coordinator) = 2 downstream findings when audits ran on the broken code. After fixing the handler and re-running audits, downstream findings dropped to 0. **100% reduction.** The single failing pytest test was a perfect predictor of both downstream BLOCKERs.

**Acceptance criteria**:
- 100% of builds with Phase 4 failures are stopped before Phase 5
- Zero builds proceed to integration with failing tests
- Fix waves triggered by Phase 4 failures produce `re-audit-report.md`

**Source**: Gym E16 (H106), FB20/FB21 fitness builds.
**See also**: `references/integration-checklist.md` Check 57, `references/hypotheses.md` H108.

## Pattern: Frontend Page Stub Detection (Discovered FB23)

**Problem**: Frontend pages that exist only as structural stubs (`return <div>Name</div>`
with `void` imports) pass integration checks because routes and wiring are correct,
but provide zero functional value and hide missing data-fetching logic.

**Detection rule**: If a page component is <15 lines and contains only:
- `void` references to suppress unused-import warnings, AND
- A single `<div>Label</div>` return,
flag as ISSUE.

**Remediation**: The page must contain at least one of:
- A real GraphQL query / REST call
- A conditional render based on loaded data
- A non-trivial form or interactive element

**Affected**: vsm_frontend_coder, vsm_coordinator.
**Source**: FB23 Dashboard.tsx, Jobs.tsx, Candidates.tsx etc. were all 6–18 line
stubs with `void` imports. Integration report still PASSed them.
