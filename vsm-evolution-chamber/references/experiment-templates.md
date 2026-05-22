# Experiment Templates

> **Mutation rules**: Append new templates as experiment types are discovered.
> Mark obsolete templates with notes. Never delete.

---

## Template: Security Vulnerability Test

**Purpose**: Test whether vsm_security catches a specific vulnerability class.

**Structure**:
```
/tmp/vsm-exp-{hypothesis-id}/
├── main.py          # Minimal FastAPI/Flask app with ONE intentional vulnerability
├── .env.example     # (optional) If testing env var patterns
└── requirements.txt # Minimal dependencies
```

**Design rules**:
- Only ONE vulnerability per experiment
- No auth scaffolding beyond what's needed to trigger the vulnerability
- Include a "safe" version commented out for comparison
- The vulnerability should be realistic (not contrived)

**Evaluation**:
- Run vsm_security against main.py
- If it flags CRITICAL/HIGH → skill already knows (reject hypothesis)
- If it passes or flags only LOW → skill has a gap (confirm hypothesis)

---

## Template: Integration Mismatch Test

**Purpose**: Test whether vsm_coordinator detects cross-file contract mismatches.

**Structure**:
```
/tmp/vsm-exp-{hypothesis-id}/
├── backend/
│   ├── tasks.py     # Defines Celery tasks or event names
│   └── models.py    # Database models
└── frontend/
    ├── api.ts       # API client that imports from backend contracts
    └── types.ts     # TypeScript types (potentially mismatched)
```

**Design rules**:
- Introduce ONE mismatch (task name, type shape, env var name)
- Keep other contracts correct to avoid confusion
- The mismatch should be subtle (not obvious on visual inspection)

**Evaluation**:
- Run vsm_coordinator across both directories
- If it detects the mismatch → skill already knows (reject hypothesis)
- If it passes → skill has a gap (confirm hypothesis)

---

## Template: Performance / Pattern Test

**Purpose**: Test whether vsm_auditor flags a specific anti-pattern.

**Structure**:
```
/tmp/vsm-exp-{hypothesis-id}/
├── app.py           # One endpoint with the anti-pattern
└── test_app.py      # (optional) Test that demonstrates the issue
```

**Design rules**:
- The anti-pattern should cause measurable harm (N+1 queries, memory leaks)
- Include a "correct" implementation in comments for comparison
- Keep the endpoint functional so tests can run

**Evaluation**:
- Run vsm_auditor against app.py
- If it flags ISSUES/BLOCKER for the specific pattern → skill knows (reject)
- If it passes → skill has a gap (confirm)

---

## Template: Prompt Efficacy Test

**Purpose**: Test whether a custom agent prompt produces the expected behavior.

**Structure**:
```
/tmp/vsm-exp-{hypothesis-id}/
├── input/           # Code or spec sent to the agent
└── expected/        # What the agent SHOULD produce
```

**Design rules**:
- The input should be ambiguous enough to test the prompt's guidance
- The expected output should be specific and verifiable
- Test ONE prompt characteristic at a time

**Evaluation**:
- Spawn the relevant custom agent type with the current prompt
- Compare output to expected/
- If output matches → prompt works (reject hypothesis about prompt gap)
- If output deviates → prompt needs refinement (confirm hypothesis)
