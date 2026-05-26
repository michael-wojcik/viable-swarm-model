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
