# VSM Causal Index — Master Linkage Registry

> **Purpose**: Single source of truth linking Builds → Hypotheses → Experiments → Mutations.
> **Updated by**: S5 after every build, coach Phase 5, gym Phase 5.
> **Read by**: vsm_meta at startup, vsm_process_auditor for completeness checks.
> **Schema version**: 1.0

---

## Build → Hypothesis → Mutation Linkage (FB20+)

| Build | Score | Hypotheses Tested | Experiments Linked | Mutations Applied | Process Audit |
|-------|-------|-------------------|-------------------|-------------------|---------------|
| FB20 | 3.4 | H90-H93 | — | FB20-1..FB20-6 | — |
| FB21 | 3.7 | H94-H98 | — | L60, Check 58, FB21-8, FB21-24 | — |
| FB22 | 3.8 | H150-H153 | — | FB22-1, H150-H153 | — |
| FB23 | 3.2 | H154-H157 | — | H154-H157, M38-M41 | 70/100 |
| FB24 | 3.2 | H203-H205 | — | H203-H205, python-pitfalls enum | — |
| FB25 | 4.0 | H203-H205, H40, H157 | — | python-pitfalls Celery, docker-pitfalls COPY, security-lessons worker, vsm_meta checkpoint, H206-H209 | 82/100 |
| FB26 | 3.6 | H209 | — | FB26-S3, FB26-S4, FB26-S5, FB26-S6 | — |
| FB27 | 3.4 | H302 | — | FB27-1..FB27-4 | — |
| FB28 | 3.8 | H214-H219 | — | H217-H219, FB28-S3, FB28-S4, FB28-S5, FB28-A1-A5 | 70/100 |
| FB29 | 4.2 | H217, H214 | — | M1-M7 (GraphQL parity, enum 3.14, engine rule, test templates, JWT confusion, audit split, enum checklist) | — |

---

## Experiment → Hypothesis → Mutation Linkage

| Experiment | Hypothesis | Result | Mutation Applied | Build Validated |
|---|---|---|---|---|
| E15 | H105: Generic coder bypasses re-audit | CONFIRMED | vsm_backend_fix_agent prompt hardened | FB21+ |
| E16 | H106: vsm_meta catches process violations | CONFIRMED | No mutation needed | FB21+ |
| E17 | H107: Domain fix agents outperform generic | CONFIRMED | No mutation needed | FB21+ |
| E18 | H108: Stack skill reference validation | CONFIRMED | validate-agent-files.py updated | FB23 |
| E19 | H109: Knowledge broker auto-update | INCONCLUSIVE | Manual update required | FB25 |

---

## Active Hypotheses → Target Gaps

| Hypothesis | Status | Target Gap | Validation Build |
|---|---|---|---|
| H217 | CONFIRMED | G9 (agent timeout) | FB29 |
| H214 | CONFIRMED | G1 (foundation handoff) | FB28 |
| H215 | CONFIRMED | — (meta hallucination) | FB28 |
| H302 | CONFIRMED | G6 (process audit bypass) | FB27 |
| H154 | CONFIRMED | G2 (Phase 4 bypass) | FB25 |
| H157 | CONFIRMED | G3 (frontend stubs) | FB25 |
| H203 | CONFIRMED | — (enum type safety) | FB25 |
| H206 | CONFIRMED | — (auditor false positives) | FB25 |
| H208 | CONFIRMED | — (fix agent quality) | FB25 |
| H210 | UNTESTED | — (dockerignore ownership) | — |
| H211 | UNTESTED | — (CORS severity) | — |
| H212 | UNTESTED | — (port parity automation) | — |

---

## Mutation Lifecycle Tracker

| Mutation ID | Target Failure | Applied | Builds Tested | Effectiveness | Status |
|---|---|---|---|---|---|
| FB25-S1 | False hook claim removal | FB25 | 5 | Effective | Keep |
| FB25-S2 | Mutation checkpoint bypass | FB25 | 1 | Ineffective (1) | **REMOVED → R-3** |
| FB24-1 | Phase 4 bypass when 1 test fails | FB24 | 6 | Effective | Keep |
| FB24-2 | Enum type safety audit | FB24 | 6 | Effective | Keep |
| FB23-4 | Frontend build script verification | FB23 | 7 | Effective | Keep |
| FB21-8 | Security-lessons topical reorg | FB21 | 9 | Effective | Keep |
| FB21-24 | Process auditor spawn | FB21 | 9 | Effective | Keep |
| R19 | Contract repopulation | FB21 | 9 | Effective | Keep |
| R20 | Validate agent files script | FB21 | 9 | Effective | Keep |
| FB27-1 | UUID coercion `model_validator` | FB27 | 2 | Ineffective (2) | Redesigned → FB28 |

---

## Causal Integrity Checks

**Check 1 — Forward traceability**: Can every build be traced to ≥1 hypothesis?
- FB20: ⚠️ H90-H93 not in active hypotheses.md (archived)
- FB21-FB29: ✅ All traceable

**Check 2 — Backward traceability**: Can every active hypothesis be traced to ≥1 build?
- H210-H212: ❌ No build has tested these

**Check 3 — Mutation coverage**: Are all mutations from last 5 builds in this index?
- FB25-FB29: ✅ Complete

**Check 4 — Experiment linkage**: Are all experiments linked to a hypothesis AND a mutation?
- E15-E17: ✅ Complete
- E18-E19: ⚠️ Partial (no mutation for E19)

---

*Last updated: 2026-06-04 by comprehensive audit*

## CC-1
**Hypothesis**: N/A
**Experiment**: N/A
**Mutation**: PM1
**Target Failure**: FB26-S6 (process auditor broker scored check) was prompt-only and insufficient under time pressure. S5 skipped spawning vsm_process_auditor in 2 consecutive builds (FB28, FB29).
**Builds Tested**: MANUAL
**Result**: [pending — update after measurement]
**Score Trend**: [pending]


## CC-2
**Hypothesis**: N/A
**Experiment**: N/A
**Mutation**: PM2
**Target Failure**: `vsm_meta` claims artifacts exist in the meta-report without verifying them on disk, producing false claims like "Re-audit report artifact produced" when the file is absent.
**Builds Tested**: MANUAL
**Result**: [pending — update after measurement]
**Score Trend**: [pending]


## CC-3
**Hypothesis**: N/A
**Experiment**: N/A
**Mutation**: PM3
**Target Failure**: Mutation-state.md and mutation-log.md updates are systematically forgotten because S5 must manually run a script after every build. The auto-update script exists but is not self-enforcing.
**Builds Tested**: MANUAL
**Result**: [pending — update after measurement]
**Score Trend**: [pending]


## CC-4
**Hypothesis**: N/A
**Experiment**: N/A
**Mutation**: PM4
**Target Failure**: GraphQL admin override resolvers lack specificity — they check `if user.role == "admin"` but do not verify the admin role exists in the data model or that the requesting user is actually active.
**Builds Tested**: MANUAL
**Result**: [pending — update after measurement]
**Score Trend**: [pending]


## CC-5
**Hypothesis**: N/A
**Experiment**: N/A
**Mutation**: PM5
**Target Failure**: Python 3.14 changed `str(Enum.member)` from `"member"` to `"Class.member"`, breaking JWT claims, RBAC comparisons, and ownership checks that use `str(role)` instead of `role.value`.
**Builds Tested**: MANUAL
**Result**: [pending — update after measurement]
**Score Trend**: [pending]


## CC-6
**Hypothesis**: N/A
**Experiment**: N/A
**Mutation**: PM7
**Target Failure**: S5 manually fixes implementation code during builds, consuming orchestration context and bypassing agent learning loops. FB29 had 3+ manual S5 fixes.
**Builds Tested**: MANUAL
**Result**: [pending — update after measurement]
**Score Trend**: [pending]


## CC-7
**Hypothesis**: N/A
**Experiment**: N/A
**Mutation**: C1
**Target Failure**: FastAPI `@app.on_event("startup")` / `@app.on_event("shutdown")` is deprecated, harder to test, and encourages module-level engine instantiation.
**Builds Tested**: MANUAL
**Result**: [pending — update after measurement]
**Score Trend**: [pending]


## CC-8
**Hypothesis**: N/A
**Experiment**: N/A
**Mutation**: C2
**Target Failure**: Pydantic V2 `list[str]` settings fail when env var contains comma-separated values because Pydantic does not auto-split strings.
**Builds Tested**: MANUAL
**Result**: [pending — update after measurement]
**Score Trend**: [pending]

