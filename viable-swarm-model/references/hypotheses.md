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
|------------|--------|
| H104 | untested |
| H150 | untested |
| H151 | untested |
| H152 | untested |
| H153 | untested |
| H154 | untested |
| H155 | untested |
| H156 | untested |
| H201 | untested |
| H202 | untested |
| H[N+3] | untested |
| H[N+4] | untested |
| H206 | untested |
| H207 | untested |
| H208 | untested |

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

## H150: Requiring agents to verify dependencies against requirements.txt before importing would prevent 100% of non-existent library usage

**Status**: untested
**Proposed**: 2026-05-25
**Rationale**: FB22 graphql.py agent used `strawberry_sqlalchemy_mapper` — a third-party library not in requirements.txt. The agent spent 15+ minutes trying to verify imports before failing. No existing rule forces agents to check requirements.txt before adding new imports.
**Source**: Fitness build FB22
**Experiment**: Add "Before importing any non-stdlib library, verify it exists in requirements.txt or package.json" to vsm_backend_coder and vsm_frontend_coder gotchas. Run next fitness build and count instances of agents using libraries not in dependency manifests.
**Expected**: Zero instances of non-existent library usage in next build.
**Tested by**: —

---

## H151: Elevating Pydantic `class Config` deprecation from ISSUE to BLOCKER would eliminate the pattern from all new code

**Status**: untested
**Proposed**: 2026-05-25
**Rationale**: FB22 produced 9 router files using `class Config:` inside Pydantic BaseModel subclasses, generating 201 pytest warnings. The current vsm_backend_coder prompt mentions this as a deprecation avoidance gotcha but does not elevate it to BLOCKER.
**Source**: Fitness build FB22
**Experiment**: Update vsm_backend_coder.md to state: "`class Config:` inside Pydantic models is a BLOCKER. Use `model_config = ConfigDict(...)` instead." Run next fitness build and grep for `class Config:` in new Python files.
**Expected**: Zero occurrences of `class Config:` in new code.
**Tested by**: —

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

## H153: Standardizing Vite alias key as `"@"` (not `"@/"`) would prevent production build failures

**Status**: untested
**Proposed**: 2026-05-25
**Rationale**: FB22 frontend scaffold agent created `vite.config.ts` with alias `"@/": path.resolve(__dirname, "./src/")`. TypeScript compilation passed, but Vite's Rollup failed to resolve `@/graphql/queries` in production build. Changing to `"@": path.resolve(__dirname, "./src")` fixed it.
**Source**: Fitness build FB22
**Experiment**: Update vsm_frontend_coder.md scaffold template to use `"@"` alias key. Run next frontend build and verify `npm run build` succeeds without alias resolution errors.
**Expected**: Zero alias resolution failures in production builds.
**Tested by**: —

---

## H154: Requiring `npm run build` as a Phase 4 hard gate would prevent TypeScript/build failures from leaking into Phase 6

**Status**: untested
**Proposed**: 2026-05-26
**Rationale**: FB23 frontend build failed in Phase 6 because `tsc -b` errors (unused imports, vite config type mismatch) were not caught in Phase 4.
**Source**: Fitness build FB23
**Experiment**: Add "Frontend `npm run build` must pass" to Phase 4 exit criteria in next build.
**Expected**: Zero build failures discovered in Phase 6.
**Tested by**: —

---

## H155: Exhaustive module-level settings audit across ALL Python files (not just `main.py`) would catch 100% of import-time env side effects

**Status**: untested
**Proposed**: 2026-05-26
**Rationale**: FB23 wiring agent audited only `main.py`, `main.tsx`, `App.tsx` and missed `celery_app.py` module-level instantiation.
**Source**: Fitness build FB23
**Experiment**: Update `vsm_wiring` checklist to grep for `get_settings()` and `Settings()` in all `*.py` files.
**Expected**: Zero module-level instantiation orphans in next build.
**Tested by**: —

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

## H201: Custom agent files reduce per-subagent context usage by >30% vs prompt injection

**Status**: untested
**Proposed**: 2026-05-26
**Rationale**: In the old architecture, the entire agent definition (role, job, 16 gotchas, tool list) was embedded as a user prompt into `subagent_type="coder"`. With custom agent files, this content becomes a system prompt loaded once at agent initialization. The task prompt only needs the specific task context. This should significantly reduce input tokens per subagent turn.
**Source**: Custom agent file migration
**Experiment**: Compare subagent turn token usage in FB23 (custom agent files) vs FB22 (prompt injection). Measure input tokens for comparable backend coder tasks.
**Expected**: >30% reduction in per-subagent input tokens.
**Tested by**: —

---

## H202: Tool-enforced read-only boundaries prevent auditor "helpfulness" override better than prompt-only instructions

**Status**: untested
**Proposed**: 2026-05-26
**Rationale**: In the old architecture, auditor read-only status was declared in the user prompt. In a real build, an auditor might be socially engineered or "helpfully" attempt to fix a BLOCKER it finds. With custom agent files, the auditor's YAML explicitly excludes `WriteFile`, `StrReplaceFile`, and `Shell` from its tool list. Even if the model wants to help, it cannot call write tools.
**Source**: Custom agent file migration
**Experiment**: Deliberately ask the auditor subagent to write a file or fix a BLOCKER in FB23. Measure refusal rate and whether the refusal cites tool absence vs role policy.
**Expected**: 100% refusal rate with explicit tool-absence citation.
**Tested by**: —

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

## H206: Auditor batch-size limit (≤10 files) eliminates ≥50% of BLOCKER-level false positives in builds with >15 source files

**Status**: untested
**Proposed**: 2026-06-02
**Rationale**: FB25 implementation audit reviewed ~25 files and produced 0 BLOCKERs (all ISSUEs). FB13 had 3 BLOCKER false positives on 26 files before the batch limit was introduced. FB25 had 0 false positives. Correlation suggests the limit works, but sample size = 1.
**Source**: Fitness build FB25, Phase 3b
**Experiment**: Run gym experiment: audit identical codebase with batch limit ON vs OFF. Count BLOCKER false positives.
**Expected**: Batch-limit ON produces ≤1 false positive; OFF produces ≥2.
**Tested by**: —

---

## H207: Phase 3c Mid-Wave S2 Check catches contract drift before Phase 3b auditor, reducing Phase 3b BLOCKER count by ≥30%

**Status**: untested
**Proposed**: 2026-06-02
**Rationale**: FB25 had 0 BLOCKERs in Phase 3b. Prior builds (FB4–FB7) without Phase 3c averaged 2.3 BLOCKERs in Phase 3b from GraphQL field drift, auth contract mismatch, and WebSocket event name drift. Correlation is suggestive but not causal — prevention rules also matured between FB7 and FB25.
**Source**: Fitness build FB25, Phase 3c/3b
**Experiment**: Run regression build on FB4-equivalent spec with Phase 3c enabled vs disabled. Measure Phase 3b BLOCKER count.
**Expected**: Phase 3c enabled → ≤1 BLOCKER in 3b; disabled → ≥2 BLOCKERs.
**Tested by**: —

---

## H208: Domain-specific fix agents produce fewer test regressions than generic coder agents when fixing security findings

**Status**: untested
**Proposed**: 2026-06-02
**Rationale**: FB25 fix wave modified 6 files; full test suite went from 80 → 82 tests with 0 regressions. Generic coder in FB21 fix wave broke 4 unrelated GraphQL tests. Sample is small and confounded by build complexity differences.
**Source**: Fitness build FB25, Phase 7
**Experiment**: Gym dry-run: inject identical CRITICAL findings into minimal FastAPI app. Fix with `vsm_backend_fix_agent` vs generic `coder` agent. Measure test pass rate post-fix.
**Expected**: Domain agent: 100% pass rate, 0 regressions. Generic coder: ≤90% pass rate.
**Tested by**: —

---

## H210: `.dockerignore` absence persists because no agent owns its creation in the current task topology

**Status**: untested
**Proposed**: 2026-06-03
**Rationale**: FB26 foundation audit B5 flagged missing `.dockerignore`. DevOps agent created Dockerfiles but not `.dockerignore`. The scaffold checklist in vsm_devops_coder does not include it.
**Source**: Fitness build FB26, Phase 2
**Experiment**: Add `.dockerignore` to vsm_devops_coder scaffold checklist. Run next fitness build and verify `.dockerignore` exists in build directory.
**Expected**: `.dockerignore` present in 100% of builds with Dockerfiles.

---

## H211: CORS wildcards persist because `security-patterns` severity calibration labels them LOW

**Status**: untested
**Proposed**: 2026-06-03
**Rationale**: FB26 security gate rated `allow_methods=["*"]` and `allow_headers=["*"]` as LOW. They were deferred and remain unfixed. Elevating to MEDIUM would force fix.
**Source**: Fitness build FB26, Phase 5
**Experiment**: Elevate CORS wildcard from LOW → MEDIUM in security-patterns. Run next build and check if CORS wildcards are fixed.
**Expected**: Zero CORS wildcards in final build.

---

## H212: No automated cross-reference check exists between docker-compose service ports and `.env.example` defaults

**Status**: untested
**Proposed**: 2026-06-03
**Rationale**: FB26 `.env.example` had `VITE_WS_URL=ws://localhost:8000` but docker-compose realtime service exposes port 8001. Caught by coordinator but never fixed.
**Source**: Fitness build FB26, Phase 5/6
**Experiment**: Add port parity check to vsm_coordinator contract validation. Run next build and verify port matches.
**Expected**: Zero port mismatches in next build.

---

## H213: `mutation-state.md` is not updated because S5 lacks a concrete, copy-pasteable command/template

**Status**: untested
**Proposed**: 2026-06-03
**Rationale**: FB26 meta-report noted mutation-state.md has no measured effects from this build's S5. The backfill table exists in the fitness report but S5 must manually transcribe it. A template or hook would automate this.
**Source**: Fitness build FB26, Phase 8b
**Experiment**: Add a concrete shell command or template to SKILL.md Phase 8c-ii that S5 can copy-paste. Run next build and check if mutation-state.md is updated.
**Expected**: mutation-state.md updated within 5 minutes of mutations-applied.md creation.


---

## FB28 Hypothesis Updates

### H213 Update
**Status**: testing → monitor
**Tested by**: FB28
**Result**: S5 did NOT manually update mutation-state.md. Session-end hook status pending. Cannot confirm until session terminates.

---

## H214: Check 16 early handoff verification prevents late BLOCKERs
**Status**: confirmed
**Proposed**: 2026-06-03
**Tested by**: FB28
**Result**: Check 16 run in Phase 2b caught auth raw-dict returns (BLOCKER). Zero handoff BLOCKERs discovered in Phase 3c. Fix applied before implementation wave completed.
**Rationale**: Early verification gates are worth the overhead. Should be mandatory in Tier 2+ builds.
**Source**: Fitness build FB28, Phase 2b
**Experiment**: Run Check 16 in Phase 2b of next build. Count handoff BLOCKERs in Phase 3c.
**Expected**: Zero handoff BLOCKERs in Phase 3c.

---

## H215: vsm_meta file verification protocol prevents hallucination
**Status**: confirmed
**Proposed**: 2026-06-03
**Tested by**: FB28
**Result**: Meta agent verified file existence with `ls -la` before claiming files missing. No hallucinated missing files in meta-report. All file references accurate.
**Rationale**: File verification protocol prevents false claims about missing artifacts.
**Source**: Fitness build FB28, Phase 8b
**Experiment**: Continue requiring `ls -la` verification in meta agent prompt. Monitor for false claims.
**Expected**: Zero hallucinated missing files.

---

## H216: Casing convention contract prevents camelCase↔snake_case drift
**Status**: confirmed
**Proposed**: 2026-06-03
**Tested by**: FB28
**Result**: Explicit camelCase declaration in shared-contracts.md ensured all schemas, GraphQL queries, and TypeScript interfaces aligned. Zero casing-related test failures. Frontend build green. GraphQL introspection shows camelCase fields.
**Rationale**: Explicit architectural contracts prevent cross-layer drift.
**Source**: Fitness build FB28, Phase 1
**Experiment**: Continue requiring casing declaration in shared-contracts.md. Monitor for casing failures.
**Expected**: Zero casing-related test failures.

---

## H217: Agent timeout is the primary drag on Tier 2+ build scores
**Status**: untested
**Proposed**: 2026-06-03
**Rationale**: FB28 had 5 agent timeouts (backend_coder, frontend_coder, backend_tester, frontend_tester, foundation_auditor). S5 had to manually complete foundation audit, write tests, fix auth returns, and wire main.py. This forced S5 into coding tasks that should be agent-owned.
**Source**: Fitness build FB28, Phase 2/4
**Experiment**: Split Tier 2+ agent tasks into smaller chunks (<500 lines per spawn). Measure timeout rate.
**Expected**: Timeout rate drops from 5/10 to ≤1/10.

---

## H218: GraphQL context getter must reference imported function, never lambda/static dict
**Status**: untested
**Proposed**: 2026-06-03
**Rationale**: FB28 main.py used `context_getter=lambda: {"settings": settings}` which broke all authenticated GraphQL. No existing skill rule checks this.
**Source**: Fitness build FB28, Phase 3
**Experiment**: Add rule to graphql-pitfalls. Next build with GraphQL — verify no placeholder lambdas.
**Expected**: Zero GraphQL context getter lambdas.

---

## H219: Pydantic `type` statement + `Field(alias=...)` produces warnings
**Status**: untested
**Proposed**: 2026-06-03
**Rationale**: FB28 pytest output had 100+ `UnsupportedFieldAttributeWarning` about `alias`/`validation_alias`/`serialization_alias` on `Field()` when used with Python 3.12+ `type` statement.
**Source**: Fitness build FB28, Phase 4
**Experiment**: Add rule to python-pitfalls. Next build — monitor warning count.
**Expected**: Zero `UnsupportedFieldAttributeWarning` in test output.

---

## FB30 Hypothesis Updates

### H217: Agent task sizing ≤500 lines per spawn prevents timeouts
**Status**: partially confirmed
**Tested by**: FB30
**Result**: Backend code agents completed without timeout (improvement). Architect and backend tester still timed out. H217 scope is too narrow — covers implementation agents but not design/test agents.
**Rationale**: Code-writing agents benefit from smaller tasks; design agents producing multi-document architecture specs still exceed timeout limits.

### H218: GraphQL context getter must reference imported function, never lambda/static dict
**Status**: confirmed
**Tested by**: FB30
**Result**: `get_graphql_context` is imported function in `graphql.py`. Zero lambda usage. Context builder works correctly.

### H219: Pydantic `type` statement + `Field(alias=...)` produces warnings
**Status**: confirmed
**Tested by**: FB30
**Result**: `UnsupportedFieldAttributeWarning` present in test output but non-functional. Warning is cosmetic; no test failures or runtime errors.

### H220: GraphQLRouter prevents 307 redirect issues vs ASGI mount
**Status**: confirmed
**Tested by**: FB30
**Result**: `app.mount("/graphql", GraphQL(...))` caused 307 redirects on POST. Switching to `strawberry.fastapi.GraphQLRouter` with `app.include_router` fixed the issue. All GraphQL tests pass.

### H221: SQLite UUID compatibility requires explicit bind processor
**Status**: confirmed
**Tested by**: FB30
**Result**: Tests failed on `gen_random_uuid()` (PostgreSQL-only) and UUID type binding. Required `default=uuid.uuid4` in models and bind processor patch in conftest.

### H222: S5 manual work cap (≤1 file) cannot be enforced by prompt alone
**Status**: confirmed
**Tested by**: FB30
**Result**: S5 manually wrote 5+ files due to agent timeouts. Process audit scored this 6/10. Prompt-only cap fails under time pressure.


### H301: Architect 5-spawn split prevents timeout vs 3-spawn split
**Status**: untested
**Proposed**: 2026-06-04
**Rationale**: FB31 showed 3-spawn split insufficient — api-spec.md (2085 lines) and data-model+shared-contracts still timed out. Need finer granularity: architecture.md, api-spec.md, data-model.md, shared-contracts.md, sio-graphql-spec.md as 5 separate spawns.
**Source**: Fitness build FB31
**Experiment**: Run FB32 with 5-spawn architect. Measure timeout rate.
**Expected**: 0 timeouts across all 5 spawns

### H302: Coordinator GraphQL schema introspection check prevents frontend-backend decoupling
**Status**: untested
**Proposed**: 2026-06-04
**Rationale**: FB31 coordinator missed that frontend queries.ts referenced 10+ non-existent backend schema fields. Current Check 24 only verifies imports, not field existence.
**Source**: Fitness build FB31
**Experiment**: Add coordinator check that runs `strawberry.export_schema()` and cross-references every field in queries.ts against exported schema.
**Expected**: Coordinator catches schema mismatch before implementation phase ends

### H303: Persistent pytest report requirement prevents phase4-gate inflation
**Status**: untested
**Proposed**: 2026-06-04
**Rationale**: FB31 phase4-gate.md falsely claimed 50 tests passed when actual count was 46. S5 copied from agent reports without verification.
**Source**: Fitness build FB31
**Experiment**: Require `pytest --collect-only` or `pytest -v > pytest-report.md` before writing gate document. Gate must cite persistent report file.
**Expected**: Zero inflated test counts in gate documents

### H304: 3-sub-wave tester split prevents timeout better than 2-sub-wave
**Status**: untested
**Proposed**: 2026-06-04
**Rationale**: FB31 H223 2-sub-wave split had split 2 timeout. Need 3 sub-waves: auth/recipes, ingredients/meal-plans/shopping, GraphQL/social.
**Source**: Fitness build FB31
**Experiment**: Run FB32 with 3-sub-wave tester. Measure timeout rate.
**Expected**: All 3 tester spawns complete within timeout
