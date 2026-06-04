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

---

## Rule: Test Database Must Be Compatible with Production Schema

**Applies to**: Backend tests using SQLite as test DB for PostgreSQL apps
**Severity**: BLOCKER
**Source**: FB30

**Problem**: PostgreSQL-specific features (`gen_random_uuid()`, `sa.UUID`, `Decimal` with CHECK constraints) fail on SQLite.

**Prevention rules**:
1. If using SQLite for tests, models MUST use `default=uuid.uuid4` instead of `server_default=sa.text("gen_random_uuid()")`.
2. Add UUID bind processor in conftest for SQLite compatibility.
3. Verify `Base.metadata.create_all()` succeeds in test setup before running any tests.

---

## Rule: GraphQL Tests Must Use camelCase Field Names

**Applies to**: GraphQL test suites with Strawberry schema
**Severity**: BLOCKER
**Source**: FB30

**Problem**: Strawberry auto-camelCases schema fields. Test queries using snake_case fail with "Cannot query field" errors.

**Example failure**:
```graphql
# WRONG — test query
mutation { create_budget(name: "X", start_date: "2024-01-01") { id } }

# CORRECT — test query
mutation { createBudget(name: "X", startDate: "2024-01-01") { id } }
```

**Prevention rules**:
1. Backend tester MUST verify all GraphQL test queries use camelCase field names.
2. Run `strawberry export-schema` and grep for snake_case in test files.


---

## Rule: Frontend `npm run build` as Phase 4 Hard Gate (H154)

**Status**: Active (FB23-sourced, confirmed by gym experiment 2026-06-04)
**Severity**: BLOCKER for frontend builds
**Applies to**: vsm_frontend_tester, vsm_coordinator

**Problem**: Vitest (`npm test -- --run`) uses esbuild which transpiles TypeScript
without full type checking. It can PASS even when `tsc -b` would FAIL on:
- Unused imports (`noUnusedLocals`)
- Unused parameters (`noUnusedParameters`)
- Type mismatches in unreachable code
- Vite config type errors

**Gym experiment H154** (2026-06-04) confirmed: a React component with an unused
`useState` import passed Vitest but failed `npm run build` with:
```
src/main.tsx(1,1): error TS6133: 'useState' is declared but its value is never read.
```

**Correct pattern** (Phase 4 exit criteria):
```markdown
## Frontend Phase 4 Gate Checklist

- [ ] `npm test -- --run` passes (all tests green)
- [ ] `npm run build` passes with exit code 0 (type-check + build)
- [ ] No TypeScript errors in `tsc -b` output
```

**Incorrect pattern** (gate bypass):
```markdown
## Frontend Phase 4 Gate Checklist (INCOMPLETE)

- [ ] `npm test -- --run` passes
# MISSING: npm run build check — tsc errors leak to Phase 6
```

**Prevention rules**:
1. **Frontend tester MUST** run `npm run build` (not just `npm test`) before
deleting `node_modules` or declaring Phase 4 complete.
2. **Coordinator MUST** verify `npm run build` exit code is 0 during integration.
3. **Any build failure in Phase 6** that `tsc -b` would have caught in Phase 4
is a **process violation** — the Phase 4 gate was bypassed.
4. **Build scripts SHOULD** set `"build": "tsc -b && vite build"` in
`package.json` so `npm run build` always runs the type checker.

**Source**: FB23 frontend build failed in Phase 6 because `tsc -b` errors were
not caught in Phase 4. Gym experiment H154 reproduced the exact failure mode.
