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
