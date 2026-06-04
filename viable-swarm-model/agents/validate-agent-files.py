#!/usr/bin/env python3
"""
Validate VSM custom agent files.

Checks:
1. Every .yaml file parses correctly.
2. Every .yaml's system_prompt_path points to an existing .md file.
3. Every ${VAR} in .md files is either a built-in var or defined in the
   corresponding .yaml's system_prompt_args (including inherited args).
4. Every {% include './xxx.md' %} in .md files resolves to an existing file.
5. No unescaped ${...} shell-variable patterns (e.g., ${VAR:-default}).
6. Intermediate templates (vsm-main.md, vsm-*.md) are framework-agnostic
   (no FastAPI, React, etc. keywords).
7. Every leaf .yaml is registered in vsm-main.yaml's subagents block.
8. No orphaned .md files (no matching .yaml, not included by any chain).
9. No unfilled bracket placeholders ([...]) in leaf agent prompts.
10. External file references (~/vsm/...) resolve to real paths.
11. Every skill referenced in agent prompts is listed in SKILL-REGISTRY.md.
12. Every skill listed in SKILL-REGISTRY.md has a SKILL.md file on disk.

Run from the agents/ directory:
    python3 validate-agent-files.py
"""

import os
import re
import sys
import yaml

AGENTS_DIR = os.path.dirname(os.path.abspath(__file__))
VSM_ROOT = os.path.dirname(AGENTS_DIR)

BUILT_IN_VARS = {
    "KIMI_NOW",
    "KIMI_WORK_DIR",
    "KIMI_WORK_DIR_LS",
    "KIMI_AGENTS_MD",
    "KIMI_SKILLS",
    "KIMI_ADDITIONAL_DIRS_INFO",
}

# Framework keywords that should NOT appear in base/intermediate templates.
FORBIDDEN_KEYWORDS = [
    "FastAPI", "Pydantic", "SQLAlchemy", "Strawberry",
    "React", "Vite", "Apollo", "Zustand",
    "pytest", "vitest"
]


def load_yaml(path: str):
    with open(path) as f:
        return yaml.safe_load(f)


def collect_system_prompt_args(yaml_path: str, visited=None) -> dict:
    """Recursively collect system_prompt_args following extend chain."""
    if visited is None:
        visited = set()
    abs_path = os.path.abspath(yaml_path)
    if abs_path in visited:
        return {}
    visited.add(abs_path)

    data = load_yaml(yaml_path)
    agent_cfg = data.get("agent", {})
    args = dict(agent_cfg.get("system_prompt_args", {}))

    extend = agent_cfg.get("extend")
    if extend and extend != "default":
        parent_path = os.path.join(os.path.dirname(yaml_path), extend)
        parent_args = collect_system_prompt_args(parent_path, visited)
        # Child overrides parent
        merged = dict(parent_args)
        merged.update(args)
        return merged

    return args


def extract_vars(md_content: str) -> set:
    return set(re.findall(r"\$\{([A-Za-z_][A-Za-z0-9_]*)\}", md_content))


def is_intermediate_template(md_name: str) -> bool:
    """Intermediate templates are framework-agnostic and must not mention stacks."""
    return md_name == "vsm-main.md" or md_name.startswith("vsm-")


def resolve_include_chain(md_path: str, visited=None) -> set:
    """Recursively collect all .md files included by a given .md file."""
    if visited is None:
        visited = set()
    abs_path = os.path.abspath(md_path)
    if abs_path in visited:
        return visited
    visited.add(abs_path)

    with open(md_path) as f:
        content = f.read()

    includes = re.findall(r"{%\s+include\s+['\"](.+?)['\"]\s+%}", content)
    for inc in includes:
        inc_path = os.path.join(os.path.dirname(md_path), inc)
        if os.path.exists(inc_path):
            resolve_include_chain(inc_path, visited)

    return visited


def main():
    errors = []
    warnings = []

    yaml_files = sorted(f for f in os.listdir(AGENTS_DIR) if f.endswith(".yaml"))

    # --- Pre-compute include chains and subagent registry ---

    # Build map of which .md files include which other .md files
    all_md_files = {f for f in os.listdir(AGENTS_DIR) if f.endswith(".md")}
    included_by = {md: set() for md in all_md_files}
    for md_name in all_md_files:
        md_path = os.path.join(AGENTS_DIR, md_name)
        chain = resolve_include_chain(md_path)
        for inc in chain:
            inc_name = os.path.basename(inc)
            if inc_name in included_by:
                included_by[inc_name].add(md_name)

    # Load vsm-main.yaml subagents registry
    vsm_main_path = os.path.join(AGENTS_DIR, "vsm-main.yaml")
    registered_subagents = set()
    if os.path.exists(vsm_main_path):
        vsm_main = load_yaml(vsm_main_path)
        registered_subagents = set(vsm_main.get("agent", {}).get("subagents", {}).keys())
    else:
        errors.append("vsm-main.yaml not found — cannot verify subagent registration")

    # --- Per-yaml validation ---

    for yaml_name in yaml_files:
        yaml_path = os.path.join(AGENTS_DIR, yaml_name)
        try:
            data = load_yaml(yaml_path)
        except yaml.YAMLError as e:
            errors.append(f"{yaml_name}: YAML parse error: {e}")
            continue

        agent_cfg = data.get("agent", {})
        sp_path = agent_cfg.get("system_prompt_path")
        if not sp_path:
            warnings.append(f"{yaml_name}: no system_prompt_path")
            continue

        md_path = os.path.join(os.path.dirname(yaml_path), sp_path)
        if not os.path.exists(md_path):
            errors.append(f"{yaml_name}: system_prompt_path not found: {sp_path}")
            continue

        with open(md_path) as f:
            md_content = f.read()

        md_name = os.path.basename(md_path)

        # 4. Check Jinja2 includes resolve
        includes = re.findall(r"{%\s+include\s+['\"](.+?)['\"]\s+%}", md_content)
        for inc in includes:
            inc_path = os.path.join(os.path.dirname(md_path), inc)
            if not os.path.exists(inc_path):
                errors.append(f"{yaml_name} ({sp_path}): include not found: {inc}")

        # 6. Forbidden keywords — only for intermediate templates
        if is_intermediate_template(md_name):
            for keyword in FORBIDDEN_KEYWORDS:
                if keyword in md_content:
                    errors.append(f"{yaml_name}: forbidden keyword '{keyword}' in intermediate template {md_name}")

        # 9. Unfilled bracket placeholders in LEAF agent prompts
        # Leaf = not an intermediate template (i.e., final agent prompt)
        if not is_intermediate_template(md_name):
            placeholders = re.findall(r"\[([A-Za-z\s\-]+)\]", md_content)
            # Filter out legitimate markdown link text and common terms
            common_ok = {"source", "build", "fb", "fix", "backend", "frontend", "devops"}
            bad_placeholders = [p for p in placeholders if p.lower() not in common_ok and len(p) > 3]
            if bad_placeholders:
                warnings.append(
                    f"{yaml_name} ({sp_path}): unfilled bracket placeholders: {', '.join(sorted(set(bad_placeholders)))}"
                )

        # 10. External file existence check
        external_refs = re.findall(r"~/vsm/([A-Za-z0-9_\-/]+\.md)", md_content)
        for ref in external_refs:
            full_path = os.path.expanduser(f"~/vsm/{ref}")
            if not os.path.exists(full_path):
                errors.append(f"{yaml_name} ({sp_path}): external file not found: ~/vsm/{ref}")

    # --- Post-yaml validation: SKILL-REGISTRY completeness ---

    # 11. Verify every skill referenced in agent prompts exists in registry and on disk
    registry_path = os.path.expanduser("~/vsm/vsm-stack-skills/SKILL-REGISTRY.md")
    registered_skills = set()
    if os.path.exists(registry_path):
        with open(registry_path) as f:
            registry_content = f.read()
        # Extract skill names from registry tables
        for line in registry_content.split('\n'):
            if line.startswith('|') and not line.startswith('|---'):
                parts = [p.strip() for p in line.split('|')]
                parts = [p for p in parts if p]
                if len(parts) >= 3 and parts[0] not in ('Skill', 'Pattern Skills', 'Pitfall Skills'):
                    registered_skills.add(parts[0])

    for yaml_name in yaml_files:
        agent_name = yaml_name.replace(".yaml", "")
        if agent_name in ("vsm-main",):
            continue  # Base template references skills generically
        yaml_path = os.path.join(AGENTS_DIR, yaml_name)
        data = load_yaml(yaml_path)
        agent_cfg = data.get("agent", {})
        sp_path = agent_cfg.get("system_prompt_path")
        if not sp_path:
            continue
        md_path = os.path.join(os.path.dirname(yaml_path), sp_path)
        if not os.path.exists(md_path):
            continue
        with open(md_path) as f:
            md_content = f.read()

        # Find all skill references: ~/vsm/vsm-stack-skills/NAME/SKILL.md
        skill_refs = re.findall(r"~/vsm/vsm-stack-skills/([A-Za-z0-9_\-]+)/SKILL\.md", md_content)
        for skill_name in skill_refs:
            if skill_name not in registered_skills:
                errors.append(
                    f"{yaml_name}: references skill '{skill_name}' NOT in SKILL-REGISTRY.md"
                )
            skill_dir = os.path.expanduser(f"~/vsm/vsm-stack-skills/{skill_name}")
            skill_file = os.path.join(skill_dir, "SKILL.md")
            if not os.path.exists(skill_file):
                errors.append(
                    f"{yaml_name}: references skill '{skill_name}' but ~/vsm/vsm-stack-skills/{skill_name}/SKILL.md does not exist"
                )

    # 12. Verify every skill in SKILL-REGISTRY.md has a SKILL.md file
    if registered_skills:
        for skill_name in registered_skills:
            skill_file = os.path.expanduser(f"~/vsm/vsm-stack-skills/{skill_name}/SKILL.md")
            if not os.path.exists(skill_file):
                errors.append(
                    f"SKILL-REGISTRY.md lists skill '{skill_name}' but ~/vsm/vsm-stack-skills/{skill_name}/SKILL.md does not exist"
                )

        vars_in_md = extract_vars(md_content)
        defined_args = collect_system_prompt_args(yaml_path)
        undefined = vars_in_md - set(defined_args.keys()) - BUILT_IN_VARS

        if undefined:
            errors.append(
                f"{yaml_name} ({sp_path}): undefined variables: {', '.join(sorted(undefined))}"
            )

        # 5. Check for unescaped ${...} patterns that are NOT valid template variables
        # Remove {% raw %} blocks entirely before checking
        md_without_raw = re.sub(r"{%\s*raw\s*%}(.*?){%\s*endraw\s*%}", "", md_content, flags=re.DOTALL)

        all_dollar_patterns = set(re.findall(r"\$\{([^}]+)\}", md_without_raw))
        valid_vars = set(defined_args.keys()) | BUILT_IN_VARS | vars_in_md
        bad_patterns = all_dollar_patterns - valid_vars
        if bad_patterns:
            errors.append(
                f"{yaml_name} ({sp_path}): unescaped ${'{...}'} patterns (not valid template vars): {', '.join(sorted(bad_patterns))}"
            )

    # 7. Subagent registration check
    for yaml_name in yaml_files:
        agent_name = yaml_name.replace(".yaml", "")
        # Skip intermediate/base templates
        if agent_name in ("vsm-main", "vsm-coder", "vsm-fixer", "vsm-tester", "vsm-reporter", "vsm-researcher"):
            continue
        if agent_name not in registered_subagents:
            errors.append(f"{yaml_name}: NOT registered in vsm-main.yaml subagents block")

    # 8. Orphaned .md file check
    for md_name in all_md_files:
        yaml_match = md_name.replace(".md", ".yaml")
        has_yaml = yaml_match in {y.replace(".yaml", "") for y in yaml_files}
        # Also check hyphen vs underscore
        yaml_match_alt = yaml_match.replace("_", "-")
        has_yaml_alt = yaml_match_alt in {y.replace(".yaml", "") for y in yaml_files}

        is_included = len(included_by.get(md_name, set())) > 0

        if not has_yaml and not has_yaml_alt and not is_included:
            warnings.append(f"{md_name}: orphaned — no matching .yaml and not included by any file")

    if errors:
        print("ERRORS:", file=sys.stderr)
        for e in errors:
            print(f"  ❌ {e}", file=sys.stderr)
    if warnings:
        print("WARNINGS:")
        for w in warnings:
            print(f"  ⚠️  {w}")

    if not errors and not warnings:
        print("✅ All agent files validated successfully.")
        return 0
    elif not errors:
        print("✅ No errors, but warnings present.")
        return 0
    else:
        return 1


if __name__ == "__main__":
    sys.exit(main())
