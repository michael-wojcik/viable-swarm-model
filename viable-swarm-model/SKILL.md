---
name: viable-swarm-model
description: >
  A self-modifying cybernetic development swarm for Kimi Code CLI based on
  Stafford Beer's Viable System Model. This skill is a learning organism:
  it reads its own acquired wisdom at startup, executes
  builds with custom sub-agent types, and appends new lessons to BOTH the
  project-local memory AND its own files. Invoke with /flow:viable-swarm-model.
type: flow
triggers:
  - "build a new project"
  - "create an application"
  - "refactor this codebase"
  - "multi-file implementation"
  - "design a system"
  - "add a feature"
  - "full-stack"
  - "implement"
---

## 1. Overview

The `viable-swarm-model` skill is the **athlete** of the ecosystem. It does
the actual work — building real projects under pressure, performing in messy
conditions, and getting stronger with every session. Between builds, it
modifies its own files based on empirical results. The skill that loads in
conversation N+1 is structurally different from the skill that loaded in
conversation N.

**Mental model**: If `viable-swarm-model` is the athlete, then
`vsm-fitness-coach` is the coach (designs training, evaluates
performance) and `vsm-fitness-gym` is the gym (isolated equipment for
targeted workouts).

**How learning works**:
1. At startup (Phase 0), the skill reads its own `references/acquired-wisdom.md`
   (if it exists) and the project-local `.kimi/lessons.md`.
2. During execution, it applies prevention rules, patterns, and anti-patterns.
3. At shutdown (Phase 8b), it evaluates its own performance, proposes new
   hypotheses, and appends new knowledge to its own files.

**Primary invocation**: `/flow:viable-swarm-model` executes the full workflow.
Must be embedded in a message (e.g., `Let's build something. /flow:viable-swarm-model Build a React app`).
**Reference loading**: `/skill:viable-swarm-model` loads knowledge without execution.

**Path convention**: This skill assumes installation at
`~/vsm/viable-swarm-model/`. When self-modifying, the model uses
absolute paths from this root. If installed elsewhere (e.g. via `extra_skill_dirs`),
use symlinks or update paths in mutation commands.

## 2. How to Invoke This Skill

- **`/flow:viable-swarm-model <task>`** — Execute the full VSM workflow. The model
  follows the Mermaid flow diagram step-by-step, outputting `<choice>branch</choice>`
  at decision nodes to select paths. Must include some natural language text
  before or around the command for Kimi CLI to process it.
- **`/skill:viable-swarm-model`** — Load as knowledge reference. Use when you
  need patterns, anti-patterns, or checklists without triggering the full workflow.

## 3. VSM Role Map with Custom Sub-Agent Types

| VSM System | CLI Implementation | Custom Type | Activation | Produces |
|---|---|---|---|---|
| **S5 (Policy)** | Main conversation agent (you) | — | Always | Decisions, escalation, mutations |
| **S4 (Intelligence)** | `vsm_architect` subagent | Custom | Phase 1 | Architecture doc, API spec |
| **S4 (Intelligence)** | `vsm_product` subagent | Custom | Phase 0 (conditional) | Product brief, user stories, acceptance criteria |
| **S3 (Control)** | Main agent via SetTodoList | — | All phases | Progress tracking, mutation decisions |
| **S3* (Audit)** | `vsm_auditor` subagent | Custom | After waves | PASS/ISSUES/BLOCKER |
| **S2 (Coordination)** | `vsm_coordinator` subagent | Custom | After Wave 3 | Integration report |
| **S1-Backend** | `coder` subagent | Built-in | Phases 2,3 | Backend code |
| **S1-Frontend** | `coder` subagent | Built-in | Phases 2,3 | Frontend code |
| **S1-Tester** | `vsm_tester` subagent | Custom | Phase 4 | Tests, coverage |
| **S1-Security** | `vsm_security` subagent | Custom | Phase 5 | Security findings |
| **S1-DevOps** | `coder` subagent | Built-in | Phase 4 | Docker, CI/CD |
| **Algedonic** | Main agent detects/stops | — | Any phase | TaskStop, AskUserQuestion |

**Terminology**: `S5` refers to the main conversation agent (you, the LLM executing
this skill). The word `user` refers to the human operator. S5 may escalate to the
user via `AskUserQuestion` or `EnterPlanMode` when human policy input is required.

### Custom Type Prompt Characteristics

**`vsm_product`** (S4 Intelligence — Product): Analyzes problem-oriented prompts,
defines success criteria, proposes minimal viable feature set, outputs structured
product brief with user stories and acceptance criteria. Does NOT design systems
or write code. Defined in `agents/vsm_product.md`.

**`vsm_architect`** (S4 Intelligence — Technical): Reads codebase, researches tech, produces
 design documents ONLY (never code). Validates against S5 policy. Uses product
brief (if present) as input. Defined in `agents/vsm_architect.md`.

**`vsm_auditor`** (S3* Audit): Read-only. Reads EVERY source file. Produces
PASS/ISSUES/BLOCKER per file. Checks correctness, security, performance,
maintainability. Includes full cross-file checklist. Defined in
`agents/vsm_auditor.md`.

**`vsm_coordinator`** (S2 Coordination): Read-only. Compares S1 outputs.
Validates imports, interfaces, naming, type alignment. Checks WebSocket contracts,
GraphQL SDL, Prisma relations, env vars. Defined in `agents/vsm_coordinator.md`.

**`vsm_security`** (Security Audit): Read-only security specialist. Runs 15+
point security checklist. Prevents, not detects — knows all anti-patterns.
Defined in `agents/vsm_security.md`.

**`vsm_tester`** (S1 Quality): Reads implementation, writes tests (unit,
integration, edge cases). Bug-Fix Bonus: fixes bugs inline. Runs tests via
Shell. Defined in `agents/vsm_tester.md`.

### Agent Output Types

**Writes implementation code:**
- `coder` (built-in) — features, backend, frontend, infrastructure
- `vsm_tester` (custom) — tests, bug fixes inline

**Writes design/requirements documents:**
- `vsm_product` (custom) — product briefs, user stories, acceptance criteria
- `vsm_architect` (custom) — architecture docs, API specs

**Read-only evaluation (reports, audits, checklists):**
- `vsm_auditor` (custom) — correctness audit per file
- `vsm_coordinator` (custom) — cross-file contract validation
- `vsm_security` (custom) — security audit, anti-pattern detection

## 4. The Golden Rule of Parallelism

```
Independent subagents -> run_in_background=true (parallel, up to configured limit in `background.max_running_tasks`)
Dependent subagents   -> sequential (TaskOutput block=true before next)
```

## 5. Executable Flow Diagram

When invoked via `/flow:viable-swarm-model`, follow this diagram. At diamond
decision nodes, output `<choice>branch name</choice>` to select the next step.

```mermaid
flowchart TD
    BEGIN([BEGIN])
    P0[Phase 0: Viability Check + Self-Test<br/>S5 Main Agent]
    P0D{<choice>trivial</choice>?}
    P0R[Read .kimi/lessons.md<br/>Read references/acquired-wisdom.md<br/>Read references/hypotheses.md<br/>Self-test skill files<br/>Classify prompt<br/>Write plan.md]
    P0P[Conditional: Spawn vsm_product<br/>If problem-oriented prompt]
    P1[Phase 1: Intelligence<br/>vsm_architect subagent<br/>Uses product brief if present]
    P1H{<choice>S3/S4 deadlock</choice>?}
    P1A[EnterPlanMode<br/>User Approval]
    P1D{<choice>approved</choice>?}
    P2[Phase 2: Foundation Wave<br/>parallel coder agents<br/>run_in_background=true]
    P2S[TaskOutput block=true]
    P2A[Phase 2b: Audit<br/>vsm_auditor]
    P2M[Phase 2c: Model Validation<br/>S5 checks models.py vs data-model.md]
    P2D{<choice>BLOCKERs</choice>?}
    P3[Phase 3: Implementation Wave<br/>Parallel coder agents]
    P3S[TaskOutput block=true]
    P3M[Phase 3c: Mid-Wave S2 Check<br/>vsm_coordinator (conditional, Tier 2+)]
    P3A[Phase 3b: Audit + Coordination<br/>vsm_auditor + vsm_coordinator]
    P3D{<choice>BLOCKERs</choice>?}
    P3E[Entry Point Wiring<br/>MANDATORY]
    P3D2[Phase 3d: Frontend Config Validation<br/>S5 checks frontend config files]
    P4[Phase 4: Testing + Infra Wave<br/>vsm_tester + coder]
    P4S[TaskOutput block=true]
    P4R[Shell: run tests]
    P5[Phase 5: Security Gate<br/>vsm_security]
    P5D{<choice>CRITICAL/HIGH</choice>?}
    P5L[Document LOW as<br/>known limitation]
    P6[Phase 6: Integration Verification<br/>vsm_coordinator + vsm_auditor]
    P6D{<choice>ANY failure</choice>?}
    P7[Phase 7: Fix Wave<br/>coder agents]
    P7R[Re-audit changed files]
    P7D{<choice>BLOCKERs remain<br/>iterations < 3</choice>?}
    P7E[Escalate to User<br/>AskUserQuestion]
    P7S[Phase 7b: Post-Fix Security Re-Check<br/>vsm_security on modified auth/GraphQL/WebSocket]
    P7F{<choice>regressions found</choice>?}
    P8[Phase 8: Reflection<br/>Append to .kimi/lessons.md]
    P8M[Phase 8b: Meta-Reflection + Hypothesis Generation<br/>Evaluate performance<br/>Write new hypotheses to hypotheses.md<br/>Bucket mutations: append-only vs refinement vs structural]
    P8W[Write append-only mutations<br/>security-lessons.md, pattern-library.md,<br/>anti-patterns.md, integration-checklist.md,<br/>experiments.md, hypotheses.md,<br/>mutation-log.md]
    P8R[Apply refinement mutations<br/>Single file, preserve structure<br/>agents/*.md, references/*.md]
    P8A{<choice>structural mutations<br/>approved by user</choice>?}
    P8WS[Write approved structural mutations<br/>SKILL.md, flow diagram,<br/>phase logic, agent architecture]
    P8L[Log rejection rationale<br/>to mutation-log.md]
    P8C[git commit all changes]
    END([END])

    BEGIN --> P0
    P0 --> P0D
    P0D -->|<choice>yes</choice>| END
    P0D -->|<choice>no</choice>| P0R
    P0R --> P0P
    P0P --> P1
    P1 --> P1H
    P1H -->|<choice>yes</choice>| P1
    P1H -->|<choice>no</choice>| P1A
    P1A --> P1D
    P1D -->|<choice>rejected</choice>| P1
    P1D -->|<choice>approved</choice>| P2
    P2 --> P2S
    P2S --> P2A
    P2A --> P2M
    P2M --> P2D
    P2D -->|<choice>yes</choice>| P7_FOUNDATION
    P2D -->|<choice>no</choice>| P3
    P3 --> P3S
    P3S --> P3M
    P3M --> P3A
    P3A --> P3D
    P3D -->|<choice>yes</choice>| P7_IMPL
    P3D -->|<choice>no</choice>| P3E
    P3E --> P3D2
    P3D2 --> P4
    P4 --> P4S
    P4S --> P4R
    P4R --> P5
    P5 --> P5D
    P5D -->|<choice>yes</choice>| P7_IMPL
    P5D -->|<choice>LOW only</choice>| P5L
    P5D -->|<choice>none</choice>| P6
    P5L --> P6
    P6 --> P6D
    P6D -->|<choice>yes</choice>| P7_IMPL
    P6D -->|<choice>no</choice>| P8
    P7_FOUNDATION[Phase 7: Fix Wave<br/>Foundation BLOCKERs]
    P7_FOUNDATION --> P7R_F[Re-audit changed files]
    P7R_F --> P7D_F{BLOCKERs remain<br/>iterations < 3?}
    P7D_F -->|<choice>yes</choice>| P7_FOUNDATION
    P7D_F -->|<choice>no, max reached</choice>| P7E
    P7D_F -->|<choice>no, all clear</choice>| P2
    P7_IMPL[Phase 7: Fix Wave<br/>Implementation BLOCKERs]
    P7_IMPL --> P7R_I[Re-audit changed files]
    P7R_I --> P7D_I{BLOCKERs remain<br/>iterations < 3?}
    P7D_I -->|<choice>yes</choice>| P7_IMPL
    P7D_I -->|<choice>no, max reached</choice>| P7E
    P7D_I -->|<choice>no, all clear</choice>| P7S
    P7S --> P7F
    P7F -->|<choice>yes</choice>| P7_IMPL
    P7F -->|<choice>no</choice>| P4
    P7E --> END
    P8 --> P8M
    P8M --> P8W
    P8W --> P8R
    P8R --> P8A
    P8A -->|<choice>yes</choice>| P8WS
    P8A -->|<choice>no</choice>| P8L
    P8WS --> P8C
    P8L --> P8C
    P8C --> END
```

## 6. Phase Details

### Phase 0: Viability Check + Self-Test
Main agent (S5) performs:
1. **Viability check**: trivial (<50 lines, one file)? If yes, respond directly.
2. **Classify prompt**: Prescriptive ("Build X with Y") or problem-oriented
   ("Users need Z")? If problem-oriented, spawn `vsm_product` subagent to
   produce a product brief with user stories and acceptance criteria.
3. **Read project memory**: `.kimi/lessons.md` if exists.
4. **Read acquired wisdom**: `~/vsm/viable-swarm-model/references/acquired-wisdom.md`
   if exists.
5. **Read hypotheses**: `~/vsm/viable-swarm-model/references/hypotheses.md`
   if exists. Note any untested hypotheses that are relevant to this project.
5. **Self-test**: Verify all referenced files exist and are readable. Verify
the flow diagram parses. Verify the skill can describe its own phase sequence
without contradiction. If any check fails → emit algedonic, write diagnosis
to `~/vsm/viable-swarm-model/references/mutation-log.md`, ask user to review.
6. **Read runtime capacity**: Read `~/.kimi/config.toml` and extract
   `background.max_running_tasks` (default 4 if absent). Log this value in
   `plan.md` as the parallel agent ceiling. NEVER exceed this limit when
   spawning background subagents.
7. **Variety Assessment** (Ashby's Law): Estimate project complexity and classify tier.
   Use the `max_running_tasks` value read in step 6 as the agent ceiling.
   Do not invent artificial sub-limits — if the host allows 8, use up to 8.
   - **Tier 1** (<1000 lines, 1-2 services): Standard flow, no mid-wave gates needed
   - **Tier 2** (1000-3000 lines, 2-3 services): Add Phase 3c mid-wave S2 check, extend timeouts
   - **Tier 3** (3000+ lines, 3+ services): Split into sub-builds OR accept that single-session coverage will be partial. Do not pretend the metasystem has requisite variety it lacks.
   Log the tier and the agent ceiling in `plan.md`. Adjust timeout expectations accordingly.
7. Write `plan.md`.

### Phase 1: Intelligence (S4)
Spawn `vsm_architect` subagent. Review output. S3/S4 homeostat: max 3
iterations before escalating to S5.

**S5 Policy Check** (before approval): Explicitly weigh:
- **S3 concern**: Can the metasystem regulate this complexity? (Check Variety Assessment tier. Do we have enough agents, time, and context?)
- **S4 concern**: Does this design position the project well for future evolution?
- **If conflict**: S5 decides which takes precedence. Security and correctness (S3*) always win over speed. Log the rationale in `plan.md`.

EnterPlanMode for user approval. Rejected plans loop back.

### Phase 2: Foundation Wave

**For multi-service or complex projects, split the foundation wave into two
sequential sub-waves to eliminate dependency race conditions.**

**Sub-Wave 2a — Core Contracts (parallel, then verify)**:
Spawn parallel `coder` subagents with `run_in_background=true` for:
- `models.py` (including engine + session factory like `AsyncSessionLocal`)
- `auth.py` + `roles.py` (stable signatures: `get_current_user`, `require_role`)
- `config.py` (lazy factory, NO default secrets)
- `shared/types.ts` + `shared/sio-events.ts`
- `requirements.txt`, `package.json`
- `.env.example` (env var naming contract established HERE)

Wait via `TaskOutput(block=true)`. Then S5 runs a **mini-audit**:
- Does `models.py` define `AsyncSessionLocal`?
- Does `auth.py` have stable `get_current_user` / `require_role` signatures?
- Are `.env.example` names finalized and consistent?
- Do all 2a files compile/import cleanly?

If any check fails → fix BEFORE dispatching Sub-Wave 2b.

**Sub-Wave 2b — Dependent Infrastructure (parallel, then verify)**:
Spawn parallel `coder` subagents with `run_in_background=true` for:
- `routers/auth.py` (MUST include `POST /login`, `POST /register`, `GET /me` endpoints)
- `graphql.py` (imports from models, auth)
- `sio.py` (imports from models, auth)
- `main.py` scaffolding (imports from config, registers middleware)
- Frontend scaffolding (Vite config, App.tsx skeleton, path aliases)
- `docker-compose.yml`

Wait via `TaskOutput(block=true)`.

**Phase 2b: Audit** — Spawn `vsm_auditor` on ALL foundation outputs (2a + 2b).
BLOCKERs trigger Phase 7.

**Phase 2c: Model Validation (S5)** — After foundation audit passes and BEFORE
spawning implementation agents, S5 MUST verify that `models.py` (or equivalent)
matches `data-model.md` field names and types exactly. If `data-model.md` exists
in the build directory and the models do not match, treat as a BLOCKER: send
back to foundation agents for correction. This prevents cascade failures in
GraphQL, frontend queries, and shared types.

### Phase 3: Implementation Wave
Pass Wave 1 outputs as input references. Spawn parallel `coder` subagents.
Entry point wiring MANDATORY after this wave. Audit + coordination check.
BLOCKERs trigger Phase 7.

**Phase 3c: Mid-Wave S2 Check (conditional)** — If project is Tier 2+ and 2+
parallel coder agents were spawned, spawn a lightweight `vsm_coordinator` check
on shared contracts after the first agents complete. Flag ONLY critical
drift that would block incomplete agents. If drift found → emit algedonic,
halt remaining agents, inject corrections.

### Phase 3d: Frontend Config Validation
After entry point wiring and BEFORE the testing wave, S5 MUST perform a
lightweight frontend config validation check:

1. Read `src/graphql/client.ts` and `src/sio/client.ts`
2. Verify NO `||` fallbacks for API/WS/GraphQL URLs
3. Verify NO `localhost` hardcoded as fallback in frontend config
4. Verify `vite.config.ts` proxy includes `/api`, `/graphql`, `/ws`
5. Verify `tsconfig.json` includes all files that `tsc -b` will type-check

ANY failure → back to Phase 3 (frontend implementation agent fixes).

This prevents frontend configuration bugs from surviving to the security gate,
where they are currently discovered too late.

### Phase 3e: Frontend Cross-File Import Check
After all parallel frontend implementation agents complete and BEFORE spawning
the auditor, S5 MUST run a lightweight cross-file import verification:

1. Run `npx tsc --noEmit` (or `npm run build`, or grep all imports) to verify
   every import statement in `src/pages/` and `src/components/` resolves
2. Verify every export from `src/graphql/queries.ts` is imported by at least
   one page or component
3. Verify every field destructured from Zustand stores exists in the store
4. Verify every type imported from `shared/types.ts` is defined in that file

ANY failure → back to Phase 3 (frontend implementation agent fixes).

This prevents frontend contract mismatches (missing exports, missing store fields)
from reaching the auditor, where they currently consume auditor capacity on
trivial integration issues.

### Phase 4: Testing & Infra Wave
Spawn `vsm_tester` + `coder` (devops) in parallel. Run tests via Shell.
Report coverage.

### Phase 5: Security Gate
Spawn `vsm_security`. CRITICAL/HIGH → stop, fix, re-audit. LOW → document.
Gather vs. Stop: planned wave → gather; mid-build → emergency stop.

**Security gate runs BEFORE integration verification** so that vulnerabilities
are caught before the coordinator invests effort in cross-file contract checks.
This reduces total fix iterations.

### Phase 6: Integration Verification
Spawn `vsm_coordinator` + `vsm_auditor`. Full 20+ point checklist (see
`references/integration-checklist.md`). ANY failure → back to Phase 3.

### Phase 7: Fix Wave (conditional)
Group fixes by file. Parallel across files, sequential within file. Spawn
`coder` subagents. MANDATORY re-audit after. **MANDATORY full test suite run after**
(`pytest tests/` and `vitest run` / `npm test`). Re-auditing changed files alone
misses regressions in unrelated tests. Max 3 iterations. Still blocked?
Escalate to user.

**Return paths differ by BLOCKER source**:
- **Foundation BLOCKERs** (Phase 2b/2c audit): After fix clears, return to
  Sub-Wave 2b (Dependent Infrastructure) to re-verify the foundation.
- **Implementation BLOCKERs** (Phase 3b, 5, or 6): After fix clears, return to
  Phase 4 (Testing) → Phase 5 (Security) → Phase 6 (Integration) before
  proceeding to Phase 8. NEVER skip Testing, Security, or Integration after
  fixing implementation-phase issues.

**Phase 7b: Post-Fix Security Re-Check** — After fix wave clears all BLOCKERs
and BEFORE returning to the main flow, S5 MUST run a lightweight security
re-check on any file modified during the fix wave that touches auth, GraphQL,
or WebSocket code. Spawn `vsm_security` with a focused scope (modified files
only). If the re-check finds CRITICAL/HIGH regressions (e.g., a fix agent
weakened auth), loop back to Phase 7. This prevents fix/test agents from
introducing vulnerabilities after the main security gate.

### Phase 8: Reflection
Write a standalone `.kimi/lessons.md` in the build directory.

**Required structure**: Follow `references/lessons-template.md`:
- One entry per significant issue or pattern discovered
- Each entry must include: Source, Finding, Fix, Verification, Prevention rule
- Never merge reflection content into `meta-reflection.md`

**Minimum entries**: At least one entry for each phase that scored < 4 or produced a BLOCKER.

See `references/lessons-template.md` for the full template.

### Phase 8b: Meta-Reflection + Hypothesis Generation
After project reflection, evaluate the skill's own performance.

**Independent verification requirement**: Before writing `meta-reflection.md`,
S5 MUST independently run the full test suite (`pytest tests/` and `vitest run` /
`npm test`) and record the ACTUAL pass/fail counts. Do NOT repeat claims from
upstream phases without verification. If tests fail, the meta-reflection must
acknowledge the failure and propose a root-cause hypothesis.

After verification, proceed with:

1. **Effectiveness audit**: Which prevention rules caught real bugs? Which
   flagged safe code as risky (false positive)?
2. **Coverage audit**: Were any anti-patterns missed? Any vulnerability classes
   not covered by existing checklists?
3. **Phase audit**: Were any phases unnecessary? Any decision points misleading?
   Did the flow diagram match reality?
4. **Agent audit**: Did any custom agent type underperform? Do prompts need
   refinement?

**Hypothesis generation** (always append-only, always happens):
5. **Anomaly detection**: What was surprising? What did the skill get wrong?
   What vulnerability class is completely absent from our knowledge base?
6. **Propose hypotheses**: For each anomaly, write a new hypothesis to
   `~/vsm/viable-swarm-model/references/hypotheses.md` with:
   - Status: untested
   - Rationale: what was observed
   - Experiment: minimal test to validate
   - Expected result

**Three-tier mutation system:**

| Tier | Scope | Approval | Logging |
|---|---|---|---|
| **Append-only** | Add new content. Zero modifications to existing text. | Autonomous | `mutation-log.md` |
| **Refinement** | Modify existing content in a single file. Preserve structure (headings, sections, logic flow). Only in `references/` or `agents/`. No `SKILL.md`. | Autonomous | `mutation-log.md` + rationale |
| **Structural** | Multi-file, architecture, `SKILL.md`, add/remove agents or phases. | User via `AskUserQuestion` | `mutation-log.md` + rejection rationale |

**Tier 1 — Append-only** (autonomous):
If empirical findings justify it, append directly:
- New rules to `references/security-lessons.md`
- New patterns to `references/pattern-library.md`
- New anti-patterns to `references/anti-patterns.md`
- New checks to `references/integration-checklist.md`
- Experiments to `references/experiments.md`
- Rationale to `references/mutation-log.md`

**Tier 2 — Refinement** (autonomous, logged):
If findings justify surgical changes to existing content:
- Reword an agent prompt in `agents/*.md` for clarity
- Update a criterion weight in `references/evaluation-rubric.md`
- Fix a typo or unclear wording in any `references/*.md`
- Update a hypothesis status from `untested` to `confirmed`
- Refine a checklist item without adding/removing sections

Constraints: single file, preserve structure, no `SKILL.md` changes.
Log the rationale to `references/mutation-log.md`.

**Tier 3 — Structural** (user approval via `AskUserQuestion`):
If findings justify architecture changes:
1. Present to user via `AskUserQuestion`:
   - Files that would change
   - What the change does
   - Evidence from this build
2. If approved: write the changes, then **immediately `git commit`**
3. If rejected: log the rejection rationale to `references/mutation-log.md`

**Mutation amplitude limit**: Max 3 structural mutations per session.
Append-only and refinement mutations are unlimited.
`git commit` all changes.

## 7. Cross-File Integration Verification Checklist

Run ALL checks from `references/integration-checklist.md`. Summary:

1. Every export imported by a consumer; no orphaned code
2. Shared contracts consistent across files
3. Entry points register all middleware
4. Codebase compiles/builds
5. WebSocket: every backend emit has matching frontend listener
6. GraphQL SDL matches TypeScript; subscriptions have resolvers
7. Frontend paths correct; Vite proxy includes `/api`, `/graphql`, `/ws`
8. pgvector: extension enabled, dimensions match, ivfflat index exists
9. SSE: `media_type="text/event-stream"`, yields `data: {json}\n\n`
10. CRDT: PersistenceAdapter connected, BYTEA column, chronological load
11. DAG: `validate()` on mutate, 3-color DFS, topological sort
12. Redis: queue names consistent, dependent enqueue, pub/sub match
13. Frontend scaffolding: package.json, vite.config.ts, tsconfig.json, index.html, main.tsx, App.tsx
14. Rust: workspace includes all crates, no duplicate imports
15. Go: camelCase JSON tags, no snake_case leakage
16. Docker Compose: all CMD/ENTRYPOINT files exist

**Rule**: ANY failure → send back to responsible S1 BEFORE quality gates.

## 8. Security Gate Checklist

Run ALL checks from `references/security-lessons.md`. Summary:

1. No hardcoded secrets or `||` fallbacks for SECRET/KEY/PASSWORD/TOKEN
2. No fake JWT parsers — proper signature verification only
3. WebSocket auth in-band, never URL query param
4. CORS origin is explicit allowlist, never `true` or `*` with credentials
5. Document ownership filtering on ALL list endpoints
6. Public DTOs omit answer/solution fields
7. GraphQL depth limit (max 10) + complexity analysis
8. Passwords: bcrypt only, never plaintext/MD5/SHA1
9. N+1 queries: ORM relationship loading AND computed field loops
10. Auth middleware raises on failure, never returns None
11. Every service has verifiable entry point
12. Standalone workers never imported as libraries
13. Env var names match across docker-compose/.env/code
14. Frontend API URL has no localhost fallback
15. `||` fallback banned for ALL config URLs
16. JWT_SECRET required, min 32 chars, app refuses start without it
17. SSE: short-lived token exchange, never long-lived JWT in URL

## 9. Exit Criteria

Stop iterating when ALL true:
1. No BLOCKERs in **re-audit** report (not original — re-audit after fixes)
2. < 3 open ISSUES (or documented as known limitations)
3. All `plan.md` modules implemented
4. Tests pass (or test code is correct)
5. README has setup instructions

If BLOCKERs remain → another fix wave (max 3 iterations). Stuck after 3 →
escalate to user.

**Known Limitations Template**:
```markdown
| # | Severity | Issue | Impact | Planned Fix |
|---|----------|-------|--------|-------------|
| 1 | MEDIUM | Feature X not implemented | Manual workaround | v2.0 |
```

## 10. The Mutation System

This skill is a learning organism. It modifies its own files between sessions.
All files in `~/vsm/viable-swarm-model/` are mutable.

### Why Mutation Is Safe

The skill directory is a **git repository**. Every mutation is committed.
If a mutation breaks viability, the user (or the skill itself) can revert:

```bash
cd ~/vsm/viable-swarm-model
git log --oneline
git revert [commit]
```

### What Can Mutate

| File | Mutation Mode | Justification Required |
|---|---|---|
| `references/security-lessons.md` | Append new lessons; strikethrough false positives | Low: empirical finding |
| `references/pattern-library.md` | Append new patterns; mark obsolete | Low: empirical finding |
| `references/anti-patterns.md` | Append new; remove false positives | Low: empirical finding |
| `references/integration-checklist.md` | Append new checks | Low: empirical finding |
| `references/hypotheses.md` | Append new hypotheses; update status | Low: empirical finding |
| `references/experiments.md` | Append experiment records | Low: empirical finding |
| `agents/*.md` | Refine agent prompts | Medium: repeated pattern |
| `references/flow-diagram.mermaid` | Refine decision logic | High: phase audit shows mismatch |
| `SKILL.md` | Amend phase details, mutation rules | High: structural issue proven |

### Mutation Log Format

Every mutation is recorded in `references/mutation-log.md`:
```markdown
## Mutation [N] — YYYY-MM-DD
**Session**: [task description]
**File**: [path]
**Type**: [append | edit | remove | structural]
**Rationale**: [why this change improves the skill]
**Expected effect**: [what should happen in next session]
```

### Epistemic Rule for Self-Modification

"If a mutation contradicts the original design intent, the mutation wins IF it
was validated by empirical results. Design intent is a hypothesis; empirical
results are evidence."

### Rollback Procedure

If Phase 0 self-test fails because of a bad mutation:
1. Read `references/mutation-log.md` to identify the offending mutation
2. `git revert` the commit
3. Re-run Phase 0 self-test
4. Document the reversion as a new mutation entry (learning what NOT to change)

## 11. Comprehension Checkpoint

Before declaring a phase complete, explain what was built:

1. **Comprehension** — Explain without referring to original spec
2. **Connections** — Map to broader context (other files, architecture)
3. **Rationale** — Explain WHY, not just WHAT
4. **Edge cases** — Identify assumptions and limitations
5. **Consequences** — Predict impact on other system parts

If explanation reveals gaps → revisit before proceeding.

## 12. Background Task Management

Use `TaskList` to monitor active tasks. Use `TaskOutput(block=true)` to
synchronize dependent waves. Use `TaskStop` to cancel on algedonic signals.
Use `/tasks` command for interactive browser.

Max concurrent background tasks defaults to 4, configurable via `background.max_running_tasks`
in `~/.kimi/config.toml` (e.g., `max_running_tasks = 8`).

## 13. Session Resumption for Learning

When `--continue` resumes a session:
1. Read `.kimi/lessons.md` at session start
2. Read `~/vsm/viable-swarm-model/references/acquired-wisdom.md`
3. Read `~/vsm/viable-swarm-model/references/hypotheses.md`
4. Apply relevant lessons to planning
5. After delivery, append new lessons to both project-local and skill-global memory
6. Over time, this creates both a project-specific and a cross-project knowledge base

**Epistemic rule**: If `.kimi/lessons.md` contradicts this SKILL.md,
the lessons file wins. It contains empirical data; this file contains
general guidance.

## 14. Quick Decision Tree

```
User asks for software engineering work?
├── Trivial (< 50 lines, one file)?
│   └── Respond directly, no VSM workflow
└── Non-trivial?
    ├── Read .kimi/lessons.md if exists (apply learnings)
    ├── Read references/acquired-wisdom.md if exists (apply cross-project learnings)
    ├── Read references/hypotheses.md if exists (test relevant hypotheses)
    └── Execute VSM workflow via /flow:viable-swarm-model
```
