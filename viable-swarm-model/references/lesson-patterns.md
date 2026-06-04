---

# Lesson Patterns Report -- 2026-06-04 22:21 UTC

## Header

| Metric | Value |
|---|---|
| Date | 2026-06-04 22:21 UTC |
| Builds scanned | 26 |
| Total lessons | 219 |

## Recurring Patterns

| Pattern | Occurrences | Builds Affected | Most Common Fix | Recommended Mutation |
|---|---|---|---|---|
| auth / role / verification | 155 | FB1-20260522, FB10-20260524, FB14-20260524, FB15-20260525, FB16-20260524, FB17-20260526, FB18-20260525, FB19-20260525, FB2-20260522, FB20-20260525, FB21-20260525, FB22-20260525, FB24-20260602, FB25-20260602, FB26-20260603, FB28-20260603, FB29-20260603, FB3-20260522, FB30-20260604, FB32-20260604, FB4-20260522, FB5-20260523, FB6-20260523, FB7-20260523, FB8-20260523, FB9-20260523 | Changed frontend build context to `.` (project root) and updated `frontend/Docke... | Consider consolidating prevention rule for 'auth / role / verification' |
| config / cors_allowed_origins / cors_origins | 3 | FB16-20260524, FB19-20260525, FB21-20260525 | Not fixed. | Consider consolidating prevention rule for 'config / cors_allowed_origins / cors_origins' |
| context_getter / get_context / graphqlrouter | 2 | FB16-20260524, FB24-20260602 | Wired `context_getter=get_context` into GraphQLRouter. | Consider consolidating prevention rule for 'context_getter / get_context / graphqlrouter' |
| dev / docker / dockerfile | 2 | FB25-20260602, FB26-20260603 | Removed invalid COPY instruction; nginx default config is sufficient for this bu... | Consider consolidating prevention rule for 'dev / docker / dockerfile' |

## Lesson Orphans

*Prevention rules mentioned in lessons.md that do NOT appear in skill files.*
*Orphaned rules: 3*

| Build ID | Rule (excerpt) | Source File |
|---|---|---|
| FB26-20260603 | docker-pitfalls COPY syntax purity check. | -- |
| FB30-20260604 | Update graphql-pitfalls to recommend GraphQLRouter for FastAPI apps. | app.mount |
| FB30-20260604 | Frontend test runner should verify jsdom compatibility or use simpler mocking patterns. | -- |

## Agent Risk

*Agents most frequently associated with lessons (indicates where knowledge gaps or process friction concentrate).

| Agent | Lesson Mentions |
|---|---|
| vsm_security | 17 |
| vsm_tester | 7 |
| vsm_frontend_tester | 2 |
| vsm_wiring | 2 |
| vsm_meta | 2 |
| vsm_backend_coder | 2 |
| vsm_auditor | 2 |
| vsm_backend_tester | 2 |
| vsm_product | 1 |
| vsm_devops_coder | 1 |
| vsm_frontend_coder | 1 |

## Score Correlation

*Correlation between lesson count per build and overall build score.*

Weak correlation (r=-0.18): lesson count and score are largely independent

| Build | Lessons | Score |
|---|---|---|
| FB25-20260602 | 6 | 80.0 |
| FB28-20260603 | 8 | 80.0 |
| FB29-20260603 | 7 | 84.0 |
| FB30-20260604 | 6 | 76.0 |
| FB32-20260604 | 10 | 77.0 |

---
---

# Lesson Patterns Report -- 2026-06-04 22:22 UTC

## Header

| Metric | Value |
|---|---|
| Date | 2026-06-04 22:22 UTC |
| Builds scanned | 26 |
| Total lessons | 219 |

## Recurring Patterns

| Pattern | Occurrences | Builds Affected | Most Common Fix | Recommended Mutation |
|---|---|---|---|---|
| auth / role / verification | 155 | FB1-20260522, FB10-20260524, FB14-20260524, FB15-20260525, FB16-20260524, FB17-20260526, FB18-20260525, FB19-20260525, FB2-20260522, FB20-20260525, FB21-20260525, FB22-20260525, FB24-20260602, FB25-20260602, FB26-20260603, FB28-20260603, FB29-20260603, FB3-20260522, FB30-20260604, FB32-20260604, FB4-20260522, FB5-20260523, FB6-20260523, FB7-20260523, FB8-20260523, FB9-20260523 | Changed frontend build context to `.` (project root) and updated `frontend/Docke... | Consider consolidating prevention rule for 'auth / role / verification' |
| config / cors_origins / main | 3 | FB16-20260524, FB19-20260525, FB21-20260525 | Not fixed. | Consider consolidating prevention rule for 'config / cors_origins / main' |
| context_getter / graphqlrouter / get_context | 2 | FB16-20260524, FB24-20260602 | Wired `context_getter=get_context` into GraphQLRouter. | Consider consolidating prevention rule for 'context_getter / graphqlrouter / get_context' |
| null / copy / docker | 2 | FB25-20260602, FB26-20260603 | Removed invalid COPY instruction; nginx default config is sufficient for this bu... | Consider consolidating prevention rule for 'null / copy / docker' |

## Lesson Orphans

*Prevention rules mentioned in lessons.md that do NOT appear in skill files.*
*Orphaned rules: 3*

| Build ID | Rule (excerpt) | Source File |
|---|---|---|
| FB26-20260603 | docker-pitfalls COPY syntax purity check. | -- |
| FB30-20260604 | Update graphql-pitfalls to recommend GraphQLRouter for FastAPI apps. | app.mount |
| FB30-20260604 | Frontend test runner should verify jsdom compatibility or use simpler mocking patterns. | -- |

## Agent Risk

*Agents most frequently associated with lessons (indicates where knowledge gaps or process friction concentrate).

| Agent | Lesson Mentions |
|---|---|
| vsm_security | 17 |
| vsm_tester | 7 |
| vsm_frontend_tester | 2 |
| vsm_wiring | 2 |
| vsm_meta | 2 |
| vsm_backend_coder | 2 |
| vsm_auditor | 2 |
| vsm_backend_tester | 2 |
| vsm_product | 1 |
| vsm_devops_coder | 1 |
| vsm_frontend_coder | 1 |

## Score Correlation

*Correlation between lesson count per build and overall build score.*

Weak correlation (r=-0.18): lesson count and score are largely independent

| Build | Lessons | Score |
|---|---|---|
| FB25-20260602 | 6 | 80.0 |
| FB28-20260603 | 8 | 80.0 |
| FB29-20260603 | 7 | 84.0 |
| FB30-20260604 | 6 | 76.0 |
| FB32-20260604 | 10 | 77.0 |

---
