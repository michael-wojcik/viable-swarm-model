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
