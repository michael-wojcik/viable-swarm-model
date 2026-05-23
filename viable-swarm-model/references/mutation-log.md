# Mutation Log

> This file is append-only. Every modification the skill makes to its own
> files is recorded here with full rationale. If the skill becomes corrupted,
> this log is the audit trail for `git revert`.
>
> **Mutation rules**: Append only. Each entry includes: session context,
> file changed, type of change, rationale, expected effect.

---

## Mutation 1 — 2026-05-22

**Session**: Initial creation of viable-swarm-model skill
**File**: `SKILL.md`, `references/*`, `assets/*`
**Type**: create
**Rationale**: The skill was originally designed as a static instruction set.
A learning organism cannot have immutable DNA. All files must be mutable,
with regulated mutation rules, self-test at Phase 0, and a mutation log.
**Expected effect**: Future sessions will load a skill that can evaluate its
own performance and append new prevention rules, patterns, and anti-patterns
based on empirical results. The skill evolves between sessions.

---

## Mutation [N] — YYYY-MM-DD

**Session**: [Brief description of the task/session]
**File**: [Which file was modified]
**Type**: [append | edit | strikethrough | structural]
**Rationale**: [What empirical finding motivated this change. Be specific:
which build, which bug, which false positive, which missed vulnerability.]
**Expected effect**: [How the next session should behave differently because
of this mutation. What should be caught that wasn't? What should pass that
was falsely flagged?]

**Before**:
```
[content or summary of what existed]
```

**After**:
```
[content or summary of what replaced it]
```

## Mutation [2] — 2026-05-22

**Session**: Fitness build FB1 (DocuFlow)
**File**: Multiple references files
**Type**: append
**Rationale**: FB1 revealed 5 systemic gaps: (1) parallel agents overwrite entry points,
(2) fix agents claim false positives, (3) tester agent cannot function without runtime deps,
(4) GraphQL depth limiting missing from design checklist, (5) rate limiting missing from
foundation requirements. These are empirical findings from a 3500+ line multi-service build.
**Expected effect**: Next session with GraphQL will include depth limiting in design.
Next fix wave will require verification commands. Entry point conflicts will be reduced.
Tester agent environment awareness will improve.

**Files modified**:
- `references/hypotheses.md` — Added H4-H8
- `references/pattern-library.md` — Added Pattern #38 (WebSocket path token auth)
- `references/anti-patterns.md` — Added Anti-Patterns #42-43 (fix false positives, entry point overwrites)
- `references/security-lessons.md` — Added L25-L26 (GraphQL depth limit, rate limiting)
- `references/integration-checklist.md` — Added checks #21-22 (parallel coordination, WebSocket auth)

## Mutation [3] — 2026-05-22

**Session**: Fitness build FB2 (GeoQuiz)
**File**: Multiple references files
**Type**: append
**Rationale**: FB2 revealed 6 new systemic gaps: (1) docker-compose bash fallbacks embedding secrets,
(2) SQLAlchemy import shadowing by column names, (3) unbounded spatial query parameters as DoS vector,
(4) backend/frontend state machine domain mismatch, (5) tester agent wasting time installing missing deps,
(6) rate limiting still not shifting left to foundation wave. These are empirical findings from a
4000+ line multiplayer geospatial quiz platform with PostGIS, Socket.io, and Redis.
**Expected effect**: Next session with docker-compose will have no `:-` fallbacks. SQLAlchemy model
files will use aliased imports. Geo endpoints will have parameter bounds. State machine contracts
will be validated during integration. Tester agents will install deps proactively.

**Files modified**:
- `references/hypotheses.md` — Added H9-H14
- `references/security-lessons.md` — Added L37-L39 (docker-compose fallbacks, infra security, rate limiting in foundation)
- `references/pattern-library.md` — Added Patterns #39-40 (SQLAlchemy alias, spatial bounds)
- `references/integration-checklist.md` — Added Check #23 (state machine domain alignment)
- `references/anti-patterns.md` — Added Anti-Patterns #44-45 (docker fallbacks, SQLAlchemy shadowing)
- `references/custom-agent-prompts.md` — Added tester dep-install guidance and foundation rate-limiting note

## Mutation [4] — 2026-05-22

**Session**: Fitness build FB3 (TaskFlow)
**File**: Multiple references files
**Type**: append
**Rationale**: FB3 revealed 4 new systemic gaps: (1) tester agent cannot execute tests because module-level Pydantic Settings instantiation crashes on import without env vars, (2) GraphQL enum case mismatches slip through coordinator (SUCCESS vs "success"), (3) rate limiting middleware (SlowAPIMiddleware) still missing despite decorators being present in foundation wave, (4) frontend Dockerfile bakes undefined API URLs because build args are missing. Additionally, FB3 validated that FB2 mutations worked: zero docker-compose fallbacks, SQLAlchemy aliased imports, GraphQL depth limiting installed, rate limiting scaffolding shifted left to foundation wave. Security gate had zero CRITICAL/HIGH findings for the first time.
**Expected effect**: Next session with Pydantic Settings will use lazy factory pattern. Tester agents will write conftest.py before importing backend modules. GraphQL enum case will be checked during integration. Rate limiting will include both decorators and middleware. Frontend Docker builds will include API URL build args.

**Files modified**:
- `references/hypotheses.md` — Added H15-H18
- `references/security-lessons.md` — Added L40 (rate limiting requires both decorators AND middleware)
- `references/pattern-library.md` — Added Pattern #41 (lazy Pydantic Settings factory for testability)
- `references/integration-checklist.md` — Added Checks #24-25 (enum case alignment, frontend Dockerfile build args)
- `references/anti-patterns.md` — Added Anti-Pattern #46 (module-level Pydantic Settings instantiation)
- `references/custom-agent-prompts.md` — Added tester env-var injection guidance (FB3 finding)
