# Experiment Templates

> **Mutation rules**: Append new templates as experiment types are discovered.
> Mark obsolete templates with notes. Never delete.

---

## Template: Security Vulnerability Test

**Purpose**: Test whether vsm_security catches a specific vulnerability class.

**Structure**:
```
~/vsm-fitness-builds/gym/{hypothesis-id}/
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
~/vsm-fitness-builds/gym/{hypothesis-id}/
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
~/vsm-fitness-builds/gym/{hypothesis-id}/
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
~/vsm-fitness-builds/gym/{hypothesis-id}/
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

---

## Template: Process Audit + Meta-Evaluation Test

**Purpose**: Test whether `vsm_meta` catches process violations, or whether a
hypothesis about process behavior (e.g., "skipping Phase X correlates with Y")
holds up when evaluated against documented build artifacts.

**Structure**:
```
~/vsm-fitness-builds/gym/{hypothesis-id}/
├── plan.md                    # Build plan and tier classification
├── .kimi/lessons.md           # Project-specific lessons (optional)
├── audits/
│   ├── auditor-report.md      # Phase 3b audit findings
│   ├── coordinator-report.md  # Phase 6 integration report
│   ├── security-report.md     # Phase 5 security gate findings
│   └── test-results.md        # Phase 4 test outcomes
├── inline-fix-evidence.md     # Documented process violations (optional)
└── [any other build artifacts]
```

**Design rules**:
- Create fictional but realistic build artifacts that simulate a real build
- Include explicit evidence of the process violation being tested
- Do NOT run actual code — this is a document-reading experiment
- The experiment tests the META agent's ability to read artifacts and detect gaps

**Evaluation**:
- Spawn `vsm_meta` with the build directory and skill references
- Compare its output against the known process violations
- If vsm_meta catches all violations → mechanism validated (hypothesis supported)
- If vsm_meta misses violations → prompt needs refinement (hypothesis gap confirmed)

**Source**: Gym E16 (H106) — fictional FB20-Test artifacts with documented inline fixes, missing re-audit reports, and skipped Phase 8b.


---

## Template: Behavioral / Agent Hang Test

**Purpose**: Test whether a specific agent behavior (e.g., hanging, looping,
perfectionism) occurs under controlled conditions. Used for hypotheses about
agent runtime reliability.

**Structure**:
```
~/vsm-fitness-builds/gym/{hypothesis-id}/
├── task.md            # Exact task prompt given to the agent
├── task_variant.md    # (optional) Alternative prompt for A/B testing
├── project/           # Codebase the agent must read/modify
│   ├── module_a.py
│   └── ...
└── test_*.py          # Tests that verify agent output correctness
```

**Design rules**:
- Keep the writing task simple enough to pass tests on first correct attempt
- The independent variable should be manipulable at the TASK prompt level
- Account for agent prompt contamination (see WARNING below)
- Record: duration, tool call count, test runs, post-pass modifications

**WARNING — Agent Prompt Contamination (E26 finding)**:
When a mutation is embedded in the agent's YAML prompt template
(e.g., FB35-2 in `vsm_backend_coder.md`) AND the agent reads
`mutation-state.md` at startup, the mutation rules are applied
**regardless of task-level instructions**. This makes A/B testing of
prompt variants impossible unless the mutation is temporarily removed
from the base prompt template (structural mutation, requires approval).

**Mitigations**:
1. Check `agents/vsm_{type}.md` for the mutation being tested before designing
2. If the mutation IS in the base prompt, test via structural mutation
   approval (remove → test → restore) rather than task-level manipulation
3. Document contamination in the experiment report as a confound

**Evaluation**:
- Spawn the agent with the task prompt
- Observe whether it terminates cleanly or enters extended loops
- Compare metrics across conditions
- If agent hangs under test condition → hypothesis confirmed
- If agent terminates cleanly in all conditions → hypothesis not confirmed
  (but may need stronger stimulus — see H503 threshold discussion)

**Source**: Gym E25 (H503) + E26 (H504) — testing context pressure and
post-write perfectionism in background agent behavior.
