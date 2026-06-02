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
| H157 | untested |
| H201 | untested |
| H202 | untested |
| H203 | untested |
| H[N+3] | untested |
| H[N+4] | untested |
| H206 | untested |
| H207 | untested |
| H208 | untested |
| H209 | untested |

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


## H157: Frontend pages generated as stubs (void-referenced imports, no real logic) correlate with missed integration checklist items

**Status**: untested
**Proposed**: 2026-05-26
**Rationale**: FB23 frontend pages (Dashboard, Jobs, Candidates, etc.) are all `<div>Name</div>` stubs. The integration report still PASSed them because they exist and routes are wired, not because they implement functionality.
**Source**: Fitness build FB23
**Experiment**: Add "Verify at least one page contains non-trivial data fetching/rendering" to integration checklist.
**Expected**: Next build has ≥1 page with actual GraphQL query execution and rendered data.
**Tested by**: —


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


## H203: SQLAlchemy `Mapped[Enum] = mapped_column(sa.String)` causes runtime `.value` AttributeErrors that no agent currently detects

**Status**: confirmed
**Proposed**: 2026-06-02
**Rationale**: FB24 `app/routers/stock.py:338` crashed with `AttributeError: 'str' object has no attribute 'value'` because `StockTransfer.status` was declared `Mapped[TransferStatus] = mapped_column(sa.String(50))`. SQLAlchemy loads the column as a plain `str` from the database, but the endpoint code called `.value` on it. All four audit agents (foundation, implementation, security, re-audit) missed this bug. The single failing pytest test correctly identified it, but the build proceeded past Phase 4 anyway.
**Source**: Fitness build FB24, Phase 4/8b
**Experiment**: Build a minimal FastAPI app with `class Role(str, enum.Enum)` and `Mapped[Role] = mapped_column(sa.String(20))`. Add an endpoint that calls `obj.role.value`. Run vsm_auditor on the codebase. Does it flag the type mismatch?
**Expected**: If auditor PASSes → confirmed (gap exists). If BLOCKER → rejected.
**Tested by**: FB24
**Result**: The enum `.value` crash was the ONLY bug caught by tests that ALL auditors missed. Auditor gap confirmed. Prevention rule should be added to `python-pitfalls`.

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

## H209: The Mutation Verification Checkpoint (`mutations-applied.md`) is bypassed because `vsm_meta` lacks tool-enforced authority to block Phase 8 completion

**Status**: untested
**Proposed**: 2026-06-02
**Rationale**: FB18-10 structural mutation mandated `mutations-applied.md` production. FB25 (and FB23, FB24 per meta-reflection.md Entry 2) produced no such file. Prompt-only instructions are insufficient; S5 attention degrades at session end.
**Source**: Fitness builds FB23, FB24, FB25, Phase 8b
**Experiment**: Add explicit `mutations-applied.md` presence check to `vsm_meta.md` output template. In next build, verify if the file exists before S5 declares completion.
**Expected**: If `vsm_meta.md` is updated → file exists in next build. If not → file absent again.
**Tested by**: —
