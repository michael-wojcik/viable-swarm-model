#!/usr/bin/env python3
"""Validate vsm-stack-skills/ directory consistency and content quality."""

import re
import sys
from pathlib import Path

SKILLS_DIR = Path.home() / "vsm" / "vsm-stack-skills"
REGISTRY_FILE = SKILLS_DIR / "SKILL-REGISTRY.md"

# Minimum content thresholds
MIN_LINES_FULL = 40
MIN_LINES_STUB = 10
MIN_RULES = 5


def parse_registry_tables(content):
    """Extract skill names, dependencies, status, and relevant agents from markdown tables."""
    skills = {}
    in_table = False
    header_idx = {}
    for line in content.splitlines():
        if line.startswith("| Skill "):
            in_table = True
            headers = [h.strip() for h in line.split("|")]
            header_idx = {h: i for i, h in enumerate(headers) if h}
            continue
        if in_table and line.startswith("| -"):
            continue
        if in_table and line.startswith("|"):
            parts = [p.strip() for p in line.split("|")]
            if len(parts) > 1 and parts[1] and parts[1] != "Skill" and parts[1] != "---":
                name = parts[1]
                status = ""
                if "Status" in header_idx:
                    idx = header_idx["Status"]
                    if idx < len(parts):
                        status = parts[idx]
                depends_on = ""
                if "Depends On" in header_idx:
                    idx = header_idx["Depends On"]
                    if idx < len(parts):
                        depends_on = parts[idx]
                relevant_agents = ""
                if "Relevant Agents" in header_idx:
                    idx = header_idx["Relevant Agents"]
                    if idx < len(parts):
                        relevant_agents = parts[idx]
                skills[name] = {
                    "depends_on": depends_on,
                    "status": status,
                    "relevant_agents": relevant_agents,
                }
        elif in_table and not line.startswith("|"):
            in_table = False
    return skills


def count_rules(skill_md_content):
    """Count empirical rules (lines starting with ## or bullet points with substance)."""
    rules = 0
    for line in skill_md_content.splitlines():
        stripped = line.strip()
        if stripped.startswith("## ") and not stripped.startswith("## Table"):
            rules += 1
        elif re.match(r"^(- |\d+\.\s+)", stripped) and len(stripped) > 10:
            rules += 1
    return rules


def check_agent_references(skill_name, content, relevant_agents):
    """Verify that relevant agent types are referenced in the skill content."""
    missing = []
    if not relevant_agents or relevant_agents == "—":
        return missing
    # Extract agent names from the relevant_agents cell
    # Agent names may be comma-separated, possibly with "all coders" shorthand
    agent_names = [a.strip() for a in relevant_agents.split(",")]
    for agent in agent_names:
        if agent == "all coders":
            # Expand to common coder agent names
            expanded = [
                "vsm_backend_coder",
                "vsm_frontend_coder",
                "vsm_devops_coder",
            ]
            for expanded_agent in expanded:
                if expanded_agent not in content:
                    missing.append(expanded_agent)
        elif agent:
            # Map shorthand registry names to full agent names if needed
            full_name = agent
            if not agent.startswith("vsm_"):
                full_name = f"vsm_{agent}"
            if full_name not in content and agent not in content:
                missing.append(agent)
    return missing


def main():
    errors = []
    warnings = []

    if not REGISTRY_FILE.exists():
        errors.append(f"Registry not found: {REGISTRY_FILE}")
        print("\n".join(errors))
        sys.exit(1)

    registry_content = REGISTRY_FILE.read_text()
    registered_skills = parse_registry_tables(registry_content)

    actual_skills = set()
    for item in SKILLS_DIR.iterdir():
        if item.is_dir() and not item.name.startswith("."):
            skill_md = item / "SKILL.md"
            if not skill_md.exists():
                errors.append(f"Missing SKILL.md in {item.name}/")
            else:
                # Content validation
                content = skill_md.read_text()
                lines = content.splitlines()
                line_count = len(lines)
                rules = count_rules(content)

                skill_info = registered_skills.get(item.name, {})
                status = skill_info.get("status", "").lower()

                if status == "full":
                    if line_count < MIN_LINES_FULL:
                        errors.append(
                            f"Skill '{item.name}' is Full but SKILL.md is only "
                            f"{line_count} lines (min {MIN_LINES_FULL})"
                        )
                    if rules < MIN_RULES:
                        warnings.append(
                            f"Skill '{item.name}' is Full but has only {rules} "
                            f"empirical rules (min {MIN_RULES})"
                        )
                    # Empirical evidence check: Full skills must cite at least one build/experiment
                    has_build_id = bool(
                        re.search(r"\b(FB\d+|H\d+|Gym\s+E\d+|E\d+)\b", content)
                    )
                    if not has_build_id:
                        errors.append(
                            f"Skill '{item.name}' is Full but contains no build/experiment "
                            f"IDs (e.g., FB24, H150, Gym E15). Full skills must be grounded "
                            f"in empirical evidence."
                        )

                    # Agent prompt reference check
                    missing_agents = check_agent_references(
                        item.name, content, skill_info.get("relevant_agents", "")
                    )
                    if missing_agents:
                        warnings.append(
                            f"Skill '{item.name}' lists agents {missing_agents} in registry "
                            f"but does not reference them in SKILL.md"
                        )

                elif status in ("stub", "planned", "icebox"):
                    has_todo = any(
                        "TODO" in line or "Awaiting" in line or "Placeholder" in line
                        for line in lines
                    )
                    if line_count < MIN_LINES_STUB and not has_todo:
                        warnings.append(
                            f"Skill '{item.name}' is {status} with only {line_count} lines "
                            f"and no TODO marker (min {MIN_LINES_STUB} or TODO)"
                        )
                elif status == "deprecated":
                    # Deprecated skills are pointers; minimal validation
                    pass
                elif not status:
                    warnings.append(
                        f"Skill '{item.name}' has no status in registry"
                    )

            actual_skills.add(item.name)

    missing_from_registry = actual_skills - set(registered_skills.keys())
    missing_from_dir = set(registered_skills.keys()) - actual_skills

    for skill in sorted(missing_from_registry):
        errors.append(f"Skill '{skill}' exists but not in registry")
    for skill in sorted(missing_from_dir):
        errors.append(f"Skill '{skill}' in registry but directory missing")

    for skill, info in registered_skills.items():
        deps = info.get("depends_on", "")
        if deps and deps != "—":
            dep_names = [d.strip().strip("`[]") for d in deps.split(",")]
            for dep in dep_names:
                if dep == "language]-pitfalls":
                    continue
                if dep not in registered_skills:
                    errors.append(
                        f"Skill '{skill}' depends on '{dep}' which is not in registry"
                    )

    if errors:
        print("VALIDATION FAILED:")
        for err in errors:
            print(f"  ERROR: {err}")
    if warnings:
        for warn in warnings:
            print(f"  WARN:  {warn}")

    if errors:
        sys.exit(1)
    else:
        print(f"OK: {len(actual_skills)} skills validated")
        if warnings:
            print("(warnings present but not blocking)")
        sys.exit(0)


if __name__ == "__main__":
    main()
