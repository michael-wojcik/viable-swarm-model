---

# Lesson Patterns Report -- 2026-06-07 10:46 UTC

## Header

| Metric | Value |
|---|---|
| Date | 2026-06-07 10:46 UTC |
| Builds scanned | 28 |
| Total lessons | 235 |

## Recurring Patterns

| Pattern | Occurrences | Builds Affected | Most Common Fix | Recommended Mutation |
|---|---|---|---|---|
| auth / role / verification | 171 | FB1-20260522, FB10-20260524, FB14-20260524, FB15-20260525, FB16-20260524, FB17-20260526, FB18-20260525, FB19-20260525, FB2-20260522, FB20-20260525, FB21-20260525, FB22-20260525, FB24-20260602, FB25-20260602, FB26-20260603, FB28-20260603, FB29-20260603, FB3-20260522, FB30-20260604, FB32-20260604, FB33-20260604, FB34-20260606, FB4-20260522, FB5-20260523, FB6-20260523, FB7-20260523, FB8-20260523, FB9-20260523 | Changed frontend build context to `.` (project root) and updated `frontend/Docke... | Consider consolidating prevention rule for 'auth / role / verification' |
| config / main / cors_allowed_origins | 3 | FB16-20260524, FB19-20260525, FB21-20260525 | Not fixed. | Consider consolidating prevention rule for 'config / main / cors_allowed_origins' |
| context_getter / get_context / graphqlrouter | 2 | FB16-20260524, FB24-20260602 | Wired `context_getter=get_context` into GraphQLRouter. | Consider consolidating prevention rule for 'context_getter / get_context / graphqlrouter' |
| shell / dockerfile / copy | 2 | FB25-20260602, FB26-20260603 | Removed invalid COPY instruction; nginx default config is sufficient for this bu... | Consider consolidating prevention rule for 'shell / dockerfile / copy' |

## Lesson Orphans

*Prevention rules mentioned in lessons.md that do NOT appear in skill files.*
*Orphaned rules: 0*

*All prevention rules are reflected in skill files.*

## Agent Risk

*Agents most frequently associated with lessons (indicates where knowledge gaps or process friction concentrate).

| Agent | Lesson Mentions |
|---|---|
| vsm_security | 17 |
| vsm_tester | 7 |
| vsm_backend_tester | 3 |
| vsm_frontend_tester | 2 |
| vsm_wiring | 2 |
| vsm_meta | 2 |
| vsm_backend_coder | 2 |
| vsm_auditor | 2 |
| vsm_product | 1 |
| vsm_devops_coder | 1 |
| vsm_frontend_coder | 1 |
| vsm_backend_fix_agent | 1 |

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
