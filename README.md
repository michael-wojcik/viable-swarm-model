# viable-swarm-model

A self-modifying cybernetic development swarm for [Kimi Code CLI](https://github.com/MoonshotAI/Kimi-Chat), based on Stafford Beer's Viable System Model (VSM).

This is not a static prompt. It is a **learning organism** that evolves its own files between sessions.

> **The analogy**: `viable-swarm-model` is the **athlete** (does the real work),
> `vsm-fitness-coach` is the **coach** (designs training, evaluates
> performance), and `vsm-fitness-gym` is the **gym** (isolated equipment
> for targeted workouts).

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
| Human tests hypotheses | **Built-in scientific method**: hypothesis → experiment → falsification → theory update |
| Ad-hoc evaluation | **Structured fitness builds** with scored rubrics and standardized reports |

## Repository Structure

This repo contains **three skills** that co-evolve:

```
viable-swarm-model/                    ← the repo
├── README.md
├── viable-swarm-model/                ← main skill (the builder)
│   ├── SKILL.md
│   ├── agents/
│   │   ├── vsm_architect.md
│   │   ├── vsm_auditor.md
│   │   ├── vsm_backend_coder.md
│   │   ├── vsm_backend_fix_agent.md
│   │   ├── vsm_backend_tester.md
│   │   ├── vsm_coordinator.md
│   │   ├── vsm_devops_coder.md
│   │   ├── vsm_frontend_coder.md
│   │   ├── vsm_frontend_fix_agent.md
│   │   ├── vsm_frontend_tester.md
│   │   ├── vsm_meta.md
│   │   ├── vsm_product.md
│   │   ├── vsm_security.md
│   │   └── vsm_wiring.md
│   ├── references/
│   │   ├── acquired-wisdom.md
│   │   ├── anti-patterns.md
│   │   ├── experiments.md             ← experiment log
│   │   ├── hypotheses.md              ← hypothesis backlog
│   │   ├── integration-checklist.md
│   │   ├── mutation-log.md
│   │   ├── pattern-library.md
│   │   └── security-lessons.md
│   └── assets/
│       └── lessons-template.md
├── vsm-fitness-gym/             ← companion skill (the research lab)
│   ├── SKILL.md
│   ├── agents/
│   │   └── vsm_experiment_designer.md
│   ├── references/
│   │   └── experiment-templates.md
│   └── assets/
│       └── hypothesis-template.md
└── vsm-fitness-coach/          ← companion skill (the coach)
    ├── SKILL.md
    ├── references/
    │   ├── fitness-projects.md        ← catalog of test projects
    │   └── evaluation-rubric.md       ← scoring criteria
    └── assets/
        └── fitness-report-template.md
```

## Installation

Because this repo contains three skills, use `extra_skill_dirs`:

```bash
# Clone to a known location
git clone https://github.com/michael-wojcik/viable-swarm-model.git ~/vsm

# Add to your Kimi CLI config
echo 'extra_skill_dirs = ["~/vsm"]' >> ~/.kimi/config.toml
```

Or symlink all three skills individually:

```bash
git clone https://github.com/michael-wojcik/viable-swarm-model.git ~/vsm
ln -s ~/vsm/viable-swarm-model ~/.kimi/skills/viable-swarm-model
ln -s ~/vsm/vsm-fitness-gym ~/.kimi/skills/vsm-fitness-gym
ln -s ~/vsm/vsm-fitness-coach ~/.kimi/skills/vsm-fitness-coach
```

## Usage

### Launch with the VSM agent file

```bash
kimi --agent-file ~/vsm/viable-swarm-model/agents/vsm-main.yaml
```

This loads all 15+ custom subagent types required by the VSM workflow.

### Build a project with the full swarm

```
Let's build a project. /flow:viable-swarm-model Build a real-time collaborative document editor with React and FastAPI
```

**Note**: `/flow` commands must be embedded in a message with some natural
language text. Standalone `/flow:name` may not trigger a response.

This executes the complete VSM phase workflow:
1. **Phase 0**: Viability check + self-test
2. **Phase 1**: Intelligence (architect designs the system)
3. **Phase 2**: Foundation wave (types, config, scaffolding)
4. **Phase 3**: Implementation wave (features, wiring)
5. **Phase 4**: Testing + infrastructure wave
6. **Phase 5**: Security gate
7. **Phase 6**: Integration verification
8. **Phase 7**: Fix wave (if needed)
9. **Phase 8**: Reflection (project lessons)
10. **Phase 8b**: Meta-reflection + hypothesis generation (skill mutates itself)

### Run a comprehensive fitness build

```
Let's do a fitness build. /flow:vsm-fitness-coach
```

The fitness coach:
1. Presents a catalog of substantial test projects (DocuFlow, GeoQuiz, TaskFlow)
2. You select one
3. Creates a dedicated build directory (`~/vsm-fitness-builds/coach/FB1-20260522/`)
4. Guides the main skill through building the project **in that directory**
5. Scores every phase of the main skill's performance (1-5)
6. Identifies systemic gaps and generates hypotheses
7. Produces a structured fitness report
8. Proposes mutations to improve the main skill

**Important**: Fitness builds are isolated in `~/vsm-fitness-builds/`. They never
touch your actual project directory. Clean up old builds anytime:
```bash
rm -rf ~/vsm-fitness-builds/*
```

### Run focused experiments on specific hypotheses

```
Let's test some hypotheses. /flow:vsm-fitness-gym Test hypotheses H2, H7, H12
```

The gym:
1. Reads the main skill's hypothesis backlog
2. Designs minimal reproducible experiments
3. Builds tiny test projects with intentional bugs
4. Runs the main skill's agents against them
5. Records whether the skill caught or missed each issue
6. Proposes mutations to close confirmed gaps

### Load as knowledge reference

```
/skill:viable-swarm-model
```

This loads the skill's patterns, anti-patterns, and checklists without triggering the full workflow.

## Architecture

### Custom sub-agent types

The main skill defines **14 custom sub-agent types** that map to VSM roles:

| VSM Role | Type | Job |
|---|---|---|
| S4 Intelligence | `vsm_architect` | Reads codebase, researches tech, produces design docs |
| S4 Intelligence | `vsm_product` | Analyzes user problems, defines success criteria, proposes MVP feature set |
| S3* Audit | `vsm_auditor` | Read-only deep inspection. PASS / ISSUES / BLOCKER |
| S2 Coordination | `vsm_coordinator` | Cross-file contract validation |
| S5 Policy | `vsm_security` | Exhaustive security audit |
| S1 Operations | `vsm_backend_coder` | Backend implementation (FastAPI, SQLAlchemy, GraphQL) |
| S1 Operations | `vsm_frontend_coder` | Frontend implementation (React, TypeScript, Vite) |
| S1 Operations | `vsm_devops_coder` | Docker, CI/CD, infrastructure |
| S1 Quality | `vsm_backend_tester` | Backend tests (pytest), API contract validation |
| S1 Quality | `vsm_frontend_tester` | Frontend tests (vitest), build verification |
| S1 Fix | `vsm_backend_fix_agent` | Surgical backend fixes with re-audit protocol |
| S1 Fix | `vsm_frontend_fix_agent` | Surgical frontend fixes with re-audit protocol |
| S2 Coordination | `vsm_wiring` | Entry-point wiring (main.py, App.tsx, main.tsx) |
| S1 Meta | `vsm_meta` | Performance evaluation, hypothesis generation |

The gym adds:

| Role | Type | Job |
|---|---|---|
| Experiment Designer | `vsm_experiment_designer` | Designs minimal, isolated experiments |

The fitness coach adds:

| Role | Type | Job |
|---|---|---|
| Trainer | `vsm_trainer` | Reads build artifacts + rubric, scores phases, identifies gaps, produces fitness report |

### The mutation system

After every build, the main skill evaluates its own performance:

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
- `references/hypotheses.md` — new hypotheses to test
- `references/experiments.md` — experiment records
- `agents/*.md` — Kimi CLI custom subagent definitions
- `SKILL.md` — phase structure and mutation rules themselves

**What protects against corruption:**
- **Git history** — every mutation is committed; bad mutations can be reverted
- **Phase 0 self-test** — the skill verifies it can still parse its own workflow before executing
- **Mutation amplitude limit** — max 3 structural mutations per session
- **Mutation log** — `references/mutation-log.md` is an append-only audit trail

### The scientific method

The ecosystem learns at three scales:

1. **Fitness builds** (coach): "Let's build DocuFlow and see how the skill performs end-to-end."
   → Scores each phase, identifies systemic weaknesses, produces hypotheses.

2. **Focused experiments** (gym): "Let's test H2 with a 20-line endpoint."
   → Isolates variables, confirms/rejects hypotheses with scientific rigor.

3. **Theory update** (main skill mutation): "H2 confirmed. Append 'computed field N+1' to auditor prompt."
   → Updates skill files, commits to git.

This is how the skill discovers **new vulnerability classes** and **new patterns**
that were never in the original knowledge pack — through structured observation,
isolated experimentation, and empirical mutation.

## The closed feedback loop

```
Conversation N (fitness build):
  ├─ Load fitness coach
  ├─ Select DocuFlow from catalog
  ├─ Guide main skill through full build
  ├─ Collect all reports and artifacts
  ├─ Score each phase 1-5 against rubric
  ├─ Identify gaps, generate hypotheses
  ├─ Write fitness report
  └─ git commit

Conversation N+1 (focused experiment):
  ├─ Load gym
  ├─ Read hypothesis backlog (from fitness build + main skill)
  ├─ Design minimal experiments for top hypotheses
  ├─ Run experiments, record results
  ├─ Update hypothesis status (confirmed/rejected)
  ├─ Propose mutations to main skill
  └─ git commit

Conversation N+2 (next real project or fitness build):
  ├─ Load updated skill (smarter than before)
  ├─ Self-test passes
  ├─ Execute build from smarter position
  ├─ Phase 8b: More hypotheses...
  └─ ...repeat...
```

The one-conversation delay between observation and validated mutation is not a bug — it's how biological learning works. Experience N modifies structure; modified structure shapes behavior N+1.

## Safety

- If a mutation breaks the skill, run `git revert HEAD` in `~/vsm/`
- The `mutation-log.md` file records the rationale for every change
- Empirical append-only mutations are unlimited; structural changes to the core workflow are capped at 3 per session
- The gym runs experiments in `~/vsm-fitness-builds/gym/` — they never affect real projects

## Requirements

- [Kimi Code CLI](https://github.com/MoonshotAI/Kimi-Chat)
- Projects with `.kimi/` directory for local lesson storage
- Git (for mutation history and rollback)

## License

MIT
