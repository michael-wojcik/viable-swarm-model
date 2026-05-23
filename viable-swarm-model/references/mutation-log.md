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
- `agents/vsm_tester.md` — Added tester dep-install guidance and foundation rate-limiting note

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
- `agents/vsm_tester.md` — Added tester env-var injection guidance (FB3 finding)

## Mutation [5] — 2026-05-23

**Session**: vsm-fitness-gym — Gym run testing H1, H2, H9
**File**: `references/hypotheses.md`, `references/experiments.md`
**Type**: edit (status updates), append (experiment records)
**Rationale**: All three hypotheses tested in isolation with minimal reproducible
experiments. Results were uniformly negative — the skill already detects all three
patterns. This is strong empirical evidence that the existing prevention rules
and agent prompts are effective. No new rules are needed. The skill learned what
it already knows.

**Hypotheses tested**:
- **H1** (dynamic WebSocket JWT URL): Expected gap in dynamic URL detection.
  Security agent flagged it CRITICAL immediately. Rejected.
- **H2** (N+1 in computed field loops): Expected gap in auditor coverage beyond
  ORM relationship loading. Auditor flagged it BLOCKER immediately. Rejected.
- **H9** (docker-compose `:-` fallbacks): Expected gap because prompt emphasizes
  `||` but not `:-`. Security agent detected all 4 `:-` fallbacks as CRITICAL.
  Rejected.

**Expected effect**: Future gym sessions can deprioritize these patterns. The
skill's security and audit agents are performing as designed on these specific
vulnerability classes. Gym resources should focus on the remaining 15 untested
hypotheses (H3-H8, H10-H18).

**Before**:
- H1, H2, H9 status: `untested`
- experiments.md: only template and Experiment 0

**After**:
- H1, H2, H9 status: `rejected` with full result rationale
- experiments.md: appended E1, E2, E3 with methodology and findings

---

## Mutation 6 — 2026-05-23

**Session**: vsm-fitness-gym — Gym run testing H[N+1] and H[N+2]
**File**: `agents/vsm_architect.md`, `agents/vsm_security.md`, `references/hypotheses.md`, `references/experiments.md`
**Type**: edit (status updates, agent prompt refinements), append (experiment records)
**Rationale**: Two agent-focused hypotheses tested with minimal reproducible experiments.

**H[N+1] — CONFIRMED**: The vsm_product agent produces structured product briefs that act as effective guardrails against architect scope creep. In a single-prompt experiment, the control architect (no brief) added an entire auth subsystem, multiple lists, and quantity/unit fields — all explicitly out of scope. The treatment architect (with brief) eliminated auth entirely and produced a design with only 3 core features and 12+ explicit scope exclusions. The product brief's "Out of Scope" list was the key guardrail.

**H[N+2] — REJECTED**: The vsm_security Security Fix Mode did NOT outperform a generic coder. In a single-vulnerability experiment, the generic coder fixed all 4 CRITICAL/HIGH findings including sensitive-field stripping in response DTOs. The vsm_security agent missed Finding 4 (HIGH: public DTO exposes sensitive fields) and left `secret`/`owner` exposed. It also used overly broad `except Exception:` instead of specific `jwt.PyJWTError`. The generic coder produced cleaner, more complete fixes with 10 tests vs the security agent's 11.

**Expected effect**:
- Future problem-oriented prompts will spawn vsm_product BEFORE vsm_architect to prevent scope creep.
- Future vsm_security Security Fix Mode sessions will explicitly check response DTOs for sensitive field exposure and re-read the full audit report before concluding fixes.

**Before**:
- `vsm_architect.md`: No mention of product briefs as design guardrails.
- `vsm_security.md`: Security Fix Mode checklist did not include "strip sensitive fields from response DTOs" or "re-read audit report before concluding."
- H[N+1], H[N+2] status: `untested`

**After**:
- `vsm_architect.md`: Added instruction to use product brief out-of-scope list and success criteria as guardrails.
- `vsm_security.md`: Added DTO stripping and audit re-read steps to Security Fix Mode.
- H[N+1] status: `confirmed`; H[N+2] status: `rejected`
- experiments.md: appended E4, E5
