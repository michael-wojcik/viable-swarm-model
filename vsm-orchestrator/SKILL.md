---
name: vsm-orchestrator
description: Lightweight trigger that recommends invoking the viable-swarm-model flow skill when the user request involves multi-file changes, new features, or system design.
type: inline
whenToUse: When the user asks for multi-file implementation, a new feature, refactoring across modules, system design, or any task that would benefit from structured parallel agent execution.
disableModelInvocation: false
---

This request involves work that spans multiple files or requires structured design, implementation, testing, and integration. The **viable-swarm-model** flow skill is designed for exactly this kind of work.

**Recommended next step**: Ask the user to run the full VSM workflow:

```
Let's build this properly. /flow:viable-swarm-model $ARGUMENTS
```

**Why VSM is appropriate here**:
- The task requires coordination across backend, frontend, or infrastructure
- Quality gates (audit, security, integration) will prevent common failure modes
- The skill's learning system means past project lessons are applied automatically

**If the user declines the full workflow**, proceed with standard inline assistance but apply these VSM principles:
1. Read `.kimi/lessons.md` if it exists (project memory)
2. Use `explore` subagent for codebase mapping before making changes
3. Run tests after every significant change
4. Verify imports and types before declaring completion
