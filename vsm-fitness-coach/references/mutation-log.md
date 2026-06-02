# Mutation Log

> This file is append-only. Every modification the coach skill makes to its own
> files is recorded here with full rationale. If the skill becomes corrupted,
> this log is the audit trail for `git revert`.
>
> **Mutation rules**: Append only. Each entry includes: session context,
> file changed, type of change, rationale, expected effect, **target failure mode**,
> **measured effect**.
>
> **Convention**: Use sequential numbers (`Mutation 1`, `Mutation 2`, ...).
> Reference the fitness build ID in the Session field.
>
> **Required fields** (from now on):
> - **Target failure mode**: What specific failure was this mutation trying to prevent?
> - **Measured effect**: Did it prevent that failure in subsequent builds? Cite build IDs.

---

## Mutation 1 — 2026-05-23

**Session**: Creation of coach mutation-log infrastructure
**File**: `references/mutation-log.md`, `SKILL.md`
**Type**: structural
**Rationale**: The coach skill referenced self-modification and the three-tier
mutation system but lacked the supporting infrastructure: no mutation-log.md,
no format template, no epistemic rules, and no rollback procedure. All coach
mutations were being logged in the main skill's mutation-log.md, which violated
the principle that each skill in the ecosystem should maintain its own audit trail.

**Expected effect**: Future coach mutations (prompt refinements, rubric updates,
fitness project additions, phase logic changes) will be logged here. The coach
is now a fully self-documenting learning organism.

---

## Mutation 2 — 2026-05-23

**Session**: Coach skill refinement — hypothesis status tracking gap
**File**: `SKILL.md`
**Type**: refinement
**Rationale**: The coach generated new hypotheses from fitness build gaps but
never explicitly updated the status of existing hypotheses tested by the build.
This left the hypothesis backlog with stale "untested" items.

**Expected effect**: After every fitness build, the coach will explicitly check
which hypotheses were tested, update their status (confirmed / rejected /
inconclusive), fill in the Result field with build evidence, and record the
build ID in the Tested by field.

**Files modified**:
- `SKILL.md` — Added Phase 2b: Update Hypothesis Statuses between Phase 2
  (Evaluate Performance) and Phase 3 (Generate Hypotheses). Updated Mermaid
  flow diagram to include P2H node.

---

## Mutation 42 — YYYY-MM-DD (FB13 Documentation Fix)
**Session**: FB13 fitness build evaluation — user feedback
**File**: `SKILL.md` (Phase 6, Step 7)
**Type**: refinement
**Rationale**: User pointed out that Phase 6 does not explicitly state the FB[N+1] prompt draft is a build artifact that must NOT be committed to the skill repo. The flow diagram shows git commit before prompt writing, but the text was ambiguous. Added explicit git scope note to prevent accidental commits of build artifacts.
**Expected effect**: Future sessions do not commit `~/vsm-fitness-builds/coach/FB*-prompt-draft.md` files to the skill repo.

---

## Mutation 43 — 2026-05-24 (FB14 Post-Build)

**Session**: FB14 fitness build evaluation — EduSphere
**File**: `references/hypotheses.md` (main skill), `references/fitness-projects.md`, `~/vsm-fitness-builds/coach/FB15-prompt-draft.md`
**Type**: append + refinement
**Rationale**: FB14 exposed four systemic gaps that existing prevention rules do not cover:
1. **Frontend cross-file contract mismatches** (H66): Parallel frontend agents produced queries.ts missing exports that pages imported, and courseStore.ts missing fields pages destructured. The auditor caught these but only after the fact.
2. **Registration role validation missing from security checklist** (H67): A CRITICAL privilege escalation vulnerability (arbitrary role assignment including admin) was missed by architect, foundation, and implementation phases. Only the security gate caught it, and only because the agent happened to inspect auth code.
3. **GraphQL schema/query mismatches** (H68): Frontend queries passed wrong argument types (String vs DateTime) and expected wrong return types. Coordinator caught these manually but no automated check exists.
4. **Auth router missing from foundation wave** (H69): Despite being in api-spec.md, auth endpoints were not created until the fix wave, breaking the entire application.

**Expected effect**: 
- FB15 will test whether a frontend import check (`tsc --noEmit`) catches contract mismatches before the auditor (H66).
- FB15 will test whether an explicit security checklist item for registration role validation prevents the vulnerability (H67).
- FB15 will test whether schema introspection during integration check catches query/schema mismatches (H68).
- FB15 will test whether explicitly requiring auth router in foundation wave prevents it from being skipped (H69).

**Files modified**:
- `references/hypotheses.md` — Appended H66, H67, H68, H69
- `references/fitness-projects.md` — Appended FB14 entry
- `~/vsm-fitness-builds/coach/FB15-prompt-draft.md` — Created FB15 prompt targeting all four gaps with deliberate traps

---

## Mutation 44 — 2026-05-25 (Structural — APPLIED)

**Session**: FB19 fitness build initiation — agent confusion about execution model
**File**: `vsm-fitness-coach/SKILL.md` (Phase 1 section)
**Type**: structural
**Rationale**: The Phase 1 instruction "Instruct the model to run the `viable-swarm-model` workflow" is ambiguous. S5 (the root agent executing the coach flow) interpreted this as "spawn a single subagent to execute the entire VSM workflow," which failed because subagents cannot spawn subagents. The skill needs an explicit clarification that S5 PERSONALLY executes the VSM workflow phase-by-phase, spawning task-specific subagents for individual tasks only (architect, individual coders, auditor, etc.). A single subagent cannot host the entire VSM workflow.
**Expected effect**: Future coach invocations will immediately begin executing VSM phases from the root agent, not attempt to delegate the entire build to one subagent.

**Applied change to vsm-fitness-coach/SKILL.md Phase 1**:
Added after Step 1b: "**Platform Constraint — Subagent Nesting**: The VSM workflow requires spawning multiple custom subagents (`vsm_architect`, `vsm_auditor`, `vsm_security`, `vsm_coordinator`, etc.). Subagents do not have access to the `Agent` tool and cannot spawn further subagents. Therefore, S5 MUST execute the viable-swarm-model workflow directly — walking through each phase personally and spawning individual task subagents as needed. Do NOT spawn a single subagent to 'run the whole build' — this will fail at Phase 1 when that subagent attempts to spawn `vsm_architect`."

---

## Mutation 45 — 2026-05-25 (Structural — APPLIED)

**Session**: FB19 fitness build initiation — platform constraint undocumented
**File**: `viable-swarm-model/SKILL.md` (Section 2)
**Type**: structural
**Rationale**: The viable-swarm-model skill describes a workflow that requires spawning ~10+ subagents across phases, but nowhere does it document the critical platform constraint that subagents cannot spawn subagents. New agents loading this skill for the first time have no way to know they must execute the flow personally rather than delegating it.
**Expected effect**: First-time users/agents will understand immediately that the VSM flow is root-agent-only.

**Applied change to viable-swarm-model/SKILL.md**:
Added in Section 2 (How to Invoke): "**Platform constraint**: This flow MUST be executed by the root conversation agent (S5). It cannot be delegated to a single subagent because the workflow internally spawns custom subagents (`vsm_architect`, `vsm_auditor`, `vsm_security`, etc.) and subagents do not have access to the `Agent` tool."

---

## Mutation 46 — 2026-05-25 (Refinement — APPLIED)

**Session**: FB19 fitness build — agent hesitation and permission-seeking
**File**: `vsm-fitness-coach/SKILL.md` (Phase 1 section)
**Type**: refinement
**Rationale**: After reading the prompt draft, S5 asked the user "Do you want me to run the full build now?" instead of executing immediately. The fitness coach skill's Phase 1 has no explicit instruction that execution should begin immediately after Phase 0 synthesis is complete. The default assumption should be "execute now" unless the user explicitly says otherwise.
**Expected effect**: Future coach sessions will transition from Phase 0 to Phase 1 execution without asking for redundant confirmation.

**Applied change**:
Added to Phase 1 Step 1b: "Once the build directory is created and the prompt draft is copied, BEGIN EXECUTION IMMEDIATELY. Do not ask the user for confirmation to start the build. The user invoked `/flow:vsm-fitness-coach` explicitly to execute a build."

