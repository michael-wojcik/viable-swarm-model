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


## Table of Contents

- [FB1](#fb1)
- [FB2](#fb2)
- [FB3](#fb3)
- [FB4](#fb4)
- [FB5](#fb5)
- [FB6](#fb6)
- [FB7](#fb7)
- [FB8](#fb8)
- [FB9](#fb9)
- [FB10](#fb10)
- [FB11](#fb11)
- [FB12](#fb12)
- [FB13](#fb13)
- [FB14](#fb14)
- [FB15](#fb15)
- [FB16](#fb16)
- [FB17](#fb17)
- [FB18](#fb18)
- [FB19](#fb19)
- [FB20](#fb20)
- [FB21](#fb21)
- [FB23](#fb23)

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

---

## FB14: EduSphere — Online Learning & Course Management Platform

**Complexity**: High (4-5 waves, 2500-3500 lines, 4 services: API + worker + realtime + frontend)
**Expected Tier**: Tier 2 (same tier as FB13; score < 4.0 prevents escalation)
**Services**: FastAPI backend, Celery/Redis worker, Socket.io real-time service, React frontend
**Date**: 2026-05-24
**Build ID**: FB14-20260524

### Coverage Map

| Capability | Tested by |
|---|---|
| **Prevention rule validation** | |
| M39 (Auditor batch ≤10) | 3 batches (9, 9, 10 files); 0 false-positive BLOCKERs |
| M41 (Phase 8 reflection) | Standalone `.kimi/lessons.md` with structured format |
| H60 (Env var naming) | docker-compose uses exact names matching config.py |
| H61 (Vite proxy ports) | Proxy targets match docker-compose exposed ports |
| H63 (WS auth handshake) | In-band auth via authenticate event, not URL params |
| H65 (Hardcoded engine) | Lazy `_get_async_engine()` factory in models.py |
| **New hypotheses generated** | |
| H66 | Frontend cross-file import check (store/query/page contracts) |
| H67 | Security gate checklist: registration role validation |
| H68 | Schema introspection check prevents GraphQL query/schema mismatches |
| H69 | Auth router must be explicitly required in foundation wave |
| **Gaps targeted from FB13** | |
| G1 | GraphQL schema/query alignment (type mismatches, return types) |
| G2 | Frontend store/page contract mismatches |
| G3 | Security design gaps (SECRET_KEY length, role validation) |
| G4 | Missing auth router in foundation wave |
| G5 | GraphQL subscriptions infrastructure without resolvers |

### Known Stress Points
- Frontend parallel agents create incompatible contracts (queries.ts vs pages vs store)
- GraphQL schema introspection must be run during integration check
- Registration role validation must be in BOTH REST and GraphQL
- Auth router must be explicitly required in foundation wave
- SECRET_KEY must have min_length=32 validation (not just default value)
- Module-level `get_settings()` is a recurring trap (tasks.py, sio.py)

### Result
- **Score**: 3.6/5.0
- **BLOCKERs**: 8 total (Foundation: 1, Implementation: 5, Integration: 2, Security: 2 CRITICAL)
- **Fix iterations**: 1
- **Traps caught**: T1 (H65), T2 (M39), T3 (H63), T4 (H61), T5 (H60), T6 (M41), T7 (G4), T8 (G6), T9 (G8)
- **Prevention rules validated**: M39, M41, H60, H61, H63, H64, H65
- **New hypotheses**: H66, H67, H68, H69

---

## FB15: EventHorizon — Event Ticketing & Venue Management Platform

**Complexity**: High (4-5 waves, 2500-3500 lines, 4 services: API + worker + realtime + frontend)
**Expected Tier**: Tier 2 (same tier as FB14; score < 4.0 prevents escalation)
**Services**: FastAPI backend, Celery/Redis worker, Socket.io real-time service, React frontend
**Date**: 2026-05-25
**Build ID**: FB15-20260525

### Coverage Map

| Capability | Tested by |
|---|---|
| **Prevention rule validation** | |
| H66 (Frontend import check) | tsc did NOT catch `as any` bypass; coordinator caught store mismatch |
| H67 (Registration role validation) | Security gate flagged admin in allowlist as CRITICAL |
| H68 (Schema introspection) | Coordinator verified field names but NOT argument types |
| H69 (Auth router in foundation) | Auth router created in foundation wave with all endpoints |
| H65 (Engine config) | FB15 agent reverted to module-level engine despite FB14 prevention rule |
| M39 (Auditor batch ≤10) | 2 batches of 10 files; 0 false-positive BLOCKERs |
| H60 (Env var naming) | docker-compose uses exact names matching config.py |
| H61 (Vite proxy ports) | Proxy targets match docker-compose exposed ports |
| H63 (WS auth handshake) | api-spec.md documented handshake; sio.py and client.ts implemented correctly |
| H64 (Auditor false positive rate) | Foundation audit 2 batches; 0 false positive BLOCKERs |
| H55 (Strawberry extension drift) | Agent used `validation_rules` parameter that doesn't exist |
| **New hypotheses generated** | |
| H70 | Fix agents must run circular-import check before adding cross-module imports |
| H71 | Frontend `as any` usage correlates with store/page contract mismatches |
| H72 | Strawberry Schema parameter validation must be verified at runtime |

### Known Stress Points
- Module-level engine instantiation is a recurring trap (H65)
- Frontend `as any` bypasses TypeScript contract checks (H71)
- Strawberry API drift affects Schema parameters, not just extensions (H55/H72)
- Fix agents can introduce circular imports (H70)
- GraphQL argument type parity needs deeper verification than field names (H68)
- Public REST endpoints (events/venues catalog) need explicit documentation if intentionally unguarded

### Result
- **Score**: 3.7/5.0
- **BLOCKERs**: 8+ total (Foundation: 1, Integration: 7, Security: 1 CRITICAL + 4 HIGH)
- **Fix iterations**: 2
- **Traps caught**: T2 (H66, partially), T3 (H67, security flagged), T5 (H65, coordinator caught), T7 (H61), T8 (H60)
- **Traps missed/partial**: T1 (H68, coordinator verified field names only), T2 (tsc missed due to `as any`)
- **Prevention rules validated**: M39, H60, H61, H63, H64, H69
- **Prevention rules re-validated (fragile transfer)**: H65, H55
- **New mutations**: M46-M48


---

## FB16: FarmLogix — Agricultural Supply Chain & Farm Management Platform

**Complexity**: High (4-5 waves, ~3500 lines, 4 services: API + worker + realtime + frontend)
**Expected Tier**: Tier 2 (same tier as FB15; score < 4.0 prevents escalation)
**Services**: FastAPI backend, Celery/Redis worker, Socket.io real-time service, React frontend
**Date**: 2026-05-24
**Build ID**: FB16-20260524

### Coverage Map

| Capability | Tested by |
|---|---|
| **Prevention rule validation** | |
| H70 (Circular import check) | Fix wave added cross-module imports safely; 0 circular imports |
| H71 (as any anti-pattern) | Frontend agent added `profitMargin` to store; zero `as any` casts |
| H72 (Runtime API verification) | GraphQL agent verified `validation_rules` doesn't exist; avoided T1 |
| H65 (Engine config) | Lazy `_get_async_engine()` factory in models.py |
| H69 (Auth router in foundation) | Auth router created in foundation wave with all endpoints |
| M39 (Auditor batch ≤10) | 4 batches (10, 8, 6, 10 files); 0 false-positive BLOCKERs from batch size |
| M46-M48 (Integration checks) | Circular import, anti-as-any, argument parity, runtime API verification checks added |
| **New hypotheses generated** | |
| H73 | Security gate HIGH/CRITICAL findings are not automatic fix-wave BLOCKERs |
| H74 | Architect does not runtime-verify framework parameters before embedding in api-spec.md |
| H75 | Frontend agents do not introspect GraphQL schema before writing queries |
| H76 | Foundation auditor scope misses wiring files and requirements.txt |
| H77 | Integration checklist misses config key name parity |
| H78 | Implementation agents treat data-model.md as advisory |
| **Gaps targeted from FB15** | |
| G1 | Foundation auditor misses module-level side effects in sio.py |
| G2 | Frontend `as any` bypasses type safety — trap avoided by schema update |
| G3 | Fix agents introduce circular imports — prevention rule worked |
| G4 | GraphQL argument type parity not verified — coordinator verified field names but not argument types |
| G5 | Agents use non-existent framework parameters — runtime verification worked |

### Known Stress Points
- Architect propagated prompt traps into api-spec.md (validation_rules, String vs DateTime, snake_case GraphQL names)
- Frontend agents wrote snake_case GraphQL queries despite Strawberry auto-camelCase — required full rewrite
- Security gate found real vulnerabilities but fix wave deferred HIGHs without escalation
- Socket.IO CORS wildcard (`*`) instead of explicit allowlist
- GraphQL RBAC mismatch: suppliers can create orders in GraphQL but REST blocks them
- Model drift: Delivery model added outside data-model.md spec
- Config key name drift: CORS_ORIGINS vs CORS_ALLOWED_ORIGINS

### Result
- **Score**: 3.4/5.0
- **BLOCKERs**: 4 foundation + 8+ implementation + 1 integration + 1 CRITICAL + 3 HIGH security
- **Fix iterations**: 1 major fix wave
- **Traps caught**: T1 (H72), T2 (H71), T5 (H65), T7 (H61), T8 (H60), T9 (route ordering)
- **Traps missed/partial**: T3 (circular import — prevention worked, no trap triggered), T4 (argument type parity — coordinator verified field names only), T6 (auditor batch — M39 worked)
- **Prevention rules validated**: H70, H71, H72, H65, H69, M39, M46-M48
- **New mutations**: M49-M52
- **Auditor false positive**: camelCase GraphQL queries flagged as BLOCKER (recurring H39/H58 false positive)

---

---

## FB18: ShipFlow — Logistics & Shipment Tracking Platform

**Complexity**: High (4-5 waves, ~3500 lines, 4 app services + 2 infra services)
**Expected Tier**: Tier 2 (same tier as FB16; score < 4.0 prevents escalation)
**Services**: FastAPI backend, Celery/Redis worker, Socket.io real-time service, React frontend
**Date**: 2026-05-25
**Build ID**: FB18-20260525

### Coverage Map

| Capability | Tested by |
|---|---|
| **Prevention rule validation** | |
| H79 (Split testers for Tier 2+) | Backend 108 tests + frontend 67 tests; both completed within timeout |
| H80 (tsconfig import path verification) | Zero incorrect import paths; `@ship/shared/types` used correctly |
| H81 (Cross-layer runtime consistency) | localStorage `access_token`, Celery broker from settings, Socket.IO namespace all consistent |
| H82 (Phase 8b meta-reflection) | Standalone `meta-reflection.md` produced with agent audit, phase scores, hypothesis generation |
| H83 (Explicit RBAC arrays) | api-spec.md used explicit `RBAC: [roles]` arrays; zero RBAC parity gaps between REST and GraphQL |
| H84 (Apollo Client usage) | All data-fetching pages use `useQuery` / `useMutation`; REST reserved for uploads/auth |
| H65 (Lazy engine factory) | `_get_async_engine()` lazy factory in models.py |
| H69 (Auth router in foundation) | Auth router created in foundation wave with all endpoints |
| **New hypotheses generated** | |
| H85 | Router registration checklist prevents 404 endpoints |
| H86 | Auth response contract documentation prevents login/register mismatches |
| H87 | GraphQL depth limit checklist item prevents missing security controls |
| H88 | Frontend file-lock coordination prevents parallel agent overwrites |
| **Gaps targeted from FB16** | |
| G1 | Foundation types misalignment — caught by foundation auditor (not zero, but caught) |
| G2 | Apollo Client dead code — trap passed; all pages use Apollo |
| G3 | Router registration gap — coordinator caught missing registrations |
| G4 | GraphQL argument parity — coordinator verified field names and arguments |
| G5 | Non-existent framework parameters — architect did not propagate traps into api-spec.md |

### Known Stress Points
- Router registration in main.py is a recurring integration failure mode
- Auth request/response contracts between frontend and backend are never explicitly documented
- GraphQL depth limiting is consistently missed in architect design docs
- Security gate agent (`vsm_security`) failed with LLM provider error — manual fallback required
- Parallel frontend agents overwrite shared files (queries.ts)
- Docker-compose `:-` fallbacks persist despite FB2 mutations
- Strawberry auto-camelCase causes auditor false positives (recurring FB16 issue)

### Result
- **Score**: 3.6/5.0
- **BLOCKERs**: 0 after fix wave (foundation: 2 pre-fix, implementation: 3+ pre-fix, integration: 1 pre-fix)
- **Fix iterations**: 1 major fix wave
- **Traps caught**: T1 (H83), T2 (H80), T3 (H84), T4 (H81), T5 (H79), T6 (H82)
- **Traps missed/partial**: None — all 6 deliberate traps passed
- **Prevention rules validated**: H79, H80, H81, H82, H83, H84, H65, H69
- **New mutations**: H85-H88, security-lessons.md L25 reinforcement, integration-checklist.md router registration check
- **Auditor false positive**: camelCase GraphQL queries flagged as BLOCKER (recurring FB16 issue)


---

## FB19 — KitchenSync (Restaurant Order Management)

**Date**: 2026-05-25
**Tier**: 2
**Classification**: Substantial project (kitchen display, POS, inventory, reporting)
**Stack**: FastAPI + SQLAlchemy 2.0 + Strawberry GraphQL + Celery + Redis + Socket.io | React 18 + Vite + Apollo Client v3 + Zustand + Recharts
**Build directory**: `~/vsm-fitness-builds/coach/FB19-20260525/`

### Coverage Map
- **Backend**: Auth (JWT/bcrypt), RBAC (4 roles), CRUD routers (7), GraphQL (Strawberry), Socket.IO, Celery tasks, SQLAlchemy 2.0 models, SlowAPI rate limiting
- **Frontend**: React 18 + Vite, Apollo Client v3, Zustand stores, Recharts reports, Socket.IO client, role-based routing
- **Infra**: Docker + docker-compose (postgres, redis, api, worker, realtime, frontend)

### Key Findings
- **Backend tests**: 18/18 passing after fix wave
- **Frontend build**: Passing
- **Security**: 1 HIGH (hardcoded postgres password, fixed), 3 LOW documented
- **Integration**: 1 mismatch (orphaned GraphQL subscription, fixed), duplicate shared types removed

### New Hypotheses
| ID | Hypothesis |
|---|---|
| H90 | httpx version drift breaks ASGI test clients |
| H91 | SQLAlchemy UUID columns + SQLite test DB require explicit uuid.UUID() conversion |
| H92 | Rate-limited auth endpoints exhaust test quotas when tests register users repeatedly |
| H93 | Celery task tests require broker mocking when Redis is unavailable |

### Result
- **Score**: [pending vsm_trainer evaluation]
- **BLOCKERs**: 0 after fix wave
- **Fix iterations**: 1 major fix wave (test suite + security + integration)
- **Prevention rules validated**: H85, H86, H87, H63
- **New mutations**: FB19-1..FB19-6, Mutation 44/45/46

---

## FB21: EduFlow — Online Course & Learning Management Platform

**Complexity**: Medium (4 waves, ~3000 lines, 4 services: API + worker + realtime + frontend)
**Date**: 2026-05-25
**Score**: 3.7 / 5.0
**Services**: FastAPI backend, Celery/Redis worker, Socket.io realtime, React frontend

### Coverage Map

| Capability | Tested by |
|---|---|
| Foundation wave | Sequenced sub-waves (2a core → 2b dependent infrastructure) |
| Parallel S1 agents | Backend routers (7) + frontend pages (7) built simultaneously |
| S2 coordination | WebSocket event contracts, GraphQL SDL, env var parity |
| S3* audit | Foundation audit caught missing `pydantic-settings` (BLOCKER) |
| Security gate | 1 CRITICAL (deliberate trap) + 7 HIGH + 2 LOW. CRITICAL false negative: Check #13 PASSed `ALLOWED_ROLES` containing `"admin"` |
| Integration verification | 10 PASS, 3 BLOCKERs (event casing, App.tsx placeholders, env var mismatch) |
| Testing wave | 30/30 backend + 37/37 frontend. Independent verification by vsm_meta confirmed accuracy |
| Meta-reflection | vsm_meta spawned successfully (H94 validated). Generated 6 hypotheses (H99–H104) |
| Fix wave | Fixes applied inline during Phase 6 (process deviation). No re-audit artifact (H98 FAIL) |
| Prevention rule validation | L60 (admin exclusion), Check 58 (CORS wildcards), Phase 6/7 boundary algedonic signal |

### Known Stress Points
- Security gate allowlist composition check must exclude superuser roles (L60)
- Rate limit exception handler must be paired with SlowAPIMiddleware (L52)
- Phase 6/7 boundary must prohibit inline fixes (structural mutation applied)
- CORS method/header wildcards must be explicit when credentials enabled (Check 58)
- GraphQL subscription ownership verification before yielding (L57)
- Zero deprecation warnings: ConfigDict, lifespan context manager (Check 56)

### Hypotheses Tested
| Hypothesis | Result |
|---|---|
| H94: Phase 8b MUST spawn vsm_meta | **confirmed** |
| H95: GraphQL subscriptions verify course access before yielding | **confirmed** |
| H96: Zero deprecation warnings | **confirmed** |
| H97: Rate limiting distributed-safe or documented | **confirmed** (TODO present, but security gate did not flag) |
| H98: Phase 7 fix wave produces re-audit artifact | **confirmed** (no artifact produced — process deviation) |

### Mutations Applied
- L60: Self-Registration Allowlist Must Exclude Superuser Roles (security-lessons.md)
- Check 58: CORS Method and Header Wildcards (integration-checklist.md)
- vsm_security.md: Check #13 refined to verify allowlist composition
- Structural: SKILL.md Phase 6/7 boundary algedonic signal (user-approved)

---

## FB5: ContractStress — Contract Lifecycle Management Platform

**Complexity**: High (4-5 waves, 3000+ lines, 4 services)
**Date**: 2026-05-23
**Score**: 3.7 / 5.0
**Services**: FastAPI backend, React frontend, Redis, Celery
**Note**: Pre-ledger entry — executed before structured result format. First build to identify Phase 8b meta-reflection as a critical gap.

### Coverage Map

| Capability | Tested by |
|---|---|
| Parallel S1 agents | 14 agents spawned — scalability stress test |
| GraphQL RBAC drift | REST vs GraphQL role validation mismatch |
| Security gate | Ownership filtering gaps, JWT in localStorage |
| Testing wave | 86 backend tests pass; zero frontend tests (major gap) |
| Meta-reflection | Absent as formal artifact — identified as critical gap |

### Result
- **Score**: 3.7/5.0
- **BLOCKERs**: 5
- **Fix iterations**: 3 (at max limit)
- **Key gap**: Phase 8b meta-reflection absent — no effectiveness audit, coverage audit, or hypothesis generation
- **Mutations**: H30–H33 generated (architect chunking, split tester, WebSocket auth check, security sequencing)

---

## FB6: DeepContract — DeepContract (Contract + eSignature Platform)

**Complexity**: High (4-5 waves, 3500+ lines, 4 services)
**Date**: 2026-05-23
**Score**: 3.6 / 5.0
**Services**: FastAPI backend, React frontend, Redis, Celery

### Coverage Map

| Capability | Tested by |
|---|---|
| GraphQL RBAC parity | REST and GraphQL role validation alignment |
| Upload filename sanitization | File upload security |
| Enum runtime safety | `str, enum.Enum` for GraphQL compatibility |
| Circular import prevention | Router → main.py import traps |
| Agent timeouts | Architect timed out at 600s; tester timed out at 900s |
| Security gate | Fail-open GraphQL context, missing httpOnly cookies |

### Result
- **Score**: 3.6/5.0
- **BLOCKERs**: 0 after fix waves
- **Fix iterations**: 3 (foundation + post-implementation + security)
- **Key gap**: Agent timeouts on large builds; security downgraded HIGH findings
- **Mutations**: H30–H36 confirmed/generated; vsm_architect chunking, vsm_tester split, WebSocket auth check, Phase 8b template

---

## FB7: JurisFlow — Legal Document & Contract Lifecycle Management

**Complexity**: High (4-5 waves, 2500+ lines, 4 services)
**Date**: 2026-05-23
**Score**: 3.5 / 5.0
**Services**: FastAPI backend, React frontend, Redis, Celery

### Coverage Map

| Capability | Tested by |
|---|---|
| Foundation model-spec alignment | `models.py` must match `data-model.md` exactly |
| GraphQL RBAC parity | REST vs GraphQL role validation |
| WebSocket auth verification | Socket.io room join auth |
| Security gate | CORS wildcard, GraphQL auth bypass |
| Tester security regression | Tester reverted security fix (L38) |
| Meta-reflection | Full structured artifact with 3 hypotheses (H34–H36) |

### Result
- **Score**: 3.5/5.0
- **BLOCKERs**: 4 (initial audit) + 2 HIGH (security)
- **Fix iterations**: 2
- **Key gap**: Foundation model drift caused cascade failures; tester actively weakened auth protections
- **Mutations**: Integration Check 31–32, vsm_tester security-aware testing, vsm_architect "read existing docs" instruction

---

## FB8: EduFlow — Online Course & Learning Management Platform

**Complexity**: High (4-5 waves, 3500+ lines, 4 services)
**Date**: 2026-05-23
**Score**: 3.9 / 5.0
**Services**: FastAPI backend, React frontend, Redis, Celery

### Coverage Map

| Capability | Tested by |
|---|---|
| Prevention rule transfer (H34–H36) | Model-spec alignment, tester auth integrity, post-fix re-check |
| GraphQL RBAC parity | Security gate escalation to CRITICAL |
| WebSocket enrollment auth | Room join verification |
| Auditor false positives | FastAPI router imports, Strawberry auto-camelCase |
| Foundation wave | Exact model-spec alignment (5/5 score) |

### Result
- **Score**: 3.9/5.0
- **BLOCKERs**: 6 (2 false positives, 4 real)
- **Fix iterations**: 1
- **Key success**: All prevention rules from FB7 passed; model-spec alignment exact; security gate correctly escalated CRITICAL
- **Mutations**: H37–H40, L42–L43, Check 30, vsm_auditor false-positive prevention

---

## FB9: HealthBridge — Telehealth & Patient Health Records Platform

**Complexity**: High (4-5 waves, 3000+ lines, 4-5 services)
**Date**: 2026-05-23
**Score**: 4.0 / 5.0
**Services**: FastAPI backend, React frontend, Redis, Celery

### Coverage Map

| Capability | Tested by |
|---|---|
| Foundation wave sequencing | Dependency race conditions between parallel foundation agents |
| JWT signature verification | `verify_signature=False` bypass caught by security gate |
| GraphQL RBAC parity | All list queries scoped to authenticated user |
| WebSocket auth | In-band auth via authenticate event |
| File upload sanitization | MIME validation, size limits, filename sanitization |
| Security gate | 20 deliberate stress points; caught CRITICAL JWT bypass introduced during fix wave |
| Tester | 54 backend + 20 frontend tests; tester fixed 5 bugs inline |

### Result
- **Score**: 4.0/5.0 (highest score to date)
- **BLOCKERs**: 5
- **Fix iterations**: 2
- **Key success**: Security gate caught a subtle JWT signature bypass introduced DURING the fix wave — exceeding expectations
- **Mutations**: Anti-Pattern #19, L28–L29, Pattern #22, H41 (sequenced foundation sub-waves)

---

## FB11

**Status**: Never executed. Only a prompt draft (`FB11-prompt-draft.md`) exists in `~/vsm-fitness-builds/coach/`. No build directory was created.

---

## FB17: ClaimFlow — Insurance Claims Processing & Fraud Detection Platform

**Complexity**: High (4-5 waves, 2500–3500 lines, 4 services)
**Date**: 2026-05-25
**Services**: FastAPI backend, React frontend, Redis, Celery
**Note**: Build executed and artifacts produced, but no formal fitness report was generated by the coach. Evaluated via wiring report and lessons only.

### Coverage Map

| Capability | Tested by |
|---|---|
| Foundation wave module-level side effects | `sio.py` module-level `get_settings()` caused import failures |
| Config typo resilience | `ndef get_settings()` SyntaxError caught |
| vsm_wiring agent | Wiring report produced for main.py, realtime.py, App.tsx, main.tsx |
| Security gate | CORS wildcard, GraphQL RBAC mismatch, unfiltered list queries |
| Architect prompt trap propagation | Unverified framework parameters, wrong GraphQL field casing |

### Result
- **Score**: [no formal fitness report]
- **BLOCKERs**: [unknown — no fitness report]
- **Fix iterations**: [unknown — no fitness report]
- **Key artifact**: `wiring-report.md` validates vsm_wiring agent checklist completeness
- **Lessons**: 2 entries documented (module-level side effects, config typo)

---

## FB20: RentFlow — Residential Property Management Platform

**Complexity**: Medium-High (4 waves, ~3200 lines, 4 services)
**Date**: 2026-05-25
**Score**: 3.4 / 5.0
**Services**: FastAPI backend, React frontend, Redis, Celery

### Coverage Map

| Capability | Tested by |
|---|---|
| Prevention rule transfer (H90–H93) | httpx version drift, SQLite UUID conversion, rate-limited auth tests, Celery broker mocking |
| Foundation deprecation debt | Pydantic `class Config`, FastAPI `@app.on_event` embedded despite prevention rules |
| Security gate | 5 CRITICAL + 3 HIGH + 1 MEDIUM; missed GraphQL subscription ACL gap |
| Phase 8b discipline | vsm_meta bypassed until external intervention forced retroactive spawn |
| Testing wave | 56 backend + 31 frontend tests passing; all 6 deliberate traps caught |

### Result
- **Score**: 3.4/5.0
- **BLOCKERs**: 9 total security findings (5 CRITICAL + 3 HIGH + 1 MEDIUM)
- **Fix iterations**: 1 main Phase 7 wave + retroactive corrections
- **Key gap**: Phase 8b bypassed — skill cannot self-assess meta-cognitive discipline without structural enforcement
- **Mutations**: FB20-1..FB20-6 (vsm_meta in SKILL.md, L57–L59, Check 56–57, H90–H93 patterns, auditor deprecation detection, Phase 8b hard block)


---

## FB23: TalentFlow — Recruitment & Talent Management Platform

**Complexity**: Medium-High (Tier 2, 4 waves, ~2000+ lines, 3 services)
**Date**: 2026-05-26
**Score**: 3.2 / 5.0
**Services**: FastAPI backend, React frontend, Redis, Celery

### Coverage Map

| Capability | Tested by |
|---|---|
| Pydantic ConfigDict V2 (H151) | Zero `class Config:` occurrences — fully validated |
| Vite alias `"@"` (H153) | Correct alias, build succeeds — fully validated |
| Module-level settings audit (H154) | `celery_app.py` module-level instantiation MISSED by wiring agent |
| Dependency manifest parity (H155) | `requirements.txt` drifted from environment — reproducibility failure |
| Settings audit exhaustiveness (H156) | Wiring agent checked `main.py`/`main.tsx` only, missed `celery_app.py` |
| Frontend page stub detection (H157) | All pages were `<div>Label</div>` stubs with void imports |
| Phase 4 build gate | `npm run build` deferred to Phase 6, failed there |
| Frontend Dockerfile production | `npm run dev` in production image — deployment anti-pattern |
| Security gate automated scan | 4 HIGH + 5 MEDIUM + 5 LOW; H1/H2 mislabeled as "IDOR" |
| Meta-reflection quality | Exceptional `meta-report.md` with independent verification, agent scores, 10 mutations |
| Reflection phase discipline | `.kimi/lessons.md` NOT produced — Phase 8 skipped |
| Integration ISSUE handling | 4 ISSUEs flagged, only BLOCKER fixed — ISSUEs orphaned |

### Result
- **Score**: 3.2/5.0
- **BLOCKERs**: 1 (frontend build failure) + 4 pre-fix (docker-compose password, test suite)
- **Fix iterations**: 1
- **Tests**: 19 backend + 9 frontend passing
- **Security gate**: 4 HIGH + 5 MEDIUM + 5 LOW; automated scan ran
- **Key gap**: Frontend implementation depth (stubs), Phase 8 reflection missing, dependency drift
- **Mutations**: H154–H157 applied; 10 mutations from meta-report; post-build agent architecture mutations (contracts, boundaries, gotchas, validator)

---

## FB22: OpsCenter — Multi-tenant IT Operations & Incident Management Platform

**Complexity**: High (Tier 3, 4-5 waves, ~3000+ lines, 7 services)
**Date**: 2026-05-25
**Score**: 3.8 / 5.0
**Services**: FastAPI backend, React frontend, Redis, Celery, Prometheus, MinIO, Socket.IO

### Coverage Map

| Capability | Tested by |
|---|---|
| vsm_product scope control (T1) | AI incident summarization explicitly excluded from MVP; architect respected constraints |
| vsm_wiring completeness (T2/T3) | All 9 backend routers registered, all 11 frontend pages routed; no missed entries |
| vsm_devops_coder infrastructure (T4/T5/T6) | 7 services in docker-compose, health checks, custom bridge network, restart policies, no :- fallbacks |
| Foundation audit effectiveness | Env var parity BLOCKER caught; auth.py ALLOWED_ROLES error caught ("editor" vs "responder") |
| Dependency awareness gap | graphql.py agent used `strawberry_sqlalchemy_mapper` (not in requirements.txt); agent killed after 15+ min |
| Pydantic V2 migration debt | 9 router files used deprecated `class Config:` — 201 pytest warnings |
| Vite alias resolution | `"@/"` alias key failed in production build; `"@"` fixed it |
| strawberry-graphql/pydantic compatibility | Runtime import blocked by environment version mismatch |

### Result
- **Score**: 3.8/5.0
- **BLOCKERs**: 4 foundation-phase (env var parity, auth roles, graphql.py mapper, main.py auth_router import)
- **Fix iterations**: 1 (S5 direct fixes for foundation BLOCKERs)
- **Tests**: 5 backend import tests pass, 1 frontend render test pass, frontend build green
- **Security gate**: Zero CRITICAL/HIGH findings; manual checklist passed
- **Key gap**: Backend coder agents lack dependency verification against requirements.txt before importing
- **Mutations**: FB22-1 (dependency verification BLOCKER in vsm_backend_coder, Vite alias BLOCKER in vsm_frontend_coder, H150-H153)

---

## FB24: InventoryFlow — Warehouse Inventory Management

**Complexity**: High (Tier 2+, 4-5 waves, ~2000+ lines, 4 services)
**Date**: 2026-06-02
**Score**: 3.2 / 5.0
**Services**: FastAPI backend, React frontend, Redis, Celery, PostgreSQL, Socket.IO

### Coverage Map

| Capability | Tested by |
|---|---|
| H158 — Frontend page verification gate | ✅ Dashboard.tsx live Recharts chart, Products.tsx sortable table — all 5 pages real data |
| H159 — lessons.md hard Phase 8 gate | ✅ 7 structured entries produced before vsm_meta spawned |
| H160 — Frontend Dockerfile production build | ✅ Multi-stage nginx build, zero `npm run dev` |
| H161 — Optional ISSUE sweep | Partial — some ISSUEs fixed, several remained unfixed (no systematic Phase 7d) |
| SQLAlchemy enum `.value` trap (H203) | Confirmed — `stock.py:338` crashed, all 4 auditors missed it, only pytest caught it |
| Phase 4 hard gate bypass (H204) | Confirmed — build proceeded with 1 failing test through Phases 5-8 |
| Fix wave scope limitation (H205) | Confirmed — 6+ unfixed ISSUEs at build completion |
| GraphQL RBAC parity | Partial — transfer mutations fixed, product mutations still gap |
| Socket.IO event pipeline | Non-functional — frontend listens, backend never emits |
| Frontend build / TypeScript | ✅ `npm run build` and `tsc -b` pass with zero errors |
| Backend tests | 84 passed, 1 failed (enum `.value` AttributeError) |
| Frontend tests | 17 passed, 0 failed |
| Security gate | 0 BLOCKERs, 0 CRITICAL, 0 HIGH, 2 MEDIUM, 4 LOW |

### Result
- **Score**: 3.2/5.0
- **BLOCKERs**: 7 code-level + 1 process-level (Phase 4 hard gate bypass)
- **Fix iterations**: 1 main fix wave + inline fixes
- **Key gap**: Phase 4 Test-First Exit Gate bypassed; SQLAlchemy enum type-safety rule missing
- **Mutations**: python-pitfalls enum trap, integration-checklist GraphQL/Socket.IO checks, fitness ledger entry


---

## FB25: BudgetWise — Personal Finance & Budget Management Platform

**Complexity**: High (Tier 2+, 4-5 waves, ~2000+ lines, 4 services)
**Date**: 2026-06-02
**Score**: 4.0 / 5.0
**Services**: FastAPI backend, React frontend, Redis, Celery, PostgreSQL, Socket.IO, Strawberry GraphQL

### Coverage Map

| Capability | Tested by |
|---|---|
| H203 — SQLAlchemy enum `.value` trap | **Avoided** — all enums use `sa.Enum(...)`; no `.value` crashes |
| H204 — Phase 4 hard gate bypass | **Prevented** — gate legitimate, 82 backend + 53 frontend passed, 0 failures |
| H205 — Fix wave scope limitation | **Prevented** — Phase 7d ISSUE sweep completed, all CRITICAL/HIGH fixed |
| H40 — GraphQL RBAC parity with REST | **Validated** — `delete_budget` admin-only, ownership filtering on list queries |
| H157 — Frontend stub pages | **Prevented** — ALL 5 pages live (Dashboard, Budgets, Transactions, Categories, Upload) |
| Foundation phase stability | Partial — 2 BLOCKERs (Celery module-level `app`, Dockerfile COPY syntax) |
| Hook enforcement system | **CRITICAL FAILURE** — 0 of 8 expected hooks fired for background subagents (H300 confirmed) |
| Security gate | 0 BLOCKERs, 2 CRITICAL + 2 HIGH + 6 MEDIUM + 3 LOW; all CRITICAL/HIGH fixed |
| Integration verification | 0 BLOCKERs, 5 ISSUEs (orphaned exports, dead wsLink, unused proxy) |
| Testing wave | 82 backend passed, 53 frontend passed, 0 failures; frontend build green |
| Fix wave | Zero regressions; defense-in-depth ownership checks at API + worker layers |
| Reflection | `lessons.md` — 6 structured entries (L1-L6) |
| Meta-reflection | `meta-report.md` — 4 new hypotheses (H206-H209), 8 mutation proposals |
| Process audit | 82/100 compliance; flagged missing `meta-report.md` and `mutations-applied.md` |

### Result
- **Score**: 4.0/5.0 (up from FB24's 3.2)
- **BLOCKERs**: 2 code-level (foundation) + 0 process-level
- **Fix iterations**: 1 fix wave + security re-check + re-audit
- **Key gap**: Hook system non-functional for background agents; foundation Dockerfile/Celery wiring still brittle
- **Mutations**: python-pitfalls Celery guard rule, docker-pitfalls COPY syntax rule, security-lessons worker defense-in-depth, vsm_meta checkpoint enforcement, H206-H209
