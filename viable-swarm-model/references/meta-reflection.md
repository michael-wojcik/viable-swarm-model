# Meta-Reflection — Skill-Level Performance Learning

> **Purpose**: Cross-build reflections on the viable-swarm-model skill's own
> performance. Synthesized from individual `meta-report.md` artifacts.
> **Location**: `${KIMI_SKILL_DIR}/references/meta-reflection.md`
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

## Example

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
