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
| H104 | untested |
| H152 | untested |
| H202 | tested |
| H217 | partially |
| H401 | testing |
| H402 | testing |
| H403 | testing |
| H404 | testing |
| H405 | testing |
| H406 | testing |
| H[N+3] | untested |
| H[N+4] | untested |
---


---


---


---

## H104: ApolloClient `uri` parameter in test environment causes stderr noise that does not fail tests but masks real client misconfiguration

**Status**: untested
**Proposed**: 2026-05-25
**Rationale**: FB21 frontend tests pass but emit `ApolloClient uri parameter` errors in stderr. `client.ts` uses `HttpLink({ uri: ... })` correctly, but test mocking may initialize `ApolloClient` differently.
**Source**: Fitness build FB21, Phase 4
**Experiment**: Inspect frontend test setup. Verify if ApolloClient is initialized with `uri` directly instead of `link`. Compare test ApolloClient init vs production ApolloClient init.
**Expected**: If test init uses `uri` parameter → confirmed. If test init uses `link` → rejected.
**Result**: [to be filled]
**Tested by**: [fitness build or gym experiment]

---


---


---


---

## H152: Pre-build environment smoke tests would catch package incompatibilities before code writing begins

**Status**: untested
**Proposed**: 2026-05-25
**Rationale**: FB22 discovered `strawberry-graphql==0.256.0` is incompatible with the installed pydantic version only after the build started and graphql.py was written. This wasted agent time and required S5 intervention.
**Source**: Fitness build FB22
**Experiment**: At Phase 0 self-test, add a step: "Run `python -c 'import strawberry; import pydantic'` and verify it succeeds." Run next build on the same environment.
**Expected**: Environment incompatibility detected at Phase 0, build halted or environment fixed before Phase 1.
**Tested by**: —

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

## H[N+3]: Native YAML custom subagents (via --agent-file) would improve agent consistency vs markdown prompts

**Status**: untested
**Proposed**: 2026-05-22
**Rationale**: Currently, custom agents (`vsm_architect`, `vsm_auditor`, etc.) are defined as markdown prompt files spawned via the `Agent` tool using built-in `subagent_type` values (`coder`, `explore`, `plan`). Kimi CLI supports native custom subagent definitions in YAML agent files with `--agent-file`, including tool restrictions (`exclude_tools`), inheritance (`extend`), and template variables (`system_prompt_args`). This could reduce prompt drift, enforce tool boundaries at the CLI level, and simplify maintenance. However, this requires session-level agent configuration, making it incompatible with the current skill-loading model (`extra_skill_dirs`). This hypothesis is **low priority** — only test if prompt drift or tool misuse becomes a measurable problem in fitness builds.
**Source**: CLI docs exploration
**Experiment**:
  1. Create `vsm-agent.yaml` defining all custom subagents with tool restrictions and inheritance
  2. Start session with `kimi --agent-file vsm-agent.yaml`
  3. Run 5 fitness builds with the YAML agent configuration
  4. Run 5 fitness builds with the current markdown prompt approach
  5. Compare: agent tool misuse rates, prompt consistency, build quality scores
**Expected**: YAML approach shows measurable reduction in agent tool misuse (e.g., auditor writing files, architect coding) and more consistent outputs. If no difference → markdown approach is sufficient; close hypothesis.
**Result**: [to be filled]
**Tested by**: [experiment ID or session]

---


---


---


---

## H[N+4]: A full product swarm (product + UX + research agents) would improve outcomes for problem-oriented prompts

**Status**: untested
**Proposed**: 2026-05-22
**Rationale**: The current skill handles prescriptive prompts well ("build X with Y") but has no product discovery phase for problem-oriented prompts ("users need Z"). A full product swarm with `vsm_product`, `vsm_ux`, and `vsm_researcher` agents could define user stories, acceptance criteria, and success metrics before architecture begins. The fitness builds have not yet tested whether problem-oriented inputs produce higher defect rates.
**Source**: Design discussion
**Experiment**:
  1. Collect 10 problem-oriented prompts
  2. Run with current skill — measure: does output match actual user need? Are acceptance criteria clear?
  3. Run with lightweight `vsm_product` agent (product brief + user stories only)
  4. Compare: does product agent reduce rework, improve user-facing outcomes?
**Expected**: Product-aware builds show 20%+ reduction in "wrong feature built" or "missing acceptance criteria" gaps in fitness reports
**Result**: [to be filled]
**Tested by**: [experiment ID or session]

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

## H401: Tool-Enforced GraphQL Stub Detection Prevents Stub Mutations Reaching Phase 6

**Status**: testing
**Proposed**: 2026-06-06
**Rationale**: FB34 probation mutation FB34-1 (GraphQL mutation completeness checklist) did not prevent six `INTERNAL_ERROR` stub mutations from reaching Phase 6. The prompt-only checklist was ignored until `vsm_auditor` flagged the parity gap in the implementation audit.
**Source**: Fitness build FB34, Phase 6 implementation audit
**Experiment**: Add a `scripts/check-graphql-stubs.py` hard gate invoked in Phase 3c and Phase 6. It introspects the Strawberry schema and fails if any `@strawberry.mutation` body contains only `pass`, `raise`, or returns a hard-coded `INTERNAL_ERROR` / `NotImplemented` payload. Run the next GraphQL-enabled build with the gate enabled.
**Expected**: Zero stub mutations reach the implementation audit; Phase 3c coordinator blocks on the gate instead of documenting parity gaps later.
**Result**: [to be filled]
**Tested by**: [experiment ID or session]

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

## H406: Skill Variety Metric Should Parse Agent Reports

**Status**: testing
**Proposed**: 2026-06-06
**Rationale**: `organism-vitals.md` in FB34 lists `integration-patterns` as an unused skill, yet `integration-contract.md` explicitly cites `integration-patterns` under "Skills consulted." The current metric counts skill reads only from S5 or Phase 0 load, not from agent reports, leading to undercounting and false variety deficits.
**Source**: Fitness build FB34, Phase 0 / Phase 6
**Experiment**: Refactor `scripts/organism-vitals.py` to grep `.kimi/*-report.md` and `.kimi/*-audit.md` for `Skills consulted:` / `Skills read:` headers and union those skill IDs with Phase 0 load. Compare the resulting skill variety score against the legacy score for FB34.
**Expected**: Skill variety for FB34 rises to ≥0.85 (from 0.75) because `integration-patterns`, `graphql-pitfalls`, and `dependency-drift-pitfalls` are confirmed consulted.
**Result**: [to be filled]
**Tested by**: [experiment ID or session]

