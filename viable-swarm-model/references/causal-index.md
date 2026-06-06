# VSM Causal Index — Master Linkage Registry

> **Purpose**: Single source of truth linking Builds → Hypotheses → Experiments → Mutations.
> **Updated by**: S5 after every build, coach Phase 5, gym Phase 5.
> **Read by**: vsm_meta at startup, vsm_process_auditor for completeness checks.
> **Schema version**: 2.0 (corrected 2026-06-04)

---

## Master Build Linkage Table (FB24+)

| Build | Score | Hypotheses Tested | Experiments Run | Mutations Applied | Effectiveness |
|-------|-------|-------------------|-----------------|-------------------|---------------|
| FB24 | 3.2 | H154, H203–H205 | — | FB24-1, FB24-2, H203–H205, python-pitfalls enum | — |
| FB25 | 4.0 | H203–H205, H40, H157, **H300** | E17¹ | python-pitfalls Celery, docker-pitfalls COPY, security-lessons worker, vsm_meta checkpoint, H206–H209, **FB25-S1 (H300)** | 4.0 |
| FB26 | 3.6 | H209, H210, H211 | E20 | FB26-1..FB26-5, FB26-S1 (H211), FB26-S2 (H210), FB26-S3 (H209), FB26-S4, FB26-S5, FB26-S6, FB26-A3 | 3.6 |
| FB27 | 3.4 | H302 | — | FB27-1..FB27-4 | 3.4 |
| FB28 | 3.8 | H214–H219, H213 | — | H217–H219, FB28-S3, FB28-S4, FB28-S5, FB28-A4, FB28-A5, S6, A6, A7, A8, A9, R3, R4 | 3.8 |
| FB29 | 3.6² | H217, H214 | — | M1–M7, PM1–PM5³, C1–C2 | 3.6 |
| FB30 | 3.6 | H301 | — | M-FB30-1..M-FB30-5 | 3.6 |
| FB31 | 3.8 | H301, H304, H302, H303 | — | FB31-1..FB31-5 | 3.8 |
| FB32 | — | H150, H151, H154 | Gym-Batch-FB32 | FB32-1..FB32-5 (probation) | — |
| FB33 | 6.3 | — | — | FB32-1 scored 2 (ineffective), FB32-2..FB32-5 scored 5 (effective) | 6.3 |

¹ **CORRECTION**: E17 tests H107, not H300. See [Known Broken Traces](#known-broken-traces).
² FB29 meta-report scored 4.2; trainer scored 3.6. Effectiveness uses trainer score.
³ PM1 and PM7 removed post-FB29. See mutation-state.md.

---

## Experiment → Hypothesis → Mutation Linkage

| Experiment | Hypothesis | Result | Mutation Applied | Build Validated |
|---|---|---|---|---|
| E15 | H105: Generic coder bypasses re-audit | CONFIRMED | vsm_backend_fix_agent prompt hardened | FB21+ |
| E16 | H106: vsm_meta catches process violations | CONFIRMED | No mutation needed | FB21+ |
| E17 | H107: Domain fix agents outperform generic | CONFIRMED | No mutation needed | FB21+ |
| E18 | H108: Stack skill reference validation | CONFIRMED | validate-agent-files.py updated | FB23 |
| E19 | H109: Knowledge broker auto-update | INCONCLUSIVE | Manual update required | FB25 |
| E20 | H209: Prompt-only mutation checkpoints bypassed | CONFIRMED | FB26-S3 structural hard gate | FB26 |
| Gym-Batch-FB32 | H150: Dependency verification prevents bad imports | CONFIRMED | python-pitfalls elevated to BLOCKER | FB32 |
| Gym-Batch-FB32 | H151: Pydantic `class Config:` deprecated | CONFIRMED | python-pitfalls elevated to BLOCKER | FB32 |
| Gym-Batch-FB32 | H154: `npm run build` as Phase 4 hard gate | CONFIRMED | testing-patterns new rule | FB32 |

---

## Active Hypotheses → Target Gaps

| Hypothesis | Status | Target Gap | Validation Build |
|---|---|---|---|
| H150 | CONFIRMED | — (dependency drift) | FB32 (gym) |
| H151 | CONFIRMED | — (Pydantic config) | FB32 (gym) |
| H154 | CONFIRMED | G2 (Phase 4 bypass) | FB24–FB32 |
| H157 | CONFIRMED | G3 (frontend stubs) | FB25 |
| H203 | CONFIRMED | — (enum type safety) | FB24–FB25 |
| H214 | CONFIRMED | G1 (foundation handoff) | FB28–FB29 |
| H217 | CONFIRMED | G9 (agent timeout) | FB28–FB29 |
| H300 | CONFIRMED | — (hook claims) | FB25 |
| H301 | CONFIRMED | — (architect task sizing) | FB30–FB31 |
| H302 | CONFIRMED | G6 (process audit bypass) | FB27–FB31 |
| H303 | CONFIRMED | — (pytest report persistence) | FB31 |
| H304 | CONFIRMED | — (tester split sizing) | FB31 |

---

## Known Broken Traces

> Traces that were discovered to be incorrect during the 2026-06-04 comprehensive audit.

### BT-1: FB25-S1 → E17 (FALSE)

**Incorrect linkage**: Early versions of `mutation-state.md` and `causal-index.md` recorded that mutation **FB25-S1** (false hook claim removal) was linked to experiment **E17**.

**Correct linkage**:
- **FB25-S1** targets hypothesis **H300** (Background subagents bypass hooks). It was validated by the FB25 build process and confirmed by empirical observation in FB25–FB29.
- **E17** tests hypothesis **H107** (Domain fix agents outperform generic coders). E17 was conducted during the FB21 era and confirmed in FB21+ builds.

**Root cause**: The experiment column in `mutation-state.md` Schema v1.0 was populated incorrectly for FB25-S1, conflating two unrelated empirical validations.

**Fix applied**: 2026-06-04. FB25-S1 now correctly links to H300 with no experiment ID (it was validated via build observation, not isolated experiment). E17 remains linked to H107.

---

## Causal Integrity Checks

**Check 1 — Forward traceability**: Can every build be traced to ≥1 hypothesis?
- FB24–FB32: ✅ All traceable

**Check 2 — Backward traceability**: Can every confirmed hypothesis be traced to ≥1 build or experiment?
- H150–H154, H157, H203, H214, H217, H300–H304: ✅ All traceable
- H210–H212: ⚠️ No build has isolated these (H210/H211 tested implicitly via FB26-S1/S2)

**Check 3 — Mutation coverage**: Are all mutations from last 5 builds in this index?
- FB28–FB32: ✅ Complete

**Check 4 — Experiment linkage**: Are all experiments linked to a hypothesis AND a mutation or build?
- E15–E20, Gym-Batch-FB32: ✅ Complete

---

*Last updated: 2026-06-04 by comprehensive audit*
*Schema: 2.0 (BT-1 correction applied)*
