---

# Lesson Patterns Report -- 2026-06-04 22:06 UTC

## Header

| Metric | Value |
|---|---|
| Date | 2026-06-04 22:06 UTC |
| Builds scanned | 22 |
| Total lessons | 138 |

## Recurring Patterns

| Pattern | Occurrences | Builds Affected | Most Common Fix | Recommended Mutation |
|---|---|---|---|---|
| auth / import / role | 95 | FB1-20260522, FB10-20260524, FB14-20260524, FB15-20260525, FB16-20260524, FB17-20260526, FB18-20260525, FB2-20260522, FB20-20260525, FB21-20260525, FB22-20260525, FB24-20260602, FB25-20260602, FB26-20260603, FB28-20260603, FB29-20260603, FB3-20260522, FB30-20260604, FB6-20260523, FB7-20260523, FB8-20260523, FB9-20260523 | Fix wave restored both sets of changes. Future builds should either serialize en... | Consider consolidating prevention rule for 'auth / import / role' |
| redis / celery / instead | 3 | FB17-20260526, FB20-20260525, FB3-20260522 | Wrapped Celery app creation in `_get_celery_app()` function that reads `get_sett... | Consider consolidating prevention rule for 'redis / celery / instead' |
| expected / lowercase / uppercase | 2 | FB10-20260524, FB21-20260525 | Define explicit Strawberry enums with lowercase member names matching the runtim... | Consider consolidating prevention rule for 'expected / lowercase / uppercase' |
| docker / dev / contained | 2 | FB25-20260602, FB26-20260603 | Removed invalid COPY instruction; nginx default config is sufficient for this bu... | Consider consolidating prevention rule for 'docker / dev / contained' |

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
| vsm_security | 9 |
| vsm_tester | 7 |
| vsm_frontend_tester | 2 |
| vsm_wiring | 2 |
| vsm_backend_coder | 2 |
| vsm_backend_tester | 2 |
| vsm_meta | 1 |
| vsm_product | 1 |
| vsm_devops_coder | 1 |
| vsm_frontend_coder | 1 |
| vsm_auditor | 1 |

## Score Correlation

*Correlation between lesson count per build and overall build score.*

No clear correlation

| Build | Lessons | Score |
|---|---|---|
| FB25-20260602 | 6 | 80.0 |
| FB28-20260603 | 8 | 80.0 |
| FB29-20260603 | 7 | 80.0 |

---
---

# Lesson Patterns Report -- 2026-06-04 22:06 UTC

## Header

| Metric | Value |
|---|---|
| Date | 2026-06-04 22:06 UTC |
| Builds scanned | 22 |
| Total lessons | 138 |

## Recurring Patterns

| Pattern | Occurrences | Builds Affected | Most Common Fix | Recommended Mutation |
|---|---|---|---|---|
| auth / import / role | 95 | FB1-20260522, FB10-20260524, FB14-20260524, FB15-20260525, FB16-20260524, FB17-20260526, FB18-20260525, FB2-20260522, FB20-20260525, FB21-20260525, FB22-20260525, FB24-20260602, FB25-20260602, FB26-20260603, FB28-20260603, FB29-20260603, FB3-20260522, FB30-20260604, FB6-20260523, FB7-20260523, FB8-20260523, FB9-20260523 | Fix wave restored both sets of changes. Future builds should either serialize en... | Consider consolidating prevention rule for 'auth / import / role' |
| redis / localhost / celery | 3 | FB17-20260526, FB20-20260525, FB3-20260522 | Wrapped Celery app creation in `_get_celery_app()` function that reads `get_sett... | Consider consolidating prevention rule for 'redis / localhost / celery' |
| expected / uppercase / lowercase | 2 | FB10-20260524, FB21-20260525 | Define explicit Strawberry enums with lowercase member names matching the runtim... | Consider consolidating prevention rule for 'expected / uppercase / lowercase' |
| dev / contained / null | 2 | FB25-20260602, FB26-20260603 | Removed invalid COPY instruction; nginx default config is sufficient for this bu... | Consider consolidating prevention rule for 'dev / contained / null' |

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
| vsm_security | 9 |
| vsm_tester | 7 |
| vsm_frontend_tester | 2 |
| vsm_wiring | 2 |
| vsm_backend_coder | 2 |
| vsm_backend_tester | 2 |
| vsm_meta | 1 |
| vsm_product | 1 |
| vsm_devops_coder | 1 |
| vsm_frontend_coder | 1 |
| vsm_auditor | 1 |

## Score Correlation

*Correlation between lesson count per build and overall build score.*

No clear correlation

| Build | Lessons | Score |
|---|---|---|
| FB25-20260602 | 6 | 80.0 |
| FB28-20260603 | 8 | 80.0 |
| FB29-20260603 | 7 | 80.0 |

---
---

# Lesson Patterns Report -- 2026-06-04 22:06 UTC

## Header

| Metric | Value |
|---|---|
| Date | 2026-06-04 22:06 UTC |
| Builds scanned | 22 |
| Total lessons | 138 |

## Recurring Patterns

| Pattern | Occurrences | Builds Affected | Most Common Fix | Recommended Mutation |
|---|---|---|---|---|
| auth / import / role | 95 | FB1-20260522, FB10-20260524, FB14-20260524, FB15-20260525, FB16-20260524, FB17-20260526, FB18-20260525, FB2-20260522, FB20-20260525, FB21-20260525, FB22-20260525, FB24-20260602, FB25-20260602, FB26-20260603, FB28-20260603, FB29-20260603, FB3-20260522, FB30-20260604, FB6-20260523, FB7-20260523, FB8-20260523, FB9-20260523 | Fix wave restored both sets of changes. Future builds should either serialize en... | Consider consolidating prevention rule for 'auth / import / role' |
| redis / broker / instead | 3 | FB17-20260526, FB20-20260525, FB3-20260522 | Wrapped Celery app creation in `_get_celery_app()` function that reads `get_sett... | Consider consolidating prevention rule for 'redis / broker / instead' |
| expected / uppercase / lowercase | 2 | FB10-20260524, FB21-20260525 | Define explicit Strawberry enums with lowercase member names matching the runtim... | Consider consolidating prevention rule for 'expected / uppercase / lowercase' |
| contained / copy / dockerfile | 2 | FB25-20260602, FB26-20260603 | Removed invalid COPY instruction; nginx default config is sufficient for this bu... | Consider consolidating prevention rule for 'contained / copy / dockerfile' |

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
| vsm_security | 9 |
| vsm_tester | 7 |
| vsm_frontend_tester | 2 |
| vsm_wiring | 2 |
| vsm_backend_coder | 2 |
| vsm_backend_tester | 2 |
| vsm_meta | 1 |
| vsm_product | 1 |
| vsm_devops_coder | 1 |
| vsm_frontend_coder | 1 |
| vsm_auditor | 1 |

## Score Correlation

*Correlation between lesson count per build and overall build score.*

No clear correlation

| Build | Lessons | Score |
|---|---|---|
| FB25-20260602 | 6 | 80.0 |
| FB28-20260603 | 8 | 80.0 |
| FB29-20260603 | 7 | 80.0 |

---
