# Experiment Log

> **Mutation rules**: Append only. Each experiment records: hypothesis tested,
> methodology, results, and proposed skill mutations. This is the lab notebook
> of the learning organism.
>
> Experiments are designed to be minimal and isolated — they test ONE hypothesis
> at a time with the smallest possible code surface.

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
**Mutations applied**: Yes — updated `references/hypotheses.md` H1 status to rejected.

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
**Mutations applied**: Yes — updated `references/hypotheses.md` H2 status to rejected.

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
**Mutations applied**: Yes — updated `references/hypotheses.md` H9 status to rejected.

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
