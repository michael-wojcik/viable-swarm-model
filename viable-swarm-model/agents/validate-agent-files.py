#!/usr/bin/env python3
"""
Validate VSM custom agent files.

Checks:
1. Every .yaml file parses correctly.
2. Every .yaml's system_prompt_path points to an existing .md file.
3. Every ${VAR} in .md files is either a built-in var or defined in the
   corresponding .yaml's system_prompt_args (including inherited args).

Run from the agents/ directory:
    python3 validate-agent-files.py
"""

import os
import re
import sys
import yaml

AGENTS_DIR = os.path.dirname(os.path.abspath(__file__))

BUILT_IN_VARS = {
    "KIMI_NOW",
    "KIMI_WORK_DIR",
    "KIMI_WORK_DIR_LS",
    "KIMI_AGENTS_MD",
    "KIMI_SKILLS",
    "KIMI_ADDITIONAL_DIRS_INFO",
}


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


def main():
    errors = []
    warnings = []

    yaml_files = sorted(f for f in os.listdir(AGENTS_DIR) if f.endswith(".yaml"))

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

        vars_in_md = extract_vars(md_content)
        defined_args = collect_system_prompt_args(yaml_path)
        undefined = vars_in_md - set(defined_args.keys()) - BUILT_IN_VARS

        if undefined:
            errors.append(
                f"{yaml_name} ({sp_path}): undefined variables: {', '.join(sorted(undefined))}"
            )

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
