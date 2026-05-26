---
name: vsm-fitness-coach
description: >
  The coaching layer of the viable-swarm-model ecosystem. Designs comprehensive
  fitness builds (substantial projects) that exercise every capability of the
  main skill, scores its performance against a rubric, identifies systemic
  weaknesses, and proposes mutations. This is the meta-coach that turns
  real builds into structured skill improvement. Invoke with
  /flow:vsm-fitness-coach.
type: flow
triggers:
  - "fitness build"
  - "test the skill"
  - "evaluate viable-swarm-model"
  - "stress test"
  - "skill workout"
---

## 1. Overview

The `vsm-fitness-coach` is the **coach** of the ecosystem. It does
not lift the weights — the athlete (`viable-swarm-model`) does. The coach's
job is to **design training programs**, **watch game tape**, and **identify
weaknesses the athlete cannot see in itself**.

The coach designs **comprehensive fitness builds** — substantial,
multi-service projects that deliberately exercise every phase, every agent
type, and every pattern in the athlete. After the build, it performs a
**structured post-mortem**: scores each phase against a rubric, identifies
systemic gaps, generates falsifiable hypotheses, and proposes mutations.

**Mental model**: If `vsm-fitness-coach` is the coach, then
`viable-swarm-model` is the athlete (does the real work) and
`vsm-fitness-gym` is the gym (isolated equipment for targeted workouts).

**Primary invocation**: `/flow:vsm-fitness-coach`
Must be embedded in a message (e.g., `Let's do a fitness build. /flow:vsm-fitness-coach Run FB2`).
**Example**: `/flow:vsm-fitness-coach Run fitness build #1 (DocuFlow)`

**Path convention**:
- Main skill: `~/vsm/viable-swarm-model/`
- Fitness builds: `~/vsm-fitness-builds/coach/[project-id]-[date]/`

If installed elsewhere (e.g. via `extra_skill_dirs`), use symlinks or update
paths in mutation commands.

**Build directory**: Every fitness build creates a dedicated, timestamped
directory. The athlete (`viable-swarm-model`) builds the project there — never
in the user's actual project directory.

## 2. How to Invoke

- **`/flow:vsm-fitness-coach [optional: domain hint or 'run next']`** —
  Execute a fitness build. The coach reads the coverage ledger, consumes a
  pre-generated prompt draft if available (from Phase 6 of the previous
  build), or synthesizes a new build design from scratch. Guides the main
  skill through execution, then evaluates performance. Must include some
  natural language text before or around the command for Kimi CLI to
  process it.
- **`/skill:vsm-fitness-coach`** — Load as knowledge reference. Use when
  you need the evaluation rubric or coverage ledger.

**Terminology**: `S5` refers to the main conversation agent (you, the LLM executing
this skill). The word `user` refers to the human operator. S5 may escalate to the
user via `AskUserQuestion` or `EnterPlanMode` when human policy input is required.

## 3. Fitness Coach Roles

| VSM System | CLI Implementation | Custom Type | Activation | Produces |
|---|---|---|---|---|
| **S5 (Policy)** | Main conversation agent (you) | — | Phase 0, Phase 4 | Build synthesis, mutation approval |
| **S4 (Selector)** | Main agent synthesizes build | — | Phase 0 | Build design, prompt draft |
| **S1 (Builder)** | `viable-swarm-model` workflow | Flow skill | Phase 1 | Substantial project |
| **S3* (Evaluator)** | `vsm_trainer` subagent | Custom | Phase 2 | Reads artifacts + rubric, scores phases, identifies gaps |
| **S2 (Synthesizer)** | Main agent | — | Phase 4 | Hypotheses, mutations |

## 4. The Golden Rule

The fitness coach does NOT build code directly. It delegates all
implementation to the main skill (`viable-swarm-model`). The coach's
value is in **selection, evaluation, and synthesis**.

## 5. Executable Flow Diagram

```mermaid
flowchart TD
    BEGIN([BEGIN])
    P0[Phase 0: Synthesize Next Build<br/>Read coverage ledger + skill state]
    P0E{<choice>FB[N+1]-prompt-draft.md<br/>exists from Phase 6?</choice>}
    P0S[Phase 0b: Synthesize Build Design<br/>Analyze gaps → select domain →<br/>draft build parameters]
    P1[Phase 1: Execute Build<br/>Run viable-swarm-model workflow<br/>Build from prompt draft]
    P1A[Collect all artifacts:<br/>plan.md, audit reports, security reports,<br/>integration report, test results, fix logs]
    P2[Phase 2: Evaluate Performance<br/>Spawn vsm_trainer<br/>Read artifacts + rubric<br/>Score each phase 1-5]
    P2H[Phase 2b: Update Hypothesis Statuses<br/>Read hypotheses.md → update tested items]
    P2S{<choice>any phase scored < 4</choice>?}
    P3[Phase 3: Generate Hypotheses<br/>One hypothesis per gap identified]
    P4[Phase 4: Propose Mutations<br/>Present structured report to S5]
    P4A{<choice>structural mutations<br/>approved by user</choice>?}
    P5[Phase 5: Apply Mutations<br/>Append-only: autonomous<br/>Structural: conditional]
    P5L[Log rejections to mutation-log.md]
    P5R[Write fitness report<br/>assets/fitness-report-template.md]
    P5G[git commit all changes]
    P5X{<choice>Structural Mutation Gate<br/>user asked about<br/>structural mutations?</choice>?}
    P6[Phase 6: Prepare Next Build Prompt<br/>Synthesize prompt from empirical results<br/>Write using assets/prompt-template.md]
    P6W[Write FB[N+1]-prompt-draft.md<br/>to ~/vsm-fitness-builds/coach/]
    END([END])

    BEGIN --> P0
    P0 --> P0E
    P0E -->|<choice>yes</choice>| P0D[Create build directory<br/>~/vsm-fitness-builds/coach/[id]-[date]/]
    P0E -->|<choice>no</choice>| P0S
    P0S --> P0D
    P0D --> P1
    P1 --> P1A
    P1A --> P2
    P2 --> P2H
    P2H --> P2S
    P2S -->|<choice>yes</choice>| P3
    P2S -->|<choice>no</choice>| P4
    P3 --> P4
    P4 --> P4A
    P4A -->|<choice>approved / none proposed</choice>| P5
    P4A -->|<choice>rejected / ambiguous</choice>| P5L
    P5 --> P5R
    P5L --> P5R
    P5R --> P5G
    P5G --> P5X
    P5X -->|<choice>no — gate not cleared</choice>| P5X
    P5X -->|<choice>yes — gate cleared</choice>| P6
    P6 --> P6W
    P6W --> END
```

## 6. Phase Details

### Phase 0: Synthesize Next Build

The fitness coach does not select from a menu. It **synthesizes** the next
experiment based on empirical state. Prompt drafts are ephemeral build
specifications — they live in `~/vsm-fitness-builds/coach/` and are consumed
by the next build.

**Step 0a: Read operational state**
1. Read `~/vsm/vsm-fitness-coach/references/fitness-projects.md` (coverage ledger)
2. Read `~/vsm/viable-swarm-model/references/hypotheses.md`
3. Read `~/vsm/viable-swarm-model/references/mutation-log.md`
4. Check for `~/vsm-fitness-builds/coach/FB[N+1]-prompt-draft.md` (from Phase 6 of previous build)

**Step 0b: Consume or synthesize**
- **If a prompt draft exists**: Use it directly as the build specification.
  This is the normal path for build N+1 after build N completed Phase 6.
- **If no prompt draft exists** (first build, or user requested fresh):
  Synthesize a new build design:
  1. Identify the lowest-scoring phase from the most recent build (or default
     to Foundation phase if this is the first build)
  2. Select a domain that naturally exercises that phase's capabilities
  3. Ensure the domain has NOT appeared in the coverage ledger previously
  4. Set complexity tier: same as previous if previous scored < 4.0;
     one tier higher if previous scored ≥ 4.0 (first build defaults to Tier 2)
  5. Draft build parameters: domain, complexity, target phase, key hypotheses

**Step 0c: Create build directory**
```bash
mkdir -p ~/vsm-fitness-builds/coach/FB[N]-[date]
cd ~/vsm-fitness-builds/coach/FB[N]-[date]
```

Copy the prompt draft into the build directory as `prompt.md` so the athlete
skill has a stable reference during the build.

### Phase 1: Create Build Directory + Execute Build

**Step 1a: Create build directory**
```bash
mkdir -p ~/vsm-fitness-builds/coach/FB1-20260522
cd ~/vsm-fitness-builds/coach/FB1-20260522
```

The athlete builds the project in this directory — never in the user's
actual project directory. This isolates the fitness build from real work.

**Step 1b: Execute build**
Once the build directory is created and the prompt draft is copied, BEGIN
EXECUTION IMMEDIATELY. Do not ask the user for confirmation to start the build.
The user invoked `/flow:vsm-fitness-coach` explicitly to execute a build.

Instruct the model to run the `viable-swarm-model` workflow using the prompt
draft as the build specification, building in
`~/vsm-fitness-builds/coach/[project-id]-[date]/`. The main skill's full
10-phase flow executes:
- Intelligence, Foundation, Implementation, Testing, Integration, Security, Fix
- Phase 8b meta-report (the main skill's own evaluation)

The coach does NOT interfere during the build. It observes and records.

> **Platform Constraint — Subagent Nesting**: The VSM workflow requires spawning
> multiple custom subagents (`vsm_architect`, `vsm_auditor`, `vsm_security`,
> `vsm_coordinator`, etc.). Subagents do not have access to the `Agent` tool and
> cannot spawn further subagents. Therefore, S5 MUST execute the
> `viable-swarm-model` workflow directly — walking through each phase personally
> and spawning individual task subagents as needed. Do NOT spawn a single
> subagent to "run the whole build" — this will fail at Phase 1 when that
> subagent attempts to spawn `vsm_architect`.

**Critical**: Collect ALL artifacts from the build directory:
- `plan.md`
- Auditor reports (Phase 2b, 3b)
- Coordinator integration report
- Security gate findings
- Test coverage report
- Fix wave logs
- Project lessons (`~/vsm-fitness-builds/coach/[id]-[date]/.kimi/lessons.md`)
- Main skill's own meta-report output

### Phase 1c: Coach Completion Verification (MANDATORY — HARD BLOCK)

**This gate is NOT optional.** S5 MUST NOT proceed to Phase 2 until ALL of the following are verified. Failure to verify ANY item means the build is NOT complete.

1. **VSM Phase 8b is fully complete** — meta-report written, mutations bucketed, skill logs updated.
2. **Security Gate has zero unfixed HIGH/MEDIUM findings** — LOW findings may be documented, but HIGH/MEDIUM must be fixed or explicitly escalated to the user with written rationale.
3. **Integration Verification has zero unfixed HIGH/MEDIUM findings** — same rule as Security Gate.
4. **All tests pass** — backend pytest green, frontend build green, import checks green.
5. **`.kimi/lessons.md` exists** in the build directory.
6. **S5 explicitly states**: "Coach Phase 1 complete. VSM build artifacts collected. Proceeding to Coach Phase 2 (Evaluate Performance)."

> **Algedonic signal**: If you find yourself about to declare the fitness build "complete" or ask the user "what next?" before running Coach Phases 2-6, STOP immediately. This is a critical process violation. The coach flow has 6 phases. Phase 1 is only the build execution.

### Phase 2: Evaluate Performance

Spawn `vsm_trainer` subagent with:
- Build directory: `~/vsm-fitness-builds/coach/[project-id]-[date]/`
- Rubric: `~/vsm/vsm-fitness-coach/references/evaluation-rubric.md`

The trainer reads all build artifacts and the rubric, then returns a structured
fitness report with phase scores, gap analysis, surprises, and false positives.

**Do not score manually.** The trainer handles all evaluation.

### Phase 2b: Update Hypothesis Statuses

Before generating new hypotheses, update the status of any hypotheses tested by this build:

1. Read `~/vsm/viable-swarm-model/references/hypotheses.md`.
2. Identify hypotheses linked to this fitness build (check the **Tested by** field and the build's prompt draft Coverage Map).
3. For each hypothesis tested, update its status based on build results:
   - **Confirmed**: Build results match the expected outcome
   - **Rejected**: Build results contradict the hypothesis
   - **Inconclusive**: Experiment design was flawed or results were ambiguous
4. Fill in the **Result** field with specific evidence from the build artifacts.
5. Fill in the **Tested by** field with the fitness build ID (e.g., "FB10").

This step prevents the hypothesis backlog from accumulating stale untested items.

### Phase 3: Generate Hypotheses

Read the trainer's fitness report. For every gap identified (phases scored < 4),
generate a hypothesis and append to the main skill's `references/hypotheses.md`:

```markdown
## H[N]: [Specific falsifiable claim]
**Status**: untested
**Proposed**: [date]
**Rationale**: [What the fitness build revealed]
**Source**: Fitness build [FB ID]
**Experiment**: [Minimal test to validate]
**Expected**: [Confirm/reject criteria]
```

### Phase 4: Propose Mutations
Map confirmed gaps to specific skill file changes:
- Scored 1-2 → High-confidence mutation
- Scored 3 → Medium-confidence (propose hypothesis, monitor next build)
- Scored 4-5 → No mutation needed

Classify each mutation:
- **Append-only**: new rules, patterns, anti-patterns, checklists
- **Structural**: agent prompt changes, flow diagram changes, phase logic changes, add/remove agents

Present all proposed mutations to S5 in a structured report:
- Phase-by-phase scoring
- Each gap with rationale
- Proposed changes (append-only vs structural)

**CRITICAL**: Structural mutations are NEVER inferred from ambiguous user responses.
They require EXPLICIT approval via `AskUserQuestion` with:
- Exact files that would change
- What the change does
- Evidence from the fitness build

**S5 response inference** (append-only and refinement ONLY):
- "apply all" / "approved" / "go ahead" → apply append-only and refinement mutations
- "only append-only" → apply append-only, log refinement and structural
- Explicit rejection → log all to mutation-log.md

**S5 response inference** (structural — NEVER autonomous):
- "apply structural" / "approve structural" → NOT sufficient. Still use `AskUserQuestion`.
- User explicitly approves EACH structural mutation in `AskUserQuestion` → apply approved, log rejected.
- User rejects or is silent → log to mutation-log.md, do NOT apply.
- If ANY structural mutation was proposed: `AskUserQuestion` is MANDATORY.

### Phase 5: Apply Mutations

Use the **three-tier mutation system** for all changes:

| Tier | Scope | Approval |
|---|---|---|
| **Append-only** | Add new content. Zero modifications to existing text. | Autonomous |
| **Refinement** | Modify existing content in a single file. Preserve structure. Only in `references/` or `agents/`. No `SKILL.md`. | Autonomous, logged |
| **Structural** | Multi-file, architecture, `SKILL.md`, add/remove agents or phases. | User via `AskUserQuestion` |

**Mutations to main skill's files** (the athlete):
- Append-only: new rules, patterns, anti-patterns, checklists
- Refinement: reword agent prompts, update checklist items, fix typos
- Structural: phase logic changes, flow diagram changes, agent architecture changes

**Mutations to coach's own files** (self-modification):
- Append-only: new build results to coverage ledger, new rubric criteria
- Refinement: update `vsm_trainer` prompt, adjust rubric weights, reword criteria
- Structural: changes to coach `SKILL.md` workflow or phase logic

Write all applied mutations to:
- Main skill: `references/*.md`, `agents/*.md`, `references/hypotheses.md`, `references/experiments.md`, `references/mutation-log.md`
- Coach self: `references/*.md`, `agents/*.md`, `assets/*.md`, `references/mutation-log.md`
- Fitness report using `assets/fitness-report-template.md`
- `git commit` all changes with descriptive message

### Phase 5b: Structural Mutation Approval Gate (MANDATORY — HARD BLOCK)

**This gate is NOT optional. It is a hard dependency for Phase 6.**

1. **Check**: Were any structural mutations proposed in Phase 4?
   - If NO: proceed to Phase 6 immediately.
   - If YES: you CANNOT proceed to Phase 6 until the user explicitly responds.

2. **Present**: Use `AskUserQuestion` with ONE question per structural mutation.
   Each question MUST include:
   - Exact files that would change
   - What the change does
   - Evidence from the fitness build
   - Expected effect on next build

3. **Record**: For EACH mutation:
   - Approved → apply immediately, log to mutation-log.md, git commit
   - Rejected → log rejection rationale to mutation-log.md
   - Deferred → log deferral rationale to mutation-log.md

4. **Verify before Phase 6**: S5 MUST explicitly state:
   "Structural Mutation Gate: [X approved, Y rejected, Z deferred]. Proceeding to Phase 6."
   If you cannot say this sentence, the gate is NOT cleared.

5. **Structural mutations MUST NOT be applied before this gate is cleared**.
   If S5 has already written changes to `SKILL.md`, agent definitions, or flow
   diagrams before presenting them to the user, REVERT those changes immediately
   and present them as proposals instead. Applying structural mutations without
   explicit user approval is a critical process violation regardless of whether
   the user later says "commit the changes."

6. **Algedonic signal**: If you find yourself about to write
   `FB[N+1]-prompt-draft.md` without having asked the user about structural
   mutations, STOP immediately. This is a critical process violation.
   - Halt all Phase 6 activity
   - Return to Step 2 of this gate
   - Present the structural mutations NOW

**Why this matters**: Structural mutations change agent architecture, workflow
logic, and phase sequencing. They affect every future build. Autonomous
application without user approval risks breaking the entire skill ecosystem.

### Phase 6: Prepare Next Build Prompt

After the fitness report is written, mutations are committed, and the
Structural Mutation Gate is cleared, **automatically synthesize** the next
build prompt. This is not optional — it is the causal output of the current
build's empirical results.

Follow this synthesis protocol **exactly**. Do not skip steps.

#### Step 1: Read all source material
Read these files in order:
1. `assets/fitness-report-template.md` — current build's fitness report
2. `~/vsm/viable-swarm-model/references/hypotheses.md` — updated statuses from Phase 2b
3. `~/vsm/viable-swarm-model/references/mutation-log.md` — mutations applied in Phase 5
4. `references/fitness-projects.md` — coverage ledger: previous build domains and results (do not repeat domains)
5. `assets/prompt-template.md` — the template to fill

#### Step 2: Extract synthesis inputs
From the fitness report, extract:
- **Lowest-scoring phase(s)** (score 1-3): these are the primary targets
- **Specific gaps**: quote the exact gap descriptions
- **False positives**: any agent flagged something correct as wrong
- **Surprises**: what went unexpectedly well or badly

From hypotheses.md, extract:
- **Confirmed hypotheses**: prevention rules that work — must be validated again
- **Rejected hypotheses**: rules that were wrong — must NOT be tested again
- **Untested hypotheses relevant to gaps**: link gap → hypothesis

From mutation-log.md, extract:
- **New prevention rules**: what was added in this session
- **Agent prompt refinements**: what agent behavior changed
- **Structural mutations**: what workflow changes were made

#### Step 3: Select domain and complexity
Rules:
- Domain MUST NOT appear in the coverage ledger (`references/fitness-projects.md`) previously
- Domain MUST naturally require the capability where the lowest-scoring phase operates
- Complexity MUST be one tier higher than the previous build if score ≥ 4.0, SAME tier if score < 4.0
  (do not increase complexity on a failing build; fix the fundamentals first)
- If previous build was Tier 3 and scored < 4.0, reduce to Tier 2 for the next build

#### Step 4: Map gaps to deliberate traps
For EACH gap from the fitness report:
1. Design a specific condition in the new domain that would trigger the same failure mode
2. State the EXACT expected behavior if the prevention rule works
3. State the EXACT failure indicator if the prevention rule fails
4. Assign severity: if the original gap was a BLOCKER, the trap MUST be a BLOCKER-equivalent

Example mapping:
- Gap: "GraphQL enum case mismatch (FB4)"
- Trap: "OrderStatus uses `str, enum.Enum` but frontend queries use camelCase field name that doesn't match auto-camelCase output"
- Expected if rule works: Coordinator flags mismatch, frontend fixes query
- Failure indicator: Runtime ValueError on enum construction

#### Step 5: Map hypotheses to critical requirements
For EACH untested hypothesis being targeted:
1. Write a specific requirement that exercises the hypothesis
2. State which agent/phase is responsible for catching it
3. State the PASS/FAIL criteria

For EACH confirmed hypothesis being re-validated:
1. Write a lighter-touch check (don't waste full trap complexity on proven rules)
2. Include it in Exit Criteria, not Deliberate Traps

#### Step 6: Verify coherence (mandatory checklist)
Before writing the prompt file, verify ALL of the following:
- [ ] At least one trap maps to each gap from the lowest-scoring phase
- [ ] No trap contradicts another trap
- [ ] All traps are testable (verifiable by audit, security, or coordinator)
- [ ] The new domain has NOT been used in any previous fitness build
- [ ] Complexity tier is appropriate (not higher after a failing build)
- [ ] Data model field names are EXACT and unambiguous (Phase 2c validation target)
- [ ] Every enum value is specified exactly (no ambiguity for Strawberry auto-camelCase)
- [ ] Exit criteria include build-specific checks derived from hypotheses
- [ ] The Purpose paragraph references the previous build score and specific gap IDs

If ANY check fails: revise the prompt. Do NOT write the file with known gaps.

#### Step 7: Write the prompt file
1. Fill `assets/prompt-template.md` with the synthesized content
2. Write to `~/vsm-fitness-builds/coach/FB[N+1]-prompt-draft.md`
3. Verify the file is complete and self-contained (no references to external context)

**Git scope**: The prompt draft is a build artifact for the *next* fitness build. It lives
in `~/vsm-fitness-builds/coach/` (outside the skill repo) and **must NOT be committed**
to the skill's git repository. The `git commit` in Phase 5 covers skill mutations only.

> **Algedonic signal**: If you find yourself about to end the session, tell the user
> "the build is complete," or ask "what would you like to do next?" without having
> produced `~/vsm-fitness-builds/coach/FB[N+1]-prompt-draft.md`, STOP immediately.
> This is a critical process violation. Phase 6 is MANDATORY. The coach flow is not
> complete until the next build prompt is written.

**Why this is last**: The next build prompt is a causal output of the current build's
empirical results. It cannot be written before evaluation, hypothesis updates, and
mutation application are complete. Skipping the synthesis protocol produces prompts
that test the wrong things, waste build resources, and fail to validate prevention rules.

## 7. The Mutation System

This skill is a learning organism. It modifies its own files between sessions.
All files in `~/vsm/vsm-fitness-coach/` are mutable.

### Why Mutation Is Safe

The skill directory is a **git repository**. Every mutation is committed.
If a mutation breaks viability, the user (or the skill itself) can revert:

```bash
cd ~/vsm/vsm-fitness-coach
git log --oneline
git revert [commit]
```

### What Can Mutate

| File | Mutation Mode | Justification Required |
|---|---|---|
| `references/fitness-projects.md` | Append build results (coverage ledger) | Low: empirical finding |
| `references/evaluation-rubric.md` | Append criteria; adjust weights | Medium: repeated pattern |
| `agents/*.md` | Refine agent prompts | Medium: repeated pattern |
| `assets/*.md` | Refine templates | Low: empirical finding |
| `SKILL.md` | Amend phase details, mutation rules | High: structural issue proven |

### Mutation Log Format

Every mutation is recorded in `references/mutation-log.md`:
```markdown
## Mutation [N] — YYYY-MM-DD
**Session**: [task description]
**File**: [path]
**Type**: [append | refinement | structural]
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

---

## 8. Fitness Report Template

See `assets/fitness-report-template.md` for the full template. Summary:

```markdown
# Fitness Report: [Project Name]

## Build Summary
- Project: [name]
- Waves executed: [count]
- Agents spawned: [count]
- BLOCKERs found: [count]
- Fix iterations: [count]

## Phase Scores
| Phase | Score | Notes |
|-------|-------|-------|
| 0. Viability | [1-5] | [notes] |
| 1. Intelligence | [1-5] | [notes] |
| 2. Foundation | [1-5] | [notes] |
| 3. Implementation | [1-5] | [notes] |
| 4. Testing | [1-5] | [notes] |
| 5. Integration | [1-5] | [notes] |
| 6. Security | [1-5] | [notes] |
| 7. Fix | [1-5] | [notes] |
| 8. Reflection | [1-5] | [notes] |
| 8b. Meta-Reflection | [1-5] | [notes] |

## Gaps Identified
1. [Gap description] → Hypothesis H[N]
2. [Gap description] → Hypothesis H[N]

## Mutations Applied
1. [File changed] → [Rationale]
2. [File changed] → [Rationale]

## Overall Assessment
[Is the skill improving? Getting worse? Any structural concerns?]
```

## 9. Design Principles

1. **The coach is not a builder**: It never writes implementation code.
   It only evaluates, scores, and synthesizes.
2. **Real builds, not toy examples**: Fitness projects are substantial
   (500-5000 lines, multi-service) to stress-test the main skill realistically.
3. **Structured evaluation**: The rubric prevents subjective "felt okay"
   assessments. Every score needs evidence.
4. **Hypothesis-driven improvement**: Every gap becomes a falsifiable claim
   that the gym can test later.
5. **Co-evolution**: The coach evaluates the main skill; the gym validates
   the hypotheses; the main skill improves. All three
   skills grow together.
