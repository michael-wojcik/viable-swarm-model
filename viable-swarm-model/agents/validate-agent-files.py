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
