# Backend Patterns

Universal backend architectural patterns. Language-agnostic.

## Auth Flow
1. Registration with role allowlist (exclude superuser roles)
2. Login returns structured response with token + role
3. JWT payload with `sub`, `role`, `exp`, `iat`
4. `get_current_user` raises 401 on ALL failure paths — never returns None
5. Refresh token queries DB for user before minting new tokens

## API Design
- REST: resource-oriented URLs, consistent error shapes
- GraphQL: depth limiting, complexity analysis, auth context propagation
  (see `security-patterns` for GraphQL security details)
- All list endpoints must filter by authenticated user (ownership)

## Middleware Ordering
CORS → Rate Limiting → Auth → Logging → Router

## Server Architecture
- Lazy initialization of shared resources (see `[language]-pitfalls` for specifics)
- Separate config from implementation
- Router-per-domain organization


## Rule: FastAPI Router Prefix Stacking Trap

**Status**: Active (FB29-sourced)
**Severity**: MEDIUM
**Applies to**: vsm_backend_coder, vsm_wiring, vsm_auditor

When a `APIRouter` already defines `prefix="/auth"`, including it in the app
with `app.include_router(router, prefix="/auth")` creates double-prefix URLs
like `/auth/auth/login`. This breaks all frontend and API client calls.

**Correct pattern**:
```python
# router.py — defines prefix
auth_router = APIRouter(prefix="/auth")

@auth_router.post("/login")
async def login(...):
    ...

# main.py — include WITHOUT repeating prefix
app.include_router(auth_router, tags=["auth"])
# URL: POST /auth/login ✅
```

**Incorrect pattern** (MEDIUM):
```python
# router.py
auth_router = APIRouter(prefix="/auth")

# main.py — WRONG: repeats the prefix
app.include_router(auth_router, prefix="/auth", tags=["auth"])
# URL: POST /auth/auth/login ❌
```

**Prevention rules**:
1. Before `app.include_router()`, check if the router already has `prefix=`.
2. If router has prefix, NEVER pass `prefix=` to `include_router()`.
3. If router has NO prefix, THEN `include_router(router, prefix="/auth")` is correct.
4. Auditor MUST verify all router URLs match `api-spec.md` exactly.

**Source**: FB29 `main.py` had `app.include_router(auth_router, prefix="/auth")`
but `auth_router` already defined `prefix="/auth"`. All auth endpoints were at
`/auth/auth/*`. Caught by S5 manual validation in Phase 2c.


## Rule: Use FastAPI Lifespan Context Manager for DB Initialization

**Status**: Active (FB29-sourced)
**Severity**: LOW (pattern preference)
**Applies to**: vsm_backend_coder, vsm_wiring

FastAPI's `@asynccontextmanager` lifespan hook is the cleanest way to initialize
and tear down database connections, create tables, and dispose of engines. It
replaces the older `on_event("startup")` / `on_event("shutdown")` pattern which
is harder to test and reason about.

**Correct pattern**:
```python
from contextlib import asynccontextmanager
from fastapi import FastAPI

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    engine = create_async_engine(settings.database_url)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    app.state.engine = engine
    yield
    # Shutdown
    await engine.dispose()

app = FastAPI(lifespan=lifespan)
```

**Incorrect pattern** (deprecated):
```python
@app.on_event("startup")
async def startup():
    engine = create_async_engine(settings.database_url)

@app.on_event("shutdown")
async def shutdown():
    await engine.dispose()
```

**Prevention rules**:
1. Prefer `lifespan` over `on_event("startup")` / `on_event("shutdown")`.
2. Lifespan MUST create the engine, run `create_all`, and store engine in
   `app.state` for access during requests.
3. Lifespan MUST dispose the engine on shutdown.
4. Tests can override the lifespan by creating the app without it.

**Source**: FB29 `main.py` used `@asynccontextmanager lifespan` for engine
creation, table creation, and disposal. This pattern eliminated module-level
engine calls and made tests import-safe.

---

## Pattern: Async Task Wiring Verification (FB32-3)

**When**: Any endpoint or GraphQL mutation claims to enqueue a background task (Celery, RQ, ARQ, etc.).
**What**: The handler body MUST contain a visible `.delay()`, `.apply_async()`, or equivalent enqueue call. A response message like "queued" or "processing" without an actual enqueue is **ceremonial wiring** and must be flagged.
**Why**: FB32 had two instances (M6, M7) where REST and GraphQL report endpoints returned `"Report generation queued"` but never called `generate_attendee_report.delay(...))`). This creates a false sense of async architecture and allows unbounded DB row creation without work being done.
**How**:

**Correct pattern**:
```python
@router.post("/reports")
async def create_report(req: ReportRequest, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    report = Report(event_id=req.event_id, status="pending", requested_by=user.id)
    db.add(report); await db.commit(); await db.refresh(report)
    # ACTUAL enqueue — not just a message
    generate_attendee_report.delay(str(report.id), str(req.event_id), user.id)
    return {"message": "Report generation queued", "report_id": str(report.id)}
```

**Incorrect pattern** (ISSUE — ceremonial wiring):
```python
@router.post("/reports")
async def create_report(req: ReportRequest, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    report = Report(event_id=req.event_id, status="pending", requested_by=user.id)
    db.add(report); await db.commit(); await db.refresh(report)
    # NO .delay() call! The message is a lie.
    return {"message": "Report generation queued", "report_id": str(report.id)}
```

**Auditor grep check**:
```bash
# Find all endpoints mentioning "queued" / "processing" / "generating"
grep -rn "queued\|processing\|generating" backend/app/routers/ backend/app/graphql_resolvers.py

# For each match, verify .delay() or .apply_async() exists in the same function
grep -A 20 "def create_report\|def request_report" backend/app/routers/reports.py backend/app/graphql_resolvers.py | grep -c "\.delay\|\.apply_async"
```

**Prevention rules**:
1. **Any endpoint returning a message containing "queued", "processing", "generating", or "async"** MUST have a visible enqueue call in the same handler body.
2. **Implementation auditor MUST** grep for these messages and verify the enqueue call exists.
3. **Security auditor MUST** flag unbounded resource creation (e.g., report rows without work being done) as MEDIUM.
4. **Coordinator MUST** verify Celery tasks are imported and called in the API layer, not just defined in `tasks.py`.

**Source**: FB32 M6 (REST reports.py) and M7 (GraphQL requestReport) both claimed queuing without enqueuing.
