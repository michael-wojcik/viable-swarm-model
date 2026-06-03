# Acquired Wisdom

> This file contains cross-project lessons learned by the skill itself.
> It is read at Phase 0 (startup) and appended to at Phase 8b (meta-reflection).
>
> **Mutation rules**: Append only. Each entry must include: context, lesson,
> verification status, number of sessions since entry.
>
> If an entry is contradicted by empirical evidence, do not delete it —
> append a correction with the contradiction and new understanding.

---

## Entry [N] — YYYY-MM-DD

**Context**: [What kind of project/task this lesson came from]
**Lesson**: [The distilled wisdom]
**Verification**: [How many times this lesson has proven correct since recorded]
**Sessions**: [Count of sessions since entry]
**Status**: [active | superseded | disputed]

---

## Entry 1 — 2026-05-22

**Context**: Initial skill creation
**Lesson**: This skill is designed to be self-modifying. The first act of any
session should be to verify that the skill files are intact and readable.
A corrupted skill should not attempt to execute — it should diagnose and ask
for user intervention.
**Verification**: Baseline — not yet tested in field
**Sessions**: 0
**Status**: active

---

## Entry 2 — 2026-05-23

**Context**: vsm-fitness-gym experiment E4 — testing vsm_product agent effectiveness
**Lesson**: When the user prompt is problem-oriented ("Users need Z") rather than prescriptive ("Build X with Y"), spawning `vsm_product` before `vsm_architect` dramatically reduces architect scope creep. In a minimal experiment, the architect without a product brief added an entire auth subsystem, multiple lists, and quantity/unit fields — all explicitly out of scope. The architect with a product brief produced a design with only 3 core features and no auth. The product brief's "Out of Scope" list is the most effective guardrail.
**Verification**: Tested once in isolation with a single ambiguous prompt
**Sessions**: 1
**Status**: active

---

## Entry 3 — 2026-05-23

**Context**: vsm-fitness-gym experiment E5 — testing vsm_security Security Fix Mode
**Lesson**: Security Fix Mode (where vsm_security writes fixes inline) is not automatically superior to read-only audit + generic coder fixes. In a controlled experiment, the generic coder fixed all 4 CRITICAL/HIGH findings including sensitive-field stripping in response DTOs, while vsm_security missed the DTO exposure finding and used overly broad exception handling. The generic coder's fixes were cleaner and more complete. Security Fix Mode must explicitly include "strip sensitive fields from response DTOs" and must re-read the full audit report before concluding.
**Verification**: Tested once in isolation with a single vulnerable FastAPI app
**Sessions**: 1
**Status**: active


---

## Entry 4 — 2026-05-25

**Context**: vsm-fitness-gym batch experiments E6–E14 — testing 8 untested + 2 inconclusive hypotheses
**Lesson**:
1. **Domain-specific coder prompts measurably improve outcomes**. A generic `coder`
   produced `allow_origins=["*"]` with credentials and skipped runtime API verification.
   A domain-specific `coder` with embedded "Known Stack Gotchas" used explicit CORS
   origins and dynamically verified `strawberry.Schema.__init__` with `inspect.signature`.
   The effect size is moderate — some gaps (e.g., `class Config` deprecation) persisted
   in both agents until explicitly elevated to BLOCKER-level.
2. **`npm run build` catches errors `vite build` misses**. When `tsconfig.json`
   includes `vite.config.ts` but `@types/node` is omitted, `tsc -b` fails while
   `vite build` passes. Frontend infra verification must always run the package.json
   build script, not just the underlying bundler.
3. **Explicit auth contracts prevent frontend/backend mismatches**. An ambiguous
   api-spec.md ("login returns token") caused a 3-field mismatch between backend
   implementation and frontend expectations. An explicit spec with exact JSON shapes
   produced perfect alignment.
4. **Fix waves are the most regression-prone phase**. Multiple builds (FB16–FB21)
   found fix agents introducing circular imports, weakening auth, bypassing re-audit,
   and creating REST/GraphQL auth divergence. Fix agents need the same domain-specific
   treatment as implementation agents.
**Verification**: Tested once in controlled gym experiments with minimal reproducible code
**Sessions**: 1
**Status**: active

---

## Entry 5 — 2026-05-25

**Context**: vsm-fitness-gym experiments E15–E17 — confirming H105, H106, H107
**Lesson**:
1. **Inline fixes during integration bypass re-audit**. When a generic coder simulates an S5 inline fix (fixing coordinator BLOCKERs directly in Phase 6), it skips `re-audit-report.md` production, skips the full test suite, and skips the subprocess import check. Domain-specific fix agents (`vsm_backend_fix_agent`, `vsm_frontend_fix_agent`) enforce the full protocol: 100% re-audit report production vs 0% for generic coder.
2. **Phase 8b is a critical feedback loop, not optional documentation**. Running `vsm_meta` on fictional build artifacts with known process violations caught ALL of them: inline fixes, missing re-audit reports, skipped security re-check, skipped Phase 8b itself. Skipping Phase 8b means these violations go undetected and uncorrected.
3. **Domain-specific fix agents measurably outperform generic coders on security invariants**. Both agents fixed surface issues correctly, but the generic coder introduced a security regression (kept `admin` in registration allowlist) while the domain agent's embedded "registration role allowlist excludes admin/superuser" gotcha prevented it.
4. **Phase 4 must be a hard gate**. Builds that proceed past Phase 4 with failing tests waste security and integration effort. The exit gate should verify zero failures across pytest, vitest, and npm run build before allowing Phase 5/6.
**Verification**: Tested in controlled gym experiments with minimal reproducible code (E15: 3 integration BLOCKERs; E16: fictional build artifacts; E17: 5 BLOCKERs with treatment/control)
**Sessions**: 3 (E15, E16, E17)
**Status**: active

---

## Entry 6 — 2026-05-25

**Context**: vsm-fitness-gym experiments E18–E19 — confirming H108 and H109
**Lesson**:
1. **Phase 4 hard gate eliminates 100% of downstream BLOCKERs caused by known test failures** (E18). A single failing pytest test (missing RateLimitExceeded handler) predicted both a security HIGH finding and a coordinator BLOCKER. Fixing the test failure before Phase 5/6 eliminated both downstream findings entirely. The hard gate is not just "good practice" — it is a deterministic BLOCKER prevention mechanism.
2. **Auditor cross-file env var parity check catches mismatches before they reach coordinator** (E19). The auditor flagged a 3-way split (`DB_HOST` / `DATABASE_HOST` / `PG_HOST`) as BLOCKER in all three files. The coordinator would have found the same issue as 1 BLOCKER in Phase 6. Early detection in Phase 2b/3b means the fix agent resolves it before integration, preventing coordinator BLOCKERs entirely.
3. **11 untested hypotheses remain.** 98 confirmed, 2 rejected, 11 untested. The mutation system is mostly empirically grounded.
**Verification**: Controlled gym experiments with minimal reproducible code (E18: 2 variants on identical buggy code; E19: auditor + coordinator on env var mismatch)
**Sessions**: 2 (E18, E19)
**Status**: active


---

## Entry 7 — 2026-05-25

**Context**: vsm-fitness-coach fitness build #22 (OpsCenter — Tier 3 full-stack project)
**Lesson**:
1. **Dependency verification must be a BLOCKER, not a suggestion.** An agent imported `strawberry_sqlalchemy_mapper` (not in `requirements.txt`) and spent ~15 minutes in an import verification loop before S5 intervention. The cost of a missing dependency check is not just a build failure — it is wasted agent capacity and delayed delivery. The BLOCKER must be enforced by both the agent's own gotcha list AND by the auditor's pre-implementation checklist.
2. **Vite alias `"@"` vs `"@/"` is a silent production killer.** The alias worked in `npm run dev` but `npm run build` failed with Rollup unable to resolve imports. Frontend config validation in Phase 3e/3f must explicitly verify the alias key, not just its presence.
3. **Environment compatibility should be checked BEFORE agents are dispatched.** The installed `strawberry-graphql==0.256.0` was incompatible with the system's pydantic version. Catching this in Phase 0 prevents agents from writing code that cannot be runtime-verified.
**Verification**: Observed once in FB22; 3 distinct agent failures prevented by these rules
**Sessions**: 1 (FB22)
**Status**: active

---

## Entry 8 — 2026-06-02

**Context**: Multi-session builds using `--continue` (FB16–FB24)
**Lesson**: Continued sessions can lose sub-agent file writes from prior waves. At the start of any continued session, S5 MUST verify that expected files exist and contain expected content. Do not assume `--continue` preserves file state across agent waves. Key verification targets: `.kimi/phase4-gate.md`, `.kimi/re-audit-report.md`, `.kimi/mutations-applied.md`, and any files written by background agents in the previous session. If expected files are missing, re-run the producing agent wave rather than proceeding with stale assumptions.
**Verification**: Observed in FB16–FB24 where continued sessions repeatedly lost Phase 4 gate documents, re-audit reports, and fix-wave changes. Anti-pattern #33 (`Session context loss destroys files`) documents the same failure mode from the agent perspective.
**Sessions**: 9+ (FB16–FB24)
**Status**: active
**See also**: `references/anti-patterns.md` #33 (Session context loss destroys files)
