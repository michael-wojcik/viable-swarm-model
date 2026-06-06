#!/usr/bin/env python3
"""
Skill Effectiveness Tracker

Tracks which stack skills are referenced in fitness build outputs and
correlates skill usage with build scores.

Reads:
  - ~/vsm/vsm-stack-skills/SKILL-REGISTRY.md (skill catalog)
  - ~/vsm-fitness-builds/coach/FB*/.kimi/*.md (agent outputs)
  - ~/vsm-fitness-builds/coach/FB*/.kimi/meta-report.md or fitness-report.md (scores)

Appends:
  - ~/vsm/viable-swarm-model/references/skill-effectiveness-log.md
"""

from __future__ import annotations

import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
HOME = Path.home()
SKILL_REGISTRY_PATH = Path(os.environ.get("SKILL_TRACKER_REGISTRY", HOME / "vsm" / "vsm-stack-skills" / "SKILL-REGISTRY.md"))
COACH_DIR = Path(os.environ.get("SKILL_TRACKER_COACH_DIR", HOME / "vsm-fitness-builds" / "coach"))
OUTPUT_LOG_PATH = Path(os.environ.get("SKILL_TRACKER_OUTPUT", HOME / "vsm" / "viable-swarm-model" / "references" / "skill-effectiveness-log.md"))


def eprint(msg: str) -> None:
    print(msg, file=sys.stderr)


# ---------------------------------------------------------------------------
# Skill registry parsing
# ---------------------------------------------------------------------------

def parse_skills(path: Path) -> list[str]:
    """Extract skill names from SKILL-REGISTRY.md tables."""
    if not path.exists():
        eprint(f"WARNING: {path} not found; using empty skill list.")
        return []

    text = path.read_text(encoding="utf-8")
    skills: set[str] = set()

    # Pattern Skills table: | Skill | Description | Relevant Agents | ...
    # Pitfall Skills table: | Skill | Language | Status | Description |
    in_pattern_table = False
    in_pitfall_table = False

    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("## Pattern Skills"):
            in_pattern_table = True
            in_pitfall_table = False
            continue
        if stripped.startswith("## Pitfall Skills"):
            in_pitfall_table = True
            in_pattern_table = False
            continue
        if stripped.startswith("## ") and "Skills" not in stripped:
            in_pattern_table = False
            in_pitfall_table = False
            continue

        if not (in_pattern_table or in_pitfall_table):
            continue
        if not stripped.startswith("|"):
            continue
        if "---" in stripped or "Skill" in stripped.split("|")[1]:
            continue

        parts = [p.strip() for p in stripped.split("|")]
        parts = [p for p in parts if p]
        if not parts:
            continue

        skill_name = parts[0].strip("*` ")
        # Filter out non-skill rows (headers, section labels, archive notes)
        if skill_name and " " not in skill_name and "-" in skill_name:
            skills.add(skill_name)

    return sorted(skills)


# ---------------------------------------------------------------------------
# Build discovery and score extraction
# ---------------------------------------------------------------------------

def discover_builds(coach_dir: Path) -> list[Path]:
    """Return paths to coach build directories that contain a .kimi/ folder."""
    if not coach_dir.exists():
        eprint(f"WARNING: {coach_dir} not found; no builds to scan.")
        return []

    builds = []
    for entry in coach_dir.iterdir():
        if entry.is_dir() and entry.name.startswith("FB") and (entry / ".kimi").is_dir():
            builds.append(entry)
    # Sort for deterministic output
    builds.sort(key=lambda p: p.name)
    return builds


def extract_build_score(build_dir: Path) -> float | None:
    """Extract the overall build score (out of 5.0) from .kimi report files."""
    kimi_dir = build_dir / ".kimi"
    candidate_files = [
        kimi_dir / "fitness-report.md",
        kimi_dir / "meta-report.md",
        kimi_dir / "meta-evaluation-report.md",
    ]

    # Ordered patterns: more specific first. Tuple of (regex, normalize_to_5)
    patterns = [
        (r"Overall Score:\s*([0-9]+(?:\.[0-9]+)?)\s*/\s*5", False),
        (r"Self[- ]?Score:\s*([0-9]+(?:\.[0-9]+)?)\s*/\s*5", False),
        (r"Score:\s*([0-9]+(?:\.[0-9]+)?)\s*/\s*5", False),
        (r"([0-9]+(?:\.[0-9]+)?)\s*/\s*5\.0", False),
        (r"Overall Score:\s*([0-9]+(?:\.[0-9]+)?)\s*/\s*100", True),
        (r"Score:\s*([0-9]+(?:\.[0-9]+)?)\s*/\s*100", True),
    ]

    for file_path in candidate_files:
        if not file_path.exists():
            continue
        text = file_path.read_text(encoding="utf-8")
        for pat, normalize in patterns:
            m = re.search(pat, text, re.IGNORECASE)
            if m:
                score = float(m.group(1))
                if normalize:
                    score = score / 20.0
                return round(score, 2)

    return None


# ---------------------------------------------------------------------------
# Skill mention scanning
# ---------------------------------------------------------------------------

def find_skills_in_build(build_dir: Path, skills: list[str]) -> set[str]:
    """Return the set of skills mentioned at least once in .kimi/*.md files."""
    kimi_dir = build_dir / ".kimi"
    found: set[str] = set()
    # Only scan .md files to avoid binary noise
    md_files = list(kimi_dir.glob("*.md"))
    if not md_files:
        return found

    for md_file in md_files:
        try:
            text = md_file.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        for skill in skills:
            if skill in text:
                found.add(skill)
    return found


# ---------------------------------------------------------------------------
# Correlation analysis
# ---------------------------------------------------------------------------

def analyze_skill_effectiveness(
    skills: list[str],
    build_data: list[dict],
) -> list[dict]:
    """For each skill, compute avg score with/without and flag negative deltas."""
    results = []
    for skill in skills:
        with_scores = [b["score"] for b in build_data if skill in b["skills"] and b["score"] is not None]
        without_scores = [b["score"] for b in build_data if skill not in b["skills"] and b["score"] is not None]

        avg_with = round(mean(with_scores), 2) if with_scores else None
        avg_without = round(mean(without_scores), 2) if without_scores else None

        if avg_with is not None and avg_without is not None:
            delta = round(avg_with - avg_without, 2)
            flag = "NEGATIVE" if delta < 0 else ""
        else:
            delta = None
            flag = "INSUFFICIENT_DATA"

        results.append({
            "skill": skill,
            "builds_used": len(with_scores),
            "avg_with": avg_with,
            "avg_without": avg_without,
            "delta": delta,
            "flag": flag,
        })

    # Sort by most negative delta first, then by most usage
    results.sort(key=lambda r: (r["delta"] if r["delta"] is not None else 0, -r["builds_used"]))
    return results


# ---------------------------------------------------------------------------
# Log output
# ---------------------------------------------------------------------------

def append_log(results: list[dict]) -> None:
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    new_section = [
        f"\n## {today}\n",
        "| Skill | Builds Used | Avg Score (with) | Avg Score (without) | Delta | Flag |",
        "|-------|-------------|------------------|---------------------|-------|------|",
    ]
    for r in results:
        avg_with = f"{r['avg_with']:.2f}" if r["avg_with"] is not None else "—"
        avg_without = f"{r['avg_without']:.2f}" if r["avg_without"] is not None else "—"
        delta = f"{r['delta']:.2f}" if r["delta"] is not None else "—"
        new_section.append(
            f"| {r['skill']} | {r['builds_used']} | {avg_with} | {avg_without} | {delta} | {r['flag']} |"
        )
    new_text = "\n".join(new_section) + "\n"

    OUTPUT_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    if OUTPUT_LOG_PATH.exists():
        existing = OUTPUT_LOG_PATH.read_text(encoding="utf-8")
        # If today's section already exists, replace it instead of appending
        section_pattern = rf"\n## {re.escape(today)}\n.*?\n(?=\n## |\Z)"
        if re.search(section_pattern, existing, re.DOTALL):
            existing = re.sub(section_pattern, new_text, existing, flags=re.DOTALL)
            OUTPUT_LOG_PATH.write_text(existing, encoding="utf-8")
            eprint(f"[skill-effectiveness-tracker] Replaced existing section for {today}")
        else:
            OUTPUT_LOG_PATH.write_text(existing + new_text, encoding="utf-8")
            eprint(f"[skill-effectiveness-tracker] Appended results to {OUTPUT_LOG_PATH}")
    else:
        header = "# Skill Effectiveness Log\n\n> Auto-generated by skill-effectiveness-tracker.py\n"
        OUTPUT_LOG_PATH.write_text(header + new_text, encoding="utf-8")
        eprint(f"[skill-effectiveness-tracker] Created {OUTPUT_LOG_PATH}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    eprint("[skill-effectiveness-tracker] Starting analysis...")

    skills = parse_skills(SKILL_REGISTRY_PATH)
    eprint(f"[skill-effectiveness-tracker] Discovered {len(skills)} skills in registry.")

    builds = discover_builds(COACH_DIR)
    eprint(f"[skill-effectiveness-tracker] Discovered {len(builds)} builds with .kimi/ output.")

    build_data = []
    for build_dir in builds:
        score = extract_build_score(build_dir)
        used_skills = find_skills_in_build(build_dir, skills)
        build_data.append({
            "name": build_dir.name,
            "score": score,
            "skills": used_skills,
        })
        score_str = f"{score:.2f}" if score is not None else "N/A"
        eprint(f"[skill-effectiveness-tracker] {build_dir.name}: score={score_str}, skills={len(used_skills)}")

    results = analyze_skill_effectiveness(skills, build_data)
    append_log(results)

    # Summary to stderr
    negative = [r for r in results if r["flag"] == "NEGATIVE"]
    if negative:
        eprint("[skill-effectiveness-tracker] WARNING: Skills with negative correlation detected:")
        for r in negative:
            eprint(f"  - {r['skill']}: delta={r['delta']:.2f}")
    else:
        eprint("[skill-effectiveness-tracker] No negative skill correlations detected.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
