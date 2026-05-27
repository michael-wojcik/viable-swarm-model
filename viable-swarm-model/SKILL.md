---
name: viable-swarm-model
description: >
  A self-modifying cybernetic development swarm for Kimi Code CLI based on
  Stafford Beer's Viable System Model. This skill is a learning organism:
  it reads its own acquired wisdom at startup, executes
  builds with custom sub-agent types, and appends new lessons to BOTH the
  project-local memory AND its own files. Invoke with /flow:viable-swarm-model.
type: flow
whenToUse: When the user wants to build, refactor, or design a multi-file software project, especially full-stack applications, new features, or system architectures.
disableModelInvocation: false
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
1. At startup (Phase 0), the skill reads its own skill-level reference files
   (`references/acquired-wisdom.md`, `references/meta-reflection.md`) and the
   project-local `.kimi/lessons.md`.

   **File Location Convention**:
   - `references/` in the skill repo (`${KIMI_SKILL_DIR}/references/`) →
     persistent skill-level knowledge (acquired-wisdom, hypotheses, meta-reflection)
   - `.kimi/` in the build directory → per-build artifacts (lessons, agent reports)
2. During execution, it applies prevention rules, patterns, and anti-patterns.
3. At shutdown (Phase 8b), it evaluates its own performance, proposes new
   hypotheses, and appends new knowledge to its own files.

**Primary invocation**: `/flow:viable-swarm-model` executes the full workflow.
Must be embedded in a message (e.g., `Let's build something. /flow:viable-swarm-model Build a [frontend framework] app`).
**Reference loading**: `/skill:viable-swarm-model` loads knowledge without execution.

**Path convention**: This skill assumes installation at
`${KIMI_SKILL_DIR}`. When self-modifying, the model uses
absolute paths from this root. If installed elsewhere (e.g. via `extra_skill_dirs`),
use symlinks or update paths in mutation commands.

## 2. Context Budget Rule (MANDATORY)

S5 has a finite context window. Every line consumed by file reads is a line
unavailable for reasoning. Apply these rules **before every `ReadFile`**:

1. **Check file size first**: Use `Shell: wc -l <file>` before `ReadFile`.
2. **>500 lines?** Never read in full. Use targeted extraction:
   - Append-only files (`hypotheses.md`, `mutation-log.md`, `fitness-projects.md`):
     `tail -n 50` for recent entries
   - Structured files: `grep -A 5 "^## H"` for hypotheses, `grep "^## Mutation"` for logs
   - Reports: read only the "Executive Summary" section (first 30 lines)
3. **Already read it this session?** Do not re-read. Reference your prior summary.
4. **Spawn subagents for bulk reading**: `vsm_synthesizer` reads multiple reports
   and produces a single executive summary. S5 reads only the synthesis.

**Violation is a BLOCKER**: Reading a 2000-line file in full consumes ~15-20%
of available context with zero benefit. S5 MUST be ruthless about context
preservation.

## 3. How to Invoke This Skill

**Prerequisite**: The swarm requires custom agent files. Launch Kimi CLI with the base agent:
```bash
kimi --agent-file ~/vsm/viable-swarm-model/agents/vsm-main.yaml
```
Then in the session:
- **`/flow:viable-swarm-model <task>`** — Execute the full VSM workflow. The model
  follows the Mermaid flow diagram step-by-step, outputting `<choice>branch</choice>`
  at decision nodes to select paths. Must include some natural language text
  before or around the command for Kimi CLI to process it.
- **`/skill:viable-swarm-model`** — Load as knowledge reference. Use when you
  need patterns, anti-patterns, or checklists without triggering the full workflow.

> **Platform constraint**: This flow MUST be executed by the root conversation agent (S5). It cannot be delegated to a single subagent because the workflow internally spawns custom subagents (`vsm_architect`, `vsm_auditor`, `vsm_security`, etc.) and subagents do not have access to the `Agent` tool.

## 4. VSM Role Map with Custom Agent Files

All swarm agents are defined as **custom Kimi CLI agent files** (`agents/*.yaml`) that extend a shared base (`agents/vsm-main.yaml`). Each YAML points to a system prompt markdown file (`agents/*.md`) via `system_prompt_path`. To spawn an agent, use `Agent(subagent_type="<name>", ...)` — the system prompt and tool list are loaded automatically; you do NOT need to read or embed the agent definition file into the prompt.

> **Important**: When using `--agent-file`, built-in subagent types (`coder`, `explore`, `plan`) are **unavailable**. S5 and all spawned agents must use the custom types defined in `agents/vsm-main.yaml`. S5 itself retains full tool access.

**Agent Spawn Hygiene — Context Isolation (MANDATORY)**
Report-producing agents (all `vsm-reporter` descendants: `vsm_auditor`,
`vsm_security`, `vsm_coordinator`, `vsm_meta`) MUST always be spawned as
**new instances** (`subagent_type="..."`) — never via `resume`. Cross-build
context contamination has caused hallucinated findings (e.g., vsm_meta reporting
FB17 data during FB23). Coding agents (all `vsm-coder` descendants) may use
`resume` within the same build wave for continuity, but start fresh on a new
build.

| VSM System | CLI Implementation | Parent Category | Custom Type | Activation | Produces |
|---|---|---|---|---|---|
| **S5 (Policy)** | Main conversation agent (you) | — | — | Always | Decisions, escalation, mutations |
| **S4 (Intelligence)** | `vsm_architect` subagent | `vsm-researcher` | Custom | Phase 1 | Architecture doc, API spec |
| **S4 (Intelligence)** | `vsm_product` subagent | `vsm-researcher` | Custom | Phase 0 (conditional) | Product brief, user stories, acceptance criteria |
| **S4 (Exploration)** | `vsm_explore` subagent | `vsm-researcher` | Custom | Any phase | Read-only file mapping, pattern search |
| **S3 (Control)** | Main agent via SetTodoList | — | — | All phases | Progress tracking, mutation decisions |
| **S3* (Audit)** | `vsm_auditor` subagent | `vsm-reporter` | Custom | After waves | PASS/ISSUES/BLOCKER |
| **S2 (Coordination)** | `vsm_coordinator` subagent | `vsm-reporter` | Custom | After Wave 3 | Integration report |
| **S2 (Synthesis)** | `vsm_synthesizer` subagent | `vsm-reporter` | Custom | After report phases | Executive summary of multiple reports |
| **S2 (Wiring)** | `vsm_wiring` subagent | `vsm-coder` | Custom | After Phase 3 | Entry-point wiring verification |
| **S1-Backend** | `vsm_backend_coder` subagent | `vsm-coder` | Custom | Phases 2,3 | Backend code |
| **S1-Frontend** | `vsm_frontend_coder` subagent | `vsm-coder` | Custom | Phases 2,3 | Frontend code |
| **S1-Backend-Fix** | `vsm_backend_fix_agent` subagent | `vsm-fixer` | Custom | Phase 7 | Backend surgical fixes, re-audit report |
| **S1-Frontend-Fix** | `vsm_frontend_fix_agent` subagent | `vsm-fixer` | Custom | Phase 7 | Frontend surgical fixes, re-audit report |
| **S1-Backend-Tester** | `vsm_backend_tester` subagent | `vsm-tester` | Custom | Phase 4 | Backend tests (framework test runner), API tests |
| **S1-Frontend-Tester** | `vsm_frontend_tester` subagent | `vsm-tester` | Custom | Phase 4 | Frontend tests (framework test runner), build verification |
| **Security** | `vsm_security` subagent | `vsm-reporter` | Custom | Phase 5 | Security findings |
| **S5-Meta** | `vsm_meta` subagent | `vsm-reporter` | Custom | Phase 8b | Performance evaluation, hypothesis generation |
| **S1-DevOps** | `vsm_devops_coder` subagent | `vsm-coder` | Custom | Phase 4 | Docker, CI/CD |
| **Algedonic** | Main agent detects/stops | — | — | Any phase | TaskStop, AskUserQuestion |

**Terminology**: `S5` refers to the main conversation agent (you, the LLM executing
this skill). The word `user` refers to the human operator. S5 may escalate to the
user via `AskUserQuestion` or `EnterPlanMode` when human policy input is required.

### Custom Type Prompt Characteristics

**`vsm_product`** (S4 Intelligence — Product): Analyzes problem-oriented prompts,
defines success criteria, proposes minimal viable feature set, outputs structured
product brief with user stories and acceptance criteria. Does NOT design systems
or write code. Launched via `Agent(subagent_type="vsm_product")`.

**`vsm_architect`** (S4 Intelligence — Technical): Reads codebase, researches tech, produces
 design documents ONLY (never code). Validates against S5 policy. Uses product
brief (if present) as input. Launched via `Agent(subagent_type="vsm_architect")`.

**`vsm_auditor`** (S3* Audit): Reads EVERY source file. Produces
PASS/ISSUES/BLOCKER per file. Writes audit reports to `.kimi/foundation-audit.md`
and `.kimi/implementation-audit.md` — never modifies source code. Checks correctness,
security, performance, maintainability. Includes full cross-file checklist.
Launched via `Agent(subagent_type="vsm_auditor")`.

**`vsm_coordinator`** (S2 Coordination): Compares S1 outputs, validates imports,
interfaces, naming, type alignment. Checks WebSocket contracts, GraphQL SDL,
[ORM/Query builder] relations, env vars. Writes integration findings to
`.kimi/integration-contract.md` — never modifies source code. May run shell commands
for import verification. Launched via `Agent(subagent_type="vsm_coordinator")`.

**`vsm_synthesizer`** (S2 Synthesis): Reads 1–5 raw audit/test/security/integration
reports and produces a single executive summary (≤50 lines). Preserves S5 context
by condensing multi-report findings into a structured verdict. Writes to
`.kimi/synthesis-[scope].md`. Every report MUST begin with an Executive Summary
so the synthesizer (and S5) can read only the critical top section.
Launched via `Agent(subagent_type="vsm_synthesizer")`.

**`vsm_wiring`** (S2 Wiring): Runs after Phase 3. Exclusively owns `entry point file`,
`realtime.py`, `root component file`, and `main.tsx`. Verifies all routers, providers,
middleware, and server instances are wired correctly. No other agent may modify
these files. Launched via `Agent(subagent_type="vsm_wiring")`.

**`vsm_backend_coder`** (S1 Backend Implementation): Writes Python backend code
with embedded domain knowledge of [backend framework], [ORM], [GraphQL library], [task queue],
and security gotchas. Replaces generic `coder` for all backend waves. Performs
runtime framework API verification, subprocess import checks, and test validation.
Launched via `Agent(subagent_type="vsm_backend_coder")`.

**`vsm_frontend_coder`** (S1 Frontend Implementation): Writes [frontend framework]
frontend code with embedded domain knowledge of [build tool], [API client], [state library],
[GraphQL library] auto-camelCase, and path aliases. Replaces generic `coder` for all
frontend waves. Verifies schema introspection before writing GraphQL queries and
runs `run frontend build` before completion. Launched via `Agent(subagent_type="vsm_frontend_coder")`.

**`vsm_backend_fix_agent`** (S1 Backend Fix): Surgical fixes to backend BLOCKERs.
Inherits all backend gotchas. Adds fix-specific rules: full test suite after every
fix, subprocess import check after cross-module changes, auth-weakening guard,
rate-limit/CORS/security freeze, GraphQL auth parity, and mandatory `.kimi/re-audit-report.md`.
Launched via `Agent(subagent_type="vsm_backend_fix_agent")`.

**`vsm_frontend_fix_agent`** (S1 Frontend Fix): Surgical fixes to frontend BLOCKERs.
Inherits all frontend gotchas. Adds fix-specific rules: `run frontend build` after every
fix, `run type checker` check, no `as any` bypasses, export verification, [API client]
consistency, and mandatory `.kimi/re-audit-report.md`. Launched via `Agent(subagent_type="vsm_frontend_fix_agent")`.

**`vsm_devops_coder`** (S1 DevOps Implementation): Writes Docker, docker-compose,
CI/CD, and infrastructure configs with embedded domain knowledge of containerization
gotchas. Replaces generic `coder` for all infrastructure waves. Verifies Dockerfile
CMD files exist, docker-compose has no `:-` fallbacks, ports match across configs,
and `.dockerignore` excludes secrets. Launched via `Agent(subagent_type="vsm_devops_coder")`.

**`vsm_security`** (Security Audit): Runs 15+ point security checklist.
Writes findings to `.kimi/security-report.md` — never modifies source code.
Prevents, not detects — knows all anti-patterns.
Launched via `Agent(subagent_type="vsm_security")`.

**`vsm_backend_tester`** (S1 Quality — Backend): Writes and runs backend tests
(framework test runner), validates fixtures, verifies API contracts. Does NOT test frontend.
Launched via `Agent(subagent_type="vsm_backend_tester")`.

**`vsm_frontend_tester`** (S1 Quality — Frontend): Writes and runs frontend tests
(framework test runner), validates TypeScript compilation, verifies component rendering. Does NOT
test backend. Launched via `Agent(subagent_type="vsm_frontend_tester")`.

**`vsm_explore`** (S4 Exploration): Fast read-only codebase exploration.
Maps directory structure, searches patterns, reads files, summarizes findings.
Primarily read-only; for investigations covering >5 files or >200 lines of
findings, MAY write `.kimi/explore-findings.md`. Never modifies source code.
Replaces the built-in `explore` subagent type. Launched via
`Agent(subagent_type="vsm_explore")`.

**`vsm_meta`** (S5 Meta — Evaluation): Evaluates the skill's own performance after a
build. Reads build artifacts, runs independent test verification, scores agent
effectiveness, audits prevention rules, and generates falsifiable hypotheses.
Does NOT write code or design systems. Produces `.kimi/meta-report.md`. Launched via `Agent(subagent_type="vsm_meta")`.

**`vsm_trainer`** (S3* Evaluator — Fitness Trainer): Part of the `vsm-fitness-coach`
ecosystem. Designs comprehensive fitness builds (substantial projects) that exercise
every capability of the main VSM skill, scores performance against a rubric,
identifies systemic weaknesses, and proposes mutations. Not spawned during normal
build flows — invoked via `/flow:vsm-fitness-coach` for skill training cycles.

**`vsm_experiment_designer`** (S4 Designer — Experiment Designer): Part of the
`vsm-fitness-gym` ecosystem. Designs and runs minimal reproducible experiments to
test hypotheses about the main skill's knowledge gaps. Reads the hypothesis backlog,
builds tiny test projects, runs relevant audit/security phases, records results,
and proposes mutations. Not spawned during normal build flows — invoked via
`/flow:vsm-fitness-gym` for scientific research cycles.

### Agent Output Types

**Writes implementation code:**
- `vsm_devops_coder` (custom) — Docker, docker-compose, CI/CD, infrastructure
**Writes design/requirements documents:**
- `vsm_product` (custom) — product briefs, user stories, acceptance criteria
- `vsm_architect` (custom) — architecture docs, API specs

**Writes evaluation reports (never modifies source code):**
- `vsm_auditor` (custom) — correctness audit per file, `.kimi/*-audit.md`
- `vsm_coordinator` (custom) — cross-file contract validation, `.kimi/integration-contract.md`
- `vsm_security` (custom) — security audit, `.kimi/security-report.md`
- `vsm_meta` (custom) — performance evaluation, `.kimi/meta-report.md`
- `vsm_explore` (custom) — read-only exploration, optionally `.kimi/explore-findings.md`

### 4.1 Agent Architecture

All 15 leaf agents inherit from a shared base via a **two-level hierarchy**:

**YAML inheritance** (`extend` field): The CLI recursively resolves `extend` by
overwriting (not appending). Child YAMLs must declare their complete tool lists.

**Markdown inheritance** (`{% include %}`): Jinja2 `FileSystemLoader` resolves
chained includes. Only `vsm-main.md` contains legitimate `${...}` template
variables. All other `.md` files MUST escape shell variables with `{% raw %}`.

```
vsm-main
├── vsm-coder → backend-coder, frontend-coder, devops-coder, wiring
│   ├── vsm-fixer → backend-fixer, frontend-fixer
│   └── vsm-tester → backend-tester, frontend-tester
├── vsm-researcher → architect, product, explore
└── vsm-reporter → auditor, security, coordinator, meta
```

**Validator**: Run `python3 validate-agent-files.py` from `agents/` before committing
agent changes. It checks YAML parse, system_prompt_path existence, `${...}`
variable resolution, Jinja2 include resolution, and unescaped shell-variable
patterns (`${VAR:-default}`).

## 5. The Golden Rule of Parallelism

```
Independent subagents -> run_in_background=true (parallel, up to configured limit in `background.max_running_tasks`)
Dependent subagents   -> sequential (TaskOutput block=true before next)
```

## 6. Executable Flow Diagram

See `references/flow-diagram.md` for the full diagram. Summary:

```
BEGIN → Phase 0 (Viability) → Phase 1 (Intelligence) → Phase 2 (Foundation)
  → Phase 2b (Audit) → Phase 3 (Implementation) → Phase 3b (Audit+Coord)
  → Phase 4 (Testing) → Phase 5 (Security) → Phase 6 (Integration)
  → Phase 7 (Fix, conditional) → Phase 8 (Reflection + Meta + Mutations) → END
```

Diamond nodes: `<choice>branch</choice>` selects path. BLOCKERs at any gate
trigger Phase 7 (max 3 iterations), then loop back to the originating phase.

## 7. Phase Details

### Phase 0: Viability Check + Self-Test
Main agent (S5) performs:
1. **Viability check**: trivial (<50 lines, one file)? If yes, respond directly.
2. **Classify prompt**: Prescriptive ("Build X with Y") or problem-oriented
   ("Users need Z")? If problem-oriented, spawn `vsm_product` subagent to
   produce a product brief with user stories and acceptance criteria.
3. **Read project memory**: `.kimi/lessons.md` if exists.
4. **Read acquired wisdom**: `${KIMI_SKILL_DIR}/references/acquired-wisdom.md`
   if exists.
5. **Read hypotheses**: `${KIMI_SKILL_DIR}/references/hypotheses.md`
6. **Read meta-reflection**: `${KIMI_SKILL_DIR}/references/meta-reflection.md`
   if exists.
   if exists. Note any untested hypotheses that are relevant to this project.
6. **Self-test**: Verify all referenced files exist and are readable. Verify
the flow diagram parses. Verify the skill can describe its own phase sequence
without contradiction. Specifically verify these custom agent definition files exist:
`vsm-main.yaml`, `vsm_architect.yaml`, `vsm_product.yaml`, `vsm_auditor.yaml`,
`vsm_coordinator.yaml`, `vsm_wiring.yaml`, `vsm_backend_coder.yaml`,
`vsm_frontend_coder.yaml`, `vsm_backend_fix_agent.yaml`, `vsm_frontend_fix_agent.yaml`,
`vsm_devops_coder.yaml`, `vsm_security.yaml`, `vsm_backend_tester.yaml`,
`vsm_frontend_tester.yaml`, `vsm_meta.yaml`, `vsm_explore.yaml`.
If any check fails → emit algedonic, write diagnosis
to `${KIMI_SKILL_DIR}/references/mutation-log.md`, ask user to review.
6b. **Agent-File Verification**: Spawn a trivial `vsm_meta` subagent with the task
`"Reply 'ok'"`. If this fails with an unknown subagent type error, **STOP immediately**.
Emit algedonic: `--agent-file not loaded. Launch with: kimi --agent-file ~/vsm/viable-swarm-model/agents/vsm-main.yaml`.
Do not proceed with the build.
6a. **Environment Compatibility Smoke Test** (conditional): If the build declares
framework dependencies (e.g., `[graphql library]`, `[validation library]`, `[orm library]`, `[backend framework]`,
`celery`), run a quick import verification in a fresh subprocess BEFORE dispatching
implementation agents:
```bash
verify imports using language-specific method for declared dependencies
```
If ANY import fails, STOP the build immediately. Report the environment
incompatibility, do NOT dispatch agents that cannot runtime-verify their code,
and ask the user to resolve the dependency conflict. Writing code that cannot be
imported wastes agent capacity and produces unverifiable artifacts.
**Source**: FB22 `strawberry-graphql==0.256.0` failed to import with installed
pydantic; the API layer file agent consumed ~15 minutes before S5 intervened (H152).
7. **Read runtime capacity**: Read `~/.kimi-code/config.toml` and extract
   `background.max_running_tasks` (default 4 if absent). Log this value in
   `plan.md` as the parallel agent ceiling. NEVER exceed this limit when
   spawning background subagents.
8. **Variety Assessment** (Ashby's Law): Estimate project complexity and classify tier.
   Use the `max_running_tasks` value read in step 7 as the agent ceiling.
   Do not invent artificial sub-limits — if the host allows 8, use up to 8.
   - **Tier 1** (<1000 lines, 1-2 services): Standard flow, no mid-wave gates needed
   - **Tier 2** (1000-3000 lines, 2-3 services): Add Phase 3c mid-wave S2 check,
     use background spawning for long-running agents (security, meta)
   - **Tier 3** (3000+ lines, 3+ services): Split into sub-builds OR accept that
     single-session coverage will be partial. Do not pretend the metasystem has
     requisite variety it lacks.
   Log the tier and the agent ceiling in `plan.md`.

**Agent Timeout Policy: No Arbitrary Limits**
Do NOT set explicit timeouts on foreground agents. The platform default is
**no timeout** (run until completion, max 1hr platform hard cap). Deep audits,
security scans, and meta-evaluations legitimately need time — killing them
early loses findings and wastes agent capacity.

For **background agents**, the CLI config typically imposes a default timeout
(commonly 15min). If a background task is expected to exceed this
(`vsm_auditor`, `vsm_security`, `vsm_meta` on large codebases), explicitly
set `timeout=3600` on the `Agent()` call.

**5-Minute Progress Check Rule** (the only anti-hang guardrail):
If ANY agent has not returned after 5 minutes, S5 MUST inspect its `output.log`
(via `TaskOutput` or `ReadFile`) before assuming it is stuck. If the agent is
making progress, let it continue. If it is looping or hung, stop it with
`TaskStop` and re-spawn.
9. Write `plan.md`.

### Phase 0: Stack Detection & Skill Verification

Before starting any build:
1. Detect the stack (user-specified, auto-detected from manifest files, or asked)
2. Verify `~/vsm/vsm-stack-skills/SKILL-REGISTRY.md` exists
3. Verify relevant `[language]-pitfalls` and `*-patterns` skills exist
4. Run `python ~/vsm/vsm-stack-skills/validate-skills.py`

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
Spawn parallel `vsm_backend_coder` and `vsm_frontend_coder` subagents with `run_in_background=true` for:
- `data models file` (including engine + session factory like `AsyncSessionLocal`)
- `auth layer file` + `roles.py` (stable signatures: `get_current_user`, `require_role`)
- `config.py` (lazy factory, NO default secrets)
- `shared/types.ts` + `shared/sio-events.ts`
- `requirements.txt`, `package.json`
- `.env.example` (env var naming contract established HERE)

Wait via `TaskOutput(block=true)`. Then S5 runs a **mini-audit**:
- Does `data models file` define `AsyncSessionLocal`?
- Does `auth layer file` have stable `get_current_user` / `require_role` signatures?
- Are `.env.example` names finalized and consistent?
- Do all 2a files compile/import cleanly?

If any check fails → fix BEFORE dispatching Sub-Wave 2b.

**Sub-Wave 2b — Dependent Infrastructure (parallel, then verify)**:
Spawn parallel `vsm_backend_coder` and `vsm_frontend_coder` subagents with `run_in_background=true` for:
- `routers/auth layer file` (MUST include `POST /login`, `POST /register`, `GET /me` endpoints)
- `API layer file` (imports from models, auth)
- `sio.py` (imports from models, auth)
- `entry point file` scaffolding (imports from config, registers middleware)
- Frontend scaffolding ([build tool] config, root component file skeleton, path aliases)
- `docker-compose.yml`

Wait via `TaskOutput(block=true)`.

**Phase 2b: Audit** — Spawn `vsm_auditor` on ALL foundation outputs (2a + 2b).
BLOCKERs trigger Phase 7.

**Phase 2c: Model + Auth Validation (S5)** — After foundation audit passes and BEFORE
spawning implementation agents, S5 MUST verify:
1. **`data models file` field parity**: `data models file` (or equivalent) matches `data-model.md`
   field names and types exactly.
2. **Auth role parity**: `auth layer file` `ALLOWED_ROLES` (or equivalent role-based access
   control list) matches the `Role` / `UserRole` enum in `data-model.md` exactly.
   Every role in the allowlist must exist in the enum; every user-facing enum value
   should be representable in the allowlist.

If EITHER check fails, treat as a BLOCKER: send back to foundation agents for
correction. Model mismatches cascade to GraphQL, frontend queries, and shared types.
Auth role mismatches cascade to registration, JWT claims, and frontend role guards.
Both must be correct before Phase 3 begins.

### Phase 3: Implementation Wave
Pass Wave 1 outputs as input references. Spawn parallel `vsm_backend_coder` and `vsm_frontend_coder` subagents.
Entry point wiring MANDATORY after this wave. Audit + coordination check.
BLOCKERs trigger Phase 7.

**Frontend Implementation Sub-Wave 3a — Shared Files (sequential, BEFORE pages)**:
For frontend builds, a **single shared-files agent** runs FIRST and exclusively
owns these files:
- `src/graphql/queries.ts` — all queries, mutations, subscriptions
- `src/graphql/client.ts` — [API client] split link configuration
- `src/shared/types.ts` — domain types and enums
- `src/shared/sio-events.ts` — WebSocket event constants
- `src/stores/*.ts` — all [state library] stores

No other frontend agent may modify these files. The shared-files agent reads
`data-model.md` and `api-spec.md` to produce complete, correct exports.

**Sub-Wave Sequencing Enforcement (MANDATORY)**:
S5 MUST spawn the shared-files agent for Sub-Wave 3a, wait via `TaskOutput(block=true)`
for it to complete, verify the shared files exist and contain valid exports, THEN
spawn Sub-Wave 3b page agents. Parallelizing shared-files and page agents causes
race conditions where page agents overwrite shared file contents or write conflicting
queries. The flow diagram shows Phase 3 as parallel for backend routers only; frontend
shared files and pages are SEQUENTIAL.

**Frontend Implementation Sub-Wave 3b — Pages & Components (parallel)**:
After shared files are complete and verified (via `TaskOutput(block=true)` on the
shared-files agent), spawn parallel `vsm_frontend_coder` subagents for pages and
components. These agents IMPORT from shared files; they never write to them. If a
page agent needs a new query, it documents the requirement and the shared-files agent
adds it.

**Backend Implementation (parallel routers)**:
Backend routers (`app/routers/*.py`) can run in parallel safely because each
router is a separate file. The wiring agent (`vsm_wiring`) handles `entry point file`
registration exclusively.

**Phase 3c: Mid-Wave S2 Check (conditional)** — If project is Tier 2+ and 2+
parallel coder agents were spawned, spawn a lightweight `vsm_coordinator` check
on shared contracts after the first agents complete. Flag ONLY critical
drift that would block incomplete agents. If drift found → emit algedonic,
halt remaining agents, inject corrections.

### Phase 3d: Entry-Point Wiring (MANDATORY)
After all implementation agents complete, spawn `vsm_wiring` subagent.
This agent exclusively owns `entry point file`, `realtime.py`, `root component file`, and `main.tsx`.
It verifies:
- All routers registered in `entry point file`
- GraphQLRouter mounted with `context_getter=get_context`
- `realtime.py` reuses `sio` from `app.sio` (never creates new AsyncServer)
- `main.tsx` wraps app in `[API client]Provider`
- `root component file` includes all routes with role guards
- No module-level `get_settings()` calls in wiring files

No implementation agent may modify these four files. The wiring agent is the
sole owner. BLOCKERs here trigger Phase 7.

### Phase 3e: Frontend Config Validation
After entry point wiring and BEFORE the testing wave, S5 MUST perform a
lightweight frontend config validation check:

1. Read `src/graphql/client.ts` and `src/sio/client.ts`
2. Verify NO `||` fallbacks for API/WS/GraphQL URLs
3. Verify NO `localhost` hardcoded as fallback in frontend config
4. Verify `build config file` proxy includes `/api`, `/graphql`, `/ws`
5. Verify `tsconfig.json` includes all files that `run type checker` will type-check

ANY failure → back to Phase 3 (frontend implementation agent fixes).

This prevents frontend configuration bugs from surviving to the security gate,
where they are currently discovered too late.

### Phase 3f: Frontend Cross-File Import Check
After all parallel frontend implementation agents complete and BEFORE spawning
the auditor, S5 MUST run a lightweight cross-file import verification:

1. Run `run frontend build` (not just the build command) to verify the full frontend build
   pipeline including TypeScript compilation. Then run `npx run type checker` to verify
   every import statement in `src/pages/` and `src/components/` resolves
2. Verify every export from `src/graphql/queries.ts` is imported by at least
   one page or component
3. Verify every field destructured from [state library] stores exists in the store
4. Verify every type imported from `shared/types.ts` is defined in that file

ANY failure → back to Phase 3 (frontend implementation agent fixes).

This prevents frontend contract mismatches (missing exports, missing store fields)
from reaching the auditor, where they currently consume auditor capacity on
trivial integration issues.

### Phase 4: Testing & Infra Wave

**Tier 1 builds** (< 1000 lines, 1-2 services):
Spawn the relevant testers (`vsm_backend_tester` for backend, `vsm_frontend_tester`
for frontend) + `vsm_devops_coder` in parallel. If the project is full-stack,
spawn both testers + devops_coder. Run tests via Shell.

**Tier 2+ builds** (≥ 1000 lines, 2+ services):
Spawn `vsm_backend_tester` + `vsm_frontend_tester` + `vsm_devops_coder` in parallel
with `run_in_background=true`. Both testers run simultaneously:
- `vsm_backend_tester`: framework test runner, database fixtures, API integration, [task queue] mocks
- `vsm_frontend_tester`: framework test runner, component rendering, TypeScript compilation, build verification

Wait via `TaskOutput(block=true)` for ALL testers to complete, then aggregate
results. If either tester times out, treat as a BLOCKER: the build surface
exceeds single-agent capacity and must be further subdivided or scoped down.

**Phase 4 Exit Gate (HARD BLOCK)**
Before proceeding to Phase 5, verify:
1. Test suite reports **zero failures** (backend)
2. `run frontend tests` / `run frontend tests` reports **zero failures** (frontend)
3. `run frontend build` / `run type checker` reports **zero errors** (frontend)
4. **Frontend production build**: `npm run build` (or equivalent) MUST succeed with zero errors. TypeScript compilation (`tsc -b`) and the bundler (Vite/Webpack) must both pass. This is a HARD BLOCK — build failures must not leak to Phase 6.
5. **Backend subprocess import check**: `verify imports using language-specific method "import app.main; import app.graphql; import app.sio; import app.tasks"` must succeed with zero errors. A NameError or ImportError at module level is a HARD BLOCK even if tests somehow pass. This catches module-level side effects (e.g., `settings = Settings()`, `engine = create_async_engine(...)`) that break imports but may not surface during test discovery.

If ANY of the above report failures, **STOP**. Do not proceed to Phase 5 (Security Gate)
or Phase 6 (Integration). Route to Phase 7 (Fix Wave). Fixing downstream integration
BLOCKERs on top of failing tests is waste. The Phase 4 exit gate is mandatory —
never treat test failures as "acceptable for now."

**Agent Report Artifacts (MANDATORY)**
All audit/security/coordinator agents now have `WriteFile` restricted to their own
report artifacts. They MUST write their reports to the `.kimi/` subdirectory in
the build directory. S5 MUST verify the report files exist before proceeding.
Name convention:
- Auditor → `.kimi/foundation-audit.md` or `.kimi/implementation-audit.md`
- Security → `.kimi/security-report.md`
- Coordinator → `.kimi/integration-contract.md`
- Backend Fix Agent → `.kimi/re-audit-report.md`
- Frontend Fix Agent → `.kimi/re-audit-report.md`
- Meta → `.kimi/meta-report.md`
- Explore (optional) → `.kimi/explore-findings.md`

If an agent fails to produce its report artifact, S5 MUST prompt it to write the
report using `WriteFile`. Failure to produce report files causes the meta-evaluator
to score agents as N/A and loses skill-effectiveness evidence.

**`.kimi/` Directory Convention**
Every build directory contains a `.kimi/` subdirectory for ephemeral agent-generated
artifacts. This separates metadata from source code:

| Location | Purpose |
|---|---|
| **Build root** | Source code, configs, design docs (`plan.md`, `architecture.md`, `docker-compose.yml`) |
| **`.kimi/`** | Agent reports, evaluations, mutation tracking (`lessons.md`, `meta-report.md`, `mutations-applied.md`, `re-audit-report.md`, `security-report.md`, `integration-contract.md`, `explore-findings.md`) |
| **`references/`** | Persistent skill knowledge (`acquired-wisdom.md`, `hypotheses.md`, `pattern-library.md`, `mutation-log.md`) |

Agents with `WriteFile` MUST restrict usage to their own `.kimi/` artifact or
`references/` append operations. They MUST NEVER modify source code or build
configs with `WriteFile`.

**Agent Notification Truncation Handling (MANDATORY)**
Agent completion notifications may truncate at ~500 characters. S5 MUST NOT act
on a partial summary. After every agent returns:
1. Check if the notification contains a clear PASS/FAIL/BLOCKER verdict and
   artifact file paths.
2. If truncated, vague, or missing artifact confirmation, `ReadFile` the agent's
   `output.log` immediately before proceeding.
3. Never route to the next phase based on an incomplete agent summary.

Report combined coverage.

### Phase 5: Security Gate

**Step 5a: Automated Scan (vsm_security)**
Spawn `vsm_security`. It writes findings to `.kimi/security-report.md`.
Read only the "Executive Summary" section (first 20 lines). If the report
exceeds 50 lines, spawn `vsm_synthesizer` with the report path and read
`.kimi/synthesis-security.md` instead.
CRITICAL/HIGH → stop, fix, re-audit. LOW → document.
Gather vs. Stop: planned wave → gather; mid-build → emergency stop.

**Tier 2+ builds (≥ 1000 lines, 2+ services)**: `vsm_security` is MANDATORY.
If `vsm_security` fails to spawn, errors out, or produces no report, treat this
as a BLOCKER. Do NOT proceed to Step 5b as a replacement. Investigate the agent
failure, fix the underlying issue, and re-spawn `vsm_security`. Manual fallback
alone has empirically missed findings that `vsm_security` caught (e.g., DTO
sensitive-field exposure, overly broad exception handling). For Tier 2+, the
automated scan AND the manual checklist are BOTH required.

**Tier 1 builds (< 1000 lines)**: If `vsm_security` fails to spawn or errors,
S5 may proceed to Step 5b manual checklist, but MUST log the agent failure in
`plan.md` as a known limitation.

**Step 5b: Mandatory Manual Fallback Checklist (S5)**
For ALL tiers, regardless of `vsm_security` results, S5 MUST run this manual
checklist. A single agent failure must never bypass security.

Manual checklist (verify by reading source, not trusting agent report):
1. **Hardcoded secrets**: grep for `SECRET`, `KEY`, `PASSWORD`, `TOKEN` with `=` or `:` assignment. No `||` fallbacks.
2. **JWT handling**: Verify `jwt.decode` uses proper signature verification. No `verify_signature=False`.
3. **Auth middleware**: Verify `get_current_user` raises 401 on ALL failure paths. Never returns `None`.
4. **CORS**: Verify explicit allowlist. No `*` or `origin: true` with credentials.
5. **Ownership filtering**: Verify ALL list endpoints filter by authenticated user.
6. **GraphQL security**: Verify `QueryDepthLimiter` in schema extensions (if GraphQL enabled).
7. **Password hashing**: Verify bcrypt. No plaintext/MD5/SHA1.
8. **WebSocket auth**: Verify in-band auth. No JWT in URL query params.
9. **docker-compose fallbacks**: Verify NO `:-` syntax for secrets.

If the manual checklist finds CRITICAL/HIGH issues that `vsm_security` missed
or could not report, treat them exactly as automated findings: stop, fix, re-audit.

**Security gate runs BEFORE integration verification** so that vulnerabilities
are caught before the coordinator invests effort in cross-file contract checks.
This reduces total fix iterations.

### Phase 6: Integration Verification

**Tier 1 builds** (< 1000 lines, 1-2 services):
Spawn `vsm_auditor`. `vsm_coordinator` is optional; S5 may run the integration
checklist manually if the build surface is small.

**Tier 2+ builds** (≥ 1000 lines, 2+ services):
`vsm_coordinator` is MANDATORY. Spawn `vsm_coordinator` + `vsm_auditor` in
parallel with `run_in_background=true`. After both complete, spawn
`vsm_synthesizer` with both report paths to produce `.kimi/synthesis-integration.md`.
S5 reads only the synthesis, not the raw reports.
If `vsm_coordinator` fails to spawn, errors out, or produces no report, treat
this as a BLOCKER. Do NOT proceed with manual integration checks as a replacement.

Full 20+ point checklist (see `references/integration-checklist.md`).
ANY failure → back to Phase 3.

> **Algedonic signal — Phase 6/7 Boundary**: If integration verification finds
> BLOCKERs, do NOT fix them inline. Route to Phase 7 (Fix Wave). Inline fixes
> bypass re-audit and post-fix security re-check, violating exit criteria. S5
> MUST spawn domain-specific fix agents (`vsm_backend_fix_agent`,
`vsm_frontend_fix_agent`, `vsm_devops_coder` for infra) for fixes, produce a `.kimi/re-audit-report.md`
> artifact, and run Phase 7c post-fix security re-check before returning to
> the main flow.

### Phase 7: Fix Wave (conditional)
Group fixes by domain (backend vs frontend). Parallel across files, sequential
within file. Spawn `vsm_backend_fix_agent` for backend BLOCKERs and
`vsm_frontend_fix_agent` for frontend BLOCKERs. If fixes span both domains,
spawn both agents in parallel with `run_in_background=true`.

**Phase 7a — Fix Execution**: Fix agents apply surgical changes and produce
`.kimi/re-audit-report.md` (advisory only).

**Phase 7b — Binding Re-Audit + Full Test Suite (MANDATORY)**: S5 MUST spawn
`vsm_auditor` to independently verify ALL modified files. Fix agent self-reports
are **not** sufficient — the auditor's PASS/ISSUES/BLOCKER verdict is binding.
Then run `run backend tests` and `run frontend tests` / `run frontend tests`. Re-auditing changed
files alone misses regressions in unrelated tests. Any remaining BLOCKERs route
back to Phase 7a. Max 3 iterations across 7a→7b. Still blocked? Escalate to user.

**Phase 7c — Post-Fix Security Re-Check (MANDATORY)**: After fix wave clears
all BLOCKERs and BEFORE returning to the main flow, S5 MUST spawn `vsm_security`
with a focused scope (modified files only) to run a lightweight security re-check
on any file that touches auth, GraphQL, or WebSocket code. If the re-check finds
CRITICAL/HIGH regressions (e.g., a fix agent weakened auth), loop back to Phase 7a.
This prevents fix/test agents from introducing vulnerabilities after the main
security gate.

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
- Lessons are per-build; skill-level meta-reflection lives in
  `references/meta-reflection.md` (see Phase 8d)

**Minimum entries**: At least one entry for each phase that scored < 4 or produced a BLOCKER.

**Phase 8 Hard Gate — MANDATORY**: Before proceeding to Phase 8b, S5 MUST verify:
1. `.kimi/lessons.md` exists in the build directory.
2. It contains at least one structured entry with Source, Finding, Fix, Verification,
   and Prevention rule.
If EITHER check fails, Phase 8 is NOT complete. Re-spawn the relevant agents or
write the missing entries before proceeding to `vsm_meta`.

See `references/lessons-template.md` for the full template.

### Phase 8b: Meta-Reflection + Hypothesis Generation
After project reflection, spawn `vsm_meta` subagent to evaluate the skill's own
performance. This agent produces a standalone `.kimi/meta-report.md` with independent
test verification, agent performance scores, rule effectiveness ratings, and
process bottleneck analysis.

**Step 8b-1: Spawn `vsm_meta` (MANDATORY — HARD BLOCK)**
S5 MUST spawn `vsm_meta` before proceeding. `vsm_meta` produces the per-build
`.kimi/meta-report.md`. S5 then synthesizes cross-build insights and appends them to
`~/vsm/viable-swarm-model/references/meta-reflection.md`.

**Step 8b-2: Verify `.kimi/meta-report.md` exists and is valid**
Before declaring Phase 8b complete, verify ALL of the following:
1. `.kimi/meta-report.md` exists in the build directory.
2. It was produced by `vsm_meta`, not written by S5. (Check for "Agent Performance Scores" table — S5 typically omits this structured section.)
3. It contains a **Phase Audit** section with process violation analysis.
4. It contains **Hypotheses Generated** with at least one falsifiable hypothesis.
5. `.kimi/mutations-applied.md` exists in the build directory with a complete
   mutation tracking table (per Phase 8c). If missing, Phase 8b is NOT complete.

If any check fails, Phase 8b is NOT complete. Re-spawn `vsm_meta` with explicit
instructions to include the missing sections.

> **Algedonic signal**: If S5 is about to write `.kimi/meta-report.md` manually,
> STOP immediately. This is a process violation. The builder cannot evaluate
> itself. Spawn `vsm_meta`. S5 MAY synthesize and append to the skill-level
> `references/meta-reflection.md` after reading the meta-report.

### Phase 8c: Skill Improvement (Conditional)

If this build discovered new empirical pitfalls or validated new patterns:
1. Append the finding to the relevant skill in `~/vsm/vsm-stack-skills/`
2. Include build ID attribution
3. If new skill needed, create it and update registry
4. `git commit` skill changes

### Phase 8c: Mutation Verification Checkpoint (MANDATORY)
Before declaring Phase 8 complete, S5 MUST run the Mutation Verification
Checkpoint. This prevents the recurring failure mode where mutations are
proposed in `.kimi/meta-report.md` but never applied.

**Step 8c-1: Produce `.kimi/mutations-applied.md`**
Create a tracking artifact in the `.kimi/` subdirectory (`mutations-applied.md`)
with this table:

```markdown
| # | Mutation | Tier | Proposed By | Status | Evidence |
|---|----------|------|-------------|--------|----------|
```

**Step 8c-2: Cross-check against `.kimi/meta-report.md`**
For every mutation proposed by `vsm_meta`, confirm one of:
- **Applied**: File was modified; git diff shows the change
- **Deferred**: Intentionally postponed with rationale logged
- **Rejected**: Intentionally rejected with rationale logged
- **Overlooked**: Unintentionally missed — STOP, apply now

**Step 8c-3: Process-level gap check**
If `vsm_meta` identified a process-level gap (e.g., "mutation tracking missing",
"agent miscategorizes structural as append-only"), verify that the gap itself
was addressed, not just the symptoms.

**Step 8c-4: Hard block**
If ANY mutation status is `overlooked`, Phase 8b is NOT complete. Apply the
missed mutation, update the table, and re-verify. Only then proceed to git commit.

The main agent (S5) reads the `.kimi/meta-report.md` **Executive Summary**
section only (first 20 lines). If the report exceeds 100 lines, spawn
`vsm_synthesizer` with the meta-report path and read `.kimi/synthesis-meta.md`
instead.

**Independent verification requirement**: Before accepting `.kimi/meta-report.md`,
S5 MUST independently run the full test suite (`run backend tests` and `run frontend tests` /
`run frontend tests`) and record the ACTUAL pass/fail counts. Do NOT repeat claims from
upstream phases without verification. If tests fail, the meta-reflection must
acknowledge the failure and propose a root-cause hypothesis.

### Phase 8d: Build Completion Rules (MANDATORY)

Before declaring the VSM workflow "complete," S5 MUST verify:

1. **`.kimi/lessons.md` exists**: A standalone lessons file MUST be written to
   the build directory during Phase 8. If missing, Phase 8 is NOT complete.

2. **Agent skill-read evidence is visible**: For every agent spawned in this
   build, verify its output artifact or completion response contains a "Skills
   read" list. If an agent's skill usage is not visible (truncated notification,
   no artifact, missing skills list), S5 MUST query the agent or read its
   `output.log` to obtain this evidence before declaring completion.

3. **No unfixed HIGH/MEDIUM findings**: If the Security Gate (Phase 5) or
   Integration Verification (Phase 6) produced HIGH or MEDIUM findings, they
   must be fixed or explicitly escalated to the user with written rationale.
   Documenting them as "known limitations" and declaring completion is a
   process violation. LOW findings may be documented.

4. **Parent flow handoff (conditional)**: If this VSM workflow was invoked BY A
   PARENT FLOW (e.g., `/flow:vsm-fitness-coach`), Phase 8 completion does NOT
   mean the parent session is over. S5 MUST return control to the parent flow
   for its post-build phases. When VSM is run standalone (`/flow:viable-swarm-model`),
   this rule does not apply — Phase 8d is complete once rules 1-3 are satisfied.

> **Algedonic signal**: If you find yourself about to say "all phases complete"
> while HIGH/MEDIUM findings remain unfixed, STOP immediately. The build is NOT
> complete. If a parent flow invoked this build, also verify the parent flow has
> finished its remaining phases.

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
   `${KIMI_SKILL_DIR}/references/hypotheses.md` with:
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

## 8. Cross-File Integration Verification Checklist

Run ALL checks from `references/integration-checklist.md`. Summary:

1. Every export imported by a consumer; no orphaned code
2. Shared contracts consistent across files
3. Entry points register all middleware
4. Codebase compiles/builds
5. WebSocket: every backend emit has matching frontend listener
6. GraphQL SDL matches TypeScript; subscriptions have resolvers
7. Frontend paths correct; [build tool] proxy includes `/api`, `/graphql`, `/ws`
8. [vector database]: extension enabled, dimensions match, ivfflat index exists
9. [server-sent events]: `media_type="text/event-stream"`, yields `data: {json}\n\n`
10. CRDT: PersistenceAdapter connected, BYTEA column, chronological load
11. DAG: `validate()` on mutate, 3-color DFS, topological sort
12. [cache/store]: queue names consistent, dependent enqueue, pub/sub match
13. Frontend scaffolding: package.json, build config file, tsconfig.json, index.html, main.tsx, root component file
14. Rust: workspace includes all crates, no duplicate imports
15. Go: camelCase JSON tags, no snake_case leakage
16. Docker Compose: all CMD/ENTRYPOINT files exist

**Rule**: ANY failure → send back to responsible S1 BEFORE quality gates.

## 9. Security Gate Checklist

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
17. [server-sent events]: short-lived token exchange, never long-lived JWT in URL

## 10. Exit Criteria

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

## 11. The Mutation System

This skill is a learning organism. It modifies its own files between sessions.
All files in `${KIMI_SKILL_DIR}` are mutable.

### Why Mutation Is Safe

The skill directory is a **git repository**. Every mutation is committed.
If a mutation breaks viability, the user (or the skill itself) can revert:

```bash
cd ${KIMI_SKILL_DIR}
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
| `vsm-stack-skills/**/*.md` | Append-only: new pitfalls/patterns; Refinement: update skill text; Structural: new skill creation | Medium-High |
| `SKILL.md` flow diagram (inline) | Refine decision logic | High: phase audit shows mismatch |
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

## 12. Orchestration Guide

See `references/orchestration-guide.md` for:
- Comprehension Checkpoint (before declaring phase complete)
- Background Task Management (`TaskList`, `TaskOutput`, concurrency limits)
- Session Resumption for Learning (`--continue` workflow)
- Quick Decision Tree (trivial vs non-trivial work routing)
