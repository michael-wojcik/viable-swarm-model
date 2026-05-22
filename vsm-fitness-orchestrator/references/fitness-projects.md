# Fitness Project Catalog

> **Mutation rules**: Append new fitness projects as new technology patterns
> emerge. Mark obsolete projects (e.g., deprecated frameworks) with notes.
> Each project should exercise a unique combination of skill capabilities.

---

## FB1: DocuFlow — Collaborative Document Editor

**Complexity**: High (4-5 waves, 2000+ lines, 2 services: API + worker)  
**Estimated duration**: 2-3 hours  
**Services**: FastAPI backend, React frontend, Redis worker

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

### Project Spec

```
BACKEND (FastAPI + PostgreSQL + Redis):
- User auth: JWT with bcrypt, no defaults, no || fallbacks
- Document CRUD with strict ownership filtering
- pgvector semantic search (text-embedding-3-small, 1536 dims)
- Yjs CRDT updates persisted to PostgreSQL BYTEA
- Redis task queue for background AI summarization
- SSE endpoint for streaming AI summaries
- WebSocket presence/awareness with in-band auth
- GraphQL API with subscriptions for document lists

FRONTEND (React + Vite + TypeScript):
- TipTap v2 rich text editor with Yjs collaborative editing
- Mobile-first responsive UI
- Vite path alias @docuflow/shared
- GraphQL split link (HTTP + ws subscriptions)
- Dark theme, 60px min touch targets

SHARED:
- TypeScript types shared between frontend and backend
- WebSocket event constants as single source of truth
```

---

## FB2: GeoQuiz — Multiplayer Geospatial Quiz Platform

**Complexity**: Medium-High (3-4 waves, 1500+ lines, 2 services)  
**Estimated duration**: 2 hours  
**Services**: FastAPI backend, React frontend

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

### Project Spec

```
BACKEND (FastAPI + PostgreSQL + Redis):
- User auth with JWT
- Quiz CRUD with question/answer management
- PostGIS: quiz locations with radius search, bounding box, MVT tiles
- Socket.io v4 rooms for game session isolation
- Server-authoritative countdown timer (asyncio task)
- Scoreboard with real-time updates
- Redis for matchmaking queue

FRONTEND (React + Vite):
- Mobile-first game UI
- Map view with quiz locations (Leaflet or MapLibre)
- Real-time game lobby with Socket.io
- Countdown display (160px+ font)
- Scoreboard

SECURITY:
- PublicQuestion DTO must omit correct_answer_index
- Document ownership on quiz lists (users see their own quizzes)
- CORS explicit allowlist
```

---

## FB3: TaskFlow — Workflow Orchestration Platform

**Complexity**: High (4-5 waves, 2500+ lines, 3 services: API + worker + scheduler)  
**Estimated duration**: 3 hours  
**Services**: FastAPI backend, Celery/Redis worker, React frontend

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

### Project Spec

```
BACKEND (FastAPI + PostgreSQL + Redis):
- User auth with JWT
- Workflow DAG editor: nodes/edges stored as JSONB
- DAG validation: 3-color DFS cycle detection, Kahn topological sort
- Redis task queue for workflow execution
- Celery workers that execute DAG nodes in topological order
- GraphQL API with subscriptions for execution progress
- SSE for real-time execution status

FRONTEND (React + Vite):
- D3.js v7 interactive DAG visualization
- Drag-and-drop node editor
- Click-to-connect edges
- Real-time execution progress via GraphQL subscriptions
- Dark theme

SHARED:
- DAG validation logic shared between backend and frontend
- Celery task names defined in shared constants
```

---

## FB[N]: [Project Name]

**Complexity**: [Low/Medium/High]  
**Estimated duration**: [hours]  
**Services**: [list]

### Coverage Map
[Which skill capabilities this project exercises]

### Known Stress Points
[Specific patterns/anti-patterns this build should trigger]

### Project Spec
[Detailed requirements]
