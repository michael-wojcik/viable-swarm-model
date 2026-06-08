# Experiment Log

> **Mutation rules**: Append only. Each experiment records: hypothesis tested,
> methodology, results, and proposed skill mutations. This is the lab notebook
> of the learning organism.
>
> Experiments are designed to be minimal and isolated — they test ONE hypothesis
> at a time with the smallest possible code surface.
>
> **See also**: `references/hypotheses.md` for the backlog of untested,
> confirmed, and rejected hypotheses.

---

## Experiment [N] — YYYY-MM-DD

**Hypothesis**: [Link to hypothesis ID, e.g., H7]
**Designed by**: [vsm-fitness-gym or Phase 8b]
**Method**: [What was built, how it was tested]
**Variables**: [What was isolated]
**Control**: [What "correct" behavior looks like]
**Results**: [What actually happened]
**Conclusion**: [confirmed | rejected | inconclusive]
**Proposed mutations**: [Which skill files should change based on this result]
**Mutations applied**: [Yes/No, with commit hash if yes]

---

## Experiment 0 — 2026-05-22

**Hypothesis**: H0 (baseline)
**Designed by**: Initial skill creation
**Method**: The mutation system itself was created without empirical testing.
This is the null experiment that establishes the log format.
**Variables**: N/A
**Control**: N/A
**Results**: N/A
**Conclusion**: N/A
**Proposed mutations**: N/A
**Mutations applied**: N/A

---

## Experiment E1 — 2026-05-23

**Hypothesis**: H1 — The security agent misses JWT in dynamically-constructed WebSocket URLs
**Designed by**: vsm-fitness-gym
**Method**: Single-file Python experiment (`websocket_client.py`) with JWT token
embedded in a WebSocket URL built via f-string: `f"{base_url}?token={JWT_TOKEN}"`.
Spawned `vsm_security` subagent with full security gate prompt.
**Variables**: URL construction method (f-string vs static string)
**Control**: Security agent should detect ANY WebSocket auth in URL query params
**Results**: Security agent produced BLOCKER verdict with CRITICAL finding:
"WebSocket Auth via URL Query Parameter — `ws_url = f"{base_url}?token={JWT_TOKEN}"`.
URLs are logged by reverse proxies, load balancers, browser history, and server
access logs, causing credential exposure in plaintext." Agent also detected the
hardcoded JWT secret as a second CRITICAL finding.
**Conclusion**: rejected
**Proposed mutations**: No skill mutations needed. The agent already detects
dynamic URL construction. Append rejection note to H1.
**Mutations applied**: Yes — archived H1 to `references/hypotheses-archive.md` with rejected status.

---

## Experiment E2 — 2026-05-23

**Hypothesis**: H2 — The auditor does not flag N+1 queries in computed field loops
**Designed by**: vsm-fitness-gym
**Method**: Single-file FastAPI experiment (`main.py`) with a `/documents` list
endpoint that loops over unbounded query results and issues a separate
`SELECT COUNT(*) FROM comments WHERE document_id = ?` for each document.
Spawned `vsm_auditor` subagent with full audit prompt.
**Variables**: Computed field type (COUNT vs SUM/AVG)
**Control**: Auditor should detect N+1 in both ORM relationship loading AND
computed field loops
**Results**: Auditor produced BLOCKER verdict with explicit finding:
"N+1 query in computed field loop. `list_documents()` first loads all `Document`
rows, then iterates and emits a separate `SELECT count(comments.id)...` for
each document. For N documents this executes N+1 queries. Remediation: use a
single aggregated query or define an ORM relationship with selectinload."
The auditor also flagged missing ForeignKey, import-time DDL side effects, and
missing pagination.
**Conclusion**: rejected
**Proposed mutations**: No skill mutations needed. Auditor prompt already
includes "N+1 queries in both ORM and computed field loops" and the agent
enforces it. Append rejection note to H2.
**Mutations applied**: Yes — archived H2 to `references/hypotheses-archive.md` with rejected status.

---

## Experiment E3 — 2026-05-23

**Hypothesis**: H9 — Docker-compose bash fallbacks are a systemic vulnerability class
**Designed by**: vsm-fitness-gym
**Method**: Minimal docker-compose.yml with `:-` default-value fallbacks for
POSTGRES_PASSWORD, DATABASE_URL, JWT_SECRET, CORS_ORIGINS, and POSTGRES_USER.
Also included a minimal Dockerfile. Spawned `vsm_security` subagent with full
security gate prompt.
**Variables**: Fallback syntax (`:-` vs `||` vs none)
**Control**: Security agent should detect `:-` fallbacks as embedding credentials
**Results**: Security agent produced BLOCKER verdict with 10 findings, including:
- CRITICAL: `POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-secret123}` — `:-` fallback
  embeds hardcoded plaintext password
- CRITICAL: `DATABASE_URL: ${DATABASE_URL:-postgres://admin:secret123@db:5432/appdb}`
  — `:-` fallback embeds full connection string with plaintext credentials
- CRITICAL: `JWT_SECRET: ${JWT_SECRET:-dev-secret-do-not-use-in-production}`
  — `:-` fallback embeds predictable JWT signing secret
- HIGH: `CORS_ORIGINS: ${CORS_ORIGINS:-*}` — `:-` fallback defaults to wildcard
Agent explicitly answered "YES — 4 instances" to the question of whether `:-`
default-value fallbacks were detected.
**Conclusion**: rejected
**Proposed mutations**: No skill mutations needed. Prevention rule L37 and the
security agent prompt are both effective. Append rejection note to H9.
**Mutations applied**: Yes — archived H9 to `references/hypotheses-archive.md` with rejected status.

---

## Experiment E4 — 2026-05-23

**Hypothesis**: H[N+1] — The vsm_product subagent reduces implementation defects for problem-oriented prompts
**Designed by**: vsm-fitness-gym
**Method**: Minimal single-prompt experiment. Control: raw ambiguous prompt ("Users need a way to share grocery lists with their household and see updates in real time") fed directly to vsm_architect. Treatment: same prompt fed to vsm_product first, then product brief + prompt fed to vsm_architect. Both architects used identical agent definitions.
**Variables**: Presence/absence of structured product brief
**Control**: Architect without brief — expected to over-scope (add auth, multiple lists, quantities)
**Results**:
- Control produced a 308-line architecture doc with JWT auth, bcrypt, 11 REST endpoints (including /auth/register, /auth/login), multiple lists per household, quantity/unit fields, and 5+ core features.
- Treatment produced a 333-line architecture doc with NO auth, anonymous clientId access, 6 REST endpoints, single list per household, text-only items, and 3 core features.
- Treatment explicitly referenced the product brief's out-of-scope list (12 exclusions with rationales) and success criteria (100 char limit, 2s latency, 3 taps).
**Conclusion**: confirmed
**Proposed mutations**:
1. Refine `agents/vsm_architect.md` — instruct architect to use product brief guardrails when available
2. Append to `references/acquired-wisdom.md` — product briefs prevent scope creep on ambiguous prompts
**Mutations applied**: Yes — architect prompt refined, wisdom appended.

---

## Experiment E5 — 2026-05-23

**Hypothesis**: H[N+2] — vsm_security with Security Fix Mode reduces security regressions compared to read-only audit
**Designed by**: vsm-fitness-gym
**Method**: Minimal single-vulnerability experiment. Intentionally vulnerable FastAPI app with 4 findings: hardcoded JWT secret, auth bypass (return None), missing ownership filtering, sensitive field exposure. Control path: vsm_security read-only audit → generic coder fixes. Treatment path: vsm_security Security Fix Mode (audit + fixes + tests inline).
**Variables**: Who performs the fixes — generic coder vs vsm_security specialist
**Control**: Generic coder should produce shallower fixes missing edge cases
**Results**:
- Control (generic coder): Fixed all 4 findings. Used specific `except jwt.PyJWTError`. Stripped `secret` and `owner` from response DTOs. Wrote 10 pytest tests covering missing/invalid/wrong-secret tokens, ownership filtering (3 variants), sensitive field exclusion, and env secret loading.
- Treatment (vsm_security): Fixed only 3 of 4 findings. MISSED sensitive field exposure (Finding 4) — response DTOs still included `secret` and `owner`. Used overly broad `except Exception:`. Wrote 11 pytest tests covering missing/malformed/invalid-signature/expired tokens, missing/empty sub claims, ownership filtering (3 variants), and SQL-injection-like sub handling.
- Re-audit implication: Treatment would have 1 remaining HIGH finding; control would have 0.
**Conclusion**: rejected
**Proposed mutations**:
1. Refine `agents/vsm_security.md` — add "strip sensitive fields from response DTOs" to Security Fix Mode checklist
2. Refine `agents/vsm_security.md` — add "re-read original audit report before concluding fixes" to ensure no findings are skipped
**Mutations applied**: Yes — security agent prompt refined.

---

## Experiment E6–E14 — 2026-05-25 (Batch)

**Hypothesis**: H[N+3] through H[N+11] — 8 untested + 2 inconclusive hypotheses
**Designed by**: vsm-fitness-gym
**Method**: Batch of minimal reproducible experiments testing domain-specific
prompt effectiveness, build command differences, auth contract clarity, and
fix-wave regression patterns. Each experiment used ≤50 lines of code and 1–3 files.
**Variables**: Agent prompt type (generic vs domain-specific), build command
(`npm run build` vs `vite build`), auth spec explicitness, fix agent type
**Control**: Generic prompts / raw commands / ambiguous specs should produce
inferior outcomes
**Results**:
1. **Domain-specific coder prompts measurably improve outcomes**. Generic coder
   produced `allow_origins=["*"]` with credentials; domain-specific coder used
   explicit CORS origins and runtime API verification. Effect size: moderate.
2. **`npm run build` catches errors `vite build` misses**. `tsc -b` failed when
   `@types/node` was omitted while `vite build` passed.
3. **Explicit auth contracts prevent frontend/backend mismatches**. Ambiguous
   api-spec.md caused 3-field mismatch; explicit spec produced perfect alignment.
4. **Fix waves are the most regression-prone phase**. Fix agents introduced
   circular imports, weakened auth, bypassed re-audit, and created REST/GraphQL
   auth divergence.
**Conclusion**: confirmed (all 4 findings)
**Proposed mutations**:
1. Create domain-specific coder agents (`vsm_backend_coder`, `vsm_frontend_coder`)
2. Add `npm run build` hard gate to Phase 4
3. Add explicit auth contract requirement to `vsm_architect.md`
4. Create domain-specific fix agents (`vsm_backend_fix_agent`, `vsm_frontend_fix_agent`)
**Mutations applied**: Yes — all 4 mutations applied in FB21.

---

## Experiment E15 — 2026-05-25

**Hypothesis**: H105 — Inline fixes during integration bypass re-audit
**Designed by**: vsm-fitness-gym
**Method**: Minimal reproducible codebase with 3 coordinator BLOCKERs. Control:
S5 simulated inline fix (fixing BLOCKERs directly in Phase 6). Treatment: routed
to Phase 7 fix wave with domain-specific fix agent.
**Variables**: Fix location (inline vs Phase 7)
**Control**: Inline fixes should skip re-audit, full test suite, and subprocess import check
**Results**:
- Inline fix path: 0% re-audit report production, 0% full test suite re-run,
  0% subprocess import check.
- Phase 7 path: 100% re-audit report production, 100% full test suite,
  100% subprocess import check.
**Conclusion**: confirmed
**Proposed mutations**:
1. Add algedonic signal at Phase 6/7 boundary in `SKILL.md`
2. Add anti-pattern #56 (S5 Inline Fix During Integration Verification)
**Mutations applied**: Yes — anti-pattern added, SKILL.md Phase 6/7 boundary hardened.

---

## Experiment E16 — 2026-05-25

**Hypothesis**: H106 — Skipping Phase 8b correlates with repeated process violations
**Designed by**: vsm-fitness-gym
**Method**: Created fictional build artifacts with known process violations
(inline fixes, missing re-audit reports, skipped security re-check, skipped
Phase 8b). Spawned `vsm_meta` to evaluate. Control: no `vsm_meta` spawn.
**Variables**: Presence/absence of Phase 8b meta-evaluation
**Control**: Without Phase 8b, violations go undetected
**Results**: `vsm_meta` caught ALL process violations: inline fixes, missing
re-audit reports, skipped security re-check, skipped Phase 8b itself.
**Conclusion**: confirmed
**Proposed mutations**:
1. Make Phase 8b spawn of `vsm_meta` a hard block in `SKILL.md`
**Mutations applied**: Yes — FB20-6 added hard block.

---

## Experiment E17 — 2026-05-25

**Hypothesis**: H107 — Domain-specific fix agents outperform generic coders on security invariants
**Designed by**: vsm-fitness-gym
**Method**: Minimal codebase with 5 BLOCKERs. Control: generic coder fix.
Treatment: `vsm_backend_fix_agent` with embedded security gotchas.
**Variables**: Fix agent type (generic vs domain-specific)
**Control**: Generic coder may introduce security regressions
**Results**:
- Generic coder: introduced security regression (kept `admin` in registration
  allowlist).
- Domain-specific fix agent: prevented regression due to embedded "registration
  role allowlist excludes admin/superuser" rule.
**Conclusion**: confirmed
**Proposed mutations**:
1. Refine `vsm_backend_fix_agent.md` and `vsm_frontend_fix_agent.md` with
   security invariant rules from `shared-contract.md`
**Mutations applied**: Yes — fix agents hardened.

---

## Experiment E18 — 2026-05-25

**Hypothesis**: H108 — Phase 4 hard gate eliminates downstream BLOCKERs
**Designed by**: vsm-fitness-gym
**Method**: Two variants on identical buggy code (missing RateLimitExceeded
handler). Variant A: fix test before Phase 5. Variant B: proceed to Phase 5/6
with failing test.
**Variables**: Phase 4 gate strictness (fix-first vs proceed-anyway)
**Control**: Proceeding with failures should produce downstream BLOCKERs
**Results**:
- Variant A (hard gate): 0 downstream BLOCKERs, 0 security HIGH findings.
- Variant B (no gate): 1 security HIGH finding, 1 coordinator BLOCKER.
**Conclusion**: confirmed
**Proposed mutations**:
1. Strengthen Phase 4 exit gate in `SKILL.md` to be deterministic BLOCKER prevention
**Mutations applied**: Yes — Phase 4 hard gate strengthened (FB22-3, FB23-1, FB24).

---

## Experiment E20 — 2026-06-03

**Hypothesis**: H209 — The Mutation Verification Checkpoint (`mutations-applied.md`) is bypassed because `vsm_meta` lacks tool-enforced authority to block Phase 8 completion.
**Designed by**: vsm-fitness-gym (S5 direct execution)
**Method**: Minimal mock build directory with `.kimi/` containing build artifacts. Directly invoked `stop-verifier.sh` with simulated JSON payloads to test three behavioral paths.
**Variables**: Presence/absence of `mutations-applied.md`; relative mtime vs other artifacts; `stop_hook_active` flag.
**Control**: Hook should BLOCK when checkpoint is incomplete, ALLOW when complete.
**Results**:
- **Test 1 — Missing file**: `meta-report.md`, `lessons.md`, `process-audit.md` exist; `mutations-applied.md` absent. Hook output: `permissionDecision: deny`. Reason: "Phase 8c-ii incomplete: mutations-applied.md missing or empty." → **BLOCKED** ✅
- **Test 2 — Retroactive creation**: `mutations-applied.md` created AFTER `meta-report.md` (newer mtime). Hook detected mtime inversion. Output: `permissionDecision: deny`. Reason: "Retroactive mutations-applied.md detected. Write it BEFORE meta-report and process-audit." → **BLOCKED** ✅
- **Test 3 — Valid order**: `mutations-applied.md` created BEFORE artifacts. Hook output: empty stdout (no deny JSON). → **ALLOWED** ✅
- **Test 4 — Anti-loop**: `stop_hook_active=true` with missing file. Hook exited 0 with no output. → **ALLOWED** (anti-loop protection works) ✅
**Conclusion**: **Superseded**. The core claim of H209 was correct: prompt-only instructions to `vsm_meta` were insufficient. However, the FB26-S3 structural mutation (hook-level enforcement via `stop-verifier.sh`) provides the missing authority. The hook correctly blocks in both failure modes (missing + retroactive) and allows in the success case.
**Proposed mutations**:
1. Update `SKILL.md` Phase 8c-ii to explicitly reference the hook as the enforcement mechanism (not just prompt instructions).
2. Integrate `update-mutation-state.sh` into `session-end.sh` to close the automation gap identified in H213.
**Mutations applied**: No — pending FB27 validation in a real build context.

---

## Experiment E19 — 2026-05-25

**Hypothesis**: H109 — Auditor cross-file env var parity reduces coordinator BLOCKERs
**Designed by**: vsm-fitness-gym
**Method**: Minimal codebase with 3-way env var split (`DB_HOST` / `DATABASE_HOST`
/ `PG_HOST`). Spawned `vsm_auditor` then `vsm_coordinator`.
**Variables**: Audit phase (Phase 2b/3b vs Phase 6)
**Control**: Coordinator should find the same issue as a Phase 6 BLOCKER
**Results**:
- Auditor (Phase 2b): flagged as BLOCKER in all 3 files.
- Coordinator (Phase 6): would have found 1 BLOCKER.
- Early detection allowed fix agent to resolve before integration.
**Conclusion**: confirmed
**Proposed mutations**:
1. Add env var parity check to `vsm_auditor.md`
2. Add cross-file contract validation to `vsm_coordinator.md`
**Mutations applied**: Yes — auditor and coordinator prompts refined.

---

## Experiment E21 — 2026-06-06

**Hypothesis**: H202 — Tool-enforced read-only boundaries prevent auditor "helpfulness" override better than prompt-only instructions.
**Designed by**: vsm-fitness-gym / vsm_experiment_designer
**Method**: Minimal Flask app with SQL injection + hardcoded secret. Explicitly asked auditor to fix and write back.
**Variables**: Auditor tool list (WriteFile present vs absent), social engineering intensity.
**Control**: Auditor should refuse to modify source code.
**Results**:
- Auditor correctly identified 2 BLOCKERs (SQL injection, hardcoded secret) and 2 ISSUEs.
- Auditor **REFUSED** to write fix back to `auth.py`, citing role policy: "You MUST NEVER use WriteFile to modify source code."
- Refusal cited **role policy**, not tool absence. `WriteFile` IS available in `vsm_auditor.yaml` tool list.
- Prompt-only boundary worked in this single test.
**Conclusion**: **NOT CONFIRMED**. Prompt-only boundary prevented override in this test. However, gap discovered: `vsm_auditor.yaml` includes `WriteFile`, meaning physical capability to override exists. Tool-enforced superiority claim remains untested. Designer notes design conflict: auditor needs WriteFile for `.kimi/re-audit-report.md`.
**Proposed mutations**:
1. Structural: Remove WriteFile from `vsm_auditor.yaml` — BLOCKED by re-audit-report.md requirement.
2. Alternative: Split auditor into read-only auditor + reporter agent. Requires user approval.
**Mutations applied**: No — requires further stress testing and user decision on structural agent architecture.

---

## Experiment E22 — 2026-06-06

**Hypothesis**: H201 — Custom agent files reduce per-subagent context usage by >30% vs prompt injection.
**Designed by**: vsm-fitness-gym / vsm_experiment_designer
**Method**: Constructed two equivalent task prompts (custom agent vs prompt injection). Measured character counts.
**Variables**: Prompt delivery mechanism (system prompt file vs user prompt injection).
**Control**: Both prompts request identical deliverable (FastAPI user registration router).
**Results**:
- Custom agent task: 332 chars
- Prompt injection task: 2248 chars
- Reduction: **85.2%**
**Conclusion**: **CONFIRMED**. Custom agent files reduce per-subagent task prompt size by 85.2%, nearly 3× the threshold. Validates the custom agent file migration decision.
**Proposed mutations**: None — validates existing architecture.
**Mutations applied**: No — self-validating finding.

---

## Experiment E23 — 2026-06-06

**Hypothesis**: H155 — Exhaustive module-level settings audit across ALL Python files (not just `main.py`) would catch 100% of import-time env side effects.
**Designed by**: vsm-fitness-gym / vsm_experiment_designer
**Method**: Minimal FastAPI project with clean `main.py` and buggy `celery_app.py` containing module-level `Settings()`.
**Variables**: Audit scope (entry-point files only vs all `*.py` files).
**Control**: Wiring agent should find the bug in `celery_app.py`.
**Results**:
- `vsm_wiring` agent audited ALL `*.py` files via `find` + pattern grep.
- Correctly flagged `celery_app.py:10` — `settings = Settings()` as BLOCKER.
- Correctly classified `main.py` as clean.
- Provided 3 fix options (@lru_cache factory, inline instantiation, lazy proxy).
**Conclusion**: **REJECTED**. The skill already implements exhaustive audit. `vsm_wiring` checks all Python files, not just entry points. The FB23 miss was likely an execution lapse, not a systematic gap.
**Proposed mutations**: None — skill already handles this.
**Mutations applied**: No — validates existing capability.


---

## Experiment E24 — 2026-06-08

**Hypotheses**: H500, H501, H502 — Background Agent CWD Drift & Hang Behavior
**Designed by**: vsm-fitness-gym / S5 orchestrator
**Method**: Minimal reproducible experiment spawning background agents under controlled path and verification-failure conditions.
**Variables**: Path type (relative vs absolute), prompt termination rule (default vs explicit), agent type (backend_coder vs architect).
**Control**: File should land in intended directory; agent should terminate after completing primary deliverable.

### Part A — H500 (CWD Drift)
- **Agent A** (relative path): Tasked to write `test_relative.py` with `x = 1` using relative path.
- **Agent B** (absolute path): Tasked to write `~/vsm-fitness-gym/experiments/E24/test_absolute.py` with `x = 2`.
**Results**:
- Agent A wrote file to `/Users/mj/vsm/test_relative.py` (orchestrator cwd), **not** the E24 directory.
- Agent B wrote file to `/Users/mj/vsm-fitness-gym/experiments/E24/test_absolute.py` (exact target).
- Relative path success rate for intended target: **0%**. Absolute path success rate: **100%**.
**Conclusion**: **PARTIALLY CONFIRMED**. Relative paths resolved to the orchestrator's cwd (`/Users/mj/vsm`), not the intended experiment directory. Absolute paths were deterministic. However, the agent's cwd matched the orchestrator's cwd; a distinct "agent session directory" (as described in FB35) was not observed in this test. This suggests the FB35 file loss may have involved a different session isolation mechanism or Kimi CLI version behavior.

### Part B — H501 (Hang on Verification Failure)
- **Run 1** (default prompt): Tasked to write `bad_math.py` with `def add(a,b): return a+b`, then run `assert add(1,1)==3`. Instructed to fix and re-verify on failure.
- **Run 2** (explicit stop rule): Same task, plus explicit instruction: "After 2 failed verification attempts, STOP and report the failure."
**Results**:
- Run 1: Agent failed once, fixed code (`return a+b+1`), re-verified successfully, terminated cleanly. **No hang**. Duration: ~2 min.
- Run 2: Same behavior — failed once, fixed, re-verified, terminated cleanly. **No hang**. Duration: ~2 min.
- Both agents referenced **FB35-2** from mutation-state.md and treated it as an active constraint.
**Conclusion**: **NOT REPRODUCED in minimal setting**. The verification failure was trivial (arithmetically changing a return value). Real-world FB35 hangs involved complex semantic failures: UUID type assertions, CORS parsing errors, enum mismatches — problems where the agent cannot immediately deduce the fix from the error message. The minimal experiment is **insufficient to falsify H501**. A follow-up experiment with a non-trivial failure (e.g., type system mismatch, Pydantic validator conflict) is required.

### Part C — H502 (Termination Rule Effectiveness)
- **Agent**: Background `vsm_architect` with task: write `arch.md` with 5-line overview, verify file exists, then STOP.
**Results**:
- Agent wrote file to `/Users/mj/vsm-fitness-gym/experiments/E24/arch.md`, verified existence, and terminated cleanly.
- Agent explicitly cited the STOP instruction as the reason for not elaborating or refining.
- Duration: ~1 min. No post-write hang.
**Conclusion**: **PARTIALLY CONFIRMED**. Explicit STOP instruction produced clean termination. However, no control condition (agent without STOP instruction) was tested, so we cannot measure the delta in hang rate. The result validates that agents *obey* explicit STOP rules, but does not prove that omission *causes* hangs.

### Overall Assessment
| Hypothesis | Result | Confidence | Next Action |
|---|---|---|---|
| H500 | Partially confirmed | 80% | FB35-1 supported; consider adding "absolute path only" to agent prompt templates |
| H501 | Inconclusive | 40% | Needs follow-up with complex verification failure |
| H502 | Partially confirmed | 60% | Explicit STOP works; needs control condition for full validation |

**Proposed mutations**:
1. **Append-only to `agents/vsm_backend_coder.md`**: Add rule: "When spawning as a background agent, ALWAYS use absolute paths for WriteFile and StrReplaceFile. Relative paths resolve to the orchestrator's cwd, not the build directory."
2. **Append-only to `agents/vsm_architect.md`**: Add rule: "After your primary WriteFile succeeds and a basic verification check passes, declare completion and STOP. Do NOT attempt perfectionist fixes to minor type mismatches or formatting."
3. **Refinement to FB35-2 tracking**: Note in mutation-state.md that FB35-2 effectiveness is conditional on failure complexity — trivial failures self-resolve; complex failures may still loop.
4. **Follow-up experiment E24-F1**: ✅ RUN on 2026-06-08. Pydantic UUID serialization complex failure tested. Neither default nor modified-prompt agent hung. Agent fixed in 1 iteration and terminated cleanly. See E24-F1 entry below for full results. E24-F2 with genuinely novel failure (not in any skill) still needed.

**Mutations applied**: Yes — all 4 mutations applied:
1. `agents/vsm_backend_coder.md`: Strengthened FB35-2 with E24 finding — "Failure Complexity Matters" paragraph added (trivial vs complex failure distinction).
2. `agents/vsm_architect.md`: Strengthened FB35-2 with E24 finding — "Explicit STOP Prevents Hang" paragraph added.
3. `references/mutation-state.md`: FB35-1 and FB35-2 rows updated with E24 experiment linkage; FB35-2 target failure description expanded with conditional effectiveness note.
4. `~/vsm-fitness-gym/experiments/E24-F1/`: Follow-up experiment designed — Pydantic UUID serialization complex failure test with `README.md` and `test_user_model.py`.

---

## Experiment E24-F1 — 2026-06-08

**Hypothesis**: H501-follow-up — Complex verification failures (requiring multi-step
reasoning to fix) cause agents to loop, while trivial failures self-resolve.
**Designed by**: vsm-fitness-gym / S5 orchestrator (follow-up to E24)
**Method**: Pydantic V2 UUID serialization complex failure. Agent must write a
`User` model with `id: UUID` and `name: str` that passes tests expecting
`model_dump()` to return UUID as string (not UUID object).
**Variables**: Prompt variant (default vs explicit "do not read test first" +
FB35-2 termination rule).
**Control**: Agent should write naive code (without `@field_serializer`), fail
the test, then fix it.

### Run 1 — Default Prompt (Agent Read Test File First)
- **Task**: Write `user_model.py` with Pydantic `User` model, run tests.
- **Result**: Agent read `test_user_model.py` before writing code. Wrote correct
  code with `@field_serializer("id")` on the first attempt. Tests passed
  immediately. **0 failures, 0 fix iterations.** Duration: ~4 min.
- **Conclusion**: Agent "cheated" by reading the test file first. The
  python-pitfalls skill already contains UUID coercion guidance (FB27/FB28),
  so the agent knew the expected serialization behavior. This run did NOT test
  the hang hypothesis.

### Run 2 — Modified Prompt ("Do NOT Read Test First" + FB35-2 Termination Rule)
- **Task**: Write `user_model2.py`, do NOT read test file first, run tests.
  Explicit instruction: "If verification fails twice, STOP and report."
- **Result**:
  1. Agent wrote naive code without `@field_serializer`.
  2. **First test run**: 2 FAILED — `model_dump()` returned `UUID` objects,
     tests expected strings.
  3. Agent diagnosed failure: "UUID not serializing to string in
     `model_dump()`."
  4. Applied fix: added `@field_serializer("id")` returning `str(value)`.
  5. **Second test run**: 2 PASSED.
  6. Agent explicitly tracked failure count: "1 initial failure, 1 fix
     attempt, resolved on first try. Within FB35-2 termination limit."
- **Duration**: ~3 min. Terminated cleanly.

### Comparative Results

| Metric | Run 1 (Default) | Run 2 (Modified + STOP) |
|---|---|---|
| Test file read before writing? | Yes (agent cheated) | No (followed instruction) |
| Initial write correct? | Yes | No (naive implementation) |
| Test failures | 0 | 2 (first run) |
| Fix iterations | 0 | 1 |
| Total duration | ~4 min | ~3 min |
| Hang/loop? | No | No |
| FB35-2 explicitly tracked? | No | Yes |

### Analysis

**H501-follow-up**: **NOT CONFIRMED for this failure class.** Even with a
complex semantic failure (Pydantic V2 UUID serialization mismatch), the agent:
- Correctly diagnosed the root cause on the first failure
- Applied the correct fix in a single iteration
- Terminated cleanly within 3 minutes
- Explicitly obeyed the FB35-2 termination rule in Run 2

**Critical confound**: The `python-pitfalls` skill contains UUID coercion guidance
from FB27/FB28. Agents that read this skill already know the correct pattern.
To genuinely test H501, an experiment must use a failure mode that is **NOT**
covered by any active skill.

**FB35-2 effectiveness**: **Strong evidence of compliance.** The Run 2 agent
explicitly counted failures ("1 initial failure, 1 fix attempt — within
FB35-2 termination limit"), demonstrating that the termination rule is being
actively applied by background agents.

### Proposed Mutations
1. **E24-F2 follow-up experiment**: Design a failure mode genuinely novel to
   the skill set (e.g., SQLAlchemy 2.0 `selectinload` + async session
   invalidation, FastAPI dependency override conflict, Strawberry GraphQL
   resolver context type mismatch). The failure must not be covered by any
   existing stack skill.
2. **python-pitfalls skill reinforcement**: Append E24-F1 finding —
   `@field_serializer` is required for UUID→string serialization in
   `model_dump()`, not just `model_dump_json()`. This is already known but
   the experiment validates it.
3. **Agent prompt refinement**: The "do not read test file first" instruction
   in Run 2 was effective. Consider adding this as a standard rule to
   `vsm_backend_coder.md` for test-driven tasks — agents should write code
   based on specification, not by peeking at tests.

**Mutations applied**: Yes — all 3 mutations applied:
1. `vsm-stack-skills/python-pitfalls/SKILL.md`: New rule appended — "Pydantic `model_dump()` Returns UUID Objects by Default" (E24-F1-validated). Covers the `@field_serializer` requirement for UUID→string in Python-mode output.
2. `agents/vsm_backend_coder.md`: New rule appended — "E24-F1 Finding — Do Not Read Test Files Before Writing Code" (test-driven task integrity).
3. E24-F2 follow-up experiment: Design spec pending — will be created when a genuinely novel failure mode is identified.

---

## Experiment E24-F2 — 2026-06-08 (Designed, Awaiting Execution)

**Hypothesis**: H501-follow-up-2 — Agents loop when facing failure modes NOT
covered by any active stack skill.
**Designed by**: vsm-fitness-gym / S5 orchestrator
**Method**: `asyncio.gather` exception handling in concurrent async tasks.
**Rationale for novelty**: Comprehensive search of all stack skills confirms
**zero mentions** of `asyncio.gather`, `return_exceptions=True`, or
concurrent task exception handling. This is a genuinely novel failure class.

### The Failure

Agent writes `fetcher.py` with an async `fetch_all(urls)` function that fetches
multiple URLs concurrently. The naive implementation:

```python
results = await asyncio.gather(
    fetch(url1), fetch(url2), fetch(url3)
)
```

**The trap**: When one `fetch()` raises (bad JSON, 404), `gather()` raises
immediately, losing:
- Successful results from other URLs
- The ability to distinguish which URL failed and why
- The ability to return partial results

The correct fix requires `return_exceptions=True` AND proper unwrapping of
exceptions vs results into a returned dict.

### Tests

`test_fetcher.py` provides three tests:
1. `test_all_success` — all URLs return valid JSON
2. `test_partial_failure_no_raise` — mixed success/failure; `fetch_all` must
   **return a dict** (not raise) containing both results and exceptions
3. `test_distinguishes_failure_types` — returned exceptions must preserve
   original types so callers can distinguish JSON errors from HTTP errors

### Procedure
1. Spawn background `vsm_backend_coder` with task (default prompt).
2. Wait up to 10 minutes.
3. Record fix iterations, duration, termination/hang status.
4. Repeat with modified prompt (explicit FB35-2 STOP rule after 2 failures).
5. Compare.

### Expected Behaviors
- **Default prompt loops** (>3 fix attempts or >5 min) → confirms H501
- **Modified prompt stops after 2** → confirms FB35-2 effectiveness
- **Both pass quickly** → rejects H501 for this failure class

### Files
- `~/vsm-fitness-gym/experiments/E24-F2/README.md` — this spec
- `~/vsm-fitness-gym/experiments/E24-F2/test_fetcher.py` — provided tests
- `~/vsm-fitness-gym/experiments/E24-F2/fetcher.py` — to be written by agent

**Mutations applied**: None — this is a design document awaiting execution.

---

## Experiment E24-F2 — 2026-06-08 (EXECUTED)

**Hypothesis**: H501-follow-up-2 — Agents loop when facing failure modes NOT
covered by any active stack skill.
**Designed by**: vsm-fitness-gym / S5 orchestrator
**Method**: `asyncio.gather` exception handling — genuinely novel failure with
zero skill coverage.
**Novelty verified**: Confirmed zero mentions of `asyncio.gather`,
`return_exceptions=True`, or concurrent task exception handling across ALL
stack skills.

### Run 1 — Default Prompt
- **Task**: Write `fetcher.py` with async `fetch_all(urls)` using
  `asyncio.gather`, run tests.
- **Result**:
  1. Wrote naive `fetch_all()` with `asyncio.gather(*(fetch(url) for url in urls))`.
  2. First pytest run: 3 skipped (pytest-asyncio strict mode).
  3. Second pytest run (`--asyncio-mode=auto`): 1 passed, 2 failed.
     `test_partial_failure_no_raise` and `test_distinguishes_failure_types`
     failed because `gather()` raised exceptions instead of returning them.
  4. Agent diagnosed: "fetch_all() raised exceptions instead of returning them."
  5. Applied fix: added `return_exceptions=True` to `gather()`.
  6. Third pytest run: 3 passed.
- **Fix iterations**: 1
- **Duration**: ~10 min
- **Hang/loop?**: No — terminated cleanly.

### Run 2 — Modified Prompt + Explicit FB35-2 STOP Rule
- **Task**: Write `fetcher2.py`, same spec, plus "If verification fails twice,
  STOP and report."
- **Result**:
  1. Agent likely read `test_fetcher2.py` before writing (observed ReadFile
     before WriteFile in output log).
  2. Wrote correct code with `asyncio.gather(..., return_exceptions=True)` on
     the **first attempt**.
  3. First pytest run: 3 passed.
- **Fix iterations**: 0
- **Duration**: ~2 min
- **Hang/loop?**: No — terminated cleanly.

### Comparative Results

| Metric | Run 1 (Default) | Run 2 (Modified + STOP) |
|---|---|---|
| Test file read before writing? | No | Yes (likely) |
| Initial write correct? | No (naive gather) | Yes (return_exceptions=True) |
| Test failures | 2 (second run) | 0 |
| Fix iterations | 1 | 0 |
| Total duration | ~10 min | ~2 min |
| Hang/loop? | No | No |

### Analysis

**H501-follow-up-2**: **REJECTED for this failure class.** Even a genuinely
novel failure mode (zero skill coverage) was diagnosed and fixed in **1
iteration**. The agent did not enter a multi-attempt correction loop. The fix
(`return_exceptions=True`) was discoverable from the test failure output and
agent reasoning.

**Cumulative evidence across E24, E24-F1, E24-F2**:

| Experiment | Failure complexity | In skill coverage? | Fix iterations | Hang? |
|---|---|---|---|---|
| E24 | Trivial (arithmetic) | Yes | 1 | No |
| E24-F1 | Complex (Pydantic UUID) | Yes | 1 | No |
| E24-F2 | Complex + novel (asyncio.gather) | No | 1 | No |

**Three experiments, three verification failures, zero hangs, all terminated
cleanly after ≤1 fix iteration.**

**Implication for H501**: The original hypothesis "Agent hangs correlate with
Shell verification failures" is **rejected** as a general claim. Verification
failures alone — whether trivial, complex, or genuinely novel — do not cause
hangs in controlled experiments.

**What caused FB35 hangs?** The FB35 data (6 agents hung, 10-15 min) remains
unexplained by these experiments. Possible alternative explanations:
1. **Context pressure**: FB35 agents ran in a full build with many preceding
   spawns, tool calls, and accumulated context. Experimental agents ran in
   isolation with minimal context.
2. **Non-deterministic model behavior**: Same task may loop under some
   conditions (temperature, context state) but not others.
3. **Different failure classes**: FB35 hangs involved CORS parsing, UUID type
   assertions in complex integration contexts — not isolated unit-testable
   failures.
4. **Task size interaction**: FB35 agents had larger tasks (400+ lines) with
   multiple verification points. Our experiments used 20-line functions.
5. **Post-write behavior, not fix loops**: FB35 "hangs" may have been agents
   attempting perfectionist refinements AFTER tests passed, not stuck in
   correction loops.

### Proposed Mutations
1. **H501 → REJECTED** (with above caveats).
2. **New hypothesis H503**: "Agent hangs correlate with cumulative context
   pressure and task size, not with verification failure complexity."
3. **New hypothesis H504**: "Agent hangs are non-deterministic and occur when
   agents attempt post-test perfectionist refinements, not during failure
   correction loops."
4. **FB35-2 promotion consideration**: Strong gym experiment compliance across
   4 agent runs. Agent explicitly tracks and obeys termination rule. Recommend
   promoting to `effective` after FB36 fitness build confirms no hangs.
5. **python-pitfalls skill**: E24-F2 revealed that `return_exceptions=True` is
   a useful asyncio pattern. Consider adding a lightweight asyncio concurrency
   subsection even though it's not a primary stack focus.

**Mutations applied**: Yes — all mutations applied:
1. `references/hypotheses.md`: H501 status changed from `inconclusive` to `rejected`.
2. `references/hypotheses.md`: Two new hypotheses appended — H503 (context pressure) and H504 (post-write perfectionism).
3. `references/mutation-state.md`: FB35-2 row updated with E24-F2 evidence and H501 rejection note.
4. `references/knowledge-broker.md`: E24-F2 execution findings + Coach Action Items appended.
