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
