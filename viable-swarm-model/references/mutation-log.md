# Mutation Log

> This file is append-only. Every modification the skill makes to its own
> files is recorded here with full rationale. If the skill becomes corrupted,
> this log is the audit trail for `git revert`.
>
> **Mutation rules**: Append only. Each entry includes: session context,
> file changed, type of change, rationale, expected effect.

---

## Mutation 1 — 2026-05-22

**Session**: Initial creation of viable-swarm-model skill
**File**: `SKILL.md`, `references/*`, `assets/*`
**Type**: create
**Rationale**: The skill was originally designed as a static instruction set.
A learning organism cannot have immutable DNA. All files must be mutable,
with regulated mutation rules, self-test at Phase 0, and a mutation log.
**Expected effect**: Future sessions will load a skill that can evaluate its
own performance and append new prevention rules, patterns, and anti-patterns
based on empirical results. The skill evolves between sessions.

---

## Mutation [N] — YYYY-MM-DD

**Session**: [Brief description of the task/session]
**File**: [Which file was modified]
**Type**: [append | edit | strikethrough | structural]
**Rationale**: [What empirical finding motivated this change. Be specific:
which build, which bug, which false positive, which missed vulnerability.]
**Expected effect**: [How the next session should behave differently because
of this mutation. What should be caught that wasn't? What should pass that
was falsely flagged?]

**Before**:
```
[content or summary of what existed]
```

**After**:
```
[content or summary of what replaced it]
```

## Mutation [2] — 2026-05-22

**Session**: Fitness build FB1 (DocuFlow)
**File**: Multiple references files
**Type**: append
**Rationale**: FB1 revealed 5 systemic gaps: (1) parallel agents overwrite entry points,
(2) fix agents claim false positives, (3) tester agent cannot function without runtime deps,
(4) GraphQL depth limiting missing from design checklist, (5) rate limiting missing from
foundation requirements. These are empirical findings from a 3500+ line multi-service build.
**Expected effect**: Next session with GraphQL will include depth limiting in design.
Next fix wave will require verification commands. Entry point conflicts will be reduced.
Tester agent environment awareness will improve.

**Files modified**:
- `references/hypotheses.md` — Added H4-H8
- `references/pattern-library.md` — Added Pattern #38 (WebSocket path token auth)
- `references/anti-patterns.md` — Added Anti-Patterns #42-43 (fix false positives, entry point overwrites)
- `references/security-lessons.md` — Added L25-L26 (GraphQL depth limit, rate limiting)
- `references/integration-checklist.md` — Added checks #21-22 (parallel coordination, WebSocket auth)

## Mutation [3] — 2026-05-22

**Session**: Fitness build FB2 (GeoQuiz)
**File**: Multiple references files
**Type**: append
**Rationale**: FB2 revealed 6 new systemic gaps: (1) docker-compose bash fallbacks embedding secrets,
(2) SQLAlchemy import shadowing by column names, (3) unbounded spatial query parameters as DoS vector,
(4) backend/frontend state machine domain mismatch, (5) tester agent wasting time installing missing deps,
(6) rate limiting still not shifting left to foundation wave. These are empirical findings from a
4000+ line multiplayer geospatial quiz platform with PostGIS, Socket.io, and Redis.
**Expected effect**: Next session with docker-compose will have no `:-` fallbacks. SQLAlchemy model
files will use aliased imports. Geo endpoints will have parameter bounds. State machine contracts
will be validated during integration. Tester agents will install deps proactively.

**Files modified**:
- `references/hypotheses.md` — Added H9-H14
- `references/security-lessons.md` — Added L37-L39 (docker-compose fallbacks, infra security, rate limiting in foundation)
- `references/pattern-library.md` — Added Patterns #39-40 (SQLAlchemy alias, spatial bounds)
- `references/integration-checklist.md` — Added Check #23 (state machine domain alignment)
- `references/anti-patterns.md` — Added Anti-Patterns #44-45 (docker fallbacks, SQLAlchemy shadowing)
- `agents/vsm_tester.md` — Added tester dep-install guidance and foundation rate-limiting note

## Mutation [4] — 2026-05-22

**Session**: Fitness build FB3 (TaskFlow)
**File**: Multiple references files
**Type**: append
**Rationale**: FB3 revealed 4 new systemic gaps: (1) tester agent cannot execute tests because module-level Pydantic Settings instantiation crashes on import without env vars, (2) GraphQL enum case mismatches slip through coordinator (SUCCESS vs "success"), (3) rate limiting middleware (SlowAPIMiddleware) still missing despite decorators being present in foundation wave, (4) frontend Dockerfile bakes undefined API URLs because build args are missing. Additionally, FB3 validated that FB2 mutations worked: zero docker-compose fallbacks, SQLAlchemy aliased imports, GraphQL depth limiting installed, rate limiting scaffolding shifted left to foundation wave. Security gate had zero CRITICAL/HIGH findings for the first time.
**Expected effect**: Next session with Pydantic Settings will use lazy factory pattern. Tester agents will write conftest.py before importing backend modules. GraphQL enum case will be checked during integration. Rate limiting will include both decorators and middleware. Frontend Docker builds will include API URL build args.

**Files modified**:
- `references/hypotheses.md` — Added H15-H18
- `references/security-lessons.md` — Added L40 (rate limiting requires both decorators AND middleware)
- `references/pattern-library.md` — Added Pattern #41 (lazy Pydantic Settings factory for testability)
- `references/integration-checklist.md` — Added Checks #24-25 (enum case alignment, frontend Dockerfile build args)
- `references/anti-patterns.md` — Added Anti-Pattern #46 (module-level Pydantic Settings instantiation)
- `agents/vsm_tester.md` — Added tester env-var injection guidance (FB3 finding)

## Mutation [5] — 2026-05-23

**Session**: vsm-fitness-gym — Gym run testing H1, H2, H9
**File**: `references/hypotheses.md`, `references/experiments.md`
**Type**: edit (status updates), append (experiment records)
**Rationale**: All three hypotheses tested in isolation with minimal reproducible
experiments. Results were uniformly negative — the skill already detects all three
patterns. This is strong empirical evidence that the existing prevention rules
and agent prompts are effective. No new rules are needed. The skill learned what
it already knows.

**Hypotheses tested**:
- **H1** (dynamic WebSocket JWT URL): Expected gap in dynamic URL detection.
  Security agent flagged it CRITICAL immediately. Rejected.
- **H2** (N+1 in computed field loops): Expected gap in auditor coverage beyond
  ORM relationship loading. Auditor flagged it BLOCKER immediately. Rejected.
- **H9** (docker-compose `:-` fallbacks): Expected gap because prompt emphasizes
  `||` but not `:-`. Security agent detected all 4 `:-` fallbacks as CRITICAL.
  Rejected.

**Expected effect**: Future gym sessions can deprioritize these patterns. The
skill's security and audit agents are performing as designed on these specific
vulnerability classes. Gym resources should focus on the remaining 15 untested
hypotheses (H3-H8, H10-H18).

**Before**:
- H1, H2, H9 status: `untested`
- experiments.md: only template and Experiment 0

**After**:
- H1, H2, H9 status: `rejected` with full result rationale
- experiments.md: appended E1, E2, E3 with methodology and findings

---

## Mutation 6 — 2026-05-23

**Session**: vsm-fitness-gym — Gym run testing H[N+1] and H[N+2]
**File**: `agents/vsm_architect.md`, `agents/vsm_security.md`, `references/hypotheses.md`, `references/experiments.md`
**Type**: edit (status updates, agent prompt refinements), append (experiment records)
**Rationale**: Two agent-focused hypotheses tested with minimal reproducible experiments.

**H[N+1] — CONFIRMED**: The vsm_product agent produces structured product briefs that act as effective guardrails against architect scope creep. In a single-prompt experiment, the control architect (no brief) added an entire auth subsystem, multiple lists, and quantity/unit fields — all explicitly out of scope. The treatment architect (with brief) eliminated auth entirely and produced a design with only 3 core features and 12+ explicit scope exclusions. The product brief's "Out of Scope" list was the key guardrail.

**H[N+2] — REJECTED**: The vsm_security Security Fix Mode did NOT outperform a generic coder. In a single-vulnerability experiment, the generic coder fixed all 4 CRITICAL/HIGH findings including sensitive-field stripping in response DTOs. The vsm_security agent missed Finding 4 (HIGH: public DTO exposes sensitive fields) and left `secret`/`owner` exposed. It also used overly broad `except Exception:` instead of specific `jwt.PyJWTError`. The generic coder produced cleaner, more complete fixes with 10 tests vs the security agent's 11.

**Expected effect**:
- Future problem-oriented prompts will spawn vsm_product BEFORE vsm_architect to prevent scope creep.
- Future vsm_security Security Fix Mode sessions will explicitly check response DTOs for sensitive field exposure and re-read the full audit report before concluding fixes.

**Before**:
- `vsm_architect.md`: No mention of product briefs as design guardrails.
- `vsm_security.md`: Security Fix Mode checklist did not include "strip sensitive fields from response DTOs" or "re-read audit report before concluding."
- H[N+1], H[N+2] status: `untested`

**After**:
- `vsm_architect.md`: Added instruction to use product brief out-of-scope list and success criteria as guardrails.
- `vsm_security.md`: Added DTO stripping and audit re-read steps to Security Fix Mode.
- H[N+1] status: `confirmed`; H[N+2] status: `rejected`
- experiments.md: appended E4, E5


---

## Mutation [N+3] — 2026-05-23
**Session**: FleetSync FB4 fitness build
**File**: `references/integration-checklist.md`
**Type**: append
**Rationale**: FB4 revealed three new failure modes not covered by existing integration checks:
1. GraphQL field name drift: Strawberry auto-camelCased `assigned_technician_id` to `assignedTechnicianId`, but frontend expected `technicianId`. This caused a BLOCKER that survived the first integration check and fix wave.
2. Auth response contract mismatch: Backend returned `access_token`, frontend expected `token`. Recurring across FB2, FB3, FB4.
3. Orphaned exports: `auth.py` defined `require_role()` never imported anywhere; duplicate of `roles.py` `require_roles()`.
4. WebSocket event name drift: `api-spec.md` used `authenticate`/`authenticated`, but `sio.py` implemented `auth`/`auth_ok`.

**Expected effect**: Future GraphQL-enabled builds will have field name alignment checked before integration gate. Future auth-enabled builds will have response contracts documented in foundation wave. Future builds will scan for orphaned exports.

---

## Mutation [N+4] — 2026-05-23
**Session**: FleetSync FB4 fitness build
**File**: `references/hypotheses.md`
**Type**: append
**Rationale**: Four new falsifiable hypotheses generated from FB4 gaps:
- H19: GraphQL field name alignment checklist prevents Strawberry auto-camelCase drift
- H20: Auth response contract documentation in foundation wave prevents login/register mismatches
- H21: Orphaned exports scan prevents dead code accumulation
- H22: WebSocket event name dictionary cross-check prevents emit/listen mismatches

**Expected effect**: Gym skill can run targeted experiments to validate each hypothesis before checklist items are promoted to permanent prevention rules.

---

## Mutation [N] — 2026-05-23
**Session**: FB5 ContractStress fitness build
**File**: `references/security-lessons.md`
**Type**: append
**Rationale**: FB5 revealed three new security gaps: GraphQL RBAC drift from REST, GraphQL list endpoints lacking ownership filtering, and upload filename XSS. These were caught by the security gate but should be prevention rules in the security lessons.
**Expected effect**: Future security gate audits will explicitly check GraphQL RBAC parity, GraphQL ownership filtering, and filename sanitization.

## Mutation [N+1] — 2026-05-23
**Session**: FB5 ContractStress fitness build
**File**: `references/integration-checklist.md`
**Type**: append
**Rationale**: FB5 revealed gaps in the integration checklist: enum runtime safety (str, enum.Enum), circular import prevention (no imports from main.py), and GraphQL-REST contract parity.
**Expected effect**: Future coordinators will verify these three contract dimensions before declaring integration complete.

## Mutation [N+2] — 2026-05-23
**Session**: FB5 ContractStress fitness build
**File**: `references/pattern-library.md`
**Type**: append
**Rationale**: FB5 produced two proven patterns: (1) using `str, enum.Enum` for Strawberry enums to avoid ValueError, and (2) extracting shared singletons to dedicated modules to prevent circular imports.
**Expected effect**: Future architects will document these patterns; future coders will apply them.

## Mutation [N+3] — 2026-05-23
**Session**: FB5 ContractStress fitness build
**File**: `agents/vsm_tester.md`
**Type**: refinement
**Rationale**: FB5 tester wrote 86 backend tests but zero frontend tests, and left `main.py`/`tasks.py` at 0% coverage. The tester prompt did not explicitly require frontend or entry-point/worker tests.
**Expected effect**: Future testing waves will produce tests for both backend and frontend, including entry-point wiring and background workers.

## Mutation [N+4] — 2026-05-23
**Session**: FB5 ContractStress fitness build
**File**: `references/hypotheses.md`
**Type**: append
**Rationale**: FB5 fitness report identified 7 gaps. Seven falsifiable hypotheses were generated (H23-H29) to guide future gym experiments and build monitoring.
**Expected effect**: Hypotheses H23-H29 are queued for testing by vsm-fitness-gym or validation in FB6+.

---

## Mutation [N] — 2026-05-23
**Session**: FB6 Fitness Build — DeepContract
**File**: `references/hypotheses.md`
**Type**: append
**Rationale**: FB6 revealed architect and tester agent timeouts on 3000+ line projects, WebSocket auth gaps, and sequencing issues between security and integration gates. Appended H30–H33 with full experiment designs.
**Expected effect**: Next fitness build will test whether split testers and architect chunking guidance reduce timeouts.

## Mutation [N+1] — 2026-05-23
**Session**: FB6 Fitness Build — DeepContract
**File**: `references/integration-checklist.md`
**Type**: append
**Rationale**: FB6 security gate found that WebSocket room subscription/unsubscription handlers did not verify socket authentication. Existing Check 29 only verified event name dictionaries, not auth. Added Check 30 for WebSocket auth & authorization.
**Expected effect**: Future WebSocket-enabled builds will catch unauthenticated room joins before the security gate.

## Mutation [N+2] — 2026-05-23
**Session**: FB6 Fitness Build — DeepContract
**File**: `references/security-lessons.md`
**Type**: append
**Rationale**: FB6 security gate found fail-open GraphQL auth context (catch-all exception → user=None) and missing httpOnly cookie implementation. Both were downgraded to MEDIUM when they are HIGH severity. Added L38 and L39 as prevention rules.
**Expected effect**: Security agent will flag auth bypass in GraphQL context builders as HIGH/BLOCKER, not MEDIUM.

## Mutation [N+3] — 2026-05-23
**Session**: FB6 Fitness Build — DeepContract
**File**: `agents/vsm_tester.md`
**Type**: refinement
**Rationale**: FB6 tester agent timed out after 900s while trying to write both backend and frontend tests. Added FB6 Finding guidance: pre-install deps first, backend-first ordering, and prioritization of critical backend tests if timeout risk is high.
**Expected effect**: Tester agents in future large builds will install dependencies immediately and write backend tests before frontend, reducing timeout frequency.

## Mutation [N+4] — 2026-05-23
**Session**: FB6 Fitness Build — DeepContract
**File**: `agents/vsm_architect.md`
**Type**: refinement
**Rationale**: FB6 architect agent timed out after 600s on a complex healthcare platform spec. The agent spent excessive time researching technologies already specified in the plan. Added chunking guidance: skip research for familiar specified stacks, write docs in dependency order (data-model → api-spec → architecture).
**Expected effect**: Architect agents on large projects will complete within timeout limits by avoiding unnecessary research and writing in dependency order.

---

## Mutation 12 — 2026-05-23

**Session**: FB7 JurisFlow fitness build evaluation
**File**: `references/hypotheses.md`
**Type**: append
**Rationale**: FB7 revealed three new systemic gaps: (1) tester security regression (H34), (2) foundation model drift (H35), (3) security gate timing (H36). Each gap needs a falsifiable hypothesis for the gym to test.
**Expected effect**: Gym experiments will validate whether these hypotheses hold across multiple builds.

---

## Mutation 13 — 2026-05-23

**Session**: FB7 JurisFlow fitness build evaluation
**File**: `references/integration-checklist.md`
**Type**: append
**Rationale**: No existing check verifies that SQLAlchemy models match the data-model.md spec. FB7 had 8+ field mismatches. Also, no check verifies security after fix waves.
**Expected effect**: Future coordinators will catch model drift and security regressions before delivery.

---

## Mutation 14 — 2026-05-23

**Session**: FB7 JurisFlow fitness build evaluation
**File**: `agents/vsm_tester.md`
**Type**: refinement
**Rationale**: FB7 tester reverted a fail-closed GraphQL auth fix, believing 401 was a bug. The agent needs explicit guidance that auth restrictions are features, not bugs.
**Expected effect**: Future testers will expect 401/403 in tests rather than weakening auth checks.

---

## Mutation 15 — 2026-05-23

**Session**: FB7 JurisFlow fitness build evaluation
**File**: `agents/vsm_architect.md`
**Type**: refinement
**Rationale**: FB7 architect (skipped) and foundation agent both failed to follow data-model.md. Explicit instruction to read existing design documents should reduce drift.
**Expected effect**: Future architects/foundation agents will read and match existing specs.


---

## Mutation 16 — 2026-05-23

**Session**: FB7 JurisFlow fitness build evaluation
**File**: `SKILL.md`
**Type**: structural
**Rationale**: User approved both structural mutations proposed in the fitness report:
1. Add Phase 2c Model Validation — S5 checks models.py against data-model.md before implementation wave
2. Add Phase 7b Post-Fix Security Re-Check — vsm_security re-audits modified auth/GraphQL/WebSocket files after fix wave
FB7 demonstrated that foundation model drift causes cascade failures, and that fix/test agents can introduce security regressions after the main security gate.
**Expected effect**: Future builds will catch model-schema drift before implementation begins, and security regressions introduced during fix waves will be caught before reflection.

**Before**:
- Phase 2: Foundation → Audit → Implementation (no model validation)
- Phase 7: Fix Wave → Re-audit → Reflection (no post-fix security check)

**After**:
- Phase 2: Foundation → Audit → Model Validation → Implementation
- Phase 7: Fix Wave → Re-audit → Post-Fix Security Re-Check → Reflection

---

## Mutation 17 — 2026-05-23

**Session**: FB8 EduFlow fitness build evaluation
**File**: `references/hypotheses.md`, `references/security-lessons.md`, `references/integration-checklist.md`, `agents/vsm_auditor.md`
**Type**: append (hypotheses, security lessons, integration checklist), refinement (auditor agent)
**Rationale**: FB8 validated all FB7 prevention rules (H34–H36, Check 31–32, H30, H31) and identified four new gaps:
1. GraphQL RBAC parity with REST — implementation agents missed it, security gate caught it (H37, L42)
2. WebSocket enrollment authorization — session verified but course enrollment was not (H38, L43)
3. Auditor false positive on FastAPI router imports — misread circular-import rule (H40)
4. Auditor false positive on Strawberry auto-camelCase — lacked framework guidance (H39)
**Expected effect**: Future security gates will explicitly verify GraphQL RBAC parity. Future integration checks will verify WebSocket enrollment. Future auditors will not falsely flag FastAPI router imports or Strawberry camelCase fields.

**Files modified**:
- `references/hypotheses.md` — Appended H37–H40
- `references/security-lessons.md` — Added L42 (GraphQL RBAC parity) and L43 (WebSocket enrollment auth)
- `references/integration-checklist.md` — Added enrollment authorization to Check 30
- `agents/vsm_auditor.md` — Added FastAPI router import and Strawberry auto-camelCase guidance


---

## Mutation 18 — 2026-05-23

**Session**: Epistemic audit of skill theoretical foundations
**File**: `viable-swarm-model/SKILL.md`, `README.md`
**Type**: refinement (structural claims removed)
**Rationale**: Empirical analysis of Kimi Code CLI's subagent architecture confirmed
that Gordon Pask's Conversation Theory cannot be implemented in this platform.
Subagents are stateless batch workers with no peer-to-peer communication channel,
no persistent P-individual identity, and no recursive mutual teachback capability.
The skill's Section 11 "Teachback Protocol" was actually a self-explanation
checklist — useful, but not Paskian teachback (which requires a minimum of two
participants, reproduction in own terms, and comparison by the originator).
Continuing to claim CT as a structural foundation was a known falsehood per the
skill's own epistemic rule: "Design intent is a hypothesis; empirical results are
evidence." The mutation wins.

**Expected effect**: Future users and agents will not expect conversational
dynamics that the platform cannot support. The VSM architecture is honestly
represented as the sole cybernetic foundation. The comprehension checkpoint
retains its value as a pre-completion validation step without theoretical
misattribution.

**Before**:
- Description claimed "based on Stafford Beer's VSM and Gordon Pask's CT"
- Section 11 titled "Teachback Protocol (from Pask CT)"

**After**:
- Description claims "based on Stafford Beer's Viable System Model"
- Section 11 titled "Comprehension Checkpoint"

---

## Mutation Log Entry — FB9-20260523

**Fitness Build**: FB9 (HealthBridge)
**Overall Score**: 4.0 / 5.0
**Gap**: Phase 2 Foundation Wave scored 3/5 due to dependency race conditions between parallel foundation agents.

### Mutations Applied (Autonomous)
1. **Append-only**: Added Anti-Pattern #19 (JWT Signature Verification Bypass) to `references/anti-patterns.md`
2. **Append-only**: Added Security Lessons L28 (JWT Signature Verification is Non-Negotiable) and L29 (Fix Agents Can Introduce Vulnerabilities) to `references/security-lessons.md`
3. **Append-only**: Added Pattern #22 (Foundation Wave Sequencing) to `references/pattern-library.md`
4. **Refinement**: Updated `agents/vsm_auditor.md` to flag `verify_signature=False` as CRITICAL/BLOCKER
5. **Refinement**: Updated `agents/vsm_tester.md` with FB9 Finding on JWT Payload / ORM Type Mismatch on SQLite
6. **Append-only**: Added Hypothesis H41 (Sequenced foundation sub-waves eliminate dependency race conditions) to `references/hypotheses.md`

### Structural Mutations Applied
7. **Structural**: Split Foundation Wave into two sequential sub-waves:
   - Updated `SKILL.md` Section 6 "Phase 2: Foundation Wave" with Sub-Wave 2a (Core Contracts) and Sub-Wave 2b (Dependent Infrastructure), including mini-audit verification gate.
   - Updated `references/flow-diagram.mermaid` to show P2A → P2AV → P2B sequence instead of single P2 node.
   - Rationale: FB9 Foundation Wave scored 3/5 due to parallel agents racing on shared dependencies (AsyncSessionLocal missing, get_current_user signature mismatch, env var drift).
   - Status: **Applied** (user approved)

### Rejected Mutations
- None

---

## Mutation 19 — 2026-05-23

**Session**: Epistemic audit of VSM fidelity + proposed refinements
**File**: `agents/vsm_architect.md`, `agents/vsm_coordinator.md`, `SKILL.md`, `references/pattern-library.md`
**Type**: refinement (4 files), append (1 file)
**Rationale**: Comprehensive audit revealed that while the skill's VSM mapping is
reasonably faithful in S3* (audit) and algedonic signals, it falls short in:
- S4 (Intelligence): Produces single designs, usurping S5's decision role
- S2 (Coordination): Retrospective checker, not real-time oscillator damper
- S3 (Control): Todo tracking ≠ continuous regulation
- S5 (Policy): Flow-follower, not S3/S4 balancer
- Recursion: Absent (platform limitation)
- Variety (Ashby's Law): No explicit complexity assessment; empirical timeouts prove violation

Four Tier 2 refinements and one Tier 1 append applied autonomously per the
skill's epistemic rule. Tier 3 structural mutation (mid-wave S2 check in Phase 3)
reserved for user approval.

**Expected effect**: 
- Architects generate options; S5 chooses (restores Beerian S4/S5 boundary)
- Coordinators have mid-wave authority and verbatim correction power (strengthens S2)
- Phase 0 variety assessment prevents Ashby violations by right-sizing metasystem capacity
- Phase 1 policy check makes S5 an explicit balancer, not a flowchart executor
- Pseudo-recursion pattern distributes minimal metasystem function into S1 agents

**Files modified**:
- `agents/vsm_architect.md` — Added step 7: generate 2-3 design options
- `agents/vsm_coordinator.md` — Added mid-wave coordination and correction authority
- `SKILL.md` Phase 0 — Added step 6: Variety Assessment (Ashby's Law)
- `SKILL.md` Phase 1 — Added S5 Policy Check before EnterPlanMode
- `references/pattern-library.md` — Added Pattern [N]: Pseudo-Recursion

---

## Mutation 20 — 2026-05-23

**Session**: Same epistemic audit (Tier 3 structural mutation)
**File**: `SKILL.md` + `references/flow-diagram.mermaid`
**Type**: structural
**Rationale**: FB9 already sequenced the foundation wave (Sub-Wave 2a/2b) to prevent
dependency races. The remaining coordination gap is in Phase 3 (Implementation Wave),
where parallel feature agents drift on shared contracts. Empirical evidence from FB4-FB7
shows GraphQL field drift, auth contract mismatches, and WebSocket event name drift all
originate in Phase 3. A lightweight mid-wave S2 check after the first 1-2 agents complete
catches drift before all agents finish, as close to Beerian real-time coordination as
the platform allows.

**User approval**: Approved. User explicitly rejected concern about diagram bloat,
stating "I'm not concerned about 'bloat' if it's genuinely useful." Phase 3c was
selected over Phase 2d because foundation wave sequencing (FB9) already addresses
coordination there; implementation wave has no mid-wave gate and is where empirical
drift occurs.

**Expected effect**: Tier 2+ builds will catch contract drift during implementation
before all agents complete, reducing BLOCKERs in Phase 3b and Phase 5.

**Files modified**:
- `SKILL.md` Phase 3 — Added Phase 3c: Mid-Wave S2 Check
- `SKILL.md` Mermaid diagram — Inserted P3M node between P3S and P3A
- `references/flow-diagram.mermaid` — Inserted P3M node between P3S and P3A

---

## Mutation 21 — 2026-05-23

**Session**: Coach skill refinement — hypothesis status tracking gap
**File**: `vsm-fitness-coach/SKILL.md`
**Type**: refinement (coach self-modification)
**Rationale**: The vsm-fitness-coach skill generated new hypotheses from fitness build gaps
but never explicitly updated the status of existing hypotheses that were tested by the build.
This left the hypothesis backlog with stale "untested" items that had actually been validated
or falsified in previous builds. The coach's Phase 3 only created new hypotheses; it did not
close the loop on old ones.

**Expected effect**: After every fitness build, the coach will explicitly check which
hypotheses were tested, update their status (confirmed / rejected / inconclusive),
fill in the Result field with build evidence, and record the build ID in the Tested by field.
This keeps the hypothesis backlog accurate and prevents redundant gym experiments.

**Files modified**:
- `vsm-fitness-coach/SKILL.md` — Added Phase 2b: Update Hypothesis Statuses between
  Phase 2 (Evaluate Performance) and Phase 3 (Generate Hypotheses). Updated Mermaid
  flow diagram to include P2H node.

---

## Mutation 22 — 2026-05-23

**Session**: Ecosystem-wide mutation-log infrastructure
**File**: `vsm-fitness-coach/SKILL.md`, `vsm-fitness-gym/SKILL.md`,
  `vsm-fitness-coach/references/mutation-log.md`, `vsm-fitness-gym/references/mutation-log.md`
**Type**: structural
**Rationale**: The vsm-fitness-coach and vsm-fitness-gym skills both referenced
self-modification and the three-tier mutation system, but neither had the
supporting infrastructure to actually do it: no mutation-log.md files, no format
templates, no rollback procedures. The coach lacked epistemic rules entirely.
All companion-skill mutations were being logged in the main skill's
mutation-log.md, violating the principle that each skill should maintain its own
audit trail. This created a single point of failure and made it impossible to
revert companion-skill mutations independently.

**Expected effect**: Both companion skills are now fully self-documenting
learning organisms with their own mutation logs, format templates, rollback
procedures, and epistemic infrastructure. Future mutations to coach prompts,
rubrics, fitness projects, gym templates, or experiment designs will be logged
locally. The main skill's mutation-log.md will only record ecosystem-wide or
main-skill mutations.

**Files modified**:
- `vsm-fitness-coach/references/mutation-log.md` — Created with template and
  initial entries (Mutation 1: infrastructure creation, Mutation 2: Phase 2b)
- `vsm-fitness-gym/references/mutation-log.md` — Created with template and
  initial entry (Mutation 1: infrastructure creation)
- `vsm-fitness-coach/SKILL.md` — Added Section 8: The Mutation System
  (format template, epistemic rules, rollback procedure). Updated Phase 5 to
  reference coach's own mutation-log.md.
- `vsm-fitness-gym/SKILL.md` — Added Section 9: The Mutation System
  (format template, rollback procedure). Updated Section 8 epistemic rules to
  acknowledge gym self-modification. Updated Phase 5 to reference gym's own
  mutation-log.md.

---

## Mutation 23 — 2026-05-24

**Session**: FB10 fitness build — integration checklist append-only mutations
**File**: `references/integration-checklist.md`
**Type**: append
**Rationale**: FB10 revealed that in-process code review misses module-level NameErrors (missing imports) that only surface at runtime. The integration checklist now requires a subprocess import check.
**Expected effect**: Future builds catch `NameError` and `ImportError` before test execution.

---

## Mutation 24 — 2026-05-24

**Session**: FB10 fitness build — frontend build verification
**File**: `references/integration-checklist.md`
**Type**: append
**Rationale**: FB10 frontend infra agent verified `vite build` but `npm run build` (which included `tsc -b`) failed due to missing `@types/node`. The checklist now requires verifying the package.json build script, not just the underlying tool.
**Expected effect**: Future builds catch script-level build failures.

---

## Mutation 25 — 2026-05-24

**Session**: FB10 fitness build — GraphQL enum serialization alignment
**File**: `references/integration-checklist.md`
**Type**: append
**Rationale**: FB10 integration found Strawberry enum values were uppercase (`CUSTOMER`) while frontend TypeScript and REST expected lowercase (`customer`). The checklist now requires verifying GraphQL enum values match frontend contracts.
**Expected effect**: Future builds catch enum serialization drift before integration.

---

## Mutation 26 — 2026-05-24

**Session**: FB10 fitness build — security lessons from security gate
**File**: `references/security-lessons.md`
**Type**: append
**Rationale**: FB10 security gate discovered three high-value findings: privilege escalation via user-supplied role in registration, GraphQL context fail-open on JWT errors, and missing explicit rate limits on auth endpoints. These are now prevention rules.
**Expected effect**: Future builds prevent privilege escalation, fail-open auth contexts, and rate-limiting gaps.

---

## Mutation 27 — 2026-05-24

**Session**: FB10 fitness build — hypothesis backlog update
**File**: `references/hypotheses.md`
**Type**: refinement + append
**Rationale**: Updated statuses for 10 hypotheses tested by FB10 (H13, H21, H23, H24, H25, H26, H29, H32, H33, H41 — all confirmed). Appended 4 new hypotheses from trainer report (H45-H48) covering subprocess import checks, fix wave test suite regression, meta-reflection verification, and frontend build script verification.
**Expected effect**: Hypothesis backlog stays current. New hypotheses provide falsifiable targets for FB11 or gym experiments.


---

## Mutation 28 — 2026-05-24

**Session**: FB10 structural mutations — user approved direct application
**File**: `agents/vsm_coordinator.md`
**Type**: structural
**Rationale**: FB10 revealed that in-process file review (ReadFile) misses module-level NameErrors that only surface at import time. The coordinator must enforce a subprocess import check as part of integration verification.
**Expected effect**: Future builds catch `NameError` and `ImportError` during integration verification, before test execution begins.

---

## Mutation 29 — 2026-05-24

**Session**: FB10 structural mutations — user approved direct application
**File**: `agents/vsm_tester.md`
**Type**: structural
**Rationale**: FB10 fix wave introduced test-schema regressions (enum redefinition broke 4 GraphQL tests) because only changed files were re-audited. The tester agent must now run the full test suite after any fix wave.
**Expected effect**: Fix-wave regressions in unrelated tests are caught immediately, preventing false "fix complete" claims.

---

## Mutation 30 — 2026-05-24

**Session**: FB10 structural mutations — user approved direct application
**File**: `SKILL.md` (Phase 7 and Phase 8b sections)
**Type**: structural
**Rationale**: FB10 meta-reflection repeated false test-pass claims from upstream phases. Phase 7 fix wave missed regressions because full test suite was not mandatory. Both phases need explicit verification requirements in the skill's core workflow.
**Expected effect**: Phase 7 fix waves are gated on full test suite pass. Phase 8b meta-reflections include independently verified test results.


---

## Mutation 31 — 2026-05-24

**Session**: FB11 fitness build — integration checklist expansion
**File**: `references/integration-checklist.md`
**Type**: append
**Rationale**: FB11 security gate found frontend `||` fallbacks for API URLs, CORS defaulting to `*`, and unauthenticated REST endpoints. These were missed by all earlier phases. Three new checklist items added: Frontend Config Fallback Check (36), CORS Configuration Validation (37), REST Endpoint Auth Guard Check (38).
**Expected effect**: Future builds catch frontend fallbacks, CORS misconfigs, and REST auth gaps before the security gate.

---

## Mutation 32 — 2026-05-24

**Session**: FB11 fitness build — hypothesis backlog update
**File**: `references/hypotheses.md`
**Type**: refinement + append
**Rationale**: H45 (subprocess import check) confirmed by FB11 — caught T1 and T5. H47 (meta-reflection independent verification) confirmed — FB11 meta-reflection independently ran tests. H48 (frontend build script) marked inconclusive — trap condition insufficient. Added 5 new hypotheses (H49-H53) from FB11 gaps.
**Expected effect**: Hypothesis backlog stays current. New targets for FB12 or gym experiments.

---

## Mutation 33 — 2026-05-24

**Session**: FB11 fitness build — fitness report and lessons
**File**: `~/vsm-fitness-builds/coach/FB11-20260524/fitness-report.md`
**Type**: append
**Rationale**: FB11 overall score 3.7/5.0 (improvement from FB10's 3.3/5.0). 5 of 6 traps caught. Key improvements: sequenced foundation sub-waves, subprocess import check, split testers. Key gaps: frontend config validation, CORS checks, REST auth guard verification.
**Expected effect**: Structured record of FB11 performance for trainer evaluation and next build design.

