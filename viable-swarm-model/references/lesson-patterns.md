---

# Lesson Patterns Report -- 2026-06-04 21:56 UTC

## Header

| Metric | Value |
|---|---|
| Date | 2026-06-04 21:56 UTC |
| Builds scanned | 22 |
| Total lessons | 138 |

## Recurring Patterns

| Pattern | Occurrences | Builds Affected | Most Common Fix | Recommended Mutation |
|---|---|---|---|---|
| graphql / auth / role | 131 | FB1-20260522, FB10-20260524, FB14-20260524, FB15-20260525, FB16-20260524, FB17-20260526, FB18-20260525, FB2-20260522, FB20-20260525, FB21-20260525, FB22-20260525, FB24-20260602, FB25-20260602, FB26-20260603, FB28-20260603, FB29-20260603, FB3-20260522, FB30-20260604, FB6-20260523, FB7-20260523, FB8-20260523, FB9-20260523 | Changed Yjs WebSocket route to `/ws/yjs/{doc_id}/{token}` and validated JWT from... | Consider consolidating prevention rule for 'graphql / auth / role' |

## Lesson Orphans

*Prevention rules mentioned in lessons.md that do NOT appear in skill files.*
*Orphaned rules: 28*

| Build ID | Rule (excerpt) | Source File |
|---|---|---|
| FB18-20260525 | Foundation auditor must verify `types.ts` against `data-model.md` before implementation wave. | App.tsx |
| FB18-20260525 | Audit agent must verify that mutation endpoints use stricter role checks than read endpoints. | -- |
| FB20-20260525 | Phase 8b MUST spawn `vsm_meta`. S5 must NOT write meta-reflection content directly. The `vsm_meta` a... | meta-reflection.md |
| FB21-20260525 | All enum definitions for the same domain concept must live in a single canonical module (e.g., `app.... | test_auth.py |
| FB21-20260525 | Any WebSocket transport that supports `connectionParams` MUST include auth tokens when the backend r... | frontend/src/graphql/client.ts |
| FB21-20260525 | After frontend page components are scaffolded, `App.tsx` must be updated in the SAME wave to wire re... | frontend/src/App.tsx |
| FB21-20260525 | Always serialize enums to their `.value` (or a canonical string) before placing them in JSON-seriali... | backend/app/auth.py |
| FB22-20260525 | Always spawn vsm_product before vsm_architect for problem-oriented prompts. | -- |
| FB22-20260525 | Keep vsm_wiring as the sole owner of entry-point files. | -- |
| FB22-20260525 | Add "Do NOT use strawberry_sqlalchemy_mapper" to vsm_backend_coder gotchas. Require agents to check ... | graphql.py |
| FB22-20260525 | Auditor env-var parity check (H109) continues to be effective. | docker-compose.yml |
| FB22-20260525 | Pin compatible versions in requirements.txt. Test environment before starting builds. | 0.256 |
| FB24-20260602 | Never type-hint `starlette.requests.Request` on `context_getter` callables passed to Strawberry's `G... | app/graphql.py |
| FB24-20260602 | Role guards must treat `null` / `undefined` role as a mismatch, not a pass. Never use `role &&` as a... | src/components/ProtectedRoute.tsx |
| FB25-20260602 | Dockerfile instructions must use pure Dockerfile syntax only. Never embed shell syntax (`||`, `&&`, ... | nginx.conf |
| FB25-20260602 | SQLAlchemy async engines are expensive to create. Cache them by connection string. Session factories... | -- |
| FB25-20260602 | Async workers must not trust enqueue-time validation alone. Re-verify authorization boundaries insid... | -- |
| FB26-20260603 | docker-pitfalls COPY syntax purity check. | -- |
| FB26-20260603 | security-patterns upload validation + python-pitfalls API verification. | documents.py |
| FB26-20260603 | H152 — pre-build environment smoke test would catch this. | 0.316 |
| FB28-20260603 | Every security dependency added to pyproject.toml must have corresponding middleware or decorator wi... | pyproject.toml |
| FB29-20260603 | | `orchestration`: "Split agent tasks to <500 lines of output scope. Prefer multiple focused paralle... | 2.5h |
| FB29-20260603 | | `graphql-pitfalls`: "When passing a session to GraphQL context, ensure it's an actual `AsyncSessio... | graphql.py |
| FB30-20260604 | H217 (task sizing ≤500 lines) is confirmed effective for code-writing agents but architect/design ag... | -- |
| FB30-20260604 | Add "Test database compatibility" checklist item to vsm_backend_tester prompt. | -- |
| FB30-20260604 | Add "Settings attribute names are UPPERCASE" to python-pitfalls. | settings.access_token_expire_minutes |
| FB30-20260604 | Update graphql-pitfalls to recommend GraphQLRouter for FastAPI apps. | app.mount |
| FB30-20260604 | Frontend test runner should verify jsdom compatibility or use simpler mocking patterns. | -- |

## Agent Risk

*Agents most frequently associated with lessons (indicates where knowledge gaps or process friction concentrate).

| Agent | Lesson Mentions |
|---|---|
| frontend tester | 2 |
| backend tester | 2 |
| vsm_meta | 1 |
| vsm_product | 1 |
| vsm_wiring | 1 |
| vsm_devops_coder | 1 |
| vsm_backend_coder | 1 |
| backend coder | 1 |
| frontend coder | 1 |
| foundation auditor | 1 |
| vsm_tester | 1 |

## Score Correlation

*Correlation between lesson count per build and overall build score.*

Negative correlation (r=-0.47): more lessons tend to associate with lower scores

| Build | Lessons | Score |
|---|---|---|
| FB20-20260525 | 6 | 98.0 |
| FB22-20260525 | 8 | 75.6 |
| FB25-20260602 | 6 | 80.0 |
| FB26-20260603 | 7 | 80.0 |
| FB28-20260603 | 8 | 80.0 |
| FB29-20260603 | 7 | 88.0 |
| FB30-20260604 | 6 | 80.0 |

---
