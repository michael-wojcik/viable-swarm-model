# Fitness Report: [Project Name]

**Fitness Build ID**: [FB1 / FB2 / FB3 / etc.]  
**Date**: [YYYY-MM-DD]  
**Duration**: [hours]  
**Total agents spawned**: [count]  
**Total lines produced**: [approximate]  
**BLOCKERs found**: [count]  
**Fix iterations**: [count]

---

## Executive Summary

[One-paragraph overview: Did the skill perform well? Any structural concerns?
Is the skill improving, stagnating, or regressing?]

---

## Phase Scores

| Phase | Score (1-5) | Evidence | Notes |
|-------|-------------|----------|-------|
| 0. Viability Check | | | |
| 1. Intelligence | | | |
| 2. Foundation Wave | | | |
| 3. Implementation Wave | | | |
| 4. Testing + Infra | | | |
| 5. Integration Verification | | | |
| 6. Security Gate | | | |
| 7. Fix Wave | | | |
| 8. Reflection | | | |
| 8b. Meta-Reflection | | | |

**Overall Score**: [average] / 5.0

---

## Gaps Identified

### Critical Gaps (Score 1-2)

1. **[Gap title]**
   - **Phase**: [which phase failed]
   - **What happened**: [specific observation]
   - **What should have happened**: [expected behavior]
   - **Root cause**: [hypothesis about why]
   - **Hypothesis**: H[N] — [link to hypothesis in main skill]

### Moderate Gaps (Score 3)

1. **[Gap title]**
   - **Phase**: [which phase underperformed]
   - **What happened**: [specific observation]
   - **Hypothesis**: H[N]

---

## Surprises

[What went BETTER than expected? Any unexpected successes?]

1. [Surprise description]
2. [Surprise description]

---

## False Positives

[Did any agent flag something as an issue when it was actually correct?]

1. [False positive description]
   - **Agent**: [which agent type]
   - **What was flagged**: [description]
   - **Why it was actually correct**: [explanation]

---

## Hypotheses Generated

| ID | Hypothesis | Status | Source Phase |
|----|-----------|--------|--------------|
| H[N] | [short claim] | untested | [phase] |

---

## Mutations Applied

| # | File | Change | Rationale | Commit |
|---|------|--------|-----------|--------|
| 1 | [path] | [summary] | [why] | [hash] |

---

## Mutation Effectiveness Audit

> For each mutation applied since the previous build, did it prevent its target
> failure mode? If a mutation was added to catch X but X recurred, the mutation
> is **ineffective** and should be flagged for removal or redesign.

| Mutation ID | Target Failure Mode | Applied In | Recurred This Build? | Effective? | Proposed Action |
|-------------|---------------------|------------|----------------------|------------|-----------------|
| [M# / H#] | [what it was supposed to prevent] | [FB#] | Yes / No | Yes / No | Keep / Remove / Redesign |

**Ineffective mutations flagged**: [count]

---

## Comparison to Previous Fitness Builds

[If this is not the first fitness build, compare scores to previous runs.
Is the skill improving? Which phases are getting better? Which are getting worse?]

| Phase | Previous Score | Current Score | Trend |
|-------|---------------|---------------|-------|
| [Phase] | [score] | [score] | ↑ / ↓ / → |

### Regression Build Comparison (if applicable)

[Only for regression builds (every 5th build). Compare to the gold standard build.]

| Metric | Gold Standard ([FB#]) | This Build | Delta |
|--------|----------------------|------------|-------|
| Overall Score | [X]/5.0 | [Y]/5.0 | [+/- Z] |
| Lowest Phase | [phase] | [phase] | — |
| BLOCKERs Found | [N] | [M] | [+/-] |

**Regression Verdict**: [Improved / Stable / Regressed]

If **Regressed**: List mutations applied since the gold standard build that may
have caused the regression. Flag for mutation review.

| Mutation | Applied Since | Suspicious? | Action |
|----------|--------------|-------------|--------|
| [M#] | [FB#] | Yes / No | Review / Clear |

---

## Recommendations

1. [High-priority recommendation]
2. [Medium-priority recommendation]
3. [Low-priority recommendation]

---

## Raw Artifacts

- plan.md: [summary or link]
- Auditor report: [summary]
- Security report: [summary]
- Integration report: [summary]
- Test results: [summary]
- Project lessons: `.kimi/lessons.md`
