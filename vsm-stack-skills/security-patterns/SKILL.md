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
