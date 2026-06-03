# Mutation State — Unified Lifecycle Tracking

> **Purpose**: Track every mutation from hypothesis → experiment → application → measurement → keep/remove.
> **Updated by**: S5 during Phase 8c-ii, coach trainer during Phase 2, gym after experiments.
> **Read by**: All skills at Phase 0 to understand which rules are active, probationary, or removed.
> **Schema version**: 1.0

---

## Legend

| Status | Meaning |
|---|---|
| `probation` | Applied < 3 builds ago; awaiting measurement |
| `effective` | Scored 4–5 on effectiveness; permanently active |
| `monitor` | Scored 3; under extended observation |
| `ineffective` | Scored 1–2; marked for removal or redesign |
| `removed` | Moved to mutation-cemetery.md; no longer active |
| `superseded` | Replaced by a newer mutation addressing same failure mode |

---

## Active Mutations (Currently Enforced)

| ID | Source | Type | Target Failure | Status | Builds Tested | Effectiveness Score | Linked Hypothesis | Linked Experiment |
|---|---|---|---|---|---|---|---|---|
| FB25-S1 | FB25 Coach | structural | False hook claim | probation | 0 | — | H300 | E17 |
| FB25-S2 | FB25 Coach | structural | Mutation checkpoint bypass | probation | 0 | — | H209 | — |
| FB24-1 | FB24 Build | append-only | Phase 4 gate bypass | probation | 1 | — | H154 | — |
| FB24-2 | FB24 Build | append-only | Enum type safety | probation | 1 | — | H203 | — |
| FB23-4 | FB23 Build | append-only | Frontend build verification | probation | 2 | — | H154 | — |
| FB21-8 | FB21 Build | append-only | Duplicate L-numbers | effective | 4 | 5 | — | — |
| FB21-24 | FB21 Build | refinement | Process auditor spawn | monitor | 4 | 3 | — | — |
| R19 | FB23 Build | refinement | Contract repopulation | effective | 2 | 4 | — | — |
| R20 | FB23 Build | refinement | Validate agent files | effective | 2 | 4 | — | — |

---

## Ineffective Mutations (Awaiting Removal/Redesign)

| ID | Source | Type | Target Failure | First Ineffective | Builds Failed | Action Required | Deadline Build |
|---|---|---|---|---|---|---|---|
| FB23-3 | FB23 Build | refinement | Inline fix prevention | FB23 | FB23, FB24 | **REMOVE** — replace with tool-enforced boundary | FB26 |
| FB22-2 | FB22 Build | append-only | Frontend stub prevention | FB23 | FB23, FB24 | **REDESIGN** — add live-data-fetch verification | FB26 |
| FB19-7 | FB19 Build | append-only | Cross-skill log review | FB19 | FB19–FB25 | **REMOVE** — no longer relevant | FB26 |
| FB18-10 | FB18 Build | structural | Mutation checkpoint | FB23 | FB23, FB24, FB25 | **REDESIGN** — hard gate in vsm_meta.md | FB26 |
| FB9 / P46 | FB9 Build | append-only | Test-First Exit Gate | FB20 | FB20, FB21, FB24 | **REDESIGN** — explicit S5 verification command | FB26 |

---

## Removed Mutations (In Cemetery)

| ID | Source | Type | Removal Build | Rationale | Replacement |
|---|---|---|---|---|---|
| *(none yet)* | | | | | |

---

## Integration Health

| Link | Active Mutations | Ineffective Mutations | Removal Rate |
|---|---|---|---|
| Gym experiment → Mutation | 3 | 0 | 0% |
| Fitness build → Mutation | 6 | 5 | 0% |
| Hypothesis → Mutation | 4 | 2 | 0% |

**Target for FB26–FB30**: Removal rate ≥ 20% (at least 1 ineffective mutation removed per 5 builds).

---

## Usage Instructions

**When applying a new mutation**:
1. Assign a unique ID (format: `FB[N]-[M]` for build-derived, `E[N]-[M]` for experiment-derived, `R[N]` for refinement)
2. Set status to `probation`
3. Link to hypothesis ID and experiment ID if applicable
4. Set `Builds Tested` to 0

**When a fitness build completes**:
1. Increment `Builds Tested` for all probation/monitor mutations
2. Score effectiveness 1–5 based on whether target failure recurred
3. If score ≥ 4: status → `effective`
4. If score = 3: status → `monitor`
5. If score ≤ 2: status → `ineffective`

**When removing a mutation**:
1. Move row from Active/Ineffective to Removed
2. Fill `Removal Build` and `Rationale`
3. If replaced, fill `Replacement`
4. Append entry to `mutation-cemetery.md`

---

*Created during comprehensive audit: 2026-06-02*
