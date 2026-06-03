# Testing Patterns

Universal testing strategy and philosophy. Language-agnostic.

## Test Pyramid
- Unit tests: fast, isolated, many
- Integration tests: API boundaries, fewer
- E2E tests: critical user flows, fewest

## Fixtures and Setup
- Database reset per test (transaction rollback or cleanup)
- Auth fixtures for each role
- Test data factories, not hardcoded data

## Mocking
- Mock external services, not internal logic
- Mock time for time-dependent tests
- Mock randomness for deterministic tests

## Coverage
- Every endpoint: at least one test
- Every auth guard: valid AND invalid token tests
- Every role guard: wrong-role user tests
- Trivial tests do not count toward coverage


## Rule: FastAPI + SQLAlchemy + PostgreSQL Test Infrastructure

**Status**: Active (FB29-sourced)
**Severity**: — (productivity pattern, not a bug preventer)
**Applies to**: vsm_backend_tester

When the production stack uses PostgreSQL + `UUID` columns but tests should run
fast without a real database, use this SQLite-based test infrastructure pattern.
It provides nested transaction rollback (clean state per test) and a UUID
monkeypatch so SQLAlchemy PostgreSQL models work with SQLite.

**`conftest.py` pattern**:
```python
import os
from uuid import UUID
from collections.abc import AsyncGenerator

import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

# Set env vars BEFORE app imports
os.environ["JWT_SECRET"] = "test-secret-key-that-is-32-chars-long-abc"
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///./test.db"

from app.main import app
from app.dependencies import get_db
from app.models import Base

# Monkeypatch PostgreSQL UUID for SQLite compatibility
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
PG_UUID.bind_processor = lambda self, dialect: None  # type: ignore


@pytest_asyncio.fixture(scope="session")
async def engine():
    engine = create_async_engine("sqlite+aiosqlite:///./test.db", future=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture
async def db(engine) -> AsyncGenerator[AsyncSession, None]:
    # Nested transaction: each test rolls back
    async with engine.connect() as conn:
        trans = await conn.begin_nested()
        session = sessionmaker(bind=conn, class_=AsyncSession, expire_on_commit=False)()

        async def override_get_db():
            yield session

        app.dependency_overrides[get_db] = override_get_db
        yield session
        await trans.rollback()
        await session.close()


@pytest_asyncio.fixture
async def client(db) -> AsyncGenerator[AsyncClient, None]:
    from httpx import AsyncClient
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
```

**Why this works**:
1. **SQLite file DB** — persistent across session, fast, no Docker needed.
2. **Nested transaction rollback** — each test gets clean state without recreating tables.
3. **Dependency override** — FastAPI injects the test session into all endpoints.
4. **UUID monkeypatch** — PostgreSQL `UUID` columns fail on SQLite without this.
5. **Session-scoped engine** — tables created once; function-scoped session rolls back.

**Prevention rules**:
1. Backend tester MUST use dependency override, not global session swapping.
2. UUID monkeypatch MUST be applied BEFORE `Base.metadata.create_all()`.
3. `JWT_SECRET` MUST be set before any app import that reads config.
4. Tests MUST NOT depend on a running PostgreSQL instance.

**Source**: FB29 achieved 36 backend tests in ~9 seconds using this exact pattern.
Tests covered auth, articles, users, media, reviews, and GraphQL without any
PostgreSQL container running.
