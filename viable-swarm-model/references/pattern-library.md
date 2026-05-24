# Proven Pattern Library

> **Mutation rules**: Append new patterns; mark obsolete patterns with
> `~~strikethrough~~` and rationale. Never delete — the log of what stopped
> working is as valuable as what currently works.

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

### 40. Strawberry `str, enum.Enum` for String-Valued GraphQL Enums
**Trigger**: Backend defines GraphQL enums that map to database string columns.  
**Solves**: `ValueError` when constructing `enum.Enum` from a string value (e.g., `Role("commander")` fails on `enum.Enum` but works on `str, enum.Enum`).  
**Implementation**: Define enums as `class Role(str, enum.Enum): COMMANDER = "commander"`. Document this requirement in `api-spec.md` so implementation agents follow it.
**Source**: Fitness build FB5. Coordinator caught `enum.Enum` runtime bug in `graphql.py`.

### 41. Extract Shared Singletons to Dedicated Modules
**Trigger**: Multiple modules need access to the same stateful singleton (limiter, config, event bus).  
**Solves**: Circular imports when routers import from `main.py` to access the singleton.  
**Implementation**: Create `app/limiter.py`, `app/events.py`, etc. Entry point (`main.py`) imports from these modules; routers also import from these modules. Never import from the entry point.
**Source**: Fitness build FB5. `auth.py` imported `limiter` from `main.py`, causing circular import.

## Pattern #22: Foundation Wave Sequencing for Multi-Service Projects

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
**Tested by**: FB9 meta-reflection hypothesis H41 (to be validated in FB10).

---

## Pattern [N]: Pseudo-Recursion — Internal Agent Self-Regulation

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
