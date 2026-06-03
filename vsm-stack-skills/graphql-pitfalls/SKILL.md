# GraphQL Pitfalls

Framework-agnostic and framework-specific GraphQL traps discovered by the VSM
swarm through fitness builds. Covers Strawberry (Python) and Apollo Client
(TypeScript) stacks.

## Schema Parameter Verification (Strawberry)

NEVER assume `strawberry.Schema` accepts `validation_rules` or any parameter.
Verify BEFORE using:
```python
import inspect
"validation_rules" in inspect.signature(strawberry.Schema.__init__).parameters
```
Using non-existent parameters causes `TypeError` on import.
**Source**: FB2 `graphql.py` agent assumed `validation_rules` existed.

## Depth Limiting + Complexity Analysis

GraphQL APIs WITHOUT `@graphql-depth-limit` or complexity analysis are HIGH
severity findings. Depth limit max 10 is the minimum baseline.
**Source**: Anti-pattern #8, `security-lessons.md` L25.

## Context Builder Fail-Closed

`get_context` or equivalent context builders MUST propagate auth exceptions
(JWT errors, missing tokens). Never silently catch auth exceptions and return
an anonymous/unauthenticated context. Auth failures MUST result in GraphQL
errors or `AuthenticationError`, not `user = None`.
**Source**: `security-lessons.md` L63, FB21.

## Context Builder Must Never Return Anonymous Context (FB28)

**Status**: Active (FB28-sourced)
**Severity**: BLOCKER
**Applies to**: vsm_backend_coder, vsm_wiring, vsm_security, vsm_auditor

Even when `GraphQLRouter(context_getter=...)` references a named function (see
previous rule), that function itself MUST be fail-closed. It must NEVER return
a context dict containing `user = None`, `user = "anonymous"`, or any
unauthenticated placeholder.

**Correct pattern** (fail-closed — raises on ANY auth failure):
```python
class AuthenticationError(Exception):
    pass

async def get_context(request: Request) -> dict:
    auth_header = request.headers.get("authorization", "")
    if not auth_header:
        raise AuthenticationError("Authorization header required")
    parts = auth_header.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise AuthenticationError("Invalid authorization header format")
    token = parts[1]
    try:
        payload = decode_token(token)
    except JWTError as exc:
        raise AuthenticationError(f"Invalid token: {exc}")
    user_id_str = payload.get("sub")
    if user_id_str is None or payload.get("type") != "access":
        raise AuthenticationError("Invalid token payload")
    user_id = UUID(user_id_str)
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
    if user is None or not user.is_active:
        raise AuthenticationError("User not found or inactive")
    return {"request": request, "user": user}
```

**Incorrect pattern** (BLOCKER — returns anonymous context on failure):
```python
async def get_context(request: Request) -> dict:
    try:
        token = request.headers.get("authorization", "").split()[1]
        payload = decode_token(token)
        user = await get_user(payload["sub"])
    except Exception:
        # NEVER do this — anonymous context bypasses ALL auth checks
        user = None
    return {"request": request, "user": user}
```

**Prevention rules**:
1. The `get_context` function MUST have ZERO `except` blocks that assign `user = None`.
2. Every failure path MUST `raise AuthenticationError(...)` — never fall through to a `return` with `user = None`.
3. Auditor MUST verify: search for `user = None` inside `app/graphql/context.py`. If found, flag as BLOCKER.
4. Security audit MUST verify the auth chain is complete: header present → Bearer format → token decodes → sub claim exists → type is "access" → user exists → user is active. Missing any step = HIGH.

**Source**: FB28 `main.py` used `context_getter=lambda: {"settings": settings}`.
Security audit caught it as BLOCKER. The fix implemented a fail-closed
`get_context` that raises `AuthenticationError` on ALL failure paths.
All authenticated GraphQL mutations then worked correctly.

## Ownership Filtering on ALL List Queries

ALL list queries MUST filter by authenticated user. Unscoped list queries that
return all documents regardless of ownership are a HIGH severity finding.
This applies to both REST list endpoints AND GraphQL list resolvers.
**Source**: FB10, FB14, FB21.

## RBAC Parity Between REST and GraphQL

REST endpoints and GraphQL resolvers MUST enforce identical access control.
Ambiguous natural-language labels like "(owner-filtered)" in `api-spec.md`
cause interpretation drift. Require explicit `RBAC: [roles]` arrays for every
endpoint.
**Source**: Anti-pattern #54, FB17.

## Auto-CamelCase Verification (Strawberry)

Strawberry auto-camelCases field names. If the frontend introspects the schema
and writes queries with camelCase, but the backend resolver expects snake_case,
queries fail at runtime. Architect MUST declare the casing convention explicitly;
implementer MUST verify field names match.
**Source**: `security-lessons.md` L44, FB17.

## Subscription Ownership Verification

GraphQL subscription resolvers MUST verify resource ownership BEFORE yielding
events. A subscription that yields updates for ALL users' resources is an IDOR
vulnerability.
**Source**: `security-lessons.md` L57, FB20.

## Orphaned Queries (Apollo Client)

Every export from `queries.ts` MUST be imported by at least one page or
component. Orphaned exports are dead code that bloat bundles.
**Source**: Anti-pattern #52, FB17.

## Apollo Client Initialized but Unused

If `main.tsx` wraps the app in `ApolloProvider` but ALL pages use REST `fetch()`,
the GraphQL infrastructure is initialized but never exercised. Integration
checklist must verify Apollo Client is actually used.
**Source**: Anti-pattern #53, FB17.

## SQLAlchemy Enum → GraphQL Type Mismatch

`Mapped[EnumType] = mapped_column(sa.String(50))` stores enum values as strings
in the database. When the GraphQL resolver returns the enum, Strawberry may
expect an Enum object but receive a string, causing `AttributeError: 'str'
object has no attribute 'value'`.
**Prevention**: Use `mapped_column(sa.Enum(EnumType))` or convert strings to
enums in the resolver before returning.
**Source**: FB24, H203.

## GraphQL RBAC Enforcement in Resolvers (FB27)

GraphQL resolvers WITHOUT explicit role checks are HIGH severity. Strawberry
does NOT auto-enforce RBAC from FastAPI dependencies. Each resolver MUST
explicitly verify the authenticated user's role.

**Prevention rules**:
1. ALL non-public resolvers MUST verify the authenticated user's role.
2. Use a `require_roles` helper or inline check — NEVER rely on FastAPI's
   `Depends(get_current_user)` alone for role authorization (it validates the
token but does not enforce role constraints for GraphQL resolvers).
3. The GraphQL `get_context` MUST inject the authenticated user object.
4. Auditor MUST verify RBAC parity: every REST endpoint with role restrictions
   MUST have a corresponding GraphQL resolver with equivalent checks.

**Pattern**:
```python
import strawberry
from strawberry.types import Info

class PermissionError(Exception):
    pass

def require_roles(allowed: list[str]):
    def checker(info: Info):
        user = info.context.get("user")
        if not user or user.role not in allowed:
            raise PermissionError("Access denied")
        return user
    return checker

@strawberry.type
class Query:
    @strawberry.field
    def admin_reports(self, info: Info) -> list[Report]:
        user = require_roles(["admin"])(info)
        # ... proceed with admin-only query
```

**Source**: FB27 GraphQL `vehicles` resolver had no RBAC. FastAPI dependency
`get_current_user` was used for REST but GraphQL resolvers were unprotected.
Security audit caught this as HIGH. The fix agent added role checks to all
non-public resolvers and updated the GraphQL context builder to propagate
auth failures.

## GraphQL Schema Depth Limiting Implementation

**Status**: Active (FB27-sourced)
**Severity**: HIGH
**Applies to**: vsm_backend_coder, vsm_security

GraphQL APIs MUST have depth limiting. The rule in `security-lessons.md` states
this is HIGH severity, but FB27 found that simply importing `graphql-depth-limit`
is insufficient — it must be wired into the schema correctly.

**Correct pattern** (Strawberry + Starlette):
```python
from graphql import GraphQLError

def depth_limiter(max_depth: int):
    class DepthLimitValidator:
        def __init__(self, max_depth: int):
            self.max_depth = max_depth

        def enter(self, node, key, parent, path, ancestors):
            if len(path) > self.max_depth:
                raise GraphQLError(f"Query exceeds max depth of {self.max_depth}")

    return DepthLimitValidator

schema = strawberry.Schema(
    query=Query,
    extensions=[MyExtension],
    # Depth limiting via query analysis middleware or extension
)
```

**Incorrect pattern** (HIGH):
```python
# Depth limit imported but never wired into the schema
import depth_limit  # noqa: F401 — dead import, no enforcement
schema = strawberry.Schema(query=Query)  # No depth protection
```

**Source**: FB27 had `depth_limit` in dependencies but it was not wired into
the Strawberry schema. Security audit caught this as HIGH. Fix agent added a
custom depth validator extension to the schema configuration.


## Rule: GraphQLRouter context_getter MUST Reference Imported Function

**Status**: Active (FB28-sourced)
**Severity**: BLOCKER
**Applies to**: vsm_backend_coder, vsm_wiring, vsm_security, vsm_auditor

`GraphQLRouter(context_getter=...)` must reference an actual imported function
that validates Bearer tokens, decodes JWT, queries the database, and injects
the authenticated `user` into context. A lambda or static dict breaks ALL
authenticated GraphQL operations.

**Correct pattern**:
```python
from app.graphql.context import get_context

app.include_router(
    GraphQLRouter(schema, context_getter=get_context),
    prefix="/graphql",
)
```

**Incorrect pattern** (BLOCKER):
```python
# Placeholder lambda — no auth, no user injection
app.include_router(
    GraphQLRouter(
        schema,
        context_getter=lambda: {"settings": settings},
    ),
    prefix="/graphql",
)
```

**Prevention rules**:
1. Auditor MUST verify `context_getter` is an imported function name, not a lambda.
2. Wiring agent MUST verify `app.graphql.context` module exists and has a `get_context` function.
3. Security audit MUST flag any `lambda` or static dict passed to `context_getter` as BLOCKER.

**Source**: FB28 `main.py` used `context_getter=lambda: {"settings": settings}`.
All authenticated GraphQL mutations failed. Security audit caught it as BLOCKER
with exact file:line evidence.
