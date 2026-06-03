# VSM Knowledge Broker — Cross-Skill Digest

> **Updated by**: Session-end hook, fitness coach Phase 5, gym Phase 5
> **Read by**: All three skills at Phase 0 (MANDATORY)
> **Schema version**: 1.0
> **Last updated**: 2026-06-02

---

## How to Use This File

**Main skill (Phase 0)**: Read this file BEFORE reading other references. Adjust build strategy based on active gaps and confirmed patterns.

**Coach (Phase 0a)**: Read this file to learn main skill's recent gaps and gym's confirmed patterns. Design build traps that target known weaknesses.

**Gym (Phase 0)**: Read this file to learn main skill's recurring failures and coach's scored gaps. Prioritize hypotheses that address active pain points.

**Staleness check**: If this file is >7 days old, emit algedonic: "Knowledge broker stale. Cross-skill learning may be impaired."

---

## Active Gaps (Confirmed, Unfixed)

> Gaps that have recurred in 2+ builds and have no effective mutation preventing them.

| ID | Gap | First Seen | Last Seen | Mutations Attempted | Status |
|---|---|---|---|---|---|
| G1 | Foundation BLOCKERs in every build | FB1 | FB25 | R19, R20, FB21-8 | Partially effective — still recurring |
| G2 | Phase 4 gate bypass when 1 test fails | FB20 | FB24 | FB24-1, FB25-S1 | PENDING — FB25 did not bypass |
| G3 | Frontend stub pages (no live data fetch) | FB21 | FB24 | FB22-2, H157 | Ineffective — recurred FB23, FB24 |
| G4 | Inline fixes during Phase 6/7 boundary | FB20 | FB23 | FB23-3, FB25-S2 | Ineffective — recurred FB23 |
| G5 | Integration ISSUEs orphaned (not fixed or documented) | FB21 | FB25 | FB24-2, Phase 7d | PENDING — FB25 had ISSUE sweep |
| G6 | `mutations-applied.md` checkpoint bypassed | FB23 | FB25 | FB18-10, FB25-S2 | Ineffective — recurred FB24, FB25 |
| G7 | Module-level Celery instantiation | FB23 | FB25 | H155 | PENDING — FB25 wiring audit caught it |
| G8 | Socket.IO non-functional | FB21 | FB24 | H66 | PENDING — not tested recently |

---

## Confirmed Patterns (Validated in 2+ Builds)

> Patterns that have been empirically validated and should be reinforced.

| ID | Pattern | Validated In | Effectiveness |
|---|---|---|---|
| P1 | `sa.Enum(...)` for SQLAlchemy enum columns (not `sa.String`) | FB25 | HIGH — prevented H203 crash |
| P2 | Frontend `npm run build` as Phase 4 hard gate | FB25 | HIGH — build did not leak to Phase 6 |
| P3 | Auditor batch-size limit (≤10 files) | FB25 | HIGH — 0 BLOCKER false positives |
| P4 | Phase 3c mid-wave S2 check on Tier 2+ | FB25 | MEDIUM — correlation suggestive |
| P5 | Domain-specific fix agents (vsm_backend_fix_agent) | FB25 | HIGH — 0 regressions on 6 modified files |
| P6 | Prompt-hardened structural gate rules (Layer 1) | FB25 | HIGH — no background agent bypasses detected |

---

## Ineffective Mutations (Score 1–2, Awaiting Removal)

> Mutations that have failed to prevent their target failure mode in 2+ builds.

| Mutation ID | Target Failure | First Ineffective | Builds Where It Failed | Action |
|---|---|---|---|---|
| FB23-3 | Inline fix prevention | FB23 | FB23, FB24 | **REMOVE** — replace with tool-enforced boundary |
| FB22-2 | Frontend stub prevention | FB23 | FB23, FB24 | **REDESIGN** — needs live-data-fetch verification in agent prompt |
| FB19-7 | Cross-skill mutation log review | FB19 | FB19–FB25 | **REMOVE** — main log still records gym/coach mutations; no longer relevant |
| FB18-10 | Mutation tracking checkpoint | FB23 | FB23, FB24, FB25 | **REDESIGN** — needs `vsm_meta` output template change + hard gate |
| FB9 / P46 | Test-First Exit Gate | FB20 | FB20, FB21, FB24 | **REDESIGN** — needs explicit S5 verification command, not just pattern |

---

## Next Build Traps (Coach-Planned)

> Deliberate failure modes the coach plans to inject in the next fitness build.

| Build | Target Gap | Trap Description | Expected Agent Catch |
|---|---|---|---|
| FB26 | G3 (stub prevention) | Require a dashboard page with real-time WebSocket data; stub page = BLOCKER | vsm_frontend_coder must fetch live data |
| FB26 | G6 (mutation checkpoint) | Build must produce `mutations-applied.md`; if absent, process auditor flags it | vsm_process_auditor checks for file |
| FB26 | G1 (foundation BLOCKERs) | Introduce subtle auth role enum mismatch in data models | Phase 2c S5 validation must catch it |

---

## Experiment Backlog (Gym-Validated)

> Recent gym experiments and their outcomes.

| Experiment | Hypothesis | Result | Mutation Applied |
|---|---|---|---|
| E15 | H105: Generic coder bypasses re-audit | CONFIRMED | vsm_backend_fix_agent prompt hardened |
| E16 | H106: vsm_meta catches process violations | CONFIRMED | No mutation needed — skill works |
| E17 | H107: Domain fix agents outperform generic | CONFIRMED | No mutation needed — skill works |

---

## Cross-Skill Integration Health

| Link | Status | Evidence |
|---|---|---|
| Gym → Main | ✅ Functional | E15–E17 produced mutations applied to main skill |
| Coach → Main | ⚠️ Partial | Trainer scores builds; mutation effectiveness unmeasured |
| Main → Coach | ⚠️ Partial | Meta-reports rarely referenced in coach Phase 0 |
| All → Broker | ❌ Broken | This file was empty until 2026-06-02 audit forced population |

---

---

## Session Append Log

> Entries appended automatically by `knowledge-broker.sh` SessionEnd hook.

---

*Digest populated during comprehensive audit: 2026-06-02*
*Next update expected: after FB26 fitness build or next gym batch*
