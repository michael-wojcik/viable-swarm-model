# Stack Skills Registry

## Pattern Skills
| Skill | Description | Relevant Agents | Depends On |
|---|---|---|---|
| architecture-patterns | System design, data modeling, API contracts | architect, product | — |
| backend-patterns | Server architecture, API design, middleware | backend_coder, backend_fix, backend_tester, coordinator | `[language]-pitfalls` |
| frontend-patterns | Component architecture, state, routing | frontend_coder, frontend_fix, frontend_tester, coordinator | `[language]-pitfalls` |
| database-patterns | Schema design, migrations, query optimization | backend_coder, backend_tester, coordinator | `[language]-pitfalls` |
| sqla-patterns | SQLAlchemy async engine management, session lifecycle, model design | backend_coder, backend_tester, auditor | `python-pitfalls` |
| testing-patterns | Test strategy, fixtures, mocking, coverage | backend_tester, frontend_tester, coordinator | `[language]-pitfalls` |
| tester-backend | Backend test templates, GraphQL mutation testing, coverage requirements | backend_tester, auditor | `testing-patterns`, `python-pitfalls` |
| security-patterns | Auth, input validation, secrets, rate limiting, data exposure | security, auditor, coordinator, all coders | — |
| devops-patterns | Containers, compose, healthchecks, CI/CD | devops_coder, coordinator | — |
| research-patterns | Investigating unfamiliar technologies | architect, explore, meta | — |
| kimi-code-migration | Port VSM skills to kimi-code CLI (no custom agents) | coordinator, meta | — |

## Pitfall Skills
| Skill | Language | Status | Description |
|---|---|---|---|
| python-pitfalls | Python | Full | Module-level instantiation, Pydantic ConfigDict, SQLAlchemy shadowing, etc. |
| typescript-pitfalls | TypeScript | Full | Vite alias failure, build gaps, `as any` bypasses, etc. |
| docker-pitfalls | Docker/Compose | Full | Containerization traps: fallback bans, layer ordering, production build verification, port parity, healthchecks |
| dependency-drift-pitfalls | All | Full | Manifest-environment parity, version drift, lockfile hygiene (FB23-sourced) |
| graphql-pitfalls | GraphQL | Full | Strawberry schema traps, depth limiting, RBAC parity, orphaned queries, enum type mismatch |
| go-pitfalls | Go | Stub | (Awaiting empirical data) |
| rust-pitfalls | Rust | Stub | (Awaiting empirical data) |
| java-pitfalls | Java | Stub | (Placeholder) |
| csharp-pitfalls | C# | Stub | (Placeholder) |
| ruby-pitfalls | Ruby | Stub | (Placeholder) |
| elixir-pitfalls | Elixir | Stub | (Placeholder) |
| kotlin-pitfalls | Kotlin | Stub | (Placeholder) |
| swift-pitfalls | Swift | Stub | (Placeholder) |
