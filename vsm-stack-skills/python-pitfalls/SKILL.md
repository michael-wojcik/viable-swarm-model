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
Creating a Celery app at module level via a factory still triggers `get_settings()`
on first import:
```python
# WRONG — crashes on import without env vars
celery_app = _get_celery_app()
```
Use a proper lazy import pattern or defer instantiation to a function that is
called only when the worker starts. The wiring agent MUST grep ALL `*.py` files
(not just `main.py`) for module-level `get_settings()` / `Settings()` calls.
