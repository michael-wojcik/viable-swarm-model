# Python Pitfalls

**Version scope**: Python 3.10+. For older versions, use `SearchWeb` to verify behavior.

Empirical traps discovered by the VSM swarm. Use `SearchWeb` for API documentation.

## Module-Level Side Effects (H65)
NEVER instantiate at module level. These crash on import without env vars:
- Pydantic Settings: `settings = Settings()` → use `@lru_cache` factory
- SQLAlchemy engine: `engine = create_async_engine(...)` → use `_get_async_engine()` factory
- Any client that reads env on init

## Pydantic ConfigDict (H151) — BLOCKER

**Severity**: BLOCKER (not ISSUE)
**Confirmed by**: Gym experiment H151 (2026-06-04)

`class Config:` inside a Pydantic model is deprecated in V2 and emits
`PydanticDeprecatedSince20` warnings. Use:
```python
model_config = ConfigDict(...)
```

**Why BLOCKER**: FB22 had 9 router files with `class Config:` generating 201
pytest warnings. The pattern still functions (models work), so agents treat it as
a minor ISSUE. But the deprecation warning can be promoted to a hard error with
`pytest -W error::DeprecationWarning`, breaking CI. Treat as BLOCKER to prevent
warning accumulation.

**Prevention rules**:
1. **Backend coder MUST NOT** write `class Config:` in any Pydantic model.
2. **Auditor MUST flag** any `class Config:` as BLOCKER, not ISSUE.
3. **Tester SHOULD run** `pytest -W error::DeprecationWarning` to mechanically
   block this pattern.

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

## Dependency Manifest Drift (H150) — BLOCKER

**Severity**: BLOCKER
**Confirmed by**: Gym experiment H150 (2026-06-04)

Before importing ANY non-stdlib package, verify it exists in the project's 
dependency manifest (`requirements.txt`, `pyproject.toml`, etc.). Using packages 
not listed is a BLOCKER.

**Why this matters**: FB22's graphql.py agent used `strawberry_sqlalchemy_mapper`
— a third-party library not in requirements.txt. This caused 15+ minutes of wasted
agent time trying to verify imports. The gym experiment confirmed that missing
dependencies cause immediate `ModuleNotFoundError` at module load time.

**Prevention rules**:
1. **Backend coder MUST check** `requirements.txt` / `pyproject.toml` BEFORE
   adding any non-stdlib `import` statement.
2. **If a library is needed but not in the manifest**, add it to
   `requirements.txt` FIRST, then use it in code.
3. **Coordinator MUST verify** all backend files import cleanly in a fresh
   subprocess: `python -c "import app.main"`.
4. **Auditor MUST flag** any import of a package not in the manifest as BLOCKER.

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


## Rule: Celery Top-Level Variable MUST Be Named `app`

**Status**: Active (FB29-sourced)
**Severity**: BLOCKER
**Applies to**: vsm_backend_coder, vsm_auditor

Celery's `find_app()` utility searches for a variable named `app` in the target
module. If the variable is named anything else (`celery_app`, `application`,
`celery`), the worker CLI command `celery -A module worker` fails with
`AttributeError: module has no attribute 'app'`.

**Correct pattern**:
```python
# celery_app.py
from celery import Celery

app = Celery("tasks")  # MUST be named `app`
app.conf.update(
    broker_url="redis://localhost:6379/0",
    result_backend="redis://localhost:6379/0",
)
```

**Incorrect pattern** (BLOCKER):
```python
# celery_app.py
from celery import Celery

celery_app = Celery("tasks")  # WRONG — Celery CLI looks for `app`, not `celery_app`
celery_app.conf.update(...)
```

**Prevention rules**:
1. The top-level Celery instance variable MUST be named `app`.
2. Auditor MUST verify `grep -q "^app = Celery" celery_app.py` passes.
3. If the module is imported elsewhere, use `from app.celery_app import app`.

**Source**: FB29 foundation audit caught `celery_app = Celery(...)` in `celery_app.py`.
`celery -A app.celery_app worker` failed because `find_app()` could not locate
an `app` attribute. Renamed to `app` fixed the worker startup.

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

## Rule: Pydantic V2 + SQLAlchemy ORM Test Fixture Pattern (FB28)

**Status**: Active (FB28-sourced)
**Severity**: MEDIUM (test reliability)
**Applies to**: vsm_backend_tester, vsm_backend_coder

When using Pydantic V2 schemas with `from_attributes=True` and SQLAlchemy ORM
models that use `UUID` primary keys, test fixtures may need `BaseModel.model_validate`
monkeypatching to handle ORM→schema serialization. The production code uses
`@field_validator("*", mode="before")` on the base model (see ORM-Based Schemas
rule above), but tests that construct ORM objects directly and then serialize
them may still hit edge cases.

**Reusable conftest.py pattern**:
```python
import os
from uuid import UUID
from pydantic import BaseModel

# Set env vars BEFORE app imports
os.environ["JWT_SECRET"] = "test-secret-key-that-is-32-chars-long-abc"
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"

# Monkeypatch BaseModel.model_validate for ORM UUID coercion
_original_model_validate = BaseModel.model_validate

@classmethod
def _patched_model_validate(cls, obj, *, strict=None, from_attributes=None, context=None):
    if hasattr(obj, "__mapper__"):
        data = {}
        for col in obj.__table__.columns:
            val = getattr(obj, col.name, None)
            data[col.name] = str(val) if isinstance(val, UUID) else val
        return _original_model_validate.__func__(cls, data, strict=strict, from_attributes=from_attributes, context=context)
    return _original_model_validate.__func__(cls, obj, strict=strict, from_attributes=from_attributes, context=context)

BaseModel.model_validate = _patched_model_validate
```

**When this pattern is needed**:
1. SQLAlchemy ORM models use `UUID` primary keys or foreign keys.
2. Pydantic response schemas inherit from a base with `from_attributes=True`.
3. Tests return raw ORM objects from endpoints (not dicts).
4. `ResponseValidationError` occurs in tests but NOT in production.

**When this pattern is NOT needed**:
- If the base model's `@field_validator("*", mode="before")` handles all ORM paths
  correctly, monkeypatching is redundant. Prefer fixing the base model over
  adding test-level workarounds.

**Prevention rules**:
1. Backend tester MUST verify tests pass WITHOUT monkeypatching first.
2. If monkeypatching is required, document WHY in `conftest.py` comments.
3. The monkeypatch MUST be applied BEFORE any app imports that use the models.
4. Prefer fixing the production base model over permanent test workarounds.

**Source**: FB28 `conftest.py` required ~230 lines of monkeypatching to handle
ORM UUID coercion in tests. The production `CamelModelORM` had both validators
but tests still needed the patch due to FastAPI's internal serialization path.
This pattern prevents each build from reinventing the workaround.


## Rule: Python 3.14+ Enum `str()` Breaking Change

**Status**: Active (FB29-sourced)
**Severity**: BLOCKER (breaks auth, RBAC, ownership checks)
**Applies to**: vsm_backend_coder, vsm_backend_tester, vsm_auditor

In Python 3.14, `str(Enum.member)` returns `"Class.member"` instead of `"member"`.
This breaks token claims, role comparisons, and ownership checks across the
entire backend.

**Correct pattern**:
```python
# Token generation — use .value, not str()
role = user.role.value  # "writer"
claims = {"sub": str(user.id), "role": role}

# Role comparison — use .value
if user.role.value not in ("writer", "editor", "publisher", "admin"):
    raise HTTPException(403, "Invalid role")

# Ownership check — use .value for admin bypass
if str(article.author_id) != str(user.id) and user.role.value != "admin":
    raise HTTPException(403, "Not owner")
```

**Incorrect pattern** (BLOCKER):
```python
# str() returns "UserRole.writer" in Python 3.14 — breaks everything
role = str(user.role)  # "UserRole.writer" — JWT claim is wrong
token = create_access_token({"sub": str(user.id), "role": role})

# Comparison fails — "UserRole.writer" != "writer"
if str(user.role) != "writer":
    ...
```

**Prevention rules**:
1. NEVER use `str(enum_member)` for value extraction. Always use `.value`.
2. Phase 2a code review MUST verify all enum usage uses `.value`.
3. Token claims MUST store `.value`, not `str()` of enum objects.
4. Role checks MUST compare against `.value` strings.
5. Backend tests MUST verify token claims contain plain strings, not
   "Class.member" format.
6. **NEW (FB29-sourced)**: Foundation audit MUST search `conftest.py` and all test
   fixtures for `str(role)` or `str(enum)` patterns. The enum bug affects tests
   too — `conftest.py` auth header fixtures are a common hiding place.

**Source**: FB29 Python 3.14 caused `str(UserRole.writer)` to return
`"UserRole.writer"` instead of `"writer"`. This broke JWT token generation,
RBAC comparisons in auth decorators, ownership checks in articles/publish_schedules,
and GraphQL resolver guards. Fixed across 4 files: `auth.py`, `articles.py`,
`publish_schedules.py`, `graphql.py`.


## Rule: JWT Library Exception Class Confusion

**Status**: Active (FB29-sourced)
**Severity**: MEDIUM (causes uncaught exceptions, 500 errors)
**Applies to**: vsm_backend_coder, vsm_backend_tester

Different JWT libraries use different exception class names. Using the wrong
exception class causes `except` clauses to miss errors, leading to 500s instead
of 401s.

| Library | Install | Exception Class |
|---|---|---|
| `python-jose` | `pip install python-jose[cryptography]` | `from jose import JWTError` |
| `PyJWT` | `pip install PyJWT` | `jwt.ExpiredSignatureError`, `jwt.InvalidTokenError` |

**Correct pattern**:
```python
# python-jose
from jose import JWTError

try:
    payload = jwt.decode(token, secret, algorithms=[alg])
except JWTError:
    raise HTTPException(401, "Invalid token")
```

**Incorrect pattern** (MEDIUM):
```python
# python-jose installed, but using PyJWT exception names
import jwt  # this IS python-jose, not PyJWT

try:
    payload = jwt.decode(token, secret, algorithms=[alg])
except jwt.PyJWTError:  # WRONG — python-jose raises JWTError, not PyJWTError
    ...  # This except NEVER catches anything
```

**Prevention rules**:
1. Check `requirements.txt` or `pyproject.toml` to confirm WHICH JWT library is
   installed before writing exception handling.
2. `python-jose` → `from jose import JWTError`.
3. `PyJWT` → `import jwt` and catch `jwt.ExpiredSignatureError` / `jwt.InvalidTokenError`.
4. Backend tests MUST verify invalid tokens return 401, not 500.

**Source**: FB29 `auth.py` used `jwt.PyJWTError` but `python-jose` was installed,
which raises `JWTError`. Invalid token test failed with 500 instead of 401.


## Rule: Pydantic `Field()` Alias Attributes in Python 3.14+

**Status**: Active (FB29-sourced)
**Severity**: LOW (warnings only, but wastes context and confuses developers)
**Applies to**: vsm_backend_coder, vsm_backend_tester

In Pydantic v2 with Python 3.14, passing `alias=`, `validation_alias=`, or
`serialization_alias=` to `Field()` in certain contexts produces
`UnsupportedFieldAttributeWarning`. This floods test output with warnings
that consume context budget and obscure real issues.

**Correct pattern**:
```python
from pydantic import BaseModel, Field
from typing import Annotated

# Use Annotated for field-level metadata (Pydantic v2 style)
class ArticleResponse(BaseModel):
    title: str
    comments: Annotated[list[str], Field(alias="commentList")]
    # Or use model_config alias_generator for camelCase conversion
```

**Incorrect pattern** (LOW):
```python
class ArticleResponse(BaseModel):
    title: str
    # Field(alias=...) attached to a single union member or type statement — no effect
    comments: list[str] = Field(alias="commentList")
    # Warning: "The 'alias' attribute with value 'commentList' was provided to
    # the Field() function, which has no effect in the context it was used."
```

**Prevention rules**:
1. Prefer `alias_generator` on the model config over per-field `Field(alias=...)`.
2. If per-field aliases are needed, use `typing.Annotated[..., Field(alias=...)]`.
3. Treat warnings in test output as signals — investigate root cause, don't ignore.
4. If warnings are expected and harmless, document WHY in a comment near the model.

**Source**: FB29 test output showed 438 warnings, many being
`UnsupportedFieldAttributeWarning: The 'alias' attribute... has no effect`.
These warnings originated from Pydantic v2 model definitions and consumed
context budget during test execution.


## Rule: `@field_validator(mode="before")` for Comma-Separated Env Strings

**Status**: Active (FB29-sourced)
**Severity**: LOW (productivity pattern)
**Applies to**: vsm_backend_coder

Environment variables are always strings. When a setting needs a list (e.g.,
`CORS_ORIGINS`, `CORS_ALLOW_METHODS`, `CORS_ALLOW_HEADERS`), Pydantic v2 will
not auto-split comma-separated strings. A `mode="before"` validator converts
the env string to a list before type validation.

**Correct pattern**:
```python
from pydantic import BaseSettings, Field, field_validator

class Settings(BaseSettings):
    cors_origins: list[str] = ["http://localhost:5173"]
    cors_allow_methods: list[str] = ["GET", "POST", "PUT", "DELETE"]

    @field_validator("cors_origins", "cors_allow_methods", mode="before")
    @classmethod
    def _split_comma_separated(cls, v):
        if isinstance(v, str):
            return [item.strip() for item in v.split(",") if item.strip()]
        return v
```

**Incorrect pattern** (LOW):
```python
class Settings(BaseSettings):
    cors_origins: list[str] = ["http://localhost:5173"]
    # Env var CORS_ORIGINS="http://a.com,http://b.com" is passed as a single
    # string. Pydantic tries to validate str as list[str] and fails with:
    # Input should be a valid list
```

**Prevention rules**:
1. Any setting typed as `list[str]` that reads from env MUST have a
   `mode="before"` validator handling the string case.
2. The validator MUST handle empty strings gracefully (return `[]` or skip).
3. Strip whitespace from each item after splitting.

**Source**: FB29 `config.py` initially failed to load `CORS_ORIGINS` from env
because the comma-separated string was not split. Added `_split_comma_separated`
validator to handle the env string → list conversion.

---

## Rule: Pydantic Settings Attribute Names Are UPPERCASE

**Applies to**: All Pydantic Settings usage
**Severity**: BLOCKER
**Source**: FB30

**Problem**: Accessing settings with lowercase attribute names fails silently at runtime because Pydantic Settings fields are declared in UPPERCASE but code may use lowercase.

**Example failure**:
```python
# config.py
class Settings(BaseSettings):
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

# auth.py — WRONG
token = jwt.encode(payload, settings.jwt_secret, algorithm="HS256")
# AttributeError: 'Settings' object has no attribute 'jwt_secret'

# auth.py — CORRECT
token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")
```

**Prevention rules**:
1. Backend coder MUST grep for `settings\.[a-z_]+` (lowercase after dot) and verify against the Settings class definition.
2. Auditor MUST flag any lowercase settings access as BLOCKER.


---

## Rule: Pydantic `model_dump()` Returns UUID Objects by Default

**Status**: Active (E24-F1-validated)
**Applies to**: vsm_backend_coder, vsm_backend_fix, vsm_backend_tester
**Severity**: ISSUE

**Problem**: Pydantic V2's `BaseModel.model_dump()` returns `UUID` objects as-is
for `UUID`-typed fields. If downstream code or tests expect string
representations (e.g., `assert result == {"id": "550e8400-...", ...}`), the
assertion will fail with a mismatch between `UUID(...)` and `"550e8400-..."`.

This is distinct from JSON serialization (`model_dump_json()`), which does
serialize UUIDs as strings automatically. The trap only triggers when code
consumes the Python dict output of `model_dump()`.

**Example failure**:
```python
from uuid import UUID
from pydantic import BaseModel

class User(BaseModel):
    id: UUID
    name: str

u = User(id="550e8400-e29b-41d4-a716-446655440000", name="Alice")
result = u.model_dump()
# result == {"id": UUID("550e8400-e29b-41d4-a716-446655440000"), "name": "Alice"}
# NOT {"id": "550e8400-e29b-41d4-a716-446655440000", "name": "Alice"}
```

**Correct pattern**:
```python
from uuid import UUID
from pydantic import BaseModel, field_serializer

class User(BaseModel):
    id: UUID
    name: str

    @field_serializer("id")
    def serialize_id(self, value: UUID) -> str:
        return str(value)
```

**Prevention rules**:
1. If a `UUID`-typed field's `model_dump()` output is consumed by Python code
   (not just sent over the wire as JSON), verify whether string serialization
   is required.
2. Use `@field_serializer("field_name")` for targeted UUID→string conversion
   in `model_dump()` output.
3. Do NOT rely on `model_dump_json()` behavior when writing assertions against
   `model_dump()` results.

**Source**: E24-F1 gym experiment. Agent wrote naive `User` model without
`@field_serializer`, tests failed because `model_dump()` returned `UUID`
objects. Agent diagnosed and fixed in 1 iteration. This rule prevents the
initial failure.

---

## Rule: `asyncio.gather` Without `return_exceptions=True` Loses Results on Partial Failure

**Status**: Active (E24-F2-validated)
**Applies to**: vsm_backend_coder, vsm_backend_fix, vsm_auditor
**Severity**: ISSUE

**Problem**: `asyncio.gather(*coros)` raises immediately when the first
coroutine raises an exception. This loses:
- Successful results from coroutines that completed before the failure
- The ability to distinguish which coroutine failed and why
- The ability to return partial results

This is especially dangerous in concurrent fetch/operation patterns where
downstream code expects a complete result mapping.

**Example failure**:
```python
import asyncio

async def fetch_all(urls):
    # Naive — raises on first failure, losing other results
    results = await asyncio.gather(*(fetch(url) for url in urls))
    return dict(zip(urls, results))
```

When one `fetch()` raises `json.JSONDecodeError`, the entire `gather()`
raises. Callers cannot tell which URL failed or access successful results.

**Correct pattern**:
```python
import asyncio

async def fetch_all(urls):
    results = await asyncio.gather(
        *(fetch(url) for url in urls),
        return_exceptions=True
    )
    return dict(zip(urls, results))
```

With `return_exceptions=True`, exceptions are returned in the results list
just like successful values. Callers can inspect `isinstance(result, Exception)`
to distinguish failures from successes.

**Prevention rules**:
1. When using `asyncio.gather` for concurrent operations where partial failure
   is possible (e.g., fetching multiple URLs, processing multiple items),
   ALWAYS use `return_exceptions=True`.
2. Document the behavior: callers MUST handle both success values and
   exception objects in the returned collection.
3. Do NOT wrap `gather()` in a broad `try/except` as a substitute for
   `return_exceptions=True` — this still loses successful results.

**Source**: E24-F2 gym experiment. Agent wrote naive `gather()`, tests failed
because exceptions propagated instead of being returned. Agent diagnosed and
fixed in 1 iteration. This rule prevents the initial failure.
