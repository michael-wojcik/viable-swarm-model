---
name: sqla-patterns
description: SQLAlchemy-specific patterns and anti-patterns for async engine management, session lifecycle, and model design.
type: reference
---

# SQLAlchemy Patterns

## Rule: NEVER Instantiate `create_async_engine()` at Module Level

**Status**: Active (FB29-sourced)
**Severity**: BLOCKER (causes import side-effects, test failures, circular imports)
**Applies to**: vsm_backend_coder, vsm_backend_tester, vsm_auditor

Creating an `AsyncEngine` at module level causes the engine to instantiate on
import. This breaks tests (DB URL not configured), causes circular import risks,
and makes the module unusable without a running database.

**Correct pattern**:
```python
# models.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine
import sqlalchemy as sa

_engine: sa.ext.asyncio.AsyncEngine | None = None

def _get_async_engine() -> sa.ext.asyncio.AsyncEngine:
    global _engine
    if _engine is None:
        database_url = sa.engine.url.make_url(
            os.environ.get("DATABASE_URL", "postgresql+asyncpg://localhost/db")
        )
        _engine = create_async_engine(str(database_url), echo=False, future=True)
    return _engine
```

```python
# dependencies.py (NOT models.py)
from sqlalchemy.ext.asyncio import async_sessionmaker
from app.models import _get_async_engine, AsyncSession

AsyncSessionLocal = async_sessionmaker(
    bind=_get_async_engine(),
    class_=AsyncSession,
    expire_on_commit=False,
)

async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session
```

**Incorrect pattern** (BLOCKER):
```python
# models.py — engine instantiated at import time
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

engine = create_async_engine(os.environ["DATABASE_URL"])  # FAILS on import if env missing
AsyncSessionLocal = async_sessionmaker(bind=engine, class_=AsyncSession)
```

**Prevention rules**:
1. `create_async_engine()` MUST be inside a lazy factory function, NEVER at module level.
2. `AsyncSessionLocal` MUST live in `dependencies.py`, NOT `models.py`.
3. Foundation audit MUST flag any `create_async_engine()` call outside a function as BLOCKER.
4. Import check (`python3 -c "import main; print('OK')"`) MUST pass without a running DB.
5. Tests MUST be able to import models without DATABASE_URL being set.

**Source**: FB29 `models.py` had `create_async_engine()` at module level. Caused
import failures in tests and required S5 validation fix. Recurring pattern across
multiple builds.
