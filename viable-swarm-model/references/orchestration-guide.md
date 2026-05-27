# Orchestration Guide

Supplementary guidance for S5 (main conversation agent) operating the VSM workflow.
Read on demand — not required for every build phase.

## Comprehension Checkpoint

Before declaring a phase complete, explain what was built:

1. **Comprehension** — Explain without referring to original spec
2. **Connections** — Map to broader context (other files, architecture)
3. **Rationale** — Explain WHY, not just WHAT
4. **Edge cases** — Identify assumptions and limitations
5. **Consequences** — Predict impact on other system parts

If explanation reveals gaps → revisit before proceeding.

## Background Task Management

Use `TaskList` to monitor active tasks. Use `TaskOutput(block=true)` to
synchronize dependent waves. Use `TaskStop` to cancel on algedonic signals.
Use `/tasks` command for interactive browser.

Max concurrent background tasks defaults to 4, configurable via `background.max_running_tasks`
in `~/.kimi-code/config.toml` (e.g., `max_running_tasks = 8`).

## Session Resumption for Learning

When `--continue` resumes a session:
1. Read `.kimi/lessons.md` at session start
2. Read `${KIMI_SKILL_DIR}/references/acquired-wisdom.md`
3. Read `${KIMI_SKILL_DIR}/references/hypotheses.md`
4. Apply relevant lessons to planning
5. After delivery, append new lessons to both project-local and skill-global memory
6. Over time, this creates both a project-specific and a cross-project knowledge base

**Epistemic rule**: If `.kimi/lessons.md` contradicts this SKILL.md,
the lessons file wins. It contains empirical data; this file contains
general guidance.

## Quick Decision Tree

```
User asks for software engineering work?
├── Trivial (< 50 lines, one file)?
│   └── Respond directly, no VSM workflow
└── Non-trivial?
    ├── Read .kimi/lessons.md if exists (apply learnings)
    ├── Read references/acquired-wisdom.md if exists (apply cross-project learnings)
    ├── Read references/hypotheses.md if exists (test relevant hypotheses)
    └── Execute VSM workflow via /flow:viable-swarm-model
```
