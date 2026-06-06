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
| H153 | untested |
| H155 | untested |
| H156 | untested |
| H201 | untested |
| H202 | untested |
| H213 | monitor |
| H217 | partially |
| H[N+3] | untested |
| H[N+4] | untested |
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

## H153: Standardizing Vite alias key as `"@"` (not `"@/"`) would prevent production build failures

**Status**: untested
**Proposed**: 2026-05-25
**Rationale**: FB22 frontend scaffold agent created `vite.config.ts` with alias `"@/": path.resolve(__dirname, "./src/")`. TypeScript compilation passed, but Vite's Rollup failed to resolve `@/graphql/queries` in production build. Changing to `"@": path.resolve(__dirname, "./src")` fixed it.
**Source**: Fitness build FB22
**Experiment**: Update vsm_frontend_coder.md scaffold template to use `"@"` alias key. Run next frontend build and verify `npm run build` succeeds without alias resolution errors.
**Expected**: Zero alias resolution failures in production builds.
**Tested by**: —

---


---

## H155: Exhaustive module-level settings audit across ALL Python files (not just `main.py`) would catch 100% of import-time env side effects

**Status**: rejected
**Proposed**: 2026-05-26
**Rationale**: FB23 wiring agent audited only `main.py`, `main.tsx`, `App.tsx` and missed `celery_app.py` module-level instantiation.
**Source**: Fitness build FB23
**Experiment**: Update `vsm_wiring` checklist to grep for `get_settings()` and `Settings()` in all `*.py` files.
**Expected**: Zero module-level instantiation orphans in next build.
**Tested by**: E23
**Result**: REJECTED — `vsm_wiring` agent already performs exhaustive audit across ALL `*.py` files. Module-level `Settings()` in `celery_app.py` was correctly flagged as BLOCKER. No skill mutation needed.

---


---

## H156: Dependency manifest-environment parity check after Phase 0 fixes would prevent reproducibility failures

**Status**: untested
**Proposed**: 2026-05-26
**Rationale**: FB23 Phase 0 upgraded `strawberry-graphql` from 0.235.2 → 0.316.0 but `requirements.txt` still specified 0.235.2, which is incompatible with pydantic 2.13.4. A clean `pip install -r requirements.txt` fails.
**Source**: Fitness build FB23
**Experiment**: Add "After any Phase 0 environment fix, update `requirements.txt` / `package.json` to match resolved versions" to Phase 0 checklist.
**Expected**: `requirements.txt` installs cleanly in a fresh venv in next build.
**Tested by**: —

---


---

## H201: Custom agent files reduce per-subagent context usage by >30% vs prompt injection

**Status**: confirmed
**Proposed**: 2026-05-26
**Rationale**: In the old architecture, the entire agent definition (role, job, 16 gotchas, tool list) was embedded as a user prompt into `subagent_type="coder"`. With custom agent files, this content becomes a system prompt loaded once at agent initialization. The task prompt only needs the specific task context. This should significantly reduce input tokens per subagent turn.
**Source**: Custom agent file migration
**Experiment**: Compare subagent turn token usage in FB23 (custom agent files) vs FB22 (prompt injection). Measure input tokens for comparable backend coder tasks.
**Expected**: >30% reduction in per-subagent input tokens.
**Tested by**: E22
**Result**: CONFIRMED — 85.2% reduction in task prompt character count (332 vs 2248 chars). Custom agent file architecture validated.

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

## H213: `mutation-state.md` is not updated because S5 lacks a concrete, copy-pasteable command/template

**Status**: confirmed
**Proposed**: 2026-06-03
**Rationale**: FB26 meta-report noted mutation-state.md has no measured effects from this build's S5. The backfill table exists in the fitness report but S5 must manually transcribe it. A template or hook would automate this.
**Source**: Fitness build FB26, Phase 8b
**Experiment**: Add a concrete shell command or template to SKILL.md Phase 8c-ii that S5 can copy-paste. Run next build and check if mutation-state.md is updated.
**Expected**: mutation-state.md updated within 5 minutes of mutations-applied.md creation.
**Tested by**: FB33
**Result**: CONFIRMED — S5 did NOT update mutation-state.md during Phase 8b. Update only happened after process auditor (30/100) explicitly flagged the gap. Even with `mutations-applied.md` present, S5 skipped the step under time pressure. Tool-enforced gate needed, not just a template.


---

## FB28 Hypothesis Updates

### H213 Update
**Status**: confirmed
**Tested by**: FB33
**Result**: S5 updated mutation-state.md and causal-index.md only AFTER process audit flagged them missing. Prompt-only/template-based discipline insufficient. Need tool-enforced gate.

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

