# Fitness Build Coverage Ledger

> **Purpose**: Historical record of all fitness builds. This is NOT a selectable
> menu — it is a coverage ledger documenting what has been tested, what was
> learned, and which domains have been used. The coach synthesizes new builds
> from empirical state; it does not select from a catalog.
>
> **Mutation rules**: Append build results after each fitness build. Do NOT
> add Project Spec sections here — build specifications live as ephemeral prompt
> drafts in `~/vsm-fitness-builds/coach/`.

---

## FB1: DocuFlow — Collaborative Document Editor

**Complexity**: High (4-5 waves, 2000+ lines, 2 services: API + worker)
**Date**: 2026-05-22
**Services**: FastAPI backend, React frontend, Redis worker
**Note**: Pre-ledger entry — executed before structured result format.

### Coverage Map

| Capability | Tested by |
|---|---|
| Foundation wave | Types, schemas, shared types between frontend/backend |
| Parallel S1 agents | Backend API + frontend UI built simultaneously |
| S2 coordination | Shared contracts, env vars, Vite path aliases |
| S3* audit | Large codebase (2000+ lines) for auditor to read |
| Security gate | Auth, JWT, ownership filtering, CORS, bcrypt |
| Integration verification | WebSocket events, GraphQL SDL, pgvector pipeline |
| Testing wave | Unit + integration tests for collaborative features |
| Real-time patterns | Yjs CRDT, WebSocket presence, SSE streaming |
| Security lessons | Document ownership, public DTOs, JWT in-band |
| Fix wave | Likely needed due to complexity |

### Known Stress Points
- Document ownership filtering is easy to miss (L9)
- WebSocket auth must be in-band, never URL (L16)
- Yjs CRDT persistence requires correct BYTEA + chronological load
- pgvector dimensions must match embedding model
- SSE requires short-lived token exchange (L33)
- Frontend scaffolding often forgotten (Pattern #3)

---

## FB2: GeoQuiz — Multiplayer Geospatial Quiz Platform

**Complexity**: Medium-High (3-4 waves, 1500+ lines, 2 services)
**Date**: 2026-05-22
**Services**: FastAPI backend, React frontend
**Note**: Pre-ledger entry — executed before structured result format.

### Coverage Map

| Capability | Tested by |
|---|---|
| PostGIS / geospatial | PostGIS stored procedures, MVT tiles, radius search |
| Real-time game patterns | WebSocket rooms, server-authoritative countdown |
| Game security | Public DTOs must not expose answers (L19) |
| Mobile-first UI | 60px buttons, 160px countdown, dark theme |
| Integration | Socket.io event contracts, shared constants |
| Canvas rendering | Optional: map visualization with D3.js |

### Known Stress Points
- Game API answer exposure (L19): GET /questions must not return correct_answer_index
- WebSocket rooms must be cleaned up on disconnect (Pattern #20)
- Server countdown must be authoritative (Pattern #21)
- PostGIS dynamic MVT generation (Pattern #6)
- Mobile-first design constraints (Pattern #18)

---

## FB3: TaskFlow — Workflow Orchestration Platform

**Complexity**: High (4-5 waves, 2500+ lines, 3 services: API + worker + scheduler)
**Date**: 2026-05-22
**Services**: FastAPI backend, Celery/Redis worker, React frontend
**Note**: Pre-ledger entry — executed before structured result format.

### Coverage Map

| Capability | Tested by |
|---|---|
| DAG validation | 3-color DFS, topological sort, cycle detection |
| Redis task queue | lpush/brpop, dependent enqueue, pub/sub |
| GraphQL + subscriptions | Complex schema with nested types |
| Multi-service integration | API, worker, scheduler communication |
| Security | Auth, permission checks on workflow execution |
| Testing | DAG validation tests, integration tests |

### Known Stress Points
- DAG validation must run on every create/update (L12)
- Redis queue name consistency between API and worker (L8)
- Celery task name mismatch across services (Anti-pattern #12)
- Standalone worker must not be imported as library (L31)
- GraphQL depth limiting (L25)
- N+1 queries in computed fields (L34)

---

## FB4: FleetSync — Real-Time Fleet & Field Operations Platform

**Complexity**: High (4-5 waves, 3000+ lines, 4 services: API + worker + realtime + mobile-web)
**Date**: 2026-05-22
**Services**: FastAPI backend, Celery/Redis worker, Socket.io real-time service, React frontend
**Note**: Pre-ledger entry — executed before structured result format.

### Coverage Map

| Capability | Tested by |
|---|---|
| PostGIS / geospatial (FB2 carry-forward) | Technician locations, service area polygons, radius search, route bounding boxes |
| File upload security | Image upload, signature capture, MIME validation, size limits |
| Role-based access control | Admin / dispatcher / driver roles with permission middleware |
| Real-time location streaming | Socket.io rooms for fleet tracking, server-side geofence alerts |
| GraphQL + subscriptions | Complex nested queries, enum case sensitivity, depth limit |
| Multi-service integration | API, worker, real-time service, frontend |
| Docker build args | Frontend VITE_API_URL injected at build time |
| Pydantic Settings testability | Lazy factory pattern or dependency injection |
| Rate limiting middleware | SlowAPIMiddleware installed in foundation wave |

### Known Stress Points
- PostGIS spatial query bounds must have upper limits (FB2 gap carry-forward)
- GraphQL enum case must match TypeScript exactly (H16)
- Pydantic Settings must use lazy factory, not module-level singleton (H15)
- SlowAPIMiddleware must be in foundation wave, not just decorators (H17)
- Frontend Dockerfile must pass VITE_API_URL as build arg (H18)
- File upload endpoints must validate MIME type and size before saving
- WebSocket auth must be in-band, never URL query param
- Role middleware must raise on failure, never return None

---

## FB10: CommerceHub — Real-Time Marketplace Platform

**Complexity**: High (4-5 waves, 2500-3500 lines, 3-4 services: API + worker + realtime + frontend)
**Date**: 2026-05-24
**Expected Tier**: Tier 2 or Tier 3 (tests Variety Assessment)
**Services**: FastAPI backend, Celery/Redis worker, Socket.io real-time service, React frontend
**Note**: Pre-ledger entry — executed before structured result format. First build to test structural mutations (Variety Assessment, S4 option generation, S5 Policy Check, Phase 3c mid-wave S2, S2 verbatim authority, pseudo-recursion).

### Coverage Map

| Capability | Tested by |
|---|---|
| **New mutations** | |
| Variety Assessment | Large enough to force Tier 2/3 classification in Phase 0 |
| S4 option generation | Architect must produce Minimal/Balanced/Robust design options |
| S5 Policy Check | Explicit speed-vs-correctness decision between monolith and service-oriented designs |
| Phase 3c mid-wave S2 | Parallel agents build product catalog, cart, checkout, orders — shared Product/Order/Cart types |
| S2 verbatim authority | Coordinator specifies exact corrections; fix agents apply verbatim |
| Pseudo-recursion | S1 agents self-check against contracts before returning output |
| **Hypotheses tested** | |
| H4 | Entry-point wiring conflicts with parallel implementation agents |
| H13 | State-machine alignment (order status: pending → confirmed → shipped → delivered → refunded) |
| H21 | Orphaned exports scan (utility functions never imported) |
| H22 | WebSocket event name dictionary cross-check |
| H23 | GraphQL RBAC parity with REST |
| H24 | GraphQL ownership filtering on list queries |
| H25 | Frontend test coverage >50% |
| H26 | Entry-point and worker test coverage |
| H29 | Circular import risk (routers importing from main.py) |
| H32 | WebSocket room auth verification |
| H33 | Security gate sequencing (Security → Integration vs. Integration → Security) |
| H41 | Sequenced foundation sub-waves eliminate dependency races |
| **Existing capabilities** | |
| Foundation wave sequencing | FB9 structural mutation — first test in a real build |
| Security gate | Payment state machine, inventory race conditions, admin access control |
| Integration verification | Cross-file contracts, enum alignment, orphaned exports |
| Testing wave | Backend + frontend + entry-point + worker tests |
| Fix wave | Likely needed due to complexity and parallel agent drift |

### Known Stress Points

1. **Inventory race conditions**: Two users buying the last item simultaneously. Requires optimistic locking or Redis-based inventory reservation.
2. **Payment state machine drift**: REST endpoint allows `pending → confirmed` but GraphQL mutation might allow `pending → shipped` (skipping confirmation).
3. **Cart abandonment/expiry**: Cart items must expire after 30 minutes. Redis TTL vs. database consistency.
4. **Public DTO exposure**: Product DTOs must NOT expose `cost_price`, `supplier_id`, `margin` to customers. Admin DTOs must include them.
5. **GraphQL list query scoping**: `orders` query must return only the authenticated user's orders (H24).
6. **WebSocket inventory sync**: Real-time stock updates must use consistent event names across `api-spec.md`, `sio.py`, and `sio-events.ts` (H22).
7. **WebSocket room auth**: `subscribe_inventory` must verify auth before allowing room join (H32).
8. **Circular imports**: Routers must NOT import from `main.py` to access shared singletons (H29).
9. **SQLAlchemy shadowing**: Model columns like `text`, `select`, `join` must use aliased imports (H10 pattern).
10. **Orphaned exports**: Utility modules often define helpers never imported anywhere (H21).
11. **Entry-point conflicts**: Parallel agents building `main.py` (product router, cart router, order router registration) overwrite each other (H4).
12. **Frontend test gap**: Tester agent must write frontend tests for React components, Zustand stores, and cart logic (H25).
13. **Enum runtime safety**: `OrderStatus` must use `str, enum.Enum` for GraphQL compatibility (H27).
14. **Pydantic Settings lazy factory**: `get_settings()` not module-level singleton (Pattern #41).
15. **Rate limiting**: SlowAPIMiddleware in foundation wave + decorators on auth endpoints.
16. **Docker build args**: `VITE_API_URL` and `VITE_WS_URL` passed as ARG in frontend Dockerfile.

---

## FB12: HealthBridge — Telemedicine & Patient Health Records Platform

**Complexity**: High (4-5 waves, 2500-3500 lines, 4 services: API + worker + realtime + frontend)
**Estimated duration**: 3-4 hours
**Expected Tier**: Tier 2
**Services**: FastAPI backend, Celery/Redis worker, Socket.io real-time service, React frontend
**Date**: 2026-05-24

### Coverage Map

| Capability | Tested by |
|---|---|
| Prevention rule transfer (H49-H53) | All 9 traps from FB11 deliberately recreated to validate new rules |
| GraphQL/Strawberry specifics | Strawberry auto-camelCase, extension version drift, RBAC parity |
| Security severity calibration | Connection string defaults vs. secret fallbacks |
| GraphQL context fail-closed | Auth exception propagation in get_context |
| Sequenced foundation sub-waves | H41 validated — 0 BLOCKERs in foundation |
| Tester timeout | Split backend/frontend testers attempted |

### Known Stress Points
- GraphQL field name camelCase alignment (H58)
- Strawberry extension version drift (H55)
- Security agent false positive CRITICALs on connection strings (H56)
- GraphQL fail-open context (H57)
- GraphQL RBAC parity with REST (T9)

### Result
- **Score**: ~3.7/5.0
- **BLOCKERs**: 1 (GraphQL patients query ownership filtering)
- **Fix iterations**: 1
- **All FB11 traps prevented or caught early**

---

## FB13: LegalVault — Legal Document & Contract Management Platform

**Complexity**: High (4-5 waves, 2500-3500 lines, 4 services: API + worker + realtime + frontend)
**Estimated duration**: 3-4 hours
**Expected Tier**: Tier 2
**Services**: FastAPI backend, Celery/Redis worker, Socket.io real-time service, React frontend
**Date**: 2026-05-24

### Coverage Map

| Capability | Tested by |
|---|---|
| Prevention rule transfer (H55-H58) | 9 traps from FB12 deliberately recreated to validate Mutations 34-37 |
| Strawberry extension awareness | T1: agent must discover QueryDepthLimiter without exact class name |
| Security severity calibration | T2: REDIS_URL default must be rated LOW, not CRITICAL |
| GraphQL context fail-closed | T3: get_context must propagate JWT exceptions |
| GraphQL field name camelCase | T4: frontend queries must match auto-camelCased schema |
| Sequenced foundation sub-waves | H41 validated — 0 BLOCKERs expected in foundation |
| Domain coder pilot (H59) | Backend/frontend domain-specific prompts (observational) |

### Known Stress Points
- Strawberry extension version drift (H55)
- Security severity calibration on connection strings (H56)
- GraphQL fail-open context (H57)
- GraphQL field name camelCase alignment (H58)
- Frontend queries.ts orphaned exports
- WebSocket auth protocol mismatch
- Vite proxy port mismatch
- Docker-compose env var prefix inconsistency

### Result
- **Score**: 3.2/5.0
- **BLOCKERs**: 12 total (Foundation: 2, Implementation: 9, Security: 1 CRITICAL)
- **Fix iterations**: 2
- **Prevention rules validated**: H55 (Strawberry extension), H56 (severity calibration), H57 (fail-closed context), H58 (camelCase alignment)
- **Prevention rules inconclusive**: H59 (domain coders)
- **New mutations applied**: M38-M41
