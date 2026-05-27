# VSM for Kimi Code CLI — Build Plan

> **Status**: Ready for execution in old CLI session (kimi-cli v1.45.0 with `--agent-file`)
> **Goal**: Create a fork of VSM skills that work on kimi-code v0.3.0+ (no custom agents)
> **Approach**: Build and validate in old CLI, then copy to new CLI

---

## Phase 1: Fork the Repo

```bash
# In old CLI session
cd ~
cp -r vsm vsm-kimi-code
cd vsm-kimi-code
git init
git add -A
git commit -m "fork: vsm for kimi-code (from vsm main)"
```

Update `extra_skill_dirs` to point to the fork:
```bash
echo 'extra_skill_dirs = ["~/vsm-kimi-code"]' >> ~/.kimi/config.toml
```

---

## Phase 2: Replace Custom Agent Spawning with Prompt-Injected Coders

### The Core Change

**OLD (custom agents — works on old CLI only):**
```
Agent(subagent_type="vsm_architect", prompt="Design a user service...")
```

**NEW (prompt-injected coder — works on both CLIs):**
```
# S5 reads the agent persona file first
ReadFile: agents/vsm_architect.md
# Then spawns a generic coder with the persona prepended
Agent(subagent_type="coder", prompt="[FULL vsm_architect.md CONTENT]\n\nDesign a user service...")
```

### Files to Modify

| File | Changes |
|---|---|
| `viable-swarm-model/SKILL.md` | Replace all `Agent(subagent_type="vsm_...")` with `Agent(subagent_type="coder")` + persona injection |
| `viable-swarm-model/SKILL.md` | Remove `--agent-file` prerequisite section |
| `viable-swarm-model/SKILL.md` | Update Phase 0 self-test: verify .md files exist (not .yaml files) |
| `vsm-fitness-coach/SKILL.md` | Remove `--agent-file` prerequisite |
| `vsm-fitness-gym/SKILL.md` | Remove `--agent-file` prerequisite |

### Agent Mapping

| Old Custom Agent | New Approach |
|---|---|
| `vsm_architect` | `coder` + architect persona |
| `vsm_product` | `coder` + product persona |
| `vsm_auditor` | `coder` + auditor persona (read-only guidance in prompt) |
| `vsm_coordinator` | `coder` + coordinator persona |
| `vsm_wiring` | `coder` + wiring persona |
| `vsm_backend_coder` | `coder` + backend coder persona |
| `vsm_frontend_coder` | `coder` + frontend coder persona |
| `vsm_backend_fix_agent` | `coder` + backend fixer persona |
| `vsm_frontend_fix_agent` | `coder` + frontend fixer persona |
| `vsm_devops_coder` | `coder` + devops persona |
| `vsm_security` | `coder` + security persona (read-only guidance) |
| `vsm_backend_tester` | `coder` + backend tester persona |
| `vsm_frontend_tester` | `coder` + frontend tester persona |
| `vsm_meta` | `coder` + meta evaluator persona |
| `vsm_synthesizer` | `coder` + synthesizer persona |
| `vsm_explore` | Built-in `explore` (no change needed!) |

### Tool Boundaries

On the old CLI, custom agent YAMLs enforced tool restrictions (e.g., auditor couldn't write files). With prompt-injected coders, tool boundaries are **prompt-based only**:

- Add explicit "You MUST NOT use WriteFile or StrReplaceFile" to auditor/security personas
- Add "You are read-only" instructions prominently
- S5 must verify agent output doesn't contain unauthorized tool calls

---

## Phase 3: A/B Test One Agent

Pick ONE agent to test first. Recommended: `vsm_architect` (low risk, no file writes).

**Test protocol:**
1. Run a build with old architecture: `Agent(subagent_type="vsm_architect")`
2. Run identical build with new architecture: `Agent(subagent_type="coder", prompt="[persona]\n[task]")`
3. Compare outputs — should be equivalent in structure, depth, and quality
4. If mismatch → refine persona prompt until equivalent
5. Repeat for next agent

---

## Phase 4: Full Migration

Once all agents are validated individually:
1. Update ALL spawn calls in `SKILL.md`
2. Run a full fitness build (coach) with the new architecture
3. Score against rubric — should be equivalent to old architecture
4. Fix any regressions

---

## Phase 5: Copy to New CLI

```bash
# Copy validated fork to new CLI skills directory
cp -r ~/vsm-kimi-code/* ~/.kimi-code/skills/

# Or symlink
ln -s ~/vsm-kimi-code/viable-swarm-model ~/.kimi-code/skills/viable-swarm-model
ln -s ~/vsm-kimi-code/vsm-fitness-gym ~/.kimi-code/skills/vsm-fitness-gym
ln -s ~/vsm-kimi-code/vsm-fitness-coach ~/.kimi-code/skills/vsm-fitness-coach
```

Test in new CLI:
```bash
kimi
/flow:viable-swarm-model Build a test project
```

Fix any new CLI-specific issues:
- Permission rules
- Context differences
- Tool behavior variations

---

## Phase 6: Maintain Both Repos

| Repo | CLI | Status |
|---|---|---|
| `~/vsm/` | kimi-cli v1.x | Stable, feature-complete |
| `~/vsm-kimi-code/` | kimi-code v0.3.0+ | Ported, maintained separately |

Both repos get independent mutations based on their respective platform's capabilities.

---

## Key Risks

1. **Context bloat**: Prepending full persona prompts to every `coder` spawn consumes more tokens than custom agents' system prompts
2. **Persona drift**: `coder` agent may not fully adopt the specialized role without YAML-enforced tool boundaries
3. **Performance**: More tokens per spawn = slower builds = potential timeouts on large projects
4. **Maintenance divergence**: Two repos = double the mutation tracking

## Success Criteria

- [ ] All 15 agent types spawn successfully as `coder` + persona
- [ ] Fitness build scores equivalent to old architecture (±0.2)
- [ ] No unauthorized tool calls from "read-only" agents
- [ ] Works on kimi-code v0.3.0+ without `--agent-file`
