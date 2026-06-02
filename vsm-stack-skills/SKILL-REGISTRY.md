# Stack Skills Registry

## Pattern Skills
| Skill | Description | Relevant Agents | Depends On |
|---|---|---|---|
| architecture-patterns | System design, data modeling, API contracts | architect, product | — |
| backend-patterns | Server architecture, API design, middleware | backend_coder, backend_fix, backend_tester, coordinator | `[language]-pitfalls` |
| frontend-patterns | Component architecture, state, routing | frontend_coder, frontend_fix, frontend_tester, coordinator | `[language]-pitfalls` |
| database-patterns | Schema design, migrations, query optimization | backend_coder, backend_tester, coordinator | `[language]-pitfalls` |
| testing-patterns | Test strategy, fixtures, mocking, coverage | backend_tester, frontend_tester, coordinator | `[language]-pitfalls` |
| security-patterns | Auth, input validation, secrets, rate limiting, data exposure | security, auditor, coordinator, all coders | — |
| devops-patterns | Containers, compose, healthchecks, CI/CD | devops_coder, coordinator | — |
| research-patterns | Investigating unfamiliar technologies | architect, explore, meta | — |

## Pitfall Skills
| Skill | Language | Status | Description |
|---|---|---|---|
| python-pitfalls | Python | Full | Module-level instantiation, Pydantic ConfigDict, SQLAlchemy shadowing, etc. |
| typescript-pitfalls | TypeScript | Full | Vite alias failure, build gaps, `as any` bypasses, etc. |
| docker-pitfalls | Docker/Compose | Full | Containerization traps: fallback bans, layer ordering, production build verification, port parity, healthchecks |
| dependency-drift-pitfalls | All | Stub | (Awaiting empirical data) |
| go-pitfalls | Go | Stub | (Awaiting empirical data) |
| rust-pitfalls | Rust | Stub | (Awaiting empirical data) |
| java-pitfalls | Java | Stub | (Placeholder) |
| csharp-pitfalls | C# | Stub | (Placeholder) |
| ruby-pitfalls | Ruby | Stub | (Placeholder) |
| elixir-pitfalls | Elixir | Stub | (Placeholder) |
| kotlin-pitfalls | Kotlin | Stub | (Placeholder) |
| swift-pitfalls | Swift | Stub | (Placeholder) |
