# Python Pitfalls

**Version scope**: Python 3.10+. For older versions, use `SearchWeb` to verify behavior.

Empirical traps discovered by the VSM swarm. Use `SearchWeb` for API documentation.

## Module-Level Side Effects (H65)
NEVER instantiate at module level. These crash on import without env vars:
- Pydantic Settings: `settings = Settings()` → use `@lru_cache` factory
- SQLAlchemy engine: `engine = create_async_engine(...)` → use `_get_async_engine()` factory
- Any client that reads env on init

## Pydantic ConfigDict (H151)
`class Config:` inside a Pydantic model is deprecated in V2. Use:
```python
model_config = ConfigDict(...)
```
Flagged as BLOCKER in audit.

## Enum Construction
Plain `enum.Enum` raises `ValueError` when constructed from strings. Always use:
```python
class Status(str, enum.Enum):
```

## SQLAlchemy Column Shadowing
Never name columns `text`, `select`, `join`, `update` — they shadow SQLAlchemy imports.
Use `sa.Text`, `sa.select`, or rename columns.

## Strawberry Schema Parameters
NEVER assume `strawberry.Schema` accepts `validation_rules` or any parameter.
Verify BEFORE using:
```python
import inspect
"validation_rules" in inspect.signature(strawberry.Schema.__init__).parameters
```
Using non-existent parameters causes `TypeError` on import.

## Dependency Manifest Drift
Before importing ANY non-stdlib package, verify it exists in the project's 
dependency manifest (`requirements.txt`, `pyproject.toml`, etc.). Using packages 
not listed is a BLOCKER.

## Import Verification
After writing backend files, verify they import cleanly in a fresh subprocess.
Use the project's top-level package names:
```bash
python -c "import app.main; import app.graphql"
```
(Adjust `app.main`, `app.graphql` to match the actual project structure.)
Module-level NameError / ImportError is a BLOCKER.

## FastAPI Lifespan Events
`@app.on_event("startup")` / `@app.on_event("shutdown")` are deprecated.
Use `lifespan` context managers instead.

## Rate Limiting Handler
When using `SlowAPIMiddleware`, ALWAYS install:
```python
@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request, exc):
    return JSONResponse(status_code=429, content={"detail": "Rate limit exceeded"})
```
Without the handler, rate-limited requests crash with 500 instead of 429.

## Celery App Module-Level Instantiation (Discovered FB23)
A module-level `celery_app = ...` is **NOT a BLOCKER** if it does NOT trigger
any env-dependent factory at import time. The BLOCKER is specifically if the
assignment calls a function that accesses `get_settings()` / `Settings()` /
`os.environ` or any env-dependent resource before the Celery worker process
initializes:
```python
# WRONG — crashes on import without env vars
celery_app = _get_celery_app()   # if _get_celery_app() calls Settings()
```
Safe pattern: keep the module-level assignment but make the factory itself
lazy (use `@lru_cache` for settings, or have the factory defer env reads to
`celery.conf.update(...)` called at worker boot). The wiring agent MUST grep
ALL `*.py` files (not just `main.py`) for module-level `get_settings()` /
`Settings()` calls. Audit MUST distinguish "module-level assignment" from
"module-level env-dependent side effect."

## SQLAlchemy String-Mapped Enum `.value` Trap (FB24)

When an enum column is declared as:
```python
class Status(str, enum.Enum):
    pending = "pending"
    done = "done"

class Task(Base):
    status: Mapped[Status] = mapped_column(sa.String(50))
```

SQLAlchemy loads the value from the database as a **plain `str`**, NOT as the
`Status` enum instance. Endpoint code that calls `task.status.value` will crash
with `AttributeError: 'str' object has no attribute 'value'`.

**Prevention rules**:
1. Prefer `sa.Enum(Status)` over `sa.String(N)` for enum columns.
2. If `sa.String(N)` must be used, NEVER call `.value` on the attribute.
   Compare directly: `if task.status == Status.pending.value:` is wrong;
   `if task.status == Status.pending:` is also wrong (comparing str to enum).
   Use: `if task.status == "pending":` or cast explicitly.
3. Auditor MUST flag any `.value` call on a model attribute whose column is
   declared with `sa.String` rather than `sa.Enum`.

**Evidence**: FB24 `app/routers/stock.py:338` crashed with this exact bug.
All four audit passes missed it; only pytest caught it.

## CORS Wildcard with Credentials
NEVER use `allow_origins=["*"]` with `allow_credentials=True`. Always use an
explicit allowlist:
```python
allow_origins=["http://localhost:3000", "https://app.example.com"]
```
Wildcard `*` with credentials is a BLOCKER. See also `security-lessons.md` L61.

## JWT Auth Signature Verification
`jwt.decode` MUST verify signatures. Never pass
`options={"verify_signature": False}`.

`get_current_user` MUST raise `HTTPException(401)` on ALL failure paths —
never return `None`. Returning `None` silently creates an anonymous session
that bypasses auth guards.

## GraphQL Context Fail-Closed
`get_context` or equivalent context builders MUST propagate auth exceptions
(JWT errors, missing tokens). Never silently catch auth exceptions and return
an anonymous/unauthenticated context. Auth failures MUST result in GraphQL
errors or `AuthenticationError`, not `user = None`.

See also: `security-lessons.md` L63 (GraphQL context builders must be fail-closed).

## GraphQL Ownership Filtering
ALL list queries MUST filter by authenticated user. Unscoped list queries
that return all documents regardless of ownership are a HIGH severity finding.

This applies to both REST list endpoints AND GraphQL list resolvers.

## Registration Role Allowlist
`ALLOWED_ROLES` MUST exist AND exclude superuser roles ("admin", "superuser").
Self-registration must default to the lowest-privilege role.

Before finalizing `ALLOWED_ROLES`, read `data-model.md` and verify EVERY role
in the allowlist exists in the `Role` / `UserRole` enum defined there.
Mismatched roles (e.g., `"editor"` in allowlist but `"responder"` in the enum)
are a BLOCKER. The allowlist and the data model must be identical.

**Source**: FB22 `auth.py` had `ALLOWED_ROLES = ["viewer", "editor", "admin"]`
but data model defined `"viewer"`, `"responder"`, `"admin"`. `"editor"` did not
exist; `"responder"` was missing (H151).

## Celery Module-Level App Guard (FB25)
For any module consumed by `celery -A module worker`, the module MUST expose a
top-level `app` object. If module-level instantiation risks env-dependent crashes
(e.g., `get_settings()` on import), guard it with an env var skip flag:

```python
import os
if os.environ.get("_CELERY_SKIP_IMPORT") != "1":
    app = create_celery_app()
```

**Source**: FB25 `celery_app.py` had only a factory; `celery -A app.celery_app worker`
failed because the CLI could not find `app.celery_app.app`.

## Rule: Starlette UploadFile.read() Signature

**Status**: Active (FB26-sourced)
**Severity**: BLOCKER
**Applies to**: vsm_backend_coder, vsm_security

Starlette's `UploadFile.read()` signature is `read(size: int = -1)`. NEVER pass `max_bytes=` as a keyword argument — this raises `TypeError` at runtime.

**Correct pattern**:
```python
contents = await file.read(MAX_FILE_SIZE + 1)
if len(contents) > MAX_FILE_SIZE:
    raise HTTPException(status_code=413, detail="File too large")
```

**Incorrect pattern** (BLOCKER):
```python
contents = await file.read(max_bytes=MAX_FILE_SIZE)  # TypeError!
```

## Rule: Pydantic Response Model UUID Coercion

**Status**: Active (FB27-sourced)
**Severity**: BLOCKER
**Applies to**: vsm_backend_coder, vsm_backend_fix, vsm_auditor

When SQLAlchemy models use `UUID` primary keys or foreign keys, Pydantic response
models receive `UUID` objects. FastAPI's default JSON serialization of `UUID`
objects is inconsistent and may produce non-string representations that break
frontend parsing or API contract tests.

**Prevention rules**:
1. Create a base response model with a `model_validator(mode="before")` that
   recursively converts `UUID` instances to `str`.
2. ALL response schemas MUST inherit from this base model (or the equivalent
   camelCase base if one exists).
3. Do NOT rely on FastAPI's automatic `jsonable_encoder` for UUID fields.

**Pattern**:
```python
from uuid import UUID
from pydantic import BaseModel, model_validator

class ResponseBase(BaseModel):
    @model_validator(mode="before")
    @classmethod
    def coerce_uuids(cls, data):
        if isinstance(data, dict):
            return {
                k: str(v) if isinstance(v, UUID) else v
                for k, v in data.items()
            }
        return data
```

**Source**: FB27 14 backend test failures were caused by UUID objects not being
serialized as strings. The fix agent introduced `ResponseBase` with a recursive
UUID→str validator. Auditor missed it in all four passes; only pytest caught it.

## Rule: Missing `await` on Async Function Calls

**Status**: Active (FB27-sourced)
**Severity**: BLOCKER
**Applies to**: vsm_backend_coder, vsm_backend_fix, vsm_auditor, vsm_coordinator

Calling an `async def` function without `await` returns a coroutine object,
not the result. In FastAPI endpoints this causes silent failures: the response
may be a serialized coroutine string or `null`, with HTTP 200 — no exception
is raised, and the bug is invisible without test coverage.

**Prevention rules**:
1. Wiring agent MUST grep ALL `*.py` files in `app/` for `async def` functions
   that are called without `await` in endpoint/router bodies.
2. Audit MUST verify that every async service/repository call in a route handler
   is awaited.
3. Pytest catches this ONLY if the test actually asserts on the return value's
   structure or content.

**Common targets**: `optimize_waypoints()`, `get_current_user()`, repository
`get_by_id()`, `send_email()`, `upload_file()`, any service-layer async method.

**Source**: FB27 `vehicles.py` called `optimize_waypoints()` without `await`.
The endpoint returned HTTP 200 with a coroutine object string. Only pytest
`test_optimize_waypoints` caught it; four audit passes missed it.


## Rule: Pydantic `type` Statement + `Field(alias=...)` Produces Warnings

**Status**: Active (FB28-sourced)
**Severity**: LOW (noise pollution)
**Applies to**: vsm_backend_coder, vsm_backend_fix

Python 3.12+ `type` statement creates type aliases. Attaching `Field(alias=...)`,
`Field(validation_alias=...)`, or `Field(serialization_alias=...)` directly to
a `type` alias produces `UnsupportedFieldAttributeWarning` because the alias
carries no model field metadata.

**Correct pattern**:
```python
from typing import Annotated
from pydantic import Field

# Use Annotated in a class-based model, not a type alias
class MySchema(BaseModel):
    first_name: Annotated[str, Field(alias="firstName")]
```

**Incorrect pattern** (warning spam):
```python
# type alias with Field — warning has no effect
type FirstName = Annotated[str, Field(alias="firstName")]

class MySchema(BaseModel):
    first_name: FirstName  # UnsupportedFieldAttributeWarning at runtime
```

**Prevention rules**:
1. Never attach `Field(alias=...)` to a `type` alias.
2. Use `Annotated[..., Field(...)]` directly in model field definitions.
3. If 100+ `UnsupportedFieldAttributeWarning` appear in pytest output, grep for
   `type .* = .*Field` and replace with inline `Annotated`.

**Source**: FB28 pytest output had 100+ warnings from `type` aliases with
`Field(alias=...)` in schema definitions. No functional bug, but extreme
noise pollution obscures real issues.

## Rule: ORM-Based Schemas Need Field-Level UUID Coercion

**Status**: Active (FB28-sourced, redesign of FB27-1)
**Severity**: BLOCKER
**Applies to**: vsm_backend_coder, vsm_backend_fix, vsm_auditor

`model_validator(mode="before")` converting UUID→str only works when the input
is a dict. When `from_attributes=True` reads SQLAlchemy ORM objects directly,
the model validator is bypassed because the input is an object, not a dict.

**The base model MUST have BOTH validators**:
- `@model_validator(mode="before")` for dict input path
- `@field_validator("*", mode="before")` for ORM object path

**Correct pattern**:
```python
from uuid import UUID
from pydantic import BaseModel, ConfigDict, model_validator, field_validator

class ORMBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    @model_validator(mode="before")
    @classmethod
    def _coerce_uuids_dict(cls, data):
        """Handles dict input path."""
        if isinstance(data, dict):
            return {k: str(v) if isinstance(v, UUID) else v for k, v in data.items()}
        return data

    @field_validator("*", mode="before")
    @classmethod
    def _coerce_uuids_orm(cls, v):
        """Handles ORM object path (from_attributes=True)."""
        return str(v) if isinstance(v, UUID) else v
```

**Incorrect pattern** (BLOCKER):
```python
class ORMBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    @model_validator(mode="before")
    @classmethod
    def _coerce_uuids(cls, data):
        # ONLY works for dict input; ORM objects bypass this!
        if isinstance(data, dict):
            return {k: str(v) if isinstance(v, UUID) else v for k, v in data.items()}
        return data
```

**Prevention rules**:
1. ALL ORM-based base models MUST have BOTH `@model_validator(mode="before")`
   AND `@field_validator("*", mode="before")` for UUID→str coercion.
2. Auditor MUST verify both validators exist on schema base classes.
3. Tests MUST include ORM-object-to-schema serialization (not just dict input).
4. If a schema inherits from a base with `from_attributes=True`, the base MUST
   have the field_validator.

**Source**: FB27 introduced `model_validator(mode="before")` which prevented
dict-path UUID failures. FB28 revealed the ORM path bypassed it, causing
`ResponseValidationError` on all endpoints returning ORM objects. The redesigned
rule requires BOTH validators.

**Mutation history**: FB27-1 (original, scored 2 — ineffective). Redesigned in FB28.
