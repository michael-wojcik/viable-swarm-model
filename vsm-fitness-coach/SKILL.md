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

If installed elsewhere, adjust paths.

**Build directory**: Every fitness build creates a dedicated, timestamped
directory. The athlete (`viable-swarm-model`) builds the project there — never
in the user's actual project directory.

## 2. How to Invoke

- **`/flow:vsm-fitness-coach [fitness project name or ID]`** — Execute a
  fitness build. The coach reads the fitness project catalog, presents
  options to S5 (you), guides the main skill through the build, and then
  evaluates performance. Must include some natural language text before or
  around the command for Kimi CLI to process it.
- **`/skill:vsm-fitness-coach`** — Load as knowledge reference. Use when
  you need the evaluation rubric or fitness project catalog.

## 3. Fitness Coach Roles

| VSM System | CLI Implementation | Custom Type | Activation | Produces |
|---|---|---|---|---|
| **S5 (Policy)** | Main conversation agent (you) | — | Phase 0 | Project selection, mutation approval |
| **S4 (Selector)** | Main agent reads catalog | — | Phase 0 | Fitness project spec |
| **S1 (Builder)** | `viable-swarm-model` workflow | Flow skill | Phase 1 | Substantial project |
| **S3* (Evaluator)** | Main agent reads rubric | — | Phase 3 | Scored evaluation per phase |
| **S2 (Synthesizer)** | Main agent | — | Phase 4 | Hypotheses, mutations |

**Terminology**: `S5` refers to the main conversation agent (you, the LLM executing
this skill). The word `user` refers to the human operator. S5 may escalate to the
user via `AskUserQuestion` or `EnterPlanMode` when human policy input is required.

## 4. The Golden Rule

The fitness coach does NOT build code directly. It delegates all
implementation to the main skill (`viable-swarm-model`). The coach's
value is in **selection, evaluation, and synthesis**.

## 5. Executable Flow Diagram

```mermaid
flowchart TD
    BEGIN([BEGIN])
    P0[Phase 0: Select Fitness Project<br/>Read references/fitness-projects.md]
    P0S{<choice>project selected</choice>?}
    P1[Phase 1: Execute Build<br/>Run viable-swarm-model workflow<br/>Build the selected project]
    P1A[Collect all artifacts:<br/>plan.md, audit reports, security reports,<br/>integration report, test results, fix logs]
    P2[Phase 2: Evaluate Performance<br/>Read references/evaluation-rubric.md<br/>Score each phase 1-5]
    P2S{<choice>any phase scored < 4</choice>?}
    P3[Phase 3: Generate Hypotheses<br/>One hypothesis per gap identified]
    P4[Phase 4: Propose Mutations<br/>Present structured report to S5]
    P4A{<choice>structural mutations<br/>approved by user</choice>?}
    P5[Phase 5: Apply Mutations<br/>Append-only: autonomous<br/>Structural: conditional]
    P5L[Log rejections to mutation-log.md]
    P5R[Write fitness report<br/>assets/fitness-report-template.md]
    P5G[git commit all changes]
    END([END])

    BEGIN --> P0
    P0 --> P0S
    P0S -->|<choice>none</choice>| END
    P0S -->|<choice>selected</choice>| P0D[Create build directory<br/>~/vsm-fitness-builds/coach/[id]-[date]/]
    P0D --> P1
    P1 --> P1A
    P1A --> P2
    P2 --> P2S
    P2S -->|<choice>yes</choice>| P3
    P2S -->|<choice>no</choice>| P4
    P3 --> P4
    P4 --> P4A
    P4A -->|<choice>approved / none proposed</choice>| P5
    P4A -->|<choice>rejected / ambiguous</choice>| P5L
    P5 --> P5R
    P5L --> P5R
    P5R --> P5G
    P5G --> END
```

## 6. Phase Details

### Phase 0: Select Fitness Project
Read `~/vsm/vsm-fitness-coach/references/fitness-projects.md`.
Present the catalog to S5 (you). Each project includes:
- **Name & ID**: e.g., "FB1: DocuFlow"
- **Complexity**: Estimated agent waves, lines of code, services
- **Coverage**: Which skill capabilities it exercises
- **Known stress points**: Specific patterns/anti-patterns it should trigger

If invoked without argument, present all projects and let S5 select.
If invoked with argument (e.g., "Run FB1"), load that project directly.

### Phase 1: Create Build Directory + Execute Build

**Step 1a: Create build directory**
```bash
mkdir -p ~/vsm-fitness-builds/coach/FB1-20260522
cd ~/vsm-fitness-builds/coach/FB1-20260522
```

The athlete builds the project in this directory — never in the user's
actual project directory. This isolates the fitness build from real work.

**Step 1b: Execute build**
Instruct the model to run the `viable-swarm-model` workflow on the selected
project, building in `~/vsm-fitness-builds/coach/[project-id]-[date]/`. The main
skill's full 10-phase flow executes:
- Intelligence, Foundation, Implementation, Testing, Integration, Security, Fix
- Phase 8b meta-reflection (the main skill's own evaluation)

The coach does NOT interfere during the build. It observes and records.

**Critical**: Collect ALL artifacts from the build directory:
- `plan.md`
- Auditor reports (Phase 2b, 3b)
- Coordinator integration report
- Security gate findings
- Test coverage report
- Fix wave logs
- Project lessons (`~/vsm-fitness-builds/coach/[id]-[date]/.kimi/lessons.md`)
- Main skill's own meta-reflection output

### Phase 2: Evaluate Performance
Read `~/vsm/vsm-fitness-coach/references/evaluation-rubric.md`.
Score each phase of the main skill's execution from 1-5:

| Score | Meaning |
|---|---|
| 5 | Exceeded expectations. Caught issues that weren't obvious. |
| 4 | Performed as designed. No gaps. |
| 3 | Adequate but had minor gaps or inefficiencies. |
| 2 | Significant gaps. Missed important issues. |
| 1 | Failed. Phase was misleading, redundant, or harmful. |

For each phase scored < 4, write a detailed note:
- What was expected
- What actually happened
- Root cause (if identifiable)
- Severity (cosmetic, moderate, critical)

### Phase 3: Generate Hypotheses
For every gap identified in Phase 2, write a hypothesis to the main skill's
`references/hypotheses.md`:

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
- **Structural**: agent prompt changes, flow diagram changes, phase logic changes

Present all proposed mutations to S5 in a structured report:
- Phase-by-phase scoring
- Each gap with rationale
- Proposed changes (append-only vs structural)

**S5 response inference**:
- "apply all" / "approved" / "go ahead" → apply everything
- "skip structural" / "only append-only" → apply append-only, log structural
- Explicit rejection → log all to mutation-log.md
- Ambiguous or silent on structural → `AskUserQuestion`:
  "These structural mutations are proposed: [list]. Approve?"

### Phase 5: Apply Mutations

**Append-only mutations**: Write directly to main skill's files.

**Structural mutations**: Only if user approved (via natural language or
`AskUserQuestion`). If rejected or ambiguous, log rationale to `mutation-log.md`.

Write all applied mutations to:
- Main skill's reference files
- `hypotheses.md`, `experiments.md`, `mutation-log.md`
- Fitness report using `assets/fitness-report-template.md`
- `git commit` all changes with descriptive message

## 7. Fitness Report Template

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

## 8. Design Principles

1. **The coach is not a builder**: It never writes implementation code.
   It only evaluates, scores, and synthesizes.
2. **Real builds, not toy examples**: Fitness projects are substantial
   (500-5000 lines, multi-service) to stress-test the main skill realistically.
3. **Structured evaluation**: The rubric prevents subjective "felt okay"
   assessments. Every score needs evidence.
4. **Hypothesis-driven improvement**: Every gap becomes a falsifiable claim
   that the gym can test later.
5. **Co-evolution**: The coach evaluates the main skill; the evolution
   chamber validates the hypotheses; the main skill improves. All three
   skills grow together.
