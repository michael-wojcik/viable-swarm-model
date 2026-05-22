# viable-swarm-model

A self-modifying cybernetic development swarm for [Kimi Code CLI](https://github.com/MoonshotAI/Kimi-Chat), based on Stafford Beer's Viable System Model (VSM) and Gordon Pask's Conversation Theory.

This is not a static prompt. It is a **learning organism** that evolves its own files between sessions.

---

## What this is

Most AI coding assistants work like a single engineer with a checklist. This skill works like an entire development team that learns from every project:

- **S5 (Policy)** — You. You set the vision. The skill holds it.
- **S4 (Intelligence)** — An architect agent researches, designs, and proposes approaches.
- **S3 (Control)** — The orchestrator tracks progress, manages waves, and decides when to escalate.
- **S3* (Audit)** — An auditor agent reads every line of code and flags BLOCKERs.
- **S2 (Coordination)** — A coordinator agent validates cross-file contracts, imports, and type alignment.
- **S1 (Operations)** — Coder, tester, security, and DevOps agents execute in parallel waves.

The result is a structured, multi-agent workflow that produces higher-quality code than a single agent working alone.

## Why this is different

| Traditional skill | viable-swarm-model |
|---|---|
| Static rules | **Self-modifying rules** that update after every build |
| Single agent | **Parallel specialist swarm** (architect, coder, tester, auditor, security) |
| Project memory only | **Dual memory**: project-local `.kimi/lessons.md` + skill-global `acquired-wisdom.md` |
| Same skill every time | **Different skill every time** — it learns and mutates |

## Installation

```bash
# Clone into your Kimi CLI skills directory
git clone https://github.com/michael-wojcik/viable-swarm-model.git \
  ~/.kimi/skills/viable-swarm-model
```

That's it. The skill is now available via Kimi CLI.

## Usage

### Run the full workflow

```
/flow:viable-swarm-model
```

This executes the complete VSM phase workflow:
1. **Phase 0**: Viability check + self-test
2. **Phase 1**: Intelligence (architect designs the system)
3. **Phase 2**: Foundation wave (types, config, scaffolding)
4. **Phase 3**: Implementation wave (features, wiring)
5. **Phase 4**: Testing + infrastructure wave
6. **Phase 5**: Integration verification
7. **Phase 6**: Security gate
8. **Phase 7**: Fix wave (if needed)
9. **Phase 8**: Reflection (project lessons)
10. **Phase 8b**: Meta-reflection (skill mutates itself)

### Load as knowledge reference

```
/skill:viable-swarm-model
```

This loads the skill's patterns, anti-patterns, and checklists without triggering the full workflow. Useful when you need a specific checklist or pattern.

## Architecture

### Custom sub-agent types

The skill defines **5 custom sub-agent types** that map to VSM roles:

| Role | Type | Job |
|---|---|---|
| Architect | `vsm_architect` | Reads codebase, researches tech, produces design docs |
| Auditor | `vsm_auditor` | Read-only deep inspection. PASS / ISSUES / BLOCKER |
| Coordinator | `vsm_coordinator` | Cross-file contract validation |
| Security | `vsm_security` | Exhaustive security audit |
| Tester | `vsm_tester` | Writes and runs tests, fixes bugs inline |

### The mutation system

After every build, the skill evaluates its own performance:

- Did any prevention rule catch a real bug?
- Did any rule flag safe code as risky (false positive)?
- Were any vulnerability classes missed?
- Did any phase prove unnecessary?

If empirical findings justify it, the skill **appends new knowledge to its own files** and commits the change to git.

**What mutates:**
- `references/security-lessons.md` — new prevention rules
- `references/pattern-library.md` — new proven patterns
- `references/anti-patterns.md` — newly discovered failure modes
- `references/integration-checklist.md` — new cross-file checks
- `references/custom-agent-prompts.md` — refined agent prompts
- `SKILL.md` — phase structure and mutation rules themselves

**What protects against corruption:**
- **Git history** — every mutation is committed; bad mutations can be reverted
- **Phase 0 self-test** — the skill verifies it can still parse its own workflow before executing
- **Mutation amplitude limit** — max 3 structural mutations per session
- **Mutation log** — `references/mutation-log.md` is an append-only audit trail

## The closed feedback loop

```
Conversation N:
  ├─ Load skill (constitution + acquired wisdom)
  ├─ Self-test: can I execute my own workflow?
  ├─ Build executes with adapted plan
  ├─ New lessons learned (project + meta)
  ├─ Skill edits its own files
  ├─ New knowledge recorded
  └─ git commit

Conversation N+1:
  ├─ Load updated skill (smarter than before)
  ├─ Self-test passes
  ├─ Build starts from smarter position
  └─ ...repeat...
```

This is not iteration. This is **cybernetic learning**: Experience N modifies structure; modified structure shapes behavior N+1.

## Safety

- If a mutation breaks the skill, run `git revert HEAD` in `~/.kimi/skills/viable-swarm-model/`
- The `mutation-log.md` file records the rationale for every change
- Empirical append-only mutations are unlimited; structural changes to the core workflow are capped at 3 per session

## Requirements

- [Kimi Code CLI](https://github.com/MoonshotAI/Kimi-Chat)
- Projects with `.kimi/` directory for local lesson storage

## License

MIT
