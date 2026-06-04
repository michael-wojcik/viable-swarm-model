# Audit Lessons — 2026-06-04 Comprehensive Ecosystem Audit

> **Audit type**: Self-directed forensic audit of the viable-swarm-model ecosystem
> **Auditors**: S5 orchestrator + 5 parallel VSM subagents (vsm_auditor, vsm_meta, vsm_coordinator, vsm_security, vsm_explore)
> **Scope**: Main skill + fitness-coach + fitness-gym + stack-skills
> **Duration**: ~30 minutes (parallel agent execution)

---

## What the Audit Revealed That Pre-Read Didn't Catch

1. **Format mismatch in auto-update script**: Pre-read showed the script existed. The audit revealed it searches `[PENDING]` while the log uses `**PENDING**` — a silent failure that broke 95% of mutation measurement for months.

2. **Duplicate rows in mutation-state.md**: Pre-read showed 404 lines. The audit revealed 20+ duplicate mutation IDs caused by append-only updates without deduplication — a "temporal paradox" structure.

3. **Ghost mutations R19/R20**: Pre-read showed them in the active portfolio. The audit revealed they have no `## Mutation` headers in mutation-log.md — they exist only in mutation-state.md.

4. **FB25-S1 falsely linked to E17**: Pre-read accepted mutation-state.md at face value. The audit traced the link and found E17 tests H107 (domain fix agents), not H300 (hook claims).

5. **Zero `{% raw %}` tags in ANY agent .md file**: Pre-read didn't check Jinja2 escaping. The audit found ALL agent files violate SKILL.md's explicit `{% raw %}` mandate.

## Which Audit Agents Were Most/Least Effective

| Agent | Effectiveness | Why |
|-------|--------------|-----|
| **vsm_security** (gate enforcement) | ⭐⭐⭐⭐⭐ | Read full 1701-line SKILL.md, all 11 hook scripts, and produced quantitative score (23/100) with tier breakdown |
| **vsm_meta** (mutation lifecycle) | ⭐⭐⭐⭐⭐ | Used targeted shell extraction on 2249-line log, found the `[PENDING]` vs `**PENDING**` format bug |
| **vsm_coordinator** (cross-skill) | ⭐⭐⭐⭐☆ | Excellent traceability testing, caught false E17 linkage, but missed some FB27 data gaps |
| **vsm_explore** (stack skills) | ⭐⭐⭐⭐☆ | Read all 23 skills, but had some shell command failures (exit code 1 on missing files) |
| **vsm_auditor** (agent prompts) | ⭐⭐⭐☆☆ | Thorough file reading but used SearchWeb unnecessarily (3 times). Took longest to complete. Found only minor issues (escaping, numbering) because the agent architecture is actually sound |

**Key insight**: The read-only agents (vsm_security, vsm_meta) outperformed the file-reading agent (vsm_auditor) because they used targeted shell extraction instead of bulk ReadFile. This validates the Context Budget Rule.

## What the Audit Process Says About VSM Self-Awareness

The audit revealed a **meta-pattern**: The VSM ecosystem is excellent at **creating** organizational infrastructure (files, tables, scripts, checklists) but poor at **verifying** that infrastructure works. Examples:

- `validate-agent-files.py` exists and passes → but doesn't check skill-reference validity
- `update-mutation-state.sh` exists → but has a format mismatch that prevents it from working
- `knowledge-broker.sh` exists → but had a regex bug that left the broker empty for 25 builds
- 43 "MANDATORY" phrases exist → but only 3 have tool enforcement

**Diagnosis**: The organism has **proprioception** (it senses its own state via skill-state.md, meta-reflection.md) but lacks **nociception with effector response** (it feels pain but cannot reliably act on it). The audit itself is an example of effector response — but it required external S5 orchestration, not autonomous triggering.

## Proposed Mutations to the Audit Process for Next Time

1. **Autonomous audit trigger**: After every 5th fitness build, the coach SHOULD spawn a lightweight `vsm_auditor` to run `validate-agent-files.py` and check for format mismatches in hooks.

2. **Script validation gate**: Before declaring any hook/script "active," S5 MUST run it manually once and verify output. The `update-mutation-state.sh` would have been caught immediately with a single manual test.

3. **Duplicate detection in append-only files**: Add a `validate-no-duplicates.py` script that checks mutation-state.md, hypotheses.md, and experiment logs for duplicate IDs.

4. **Cross-reference validator**: Add a script that verifies every mutation ID in mutation-state.md exists in mutation-log.md (prevents ghost mutations).

5. **Agent audit efficiency**: Future agent prompt audits should use `vsm_explore` (targeted shell extraction) instead of `vsm_auditor` (bulk ReadFile). The auditor spent most of its time reading files that the explore agent could have grep'd.

---

*This audit was the first time the VSM ecosystem conducted a comprehensive self-examination using its own agents to audit itself. The fact that it worked — that 5 parallel agents produced structured findings without human micro-management — is evidence that the cybernetic architecture is viable. The fact that the findings were so damning is evidence that viability does not equal health.*
