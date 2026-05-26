#!/usr/bin/env python3
"""Validate vsm-stack-skills/ directory consistency."""

import sys
from pathlib import Path

SKILLS_DIR = Path.home() / "vsm" / "vsm-stack-skills"
REGISTRY_FILE = SKILLS_DIR / "SKILL-REGISTRY.md"

def parse_registry_tables(content):
    """Extract skill names and dependencies from markdown tables."""
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
                depends_on = ""
                if "Depends On" in header_idx:
                    idx = header_idx["Depends On"]
                    if idx < len(parts):
                        depends_on = parts[idx]
                skills[name] = depends_on
        elif in_table and not line.startswith("|"):
            in_table = False
    return skills

def main():
    errors = []
    
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
            actual_skills.add(item.name)
    
    missing_from_registry = actual_skills - set(registered_skills.keys())
    missing_from_dir = set(registered_skills.keys()) - actual_skills
    
    for skill in sorted(missing_from_registry):
        errors.append(f"Skill '{skill}' exists but not in registry")
    for skill in sorted(missing_from_dir):
        errors.append(f"Skill '{skill}' in registry but directory missing")
    
    for skill, deps in registered_skills.items():
        if deps and deps != "—":
            dep_names = [d.strip().strip("`[]") for d in deps.split(",")]
            for dep in dep_names:
                # [language]-pitfalls is a template placeholder, not a real skill
                if dep == "language]-pitfalls":
                    continue
                if dep not in registered_skills:
                    errors.append(f"Skill '{skill}' depends on '{dep}' which is not in registry")
    
    if errors:
        print("VALIDATION FAILED:")
        for err in errors:
            print(f"  - {err}")
        sys.exit(1)
    else:
        print(f"OK: {len(actual_skills)} skills validated")
        sys.exit(0)

if __name__ == "__main__":
    main()
