# Meta-Reflection — Skill-Level Performance Learning

> **Purpose**: Cross-build reflections on the viable-swarm-model skill's own
> performance. Synthesized from individual `meta-report.md` artifacts.
> **Location**: `~/vsm/viable-swarm-model/references/meta-reflection.md`
> **Read by**: `vsm_meta` at startup (if present)
> **Written by**: S5 during Phase 8, after reviewing `meta-report.md`

---

## Entry [N] — YYYY-MM-DD

**Builds**: [Which builds contributed this insight]
**Pattern**: [What systemic behavior was observed across multiple builds]
**Evidence**: [Specific scores, findings, or quotes from meta-reports]
**Implication**: [What this means for skill design]
**Action taken**: [What was changed in the skill as a result]

---

## Entry 1 — 2026-05-26

**Builds**: FB17, FB22, FB23
**Pattern**: Frontend build failures (`tsc -b`, `npm run build`) consistently leak
from Phase 4 into Phase 6 because the Phase 4 exit gate only checks test counts,
not build success.
**Evidence**: FB23 meta-report: "frontend `npm run build` was NOT run during
Phase 4 — it was deferred to Phase 6, where it failed."
**Implication**: The Phase 4 hard gate is incomplete. It must include frontend
production build verification alongside test counts.
**Action taken**: Added `npm run build` / `tsc -b` as mandatory Phase 4 gate in
`SKILL.md` (H154).

---

## Entry 2 — 2026-06-02

**Builds**: FB24
**Pattern**: Phase 4 hard gate (Pattern 46 / Test-First Exit Gate) is bypassed when exactly 1 test fails, especially if the failure is an exception rather than an assertion error. Additionally, SQLAlchemy `Mapped[Enum] = mapped_column(sa.String)` type mismatches are an entirely undetected bug class across all audit agents.
**Evidence**:
- FB24 independent test verification: 84 passed, 1 failed (`test_stock.py::test_update_transfer_status_invalid_transition` — `AttributeError: 'str' object has no attribute 'value'` at `stock.py:338`).
- Build proceeded through Phases 5, 6, 7, 8 without fixing this test.
- Foundation audit: 2 BLOCKERs, 11 ISSUEs — no enum type safety check.
- Implementation audit: 5 BLOCKERs, 8 ISSUEs — no enum type safety check.
- Security gate: 0 BLOCKERs, 2 MEDIUM, 4 LOW — missed the runtime-crash bug entirely.
- Re-audit: 0 BLOCKERs, 3 ISSUEs — checked 6 fix-wave items, missed the enum bug.
- No `mutations-applied.md` produced — Mutation Orphan failure mode (FB18-10 not enforced).
**Implication**:
1. The Test-First Exit Gate needs an explicit S5 verification command (not just a pattern in pattern-library.md).
2. A new anti-pattern is needed for SQLAlchemy String-mapped enum columns.
3. The Mutation Verification Checkpoint (FB18-10) must become a hard block, not a soft recommendation.
**Action taken**:
- Proposed 3 new hypotheses (H203, H204, H205) in `references/hypotheses.md`.
- Proposed append-only mutations to `anti-patterns.md`, `integration-checklist.md`, `security-lessons.md`.
- Proposed refinement mutations to `agents/vsm_auditor.md` and `SKILL.md` Phase 7.
- Proposed structural mutations to `SKILL.md` Phase 4 (hard gate enforcement) and Phase 8b (mutation checkpoint hard block).

---

## Entry 3 — 2026-06-02

**Builds**: FB4–FB24 (comprehensive)
**Pattern**: Fitness build scores have remained flat (3.2–4.0) for 24 builds and
80+ mutations. The peak was FB9 at 4.0 (2026-05-23). No sustained upward
trajectory exists despite continuous mutation.
**Evidence**:
- Score series: 3.6, 3.7, 3.6, 3.5, 3.9, **4.0**, 3.3, 3.7, 3.2, 3.6, 3.7,
  3.4, —, 3.6, 3.2, 3.4, 3.7, 3.8, 3.2, 3.2.
- Zero mutations have ever been removed for ineffectiveness.
- "Measured effect" field in mutation log is almost universally empty.
- Persistent failure modes: Phase 4 gate bypass (FB20, FB21, FB24), inline fixes
  (FB20, FB21, FB23), frontend stubs (FB23, FB24), architect trap propagation
  (FB16–FB18), security gate misses (FB20, FB21).
**Implication**:
1. **Detection ≠ Enforcement**. The skill has excellent detection (checklists,
   audits, tests catch issues) but poor enforcement at the S5 level. Process
   boundaries rely on S5 self-discipline, which degrades under time pressure.
2. **Mutation bloat without removal**. Rules accumulate but are never pruned.
   Fragile transfer (H65 reverted in FB15) indicates rules work once but don't stick.
3. **Effectiveness tracking is template-only**. The infrastructure exists
   (evaluation-rubric.md, fitness-report-template.md) but is not structurally
   enforced in agent output.
**Action taken**:
- Added Mutation Effectiveness Scoring to coach rubric (Phase 2a, 1–5 scale).
- Added regression build mode every 5 builds (Coach Phase 6).
- Added process auditor agent (`vsm_process_auditor`) for Phase 8b compliance.
- Added "mutation removal gate" concept: ineffective mutations should be removed.
- Added this meta-reflection entry to track the stagnation pattern.


---

## Entry 4 — 2026-06-02

**Builds**: FB25
**Pattern**: All 5 hypotheses under test (H203–H205, H40, H157) were validated successfully in a single build for the first time. The prevention-rule stack is maturing — no enum `.value` crash, no stub pages, no Phase 4 gate bypass, no inline fixes. However, the Mutation Verification Checkpoint (FB18-10) continues to be bypassed in practice despite being a structural mutation.
**Evidence**:
- FB25 meta-report: "No `mutations-applied.md` exists in `.kimi/` despite FB18-10 structural mutation mandating it."
- Agent scores: minimum 4/5 across all 8 agent types — highest since FB9.
- Independent test verification: 82 backend + 53 frontend passed, 0 failures. Phase 4 gate was legitimate.
- H203 (sa.Enum trap): All enum columns used `sa.Enum(...)`; no `.value` crash.
- H204 (hard gate): `.kimi/phase4-gate.md` written before Phase 5.
- H205 (ISSUE sweep): `issue-sweep.md` categorizes all unfixed issues.
- H40 (router imports): Consistent `APIRouter` usage verified.
- H157 (stub prevention): All 5 pages have live data fetching.
**Implication**:
1. Prevention rules work when they are specific and stack-skill-enforced.
2. Process-level mutations (like FB18-10) fail without tool-enforced or hook-level backing. Prompt-only instructions degrade under session-end time pressure.
3. The skill's detection capability is now stronger than its enforcement capability at the S5 level.
**Action taken**:
- Proposed structural mutation to enforce `mutations-applied.md` as hard block in Phase 8c.
- Proposed refinement mutation to `vsm_meta.md` to explicitly check for `mutations-applied.md`.
- Added 4 new hypotheses (H206–H209) to backlog for gym testing.

---

## Entry 5 — 2026-06-02

**Builds**: FB23
**Pattern**: Append-only mutations to 15+ agent files create structural debt (broken gotcha numbering, tool/role mismatches, missing report paths, YAML inconsistencies) that compounds silently until a comprehensive audit is forced.
**Evidence**:
- FB23-2 audit found broken sequential numbering in all 4 coder files (backend, frontend, backend fix, frontend fix).
- `vsm_product` (researcher role) retained `StrReplaceFile` in its YAML tool list despite "do not write code" instruction.
- `vsm_wiring.yaml` granted `SetTodoList` in markdown but not in YAML.
- Coordinator and security agents had `WriteFile` but no explicit `.kimi/` report path guidance.
- `vsm_explore.yaml` used quoted tool names while all other YAML files used unquoted.
**Implication**:
1. **Append-only mutation is necessary but insufficient**. Without periodic hygiene audits, structural inconsistencies proliferate.
2. **Markdown/YAML parity must be machine-checked**. Human editing of paired files drifts.
3. **Intermediate templates reduce drift surface**. DRY refactoring (5 templates replacing duplicated blocks in 15 agents) cuts the number of places inconsistencies can hide.
**Action taken**:
- Created `validate-agent-files.py` with checks for: sequential numbering, forbidden keywords, tool/markdown parity, Jinja2 include resolution.
- Added 5 intermediate templates (`vsm-coder`, `vsm-tester`, `vsm-fixer`, `vsm-researcher`, `vsm-reporter`) and rewired all 15 leaf agents.
- Standardized YAML tool list format to unquoted.

---

## Entry 6 — 2026-06-02

**Builds**: FB25
**Pattern**: The skill claimed enforcement infrastructure ("13 active VSM hooks") that empirical testing proved false for background subagents, creating a credibility gap between claimed and actual capabilities.
**Evidence**:
- FB25 fitness coach evaluation (H300) explicitly tested hook firing on 8 background subagent types.
- Result: **0 of 8 expected hooks fired**. `BackgroundAgentRunner` does not propagate the hook engine.
- Background agents perform ~90% of implementation/audit/testing work; foreground agents (S5, occasional meta) are the only ones actually hook-enforced.
- The claim appeared in build prompts, risking user trust if contradicted by observed behavior.
**Implication**:
1. **Detection ≠ Enforcement ≠ Claimed Enforcement**. The skill has three layers: (a) prompt-hardened rules, (b) kimi-cli hooks for foreground agents, (c) claimed hooks for all agents. Only (a) and (b) are real.
2. **Honesty about capability limits is a meta-system requirement**. False claims undermine the algedonic loop — if S5 believes hooks enforce rules on background agents, it relaxes prompt-level vigilance.
3. **Process-level mutations need tool-enforced or architectural backing**, not just documentation claims.
**Action taken**:
- FB25-S1 structural mutation removed "13 active VSM hooks" claim from build prompts.
- Updated SKILL.md to distinguish foreground vs background hook enforcement.
- Added this as a meta-learning case: "verify claimed infrastructure before relying on it."

---

## Entry 7 — 2026-06-02

**Builds**: FB23
**Pattern**: Cross-file integration contracts (backend↔frontend auth token key, role enum, GraphQL camelCase, CORS origin, error shape, WebSocket events) decay to empty headings after multiple append-only mutations.
**Evidence**:
- FB23-3 found `vsm_backend_coder.md` and `vsm_frontend_coder.md` both contained "Contracts" section headings with **zero content** beneath.
- Six reciprocal contracts were missing entirely. FB23 produced auth response mismatches (`token` vs `access_token`), GraphQL field case errors, and CORS origin gaps — all failure modes these contracts were designed to prevent.
- Contracts were present in earlier builds (FB21) but were truncated during subsequent refinement mutations (R19) without verification.
**Implication**:
1. **Contracts degrade when not actively tested**. Presence of a heading is not presence of content.
2. **Validator must enforce minimum contract completeness**. Automated check for heading + non-empty body + all 6 required subsections.
3. **Domain-specific coder prompts are the delivery mechanism for contracts**. If the contract is not in the agent's prompt, the agent will not honor it.
**Action taken**:
- R19 repopulated all 6 reciprocal contracts in both coder files.
- Added contract completeness check to `validate-agent-files.py` (minimum content length under each Contracts heading).
- Added shared-contract.md as a standalone file referenced by both backend and frontend coder agents.

---

## Entry 8 — 2026-06-02

**Builds**: FB1–FB25 (comprehensive ecosystem audit)
**Pattern**: A full audit of the VSM skill ecosystem (main + coach + gym) revealed that the organism has **all the organs of a learning system but none of the circulation**. Detection is excellent; enforcement is honor-system; measurement is 2% complete; removal is zero; cross-skill integration is broken.
**Evidence**:
- 99 mutations logged, 0 removed, 2% measured effect fill rate
- 5 ineffective mutations in portfolio, cemetery empty, removal gate never triggered
- Knowledge broker empty after 25 builds due to fatal regex bug in hook script
- 43 "MANDATORY" phrases in SKILL.md, all prompt-level (honor system)
- Fitness scores flat at 3.2–4.0 for 24 builds despite 80+ mutations
- 2 contradictions and 6 duplicate rules found in agent prompts
- Regression build mechanism (every 5th build) has never been executed
**Implication**:
1. **Documentation theater is the primary failure mode**. The skill creates artifacts (logs, rubrics, cemeteries, portfolios) but does not execute the processes they represent.
2. **Honor-system enforcement degrades under pressure**. S5 self-discipline is unreliable; every hard gate needs a verifiable artifact.
3. **Cross-skill integration requires structured shared memory**. The knowledge broker must have a schema, mandatory consumption, and staleness checks.
4. **Mutation lifecycle needs causal linkage**. Experiment IDs → Hypothesis IDs → Mutation IDs → Build IDs must be explicitly tracked.
**Action taken** (comprehensive audit implementation):
1. **Knowledge broker redesigned**: Structured schema with Active Gaps, Confirmed Patterns, Ineffective Mutations, Next Build Traps, Session Append Log. Hook script regex fixed.
2. **Mutation state tracking created**: `references/mutation-state.md` with unified lifecycle tracking (probation → effective/monitor/ineffective → removed).
3. **Cemetery populated**: 2 ineffective mutations (FB19-7, FB23-3) formally removed with rationale.
4. **Agent prompt fixes**: Resolved 2 contradictions (Context Budget vs auditor thoroughness; HALT vs proceed), removed 6 duplicate rules, extracted redundant re-audit artifacts.
5. **SKILL.md strengthened**: Phase 0 now mandates knowledge-broker.md and mutation-state.md. New Gate Artifact Protocol section maps every phase transition to a verifiable artifact.
6. **Phase 8c-ii hardened**: Requires mutations-applied.md + mutation-state.md update + ineffective mutation removal before completion. Process auditor checks broker freshness.
7. **Skill-state updated**: New targets for FB26–FB30: ≥2 removals per 5 builds, ≥80% measured effect fill rate, 0 gate bypasses.
**Expected effect**: FB26 will be the first build where:
- All phase transitions have verifiable artifacts
- Mutations are tracked from birth to death
- Cross-skill learning flows through the knowledge broker
- Ineffective rules are removed, not just flagged

---

## FB26-A3: Score Trend Tracking Rule

**Status**: Active (FB26-sourced)
**Type**: append-only
**Applies to**: vsm-fitness-coach, vsm_meta

Every fitness report MUST include a **Score Trend** table at the top of the Executive Summary:

```markdown
## Score Trend
| Build | Score | Delta | Primary Gap | Process or Code? |
|-------|-------|-------|-------------|------------------|
| FB24  | 4.2   | —     | —           | —                |
| FB25  | 4.0   | -0.2  | H209 bypass | Process          |
| FB26  | 3.6   | -0.4  | H209 + foundation collapse | Process |
```

**Regression Alarm**: If score drops > 0.3 from previous build, the report MUST:
1. Flag the drop in **bold** in the Executive Summary
2. Identify the root cause hypothesis (e.g., "H209 confirmed — 4th consecutive bypass")
3. Propose a structural mutation if the gap is process-related
4. Elevate the severity of any deferred issues that contributed to the drop

**Rationale**: FB26 dropped from 4.0 → 3.6 (-0.4) but this was buried in the phase scores table. No regression alarm fired. Explicit trend tracking makes decay visible before it becomes entrenched.
