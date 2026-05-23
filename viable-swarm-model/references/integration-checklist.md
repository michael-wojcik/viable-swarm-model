# Cross-File Integration Verification Checklist

> **Mutation rules**: Append new checks discovered in the field. Mark checks
> that are consistently irrelevant for certain project types with a note.
> Never delete — a check that seems irrelevant for one project type may be
> critical for another.

Run ALL of these before declaring integration complete.

**Failure rule**: If ANY check fails, send back to responsible S1 for
correction BEFORE quality gates.

---

## 1. Export/Import Verification
- [ ] Every exported utility/type is imported by at least one consumer file
- [ ] Every import statement resolves to an existing export
- [ ] No orphaned code — utilities that were created are actually used

## 2. Contract Consistency
- [ ] Shared contracts (types, interfaces) are consistently used across files
- [ ] No duplicate type definitions with different shapes

## 3. Entry Points
- [ ] Entry points (routes, main, index) import and register all middleware
- [ ] Every service has a verifiable entry point (Dockerfile CMD/ENTRYPOINT file exists)

## 4. Build Verification
- [ ] Codebase compiles/builds without errors
- [ ] No TypeScript/JavaScript syntax errors

## 5. WebSocket Event Contracts
- [ ] Every backend `emit` has matching frontend listener (and vice versa)
- [ ] WebSocket message shape: `kind` field values match exactly between backend and frontend
- [ ] Shared event constants file exists and is imported by both sides

## 6. GraphQL Contracts
- [ ] SDL types match TypeScript payload types
- [ ] Every subscription has matching resolver with `subscribe` returning AsyncIterable
- [ ] @graphql-depth-limit installed (max 10) + complexity analysis

## 7. Frontend Paths & Config
- [ ] Frontend relative path to shared types: `../../shared/` not `../shared/` in monorepos
- [ ] Vite/Webpack proxy config includes `/api`, `/graphql`, `/ws`, `/tiles` paths
- [ ] GraphQL subscriptions need `ws: true` in proxy config
- [ ] Vite path alias configured for shared types (e.g., `@flux/shared`)

## 8. pgvector Pipeline
- [ ] PostgreSQL vector extension enabled
- [ ] VECTOR(N) column matches embedding dimensions
- [ ] ivfflat index with `vector_cosine_ops` exists
- [ ] Embeddings generated before INSERT/UPDATE

## 9. Server-Sent Events (SSE)
- [ ] Backend uses `StreamingResponse(media_type="text/event-stream")`
- [ ] Backend yields `data: {json}\n\n` format
- [ ] Frontend uses `getReader()` + `TextDecoder`, not EventSource
- [ ] Frontend splits on `"\n\n"` to extract messages
- [ ] Short-lived SSE token exchange implemented (never long-lived JWT in URL)

## 10. CRDT Persistence
- [ ] Yjs PersistenceAdapter connected to doc `update` event
- [ ] BYTEA column exists in PostgreSQL
- [ ] Load path SELECTs + applies updates in chronological order (`ORDER BY created_at`)

## 11. DAG Validation
- [ ] `validate()` called on every create/update/execute
- [ ] 3-color DFS (WHITE/GRAY/BLACK) for cycle detection
- [ ] Kahn's algorithm for topological sort determines execution order

## 12. Redis Queue
- [ ] Queue name consistent between API `lpush` and worker `brpop`
- [ ] Worker re-enqueues dependents after completion
- [ ] Redis pub/sub channel names match between producer and consumer

## 13. Frontend Scaffolding
- [ ] `package.json` exists
- [ ] `vite.config.ts` exists (with path alias)
- [ ] `tsconfig.json` exists
- [ ] `index.html` exists
- [ ] `src/main.tsx` (or equivalent) exists
- [ ] `src/App.tsx` exists

## 14. Rust Workspace
- [ ] Workspace `Cargo.toml` includes ALL member crates
- [ ] No duplicate imports between `lib.rs` and local paths in same file
- [ ] Integration tests in `tests/` import from library path, not local modules

## 15. Go JSON Tags
- [ ] All JSON tags are camelCase (`json:"camelCase"`)
- [ ] No snake_case leaking to frontend via struct tags

## 16. Docker Compose
- [ ] All services have verifiable entry points (CMD/ENTRYPOINT file exists)
- [ ] Environment variable names match exactly across docker-compose/.env/code
- [ ] No `||` fallbacks for SECRET/KEY/PASSWORD/TOKEN variables

## 17. Prisma / ORM
- [ ] Relation names match on both sides (`@relation("Name")`)
- [ ] N+1 queries prevented (selectinload for relationships, batched GROUP BY for computed fields)

## 18. Auth & Middleware
- [ ] Auth middleware raises HTTPException on failure, never returns None silently
- [ ] Document ownership filtering on ALL list endpoints
- [ ] Public DTOs omit answer/solution fields for game/quiz APIs

## 19. Mobile / Game UI (if applicable)
- [ ] 60px minimum button height
- [ ] Dark theme (#0f172a) for OLED
- [ ] Tested at 375px viewport

## 20. File Structure
- [ ] No orphaned utility files
- [ ] No empty files committed
- [ ] README has setup instructions

## 21. Parallel Agent Coordination
- [ ] Entry point files (main.py, App.tsx, server.ts) are modified by at most one agent per wave
- [ ] If multiple agents must contribute to entry points, a dedicated "wiring" agent runs last
- [ ] All imports in entry points resolve (no missing modules)

## 22. WebSocket Auth Contracts
- [ ] Browser WebSocket auth uses path-based tokens (NOT query params) when headers are impossible
- [ ] Backend validates token from path parameter before accepting connection
- [ ] Token is short-lived (≤15 min) and scoped to the specific resource

## 23. State Machine Domain Alignment
- [ ] Backend state machine enum values match frontend TypeScript union types exactly
- [ ] Every state value emitted by backend is handled by frontend switch/case
- [ ] No frontend-only states that backend never emits (causes unreachable code)

## 24. Case-Sensitive Enum Alignment
- [ ] GraphQL enum values match TypeScript union types exactly (including case)
- [ ] Backend string literals match frontend string literals exactly
- [ ] Shared constants file is the single source of truth for enum values

## 25. Frontend Dockerfile Build Args
- [ ] `VITE_API_URL` and `VITE_WS_URL` passed as `ARG` in frontend Dockerfile
- [ ] Runtime env vars are not silently baked as `undefined` into static bundles

## 26. GraphQL Field Name Alignment
- [ ] GraphQL schema field names (after auto-camelCase) match frontend query field names exactly
- [ ] For Strawberry: verify that `snake_case` backend fields produce the expected `camelCase` frontend fields
- [ ] Every field queried by frontend exists in the backend schema
- [ ] No frontend queries reference fields that were renamed or removed in backend

## 27. Auth Response Contract Documentation
- [ ] Auth endpoints (`/register`, `/login`, `/refresh`) have documented exact response JSON keys in api-spec.md
- [ ] Backend implementation matches the documented contract exactly
- [ ] Frontend consumes the exact keys documented in the contract

## 28. Orphaned Exports / Dead Code Scan
- [ ] Every exported function/class in backend is imported by at least one consumer file
- [ ] Every exported function/class in frontend is imported by at least one consumer file
- [ ] No duplicate implementations of the same utility in different files

## 29. WebSocket Event Name Dictionary Cross-Check
- [ ] `api-spec.md` WebSocket event names match `sio.py` emit/handler names
- [ ] `sio.py` emit names match `shared/sio-events.ts` constant values
- [ ] `shared/sio-events.ts` constants are imported by both backend and frontend
- [ ] Every backend `emit` has a matching frontend `socket.on` listener
