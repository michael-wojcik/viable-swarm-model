# Hypothesis Backlog

> **Mutation rules**: Append new hypotheses with full rationale and experiment
> design. Update status (untested → testing → confirmed → rejected → superseded).
> Once confirmed or rejected, the hypothesis is moved to `hypotheses-archive.md`
> and its prevention rules are absorbed into the integration checklist or
> pattern library. Keep ≤20 untested hypotheses in this file.
>
> Each hypothesis is a falsifiable claim about the skill's knowledge or
> behavior. It is tested by the vsm-fitness-gym companion skill or
> during Phase 8b of a real build.
>
> **See also**: `references/experiments.md` for empirical test records of
> confirmed and rejected hypotheses.

---

## Index

| Hypothesis | Status |
|---|---|
| H152 | testing |
| H202 | tested |
| H217 | partially |
| H217-UPDATE | partially |
| H401 | testing |
| H402 | testing |
| H403 | testing |
| H404 | testing |
| H405 | testing |
| H406 | testing |
| H500 | partially |
| H502 | partially |
| H503 | tested |
| H504 | tested |
---


---


---


---


---

## H152: Pre-build environment smoke tests would catch package incompatibilities before code writing begins

**Status**: testing
**Proposed**: 2026-05-25
**Rationale**: FB22 discovered `strawberry-graphql==0.256.0` is incompatible with the installed pydantic version only after the build started and graphql.py was written. This wasted agent time and required S5 intervention.
**Source**: Fitness build FB22
**Experiment**: Tool-enforced import gate added to `scripts/integration-hard-gates.py` (H152). It reads `requirements.txt` and verifies declared packages import successfully in a fresh subprocess. Run next build with the gate enabled.
**Expected**: Environment incompatibility detected at Phase 0/3c, build halted before implementation agents are dispatched.
**Result**: Tool implemented and wired into SKILL.md Phase 0. Awaiting validation in next build with `requirements.txt`.
**Tested by**: Tests 221-222 in automation suite

---


---


---


---


---

## H202: Tool-enforced read-only boundaries prevent auditor "helpfulness" override better than prompt-only instructions

**Status**: tested — not confirmed
**Proposed**: 2026-05-26
**Rationale**: In the old architecture, auditor read-only status was declared in the user prompt. In a real build, an auditor might be socially engineered or "helpfully" attempt to fix a BLOCKER it finds. With custom agent files, the auditor's YAML explicitly excludes `WriteFile`, `StrReplaceFile`, and `Shell` from its tool list. Even if the model wants to help, it cannot call write tools.
**Source**: Custom agent file migration
**Experiment**: Deliberately ask the auditor subagent to write a file or fix a BLOCKER. Measure refusal rate and whether the refusal cites tool absence vs role policy.
**Expected**: 100% refusal rate with explicit tool-absence citation.
**Tested by**: E21
**Result**: NOT CONFIRMED — Prompt-only boundary WORKED in this test (auditor refused fix request, cited role policy). However, critical gap discovered: `vsm_auditor.yaml` currently includes `WriteFile` in tool list, contrary to hypothesis claim. Tool-enforced superiority remains untested. Further stress testing needed under varied social-engineering pressure.

---


---


---


---


---

## H217: Agent timeout is the primary drag on Tier 2+ build scores
**Status**: confirmed
**Proposed**: 2026-06-03
**Rationale**: FB28 had 5 agent timeouts (backend_coder, frontend_coder, backend_tester, frontend_tester, foundation_auditor). S5 had to manually complete foundation audit, write tests, fix auth returns, and wire main.py. This forced S5 into coding tasks that should be agent-owned.
**Source**: Fitness build FB28, Phase 2/4
**Experiment**: Split Tier 2+ agent tasks into smaller chunks (<500 lines per spawn). Measure timeout rate.
**Expected**: Timeout rate drops from 5/10 to ≤1/10.
**Tested by**: FB33
**Result**: CONFIRMED — 4-spawn architect split produced 1,601 lines with ZERO timeouts. 15+ agents spawned total, zero timeouts. FB31-1 and FB31-2 are effective mutations.

---

### H217: Agent task sizing ≤500 lines per spawn prevents timeouts
**Status**: partially confirmed
**Tested by**: FB30
**Result**: Backend code agents completed without timeout (improvement). Architect and backend tester still timed out. H217 scope is too narrow — covers implementation agents but not design/test agents.
**Rationale**: Code-writing agents benefit from smaller tasks; design agents producing multi-document architecture specs still exceed timeout limits.


---


---


---

## H401: Tool-Enforced GraphQL Stub Detection Prevents Stub Mutations Reaching Phase 6

**Status**: testing
**Proposed**: 2026-06-06
**Rationale**: FB34 probation mutation FB34-1 (GraphQL mutation completeness checklist) did not prevent six `INTERNAL_ERROR` stub mutations from reaching Phase 6. The prompt-only checklist was ignored until `vsm_auditor` flagged the parity gap in the implementation audit.
**Source**: Fitness build FB34, Phase 6 implementation audit
**Experiment**: Add a `scripts/check-graphql-stubs.py` hard gate invoked in Phase 3c and Phase 6. It introspects the Strawberry schema and fails if any `@strawberry.mutation` body contains only `pass`, `raise`, or returns a hard-coded `INTERNAL_ERROR` / `NotImplemented` payload. Run the next GraphQL-enabled build with the gate enabled.
**Expected**: Zero stub mutations reach the implementation audit; Phase 3c coordinator blocks on the gate instead of documenting parity gaps later.
**Result**: Tool implemented in R89 (`scripts/check-graphql-stubs.py`). Awaiting validation in next GraphQL-enabled build.
**Tested by**: R89 automation suite (Tests 218-219)

---


---


---

## H402: Mandatory Frontend Fix-Agent Sign-Off Improves Traceability

**Status**: testing
**Proposed**: 2026-06-06
**Rationale**: The SocketProvider `authenticate` emit fix and the `queries.ts` DRIVERS-query additions were applied during the FB34 fix wave, but `.kimi/` contains no `vsm_frontend_fix_agent` report. The fixes are traceable only through implementation-audit re-checks, not through a dedicated fix-agent artifact.
**Source**: Fitness build FB34, Phase 7 fix wave
**Experiment**: Update `SKILL.md` Phase 7 to require a `vsm_frontend_fix_agent` spawn (and `.kimi/frontend-fix-report.md`) whenever a frontend file is modified in the fix wave. Measure report presence in the next three builds that require frontend fixes.
**Expected**: 100% of frontend-modifying fix waves produce a dedicated report; S5 can verify scope and regression status without relying on auditor re-checks.
**Result**: [to be filled]
**Tested by**: [experiment ID or session]

---


---


---

## H403: Security Agent Frontend Source Scan Catches Persisted JWT and Fallback URIs

**Status**: testing
**Proposed**: 2026-06-06
**Rationale**: `security-report.md` in FB34 states "No `frontend/src/**/*.ts` or `frontend/src/**/*.tsx` files were found" despite the existence of `src/pages/*.tsx` and `src/sio/SocketProvider.tsx`. The security gate therefore missed `localStorage` JWT persistence, Apollo Client fallback URIs, and CORS credential usage.
**Source**: Fitness build FB34, Phase 5 security gate
**Experiment**: Append a mandatory frontend-source scan block to `agents/vsm_security.md` requiring `find frontend/src -type f` and explicit checks for `localStorage.setItem("token"`, `|| 'http://localhost'`, and `credentials: 'include'` without explicit origin. Run the next build with the updated prompt.
**Expected**: ≥1 MEDIUM finding per build that persists JWT in `localStorage` or bakes localhost fallbacks.
**Result**: [to be filled]
**Tested by**: [experiment ID or session]

---


---


---

## H404: GraphQL Mutation Test Coverage Floor Prevents Stub Mutations Passing Phase 4

**Status**: testing
**Proposed**: 2026-06-06
**Rationale**: The FB34 backend test suite reported 33/33 passing while six GraphQL mutations returned `INTERNAL_ERROR`. The existing tests did not exercise the mutation implementations, so stubs were invisible to the Phase 4 gate.
**Source**: Fitness build FB34, Phase 4 testing
**Experiment**: Append a rule to `vsm-stack-skills/tester-backend/SKILL.md` (and `agents/vsm_backend_tester.md`) requiring at least one test per `@strawberry.mutation` in the schema, with an explicit assertion that the resolver does not return `INTERNAL_ERROR`. Measure stub escape rate in the next GraphQL build.
**Expected**: Zero stub mutations pass the Phase 4 test suite.
**Result**: [to be filled]
**Tested by**: [experiment ID or session]

---


---


---

## H405: Session-End Mutation-State Backfill Ensures All Probation Mutations Are Scored

**Status**: testing
**Proposed**: 2026-06-06
**Rationale**: At the end of FB34, mutation-state rows FB34-1, FB34-2, FB34-3 still showed `Builds Tested = 0` and `Score = —` until manually backfilled. Manual S5 discipline is insufficient under pressure; the organism repeatedly leaves probation mutations unmeasured.
**Source**: Fitness build FB34, Phase 8b mutation tracking
**Experiment**: ~~Add a `scripts/backfill-mutation-state.py` invocation to `session-end.sh`~~ → Enhanced `hooks/auto-mutation-lifecycle.py` (already invoked by `session-end.sh`) to backfill `Score` from `mutations-applied.md` evidence when the current score is `—`. This avoids a separate script and leverages the existing lifecycle automation. Verify mutation-state within 1 hour of build close in the next fitness build.
**Expected**: 100% of probation/monitor mutations linked to a completed build have `Builds Tested ≥ 1` and a numeric score before S5 declares Phase 8 complete.
**Result**: **PARTIALLY CONFIRMED** — Score backfill implemented and tested in S5 iteration R78. `auto-mutation-lifecycle.py` now parses scores from evidence (e.g., "Score: 5") and writes them to `mutation-state.md` only when the score column is `—`. Existing scores are preserved. Automation suite has 3 tests covering dry-run, real-run, and existing-score preservation. Awaiting validation in a real fitness build where `mutations-applied.md` contains scored evidence.
**Tested by**: S5 Iteration R78

---


---


---

## H406: Skill Variety Metric Should Parse Agent Reports

**Status**: testing
**Proposed**: 2026-06-06
**Rationale**: `organism-vitals.md` in FB34 lists `integration-patterns` as an unused skill, yet `integration-contract.md` explicitly cites `integration-patterns` under "Skills consulted." The current metric counts skill reads only from S5 or Phase 0 load, not from agent reports, leading to undercounting and false variety deficits.
**Source**: Fitness build FB34, Phase 0 / Phase 6
**Experiment**: Refactor `scripts/organism-vitals.py` to grep `.kimi/*-report.md` and `.kimi/*-audit.md` for `Skills consulted:` / `Skills read:` headers and union those skill IDs with Phase 0 load. Compare the resulting skill variety score against the legacy score for FB34.
**Expected**: Skill variety for FB34 rises to ≥0.85 (from 0.75) because `integration-patterns`, `graphql-pitfalls`, and `dependency-drift-pitfalls` are confirmed consulted.
**Result**: [to be filled]
**Tested by**: [experiment ID or session]


---


---

## H500: Background Agent Session Isolation Causes CWD Drift

**Status**: partially confirmed
**Proposed**: 2026-06-08
**Rationale**: FB35 regression build: 5 of 8 background agents wrote files to their own session directories instead of the build directory. Requirements+env agent, frontend coder, routes+deliveries agent, and graphql+dead-code agent all produced files that were lost. S5 had to manually recreate ~15 files.
**Source**: Fitness build FB35, Phase 2/3
**Experiment**: Run a gym experiment spawning a background agent with a WriteFile task using a relative path, then check whether the file appears in the orchestrator's cwd or the agent's session directory. Compare with absolute path behavior.
**Expected**: Relative paths write to agent session directory; absolute paths write to correct location.
**Result**: Relative paths resolved to orchestrator cwd (`/Users/mj/vsm`), not the intended experiment directory. Absolute paths were 100% accurate. A distinct "agent session directory" was not observed in this test configuration, but the non-determinism of relative paths is confirmed. FB35-1 (absolute path requirement) is supported.
**Tested by**: E24

---


---

## H502: Explicit Termination Rule Prevents Post-Write Hang Loops

**Status**: partially confirmed
**Proposed**: 2026-06-08
**Rationale**: FB35 architect spawn 1 (406 lines) completed cleanly, while spawns 2-4 (similar size) hung. The difference may be non-deterministic, but the pattern suggests agents lack a termination condition after completing their primary deliverable. An explicit "if file is written and verification passes, STOP" rule may prevent hang loops.
**Source**: Fitness build FB35, Phase 1
**Experiment**: Add an explicit termination rule to vsm_architect.md and vsm_backend_coder.md prompts: "After your primary WriteFile succeeds and a basic import check passes, declare completion and stop. Do NOT attempt perfectionist fixes to minor type mismatches." Measure hang rate in next build.
**Expected**: Hang rate drops from 6/15 to ≤2/15.
**Result**: Explicit STOP instruction produced clean termination in a background `vsm_architect` agent. Agent cited the STOP rule as the reason for not elaborating. No control condition (without STOP) was tested, so delta in hang rate is unmeasured. FB35-2 is supported but needs full-build validation.
**Tested by**: E24

---


---

## H217-UPDATE: Agent Task Sizing Reduces but Does Not Eliminate Timeouts

**Status**: partially confirmed
**Tested by**: FB35
**Result**: Architect 4-spawn split (FB31-1) produced zero timeouts in FB34 but 3/4 timeouts in FB35. Code agents (models, auth) completed without timeout. Task sizing helps but is insufficient when agents enter post-write verification loops. H217 needs to be paired with H502 (termination rule) to be fully effective.

---


---

## H503: Agent Hangs Correlate with Cumulative Context Pressure, Not Verification Failures

**Status**: tested — not confirmed
**Proposed**: 2026-06-08
**Rationale**: E24, E24-F1, and E24-F2 all showed that verification failures —
whether trivial, complex, or genuinely novel — are fixed in ≤1 iteration with
clean termination. FB35 had 6 agent hangs after 10-15 min, but these agents were
spawned deep into a full fitness build with extensive preceding context,
multiple prior agent spawns, and accumulated tool calls. Experimental agents ran
in isolation with minimal context. The hang trigger may be context pressure
(building up over a long session) rather than the specific failure being fixed.
**Source**: E24-F2 analysis, FB35 retrospective
**Experiment**: Spawn a background agent after deliberately loading its context
with 50+ preceding tool calls (simulating a long build session). Then give it a
verification-failure task. Compare hang rate vs a fresh-context agent with the
same task.
**Expected**: High-context agent hangs; fresh-context agent terminates cleanly.
**Result**: NOT CONFIRMED — Agent with 8-file read load and 14 tool calls terminated cleanly in 60s. Context pressure threshold (hypothesized 50+ tool calls) not reached. Experiment inconclusive.
**Tested by**: E25

---


---

## H504: Agent Hangs Are Caused by Post-Write Perfectionism, Not Failure Correction Loops

**Status**: tested — not confirmed
**Proposed**: 2026-06-08
**Rationale**: E24-F2 Run 2 agent wrote correct code, passed all tests, and
immediately terminated. But FB35 reports describe agents "entering infinite
self-correction loops" after WriteFile + Shell verification. The E24-F2 agent
had a STOP instruction in its prompt. FB35 agents may have hung not because
they couldn't fix a failure, but because they kept trying to "improve" code
after tests already passed — adding unnecessary features, refactoring for
"cleanliness", or chasing minor lint warnings. An explicit "if tests pass,
STOP immediately" rule may prevent this.
**Source**: E24-F2 Run 2 observation, FB35 retrospective
**Experiment**: Spawn a background agent with a task that passes tests on the
first write. Half the agents get an explicit "STOP after tests pass" rule;
half do not. Measure whether the no-STOP cohort attempts post-pass refinements.
**Expected**: No-STOP cohort spends 2-3× more time on post-pass refinements;
some enter extended loops.
**Result**: [to be filled]
**Tested by**: [experiment ID or session]
