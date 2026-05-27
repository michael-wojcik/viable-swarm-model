# Kimi Code CLI Integration Guide for VSM

> **Scope**: This reference documents how the VSM skill ecosystem integrates with Kimi Code CLI v0.3.0+ features. It is read by S5 during Phase 0 and by `vsm_meta` during evaluation.
> **Location**: `${KIMI_SKILL_DIR}/references/kimi-code-integration.md`
> **Mutation mode**: Append-only and refinement. Log changes to `mutation-log.md`.

---

## 1. Configuration (`config.toml`)

Kimi Code CLI stores global configuration at `~/.kimi-code/config.toml` (migrated from `~/.kimi/` in v0.2.0).

### Recommended settings for VSM users

```toml
# Allow the model to auto-invoke skills based on description + whenToUse
merge_all_available_skills = true

# Extra skill directories — VSM skills live here
extra_skill_dirs = ["~/vsm"]

# Background task concurrency — VSM spawns many parallel agents
[background]
max_running_tasks = 4        # Increase to 8 on high-end hosts
agent_task_timeout_s = 900   # 15 minutes for deep audits, security scans, meta-eval
keep_alive_on_exit = false   # Stop background tasks when the session closes

# Thinking mode — recommended for complex builds
[thinking]
mode = "auto"
effort = "high"

# Permission rules — reduce approval friction for VSM workflows
[[permission.rules]]
decision = "allow"
pattern = "Read"
scope = "user"

[[permission.rules]]
decision = "allow"
pattern = "Glob"
scope = "user"

[[permission.rules]]
decision = "allow"
pattern = "Grep"
scope = "user"

[[permission.rules]]
decision = "allow"
pattern = "TaskList"
scope = "user"

[[permission.rules]]
decision = "allow"
pattern = "TaskOutput"
scope = "user"

[[permission.rules]]
decision = "allow"
pattern = "Agent"
scope = "user"

[[permission.rules]]
dision = "allow"
pattern = "AskUserQuestion"
scope = "user"

[[permission.rules]]
decision = "allow"
pattern = "TodoList"
scope = "user"

[[permission.rules]]
decision = "allow"
pattern = "SearchWeb"
scope = "user"

[[permission.rules]]
decision = "allow"
pattern = "FetchURL"
scope = "user"

# Keep manual approval for destructive operations
[[permission.rules]]
decision = "ask"
pattern = "Bash(rm -rf*)"
scope = "user"

[[permission.rules]]
decision = "ask"
pattern = "WriteFile"
scope = "user"

[[permission.rules]]
decision = "ask"
pattern = "StrReplaceFile"
scope = "user"
```

### Key config fields relevant to VSM

| Field | VSM Relevance |
|---|---|
| `extra_skill_dirs` | Must include `~/vsm` (or symlink skills into `~/.kimi-code/skills/`) |
| `background.max_running_tasks` | Hard ceiling for parallel subagents. VSM reads this in Phase 0. |
| `background.agent_task_timeout_s` | Default timeout for background agents. VSM overrides to 3600s for auditors. |
| `thinking.mode` / `thinking.effort` | Auto-thinking helps with complex architectural decisions in Phase 1. |
| `permission.rules` | Pre-approving read-only and coordination tools reduces friction. |

---

## 2. Hooks

Kimi Code CLI supports lifecycle hooks declared in `config.toml` via `[[hooks]]` array tables. The VSM ecosystem can leverage these for audit logging, safety guards, and notifications.

### Recommended VSM hooks

Copy these into `~/.kimi-code/config.toml`:

```toml
# Log every subagent dispatch to the build directory for post-hoc analysis
[[hooks]]
event = "SubagentStart"
matcher = "vsm_.*"
command = "echo '{\"ts\":\"'$(date -Iseconds)'\",\"event\":\"SubagentStart\",\"agent\":\"'${KIMI_HOOK_AGENT_NAME}'\",\"prompt_preview\":\"'${KIMI_HOOK_PROMPT_PREVIEW}'\"}' >> .kimi/agent-dispatch.log"
timeout = 2

# Block obviously dangerous Bash commands before they run
[[hooks]]
event = "PreToolUse"
matcher = "Bash"
command = "node -e 'let d=\"\";process.stdin.on(\"data\",c=>d+=c);process.stdin.on(\"end\",()=>{const p=JSON.parse(d);const cmd=p.tool_input?.command??\"\";const danger=[/rm\\s+-rf\\s+\\//,/>:\\s*\\/dev\\/null/,/curl\\s+.*\\|\\s*sh/];if(danger.some(r=>r.test(cmd))){console.error(\"Blocked dangerous command by VSM hook\");process.exit(2);}});'"
timeout = 3

# Notify when background tasks complete (useful for long-running auditors)
[[hooks]]
event = "Notification"
matcher = "task\\.completed"
command = "echo 'VSM background task finished: '"
timeout = 2
```

### Hook events useful for VSM

| Event | Use Case |
|---|---|
| `SubagentStart` / `SubagentStop` | Audit logging of agent dispatches; verify agent types match phase requirements |
| `PreToolUse` (Bash) | Block dangerous commands; log shell commands for security review |
| `PostToolUse` (WriteFile / StrReplaceFile) | Log file modifications to `.kimi/file-changes.log` |
| `Notification` (task.completed / task.failed) | Surface background task status without polling |
| `SessionStart` | Print VSM context reminder when resuming a build session |
| `SessionEnd` | Flush build logs; emit completion summary |

> **Security note**: Hooks fail-open (non-zero exit codes allow the operation). Do not treat hooks as the sole security boundary. Use permission rules for high-risk tools.

---

## 3. MCP (Model Context Protocol)

Kimi Code CLI v0.3.0+ supports MCP servers via `~/.kimi-code/mcp.json` or `.kimi-code/mcp.json` (project-level).

### VSM-relevant MCP integrations

| Server | VSM Use Case |
|---|---|
| `filesystem` | Advanced file operations beyond built-in tools |
| `github` | Pull request review, issue tracking, code search |
| `postgres` / `sqlite` | Direct database inspection during integration verification |
| `fetch` | Enhanced web fetching with custom headers |

### MCP configuration example

```json
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": { "GITHUB_PERSONAL_ACCESS_TOKEN": "ghp_xxx" }
    }
  }
}
```

> **Note**: The VSM does not require MCP to function. MCP is an optional enhancement for users who want external tool integration.

---

## 4. Modern CLI Commands Useful During VSM Builds

### `/fork`
Use when exploring alternative architectures or experimental fix approaches without disrupting the current build flow. The forked session is fully independent.

> **VSM guidance**: If S5 wants to test a risky structural mutation before applying it, use `/fork` to evaluate the change in isolation.

### `/compact [instruction]`
Manually compress context when approaching the window limit during long builds. Pass a custom instruction to preserve critical build state:

```
/compact Keep the current build plan, lessons learned, and open BLOCKERs. Drop explored file contents.
```

> **VSM guidance**: Tier 2+ builds frequently approach context limits. Use `/compact` before spawning the meta-evaluation agent in Phase 8b.

### `/init`
Generates `AGENTS.md` for the current codebase. Useful when the VSM is invoked on an existing project without prior context.

> **VSM guidance**: If `.kimi/lessons.md` does not exist and the project is unfamiliar, run `/init` before Phase 0 to populate initial context.

### `/sessions` / `/resume`
Resume previous sessions. VSM builds span many turns; use session resumption to continue after interruption.

> **VSM guidance**: Fitness builds (coach) and experiments (gym) can be long-running. Document the session ID in the build directory for later resumption.

### `/yolo [on|off]`
Toggle auto-approve mode. Useful for trusted, repetitive VSM workflows (e.g., running the full fitness coach cycle).

> **VSM guidance**: Only enable `/yolo` when you fully trust the custom agents and have reviewed the permission rules. Never use `/yolo` on untrusted codebases.

---

## 5. Skill System Enhancements (v0.3.0)

### `whenToUse` field
All VSM skills now declare `whenToUse` in frontmatter. This enables the model to auto-invoke the skill when the user's prompt matches the described scenario.

### `arguments` field
`vsm-fitness-coach` accepts a `$build_hint` argument. `vsm-fitness-gym` accepts `$hypothesis_ids`. Use named arguments for precise skill invocation:

```
/flow:vsm-fitness-coach Run fitness build targeting auth subsystem
/flow:vsm-fitness-gym Test hypotheses H12, H15
```

### `${KIMI_SKILL_DIR}` placeholder
Skill bodies can reference their own directory with `${KIMI_SKILL_DIR}`. The VSM skills use this for portable path references to `references/`, `agents/`, and `assets/`.

### Skill types
| Type | VSM Usage |
|---|---|
| `flow` | `viable-swarm-model`, `vsm-fitness-coach`, `vsm-fitness-gym` — manual invocation only |
| `prompt` | Stack skills (patterns, pitfalls) — auto-invoked by model when relevant |
| `inline` | Lightweight triggers — can be invoked via the `Skill` tool |

---

## 6. Data Directory Migration (v0.2.0 → v0.3.0)

Kimi Code CLI migrated from `~/.kimi/` to `~/.kimi-code/` in release 0.2.0:
- Skills: `~/.kimi/skills/` → `~/.kimi-code/skills/`
- Config: `~/.kimi/config.toml` → `~/.kimi-code/config.toml`
- Sessions: `~/.kimi/sessions/` → `~/.kimi-code/sessions/`

The VSM ecosystem has been updated to reference `~/.kimi-code/`. If you encounter stale `~/.kimi/` paths in downstream tools or documentation, treat them as bugs.

---

## 7. Validation Checklist

Before declaring a VSM build complete, verify Kimi Code CLI integration:

- [ ] `~/.kimi-code/config.toml` exists and `extra_skill_dirs` includes `~/vsm`
- [ ] `background.max_running_tasks` is read correctly in Phase 0
- [ ] All custom agent types spawn without "unknown subagent type" errors
- [ ] Skill frontmatter parses correctly (check `kimi` startup logs for skill loading)
- [ ] If using hooks, `config.toml` parses without errors on session start
- [ ] If using MCP, `/mcp` shows connected servers
