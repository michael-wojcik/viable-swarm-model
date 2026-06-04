# Stack Skills Registry

## Pattern Skills
| Skill | Description | Relevant Agents | Depends On | Status |
|---|---|---|---|---|
| architecture-patterns | System design, data modeling, API contracts | architect, product | — | Full |
| backend-patterns | Server architecture, API design, middleware | backend_coder, backend_fix, backend_tester, coordinator | `[language]-pitfalls` | Full |
| frontend-patterns | Component architecture, state, routing | frontend_coder, frontend_fix, frontend_tester, coordinator | `[language]-pitfalls` | Full |
| database-patterns | Schema design, migrations, query optimization | backend_coder, backend_tester, coordinator | `[language]-pitfalls` | Full |
| sqla-patterns | SQLAlchemy async engine management, session lifecycle, model design | backend_coder, backend_tester, auditor | `python-pitfalls` | Full |
| testing-patterns | Test strategy, fixtures, mocking, coverage | backend_tester, frontend_tester, coordinator | `[language]-pitfalls` | Full |
| tester-backend | Backend test templates, GraphQL mutation testing, coverage requirements | backend_tester, auditor | `testing-patterns`, `python-pitfalls` | Full |
| security-patterns | Auth, input validation, secrets, rate limiting, data exposure | security, auditor, coordinator, all coders | — | Full |
| devops-patterns | Containers, compose, healthchecks, CI/CD | devops_coder, coordinator | — | Deprecated |
| research-patterns | Investigating unfamiliar technologies | architect, explore, meta | — | Full |
| kimi-code-migration | Port VSM skills to kimi-code CLI (no custom agents) | coordinator, meta | — | Full |

## Pitfall Skills
| Skill | Language | Status | Description |
|---|---|---|---|
| python-pitfalls | Python | Full | Module-level instantiation, Pydantic ConfigDict, SQLAlchemy shadowing, etc. |
| typescript-pitfalls | TypeScript | Full | Vite alias failure, build gaps, `as any` bypasses, etc. |
| docker-pitfalls | Docker/Compose | Full | Containerization traps: fallback bans, layer ordering, production build verification, port parity, healthchecks |
| dependency-drift-pitfalls | All | Full | Manifest-environment parity, version drift, lockfile hygiene (FB23-sourced) |
| graphql-pitfalls | GraphQL | Full | Strawberry schema traps, depth limiting, RBAC parity, orphaned queries, enum type mismatch |
| go-pitfalls | Go | Planned | (Awaiting empirical data) |
| rust-pitfalls | Rust | Planned | (Awaiting empirical data) |
| java-pitfalls | Java | Icebox | (Placeholder) |
| csharp-pitfalls | C# | Icebox | (Placeholder) |
| ruby-pitfalls | Ruby | Icebox | (Placeholder) |
| elixir-pitfalls | Elixir | Icebox | (Placeholder) |
| kotlin-pitfalls | Kotlin | Icebox | (Placeholder) |
| swift-pitfalls | Swift | Icebox | (Placeholder) |

---

## Validation Notes

### `validate-skills.py` Checks
1. Every skill directory has a `SKILL.md` file.
2. Every skill in the registry has a matching directory (and vice versa).
3. Full skills meet minimum line count (`MIN_LINES_FULL = 40`) and rule count (`MIN_RULES = 5`).
4. Full skills cite at least one build or experiment ID (e.g., `FB24`, `H150`, `Gym E15`).
5. **Agent prompt references**: `validate-skills.py` SHOULD verify that every agent type listed in a skill's "Relevant Agents" column is referenced in the skill's content (e.g., `vsm_backend_coder`, `vsm_auditor`). This prevents stale registry entries where an agent is listed but never instructed to read the skill.
6. Dependency links resolve: every value in "Depends On" must exist in the registry.

### Status Definitions
| Status | Meaning |
|---|---|
| Full | Actively maintained, empirical rules with build IDs, validated by swarm |
| Planned | Identified as needed, awaiting first fitness build or gym experiment |
| Icebox | Low priority, no imminent need, kept for portfolio completeness |
| Deprecated | Consolidated into another skill; kept for backward compatibility |
| Stub | Legacy term — use Planned or Icebox instead |
