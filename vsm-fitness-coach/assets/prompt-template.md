# Fitness Build Execution Prompt Template

> **Usage**: The coach skill uses this template to generate the execution prompt
> for the next fitness build (FB[N+1]). It is filled in AFTER the current build
> completes, using the fitness report, hypothesis updates, and mutation log.
>
> **When to generate**: After Phase 5 (Apply Mutations) completes and the fitness
> report is written. Ask the user via `AskUserQuestion` before generating.
>
> **Output**: `~/vsm-fitness-builds/coach/FB[N+1]-prompt-draft.md`

---

```markdown
# FB[N+1] Execution Prompt — [Project Name]

**Invocation**: Use this prompt to run the `viable-swarm-model` workflow for Fitness Build #[N+1].

**Purpose**: Target the systemic gaps exposed by FB[N] (score [X]/5.0). This build deliberately creates conditions where the FB[N] failure modes would recur, then validates whether the new prevention rules ([list rule IDs]) catch them.

---

Build **[Project Name]** — [One-line description].

**Build Directory**: `~/vsm-fitness-builds/coach/FB[N+1]-[YYYY-MM-DD]/`
**Complexity**: [Low/Medium/High] ([N] waves, [N]+ lines, [N] services)
**Expected Tier**: [Tier 1/2/3] — triggers Variety Assessment in Phase 0

## Architecture

### Services
1. **API** (FastAPI + PostgreSQL 15 + Redis)
2. **Worker** (Celery + Redis — [background jobs])
3. **Real-time** (Socket.io v4 + Redis adapter — [real-time features])
4. **Frontend** (React 18 + Vite + TypeScript + [charting library if needed])
5. **[Optional]** Object storage (MinIO for file uploads)

### Backend Modules
- `app/config.py` — Pydantic Settings with **lazy factory** (`get_settings()`), NO module-level singleton
- `app/auth.py` — JWT with bcrypt, role-based claims (`[role1] | [role2] | [role3]`)
- `app/roles.py` — Single canonical `require_role()` that **raises HTTPException(403)** on failure
- `app/models.py` — SQLAlchemy 2.0 with **aliased imports** (`sa_select`, `sa_text`, etc.)
- `app/routers/[module].py` — [CRUD features with specific ownership/scoping rules]
- `app/graphql.py` — Strawberry GraphQL with **DepthLimitExtension(max_depth=10)**, **QueryComplexityExtension**, **eager-loaded relationships** (no N+1), **ownership filtering on ALL list queries**
- `app/sio.py` — Socket.io server with in-band auth, [room strategy]. **MUST verify auth before allowing room join**
- `app/main.py` — FastAPI entry point with **SlowAPIMiddleware**
- `app/tasks.py` — Celery tasks: `[task1]()`, `[task2]()`, `[task3]()`

### Frontend Modules
- `src/App.tsx` — Role-aware routing
- `src/pages/[Page].tsx` — [Feature pages]
- `src/graphql/queries.ts` — All queries use exact camelCase field names matching backend schema
- `src/graphql/client.ts` — Apollo split link (HTTP + ws subscriptions)
- `src/stores/[store].ts` — Zustand store
- `src/sio/client.ts` — Socket.io with in-band auth, uses shared constants

### Shared
- `shared/types.ts` — `[Enum1]`, `[Enum2]`, `[Enum3]` enums
- `shared/sio-events.ts` — `[EVENT_1]`, `[EVENT_2]`, `[EVENT_3]` constants

## Data Model (CRITICAL — Foundation Agent MUST Match Exactly)

The `data-model.md` in the build directory MUST specify these EXACT fields. Phase 2c Model Validation will verify `models.py` matches this exactly.

### [Entity 1]
- `id`: UUID PK
- `field_name`: [type] [constraints]
- `created_at`: datetime
- `updated_at`: datetime

### [Entity 2]
- `id`: UUID PK
- `fk_field`: UUID FK → [Entity 1] (NOT `alt_name`, NOT `other_name`)
- `field_name`: [type] [constraints]
- `created_at`: datetime

## Critical Requirements (Hypothesis / Prevention Rule Validation Targets)

### [H## / Rule ID] — [Short name]
[Specific requirement that tests a hypothesis or prevention rule. Include:
- What the agent MUST do
- What the auditor/security/coordinator MUST verify
- Severity if missed]

[Repeat for each hypothesis being tested by this build]

## Deliberate Traps

- **[Trap 1]**: [Specific condition designed to catch if a prevention rule fails]
- **[Trap 2]**: [Another trap]
- **CRITICAL TRAP**: [Severity calibration test — if the security gate rates [finding] as MEDIUM instead of HIGH/BLOCKER, the prevention rule failed]

## Technology Stack
- Backend: FastAPI, SQLAlchemy 2.0, asyncpg, Redis, Celery, Strawberry GraphQL, python-socketio, python-multipart, slowapi, bcrypt, PyJWT
- Frontend: React 18, Vite, TypeScript, Apollo Client, Socket.io-client, Zustand, [charting library]
- Infra: Docker Compose, pytest, pytest-asyncio, Vitest

## Exit Criteria
- All plan.md modules implemented
- Backend imports succeed (with env vars set)
- Frontend `npm run build` succeeds
- Backend tests pass (or test code is correct)
- **Frontend tests exist and run**
- **Tests cover `main.py` and `tasks.py`**
- No BLOCKERs in re-audit
- < 3 open ISSUES
- Zero GraphQL field name mismatches
- Zero orphaned exports in backend
- Zero WebSocket event name mismatches
- GraphQL RBAC matches REST exactly
- GraphQL list queries have ownership filtering
- `models.py` field names match `data-model.md` exactly (Phase 2c validation)
- WebSocket room handlers verify auth before room join
- Foundation phase has 0 BLOCKERs (H41 validation)
- Phase 8b produces standalone `meta-report.md` artifact
```

---

## Filling Instructions

When generating FB[N+1] from FB[N]'s results:

1. **Project Name**: Choose a new domain not yet covered by previous builds.
2. **Purpose**: Reference FB[N]'s score, specific gaps, and the prevention rules being tested.
3. **Architecture**: Adapt services/modules to the new domain while preserving the structural patterns that trigger known failure modes.
4. **Data Model**: Define fields with EXACT names that Phase 2c will validate. Include deliberate naming traps (e.g., `scheduled_at` NOT `appointment_date`).
5. **Critical Requirements**: Map each requirement to a specific hypothesis or prevention rule from FB[N]'s mutation log.
6. **Deliberate Traps**: Design traps that would succeed ONLY if the new prevention rules fail.
7. **Exit Criteria**: Include build-specific criteria derived from the hypotheses being tested.
