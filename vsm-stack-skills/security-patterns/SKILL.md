# Security Patterns

High-level security principle index. Language-agnostic. This skill is a **directory**
— it points to detailed empirical rules in language-specific and framework-specific
pitfall skills.

## Auth
- JWT signatures must be verified (never `verify_signature=False`)
  → See `python-pitfalls/SKILL.md` (JWT auth verification rules)
- Auth middleware raises on failure (never fail-open)
  → See `python-pitfalls/SKILL.md` (fail-closed GraphQL context)
- Registration defaults to lowest-privilege role
  → See `python-pitfalls/SKILL.md` (registration role allowlist)
- Refresh tokens query DB before issuing new tokens

## CORS
- Never `origin: *` or `origin: true` with credentials
  → See `python-pitfalls/SKILL.md` (CORS wildcard ban)
- Explicit allowlist of origins, methods, headers

## Input
- All inputs validated before processing
- SQL injection prevention (parameterized queries)
- XSS prevention (output encoding)

## Secrets
- No hardcoded secrets in source
- No default-value fallbacks for secrets in compose/config
  → See `docker-pitfalls/SKILL.md` (Docker-Compose `:-` fallback ban)
- Secrets in env vars, not committed

## Rate Limiting
- Shared store (Redis) for distributed deployments
- Exception handler returns proper status (429, not 500)
  → See `python-pitfalls/SKILL.md` (rate limiting handler)

## Data Exposure
- Response DTOs must not expose internal/sensitive fields
- Public endpoints must not leak answer/solution data
- Ownership filtering on ALL list queries
  → See `python-pitfalls/SKILL.md` (GraphQL ownership filtering)

## GraphQL-Specific
- Depth limiting + complexity analysis
  → See `python-pitfalls/SKILL.md` (GraphQL depth limiting)
- Context builders must be fail-closed
  → See `python-pitfalls/SKILL.md` (GraphQL fail-closed context)
- RBAC parity between REST and GraphQL

## WebSocket-Specific
- Auth must be in-band, never in URL
  → See `anti-patterns.md` #5 / `security-lessons.md` L16

## Async Worker Defense-in-Depth (FB25)
Celery tasks (and other async workers) that operate on user-owned resources
MUST re-verify ownership boundaries inside the worker. Do not trust enqueue-time
validation alone. A malicious actor could craft a task payload targeting another
user's resources.

Pattern:
```python
@shared_task
def process_user_resource(resource_id: str, user_id: str):
    resource = await db.get(Resource, resource_id)
    if str(resource.owner_id) != user_id:
        logger.error("Ownership mismatch")
        return {"status": "failed", "errors": ["Access denied"]}
    # ... process resource
```

**Source**: FB25 `process_csv_import` task did not verify the target budget
belonged to the user_id passed in the task arguments.

## Rule: Password Minimum Length

**Status**: Active (FB26-sourced)
**Severity**: ISSUE (elevate to BLOCKER if spec requires ≥ 8)
**Applies to**: vsm_backend_coder, vsm_security

Pydantic `Field(min_length=...)` on password fields MUST be ≥ 8. Values < 8 are an ISSUE. If the build specification explicitly requires 8, scores < 8 are a BLOCKER.

## Rule: Dockerfile Non-Root USER

**Status**: Active (FB26-sourced)
**Severity**: HIGH
**Applies to**: vsm_devops_coder, vsm_security

Every production Dockerfile that runs an application server MUST include a non-root `USER` directive before `CMD`. Example:
```dockerfile
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Rule: Celery Task Ownership Re-Verification

**Status**: Active (FB26-sourced)
**Severity**: MEDIUM
**Applies to**: vsm_backend_coder, vsm_security

Celery tasks that operate on user-scoped resources MUST accept `user_id` and re-verify ownership before processing. Tasks must not rely solely on the enqueue-time auth context.

## Rule: CORS Wildcard Severity Elevation

**Status**: Active (FB26-sourced)
**Severity**: MEDIUM (was LOW; elevated 2026-06-03)
**Applies to**: vsm_security, vsm_backend_coder

`allow_methods=["*"]` and `allow_headers=["*"]` in FastAPI CORS middleware are **MEDIUM** severity, not LOW. While they are not immediately exploitable, they violate defense-in-depth and allow unexpected methods/headers. This is a consistent deferred issue across builds.

**Correct pattern**:
```python
CORSMiddleware(
    allow_origins=["http://localhost:5173"],  # Explicit, never "*"
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    allow_headers=["Authorization", "Content-Type"],
)
```

**Deferral policy**: May be deferred ONLY if the build spec explicitly requires permissive CORS for development. Otherwise, must be fixed.

## Rule: JWT Secret Strict Validation

**Status**: Active (FB27-sourced)
**Severity**: HIGH
**Applies to**: vsm_backend_coder, vsm_security

`JWT_SECRET` MUST NOT have a default value, placeholder, or fallback. If the
environment variable is missing at runtime, the application MUST fail at startup
with a clear validation error, NOT silently use a weak/known secret.

**Correct pattern**:
```python
from pydantic import Field, field_validator

class Settings(BaseSettings):
    JWT_SECRET: str = Field(..., min_length=16)

    @field_validator("JWT_SECRET")
    @classmethod
    def reject_placeholder(cls, v: str) -> str:
        if not v or v.strip() in ("", "your-secret-key", "change-me",
                                   "placeholder", "secret", "jwt-secret"):
            raise ValueError("JWT_SECRET must be a strong secret, not a placeholder")
        return v
```

**Incorrect pattern** (HIGH):
```python
JWT_SECRET: str = "your-secret-key"  # Silent security gap — works without env
JWT_SECRET: str = Field(default="change-me", min_length=16)  # Still a fallback
```

**Source**: FB27 `config.py` had `JWT_SECRET: str = "your-secret-key"` as default.
Security audit (Phase 5) missed it entirely. Only the meta-evaluator flagged it
as a process gap during Phase 8b. The fix agent added `Field(..., min_length=16)`
with a validator that rejects empty strings and common placeholders.

## Rule: File Extension Whitelist for Uploads

**Status**: Active (FB27-sourced)
**Severity**: MEDIUM
**Applies to**: vsm_backend_coder, vsm_security

File upload endpoints MUST validate file extensions against an explicit allowlist.
Accepting arbitrary extensions (e.g., `.exe`, `.sh`, `.php`) enables upload-based
remote code execution.

**Correct pattern**:
```python
ALLOWED_EXTENSIONS = {".pdf", ".png", ".jpg", ".jpeg", ".csv", ".xlsx"}

ext = Path(filename).suffix.lower()
if ext not in ALLOWED_EXTENSIONS:
    raise HTTPException(status_code=400, detail=f"File type {ext} not allowed")
```

**Source**: FB27 document upload endpoint accepted any extension. Security audit
caught it as MEDIUM. Fix agent added extension whitelist validation.


## Rule: S3/MinIO Credentials Must Not Have Defaults in Settings

**Status**: Active (FB28-sourced)
**Severity**: MEDIUM
**Applies to**: vsm_backend_coder, vsm_security, vsm_devops_coder

S3 access keys and secret keys must use `Field(..., min_length=1)` with NO
default values. Default credentials like `"minioadmin"` silently weaken
production security if env vars are omitted.

**Correct pattern**:
```python
S3_ACCESS_KEY: str = Field(..., min_length=1)
S3_SECRET_KEY: str = Field(..., min_length=1)
S3_BUCKET_NAME: str = Field(..., min_length=1)
S3_ENDPOINT: str = Field(..., min_length=1)
```

**Incorrect pattern** (MEDIUM):
```python
S3_ACCESS_KEY: str = Field(default="minioadmin")
S3_SECRET_KEY: str = Field(default="minioadmin")
```

**Prevention rules**:
1. Security audit MUST flag any `default=` on S3/MinIO/DB credentials as MEDIUM.
2. Treat S3 secrets with the same strictness as `JWT_SECRET`.

**Source**: FB28 `config.py` had `S3_ACCESS_KEY: str = Field(default="minioadmin")`.
Security audit caught it as MEDIUM.

## Rule: Security Dependencies Must Be Wired, Not Just Installed

**Status**: Active (FB28-sourced)
**Severity**: MEDIUM
**Applies to**: vsm_backend_coder, vsm_security, vsm_wiring

Installing a security dependency (e.g., `slowapi`) in `pyproject.toml` is
insufficient. It MUST be wired as middleware or applied via decorators.

**Correct pattern**:
```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@router.post("/login")
@limiter.limit("10/minute")
async def login(request: Request, data: UserLogin):
    ...
```

**Incorrect pattern** (MEDIUM):
```python
# slowapi in pyproject.toml but NEVER wired into app or routers
# Auth endpoints remain unprotected against brute-force
```

**Prevention rules**:
1. Security audit MUST verify that every security dependency in `pyproject.toml`
   has corresponding middleware, decorator, or router wiring in source code.
2. Import presence is NOT sufficient.

**Source**: FB28 `slowapi` was in `pyproject.toml` but never added to `main.py`
or auth endpoints. Security audit caught it as MEDIUM.


## Rule: GraphQL Mutations MUST Mirror REST Endpoint Validation and Ownership

**Status**: Active (FB29-sourced)
**Severity**: HIGH
**Applies to**: vsm_backend_coder, vsm_security, vsm_auditor, vsm_wiring

GraphQL mutations frequently lag equivalent REST endpoints in validation depth
and ownership checks. This creates security parity gaps where GraphQL is the
weaker entry point.

**Correct pattern**:
```python
# REST endpoint enforces ownership
@router.put("/articles/{id}")
async def update_article(id: UUID, data: ArticleUpdate, user: User = Depends(get_current_user)):
    article = await db.get(Article, id)
    if str(article.author_id) != str(user.id) and user.role.value != "admin":
        raise HTTPException(403, "Not owner")
    # ... update

# GraphQL mutation enforces THE SAME ownership
@strawberry.mutation
async def update_article(id: UUID, data: ArticleUpdateInput, info: Info) -> Article:
    user = info.context["user"]
    article = await db.get(Article, id)
    if str(article.author_id) != str(user.id) and user.role.value != "admin":
        raise PermissionError("Not owner")
    # ... update
```

**Incorrect pattern** (HIGH):
```python
# GraphQL mutation lacks ownership check — editors can modify ANY article
@strawberry.mutation
async def update_article(id: UUID, data: ArticleUpdateInput, info: Info) -> Article:
    user = info.context["user"]
    # MISSING: author_id comparison
    if user.role.value not in ("writer", "editor", "admin"):
        raise PermissionError("Not allowed")
    # ... updates ANY article
```

**Prevention rules**:
1. For every REST endpoint with validation/ownership, the corresponding GraphQL
   mutation MUST have equivalent checks.
2. Security audit MUST cross-reference REST and GraphQL for every mutation.
3. Implementation audit MUST verify GraphQL mutation parity with REST.
4. Password policy, upload limits, and ownership guards MUST apply equally.

**Source**: FB29 GraphQL `register` accepted passwords < 8 chars (REST enforced
min_length=8). GraphQL `update_article` allowed editors to modify ANY article
(REST enforced `_check_owner()`). Security audit caught both as HIGH.


## Rule: Registration MUST Exclude Admin/Superuser Roles

**Status**: Active (FB29-sourced)
**Severity**: BLOCKER
**Applies to**: vsm_backend_coder, vsm_security, vsm_auditor

The registration endpoint must reject any attempt to create a user with
`admin`, `superuser`, `root`, or equivalent elevated roles. These roles must
be created only through a separate, authenticated admin-only endpoint or
database seeding.

**Correct pattern**:
```python
# schemas.py
ALLOWED_ROLES = {"writer", "editor", "publisher"}  # admin EXCLUDED

class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    name: str
    role: str = "writer"

    @field_validator("role")
    @classmethod
    def _validate_role(cls, v):
        if v not in ALLOWED_ROLES:
            raise ValueError(f"Role must be one of: {ALLOWED_ROLES}")
        return v
```

```python
# auth.py / router
@router.post("/register", response_model=UserResponse)
async def register(data: UserRegister, db: AsyncSession = Depends(get_db)):
    if data.role not in ALLOWED_ROLES:
        raise HTTPException(400, "Invalid role for registration")
    # ... create user
```

**Incorrect pattern** (BLOCKER):
```python
# No role validation — any role string accepted
@router.post("/register")
async def register(data: UserRegister, db: AsyncSession = Depends(get_db)):
    user = User(email=data.email, role=data.role)  # Could be "admin"!
    db.add(user)
    await db.commit()
```

**Prevention rules**:
1. `ALLOWED_ROLES` MUST explicitly exclude `admin`, `superuser`, `root`.
2. Registration schema MUST validate role against `ALLOWED_ROLES`.
3. Security audit MUST flag any registration endpoint that accepts unrestricted
   role strings as BLOCKER.
4. Admin user creation MUST be a separate, authenticated endpoint with its own
   RBAC guard.

**Source**: FB29 correctly excluded `admin` from `ALLOWED_ROLES` and validated
registration role against the allowlist. This prevented privilege escalation at
the registration boundary. Multiple prior builds had this gap.
