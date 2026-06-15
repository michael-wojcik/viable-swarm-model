#!/usr/bin/env python3
"""
Algedonic Action Plan Generator — S4*→S5 response bridge for vsm_variety_engineer.

Reads organism state files, identifies triggered algedonic signals, and generates
a concrete, prioritized action plan with SPECIFIC next steps (not generic
recommendations). The variety engineer can verify this plan rather than invent it.

Usage:
    python3 algedonic-action-plan.py [--build-dir <dir>]

If --build-dir is provided, writes:
    <build-dir>/.kimi/algedonic-action-plan.md
"""

import argparse
import os
import re
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

VSM_ROOT = Path.home() / "vsm" / "viable-swarm-model"
REFS_DIR = VSM_ROOT / "references"

MUTATION_STATE = REFS_DIR / "mutation-state.md"
HYPOTHESES = REFS_DIR / "hypotheses.md"
BUILD_HISTORY = REFS_DIR / "build-health-history.md"
SKILL_REGISTRY = Path(os.environ.get("VSM_SKILL_REGISTRY", Path.home() / "vsm" / "vsm-stack-skills" / "SKILL-REGISTRY.md"))


# ---------------------------------------------------------------------------
# Reused parsing (mirrors organism-vitals.py)
# ---------------------------------------------------------------------------

def parse_mutation_rows(path: Path) -> list[dict]:
    rows: list[dict] = []
    if not path.exists():
        return rows
    text = path.read_text()
    skip_section = False
    for line in text.splitlines():
        stripped = line.strip()
        # Track section headers to skip historical/removed/redesigned.
        # Section headers have the section name in the FIRST column (e.g., "**HISTORICAL**").
        # Data rows with bold status in later columns (e.g., "**REMOVED**", "**monitor**")
        # must NOT be treated as section headers.
        parts_header = [p.strip() for p in line.split("|")]
        parts_header = [p for p in parts_header if p]
        if stripped.startswith("|") and parts_header and parts_header[0].startswith("**"):
            header_text = parts_header[0]
            if "HISTORICAL" in header_text or "REMOVED" in header_text or "REDESIGNED" in header_text:
                skip_section = True
                continue
            else:
                # Any other section header (EFFECTIVE, PROBATION, FB30, etc.) resets
                skip_section = False
                continue
        if not stripped.startswith("|") or stripped.startswith("|---|"):
            continue
        parts = [p.strip() for p in line.split("|")]
        parts = [p for p in parts if p]
        if len(parts) < 6:
            continue
        if parts[0].startswith("**") or parts[0] == "ID":
            continue
        if parts[1] in ("Source", "", "—"):
            continue
        if skip_section:
            continue
        clean_id = re.sub(r"^~~(.+)~~$", r"\1", parts[0])
        try:
            builds_tested = int(parts[5]) if parts[5] not in ("", "—") else 0
        except ValueError:
            builds_tested = 0
        score: int | None = None
        if len(parts) > 6 and parts[6] not in ("—", ""):
            try:
                score = int(parts[6])
            except ValueError:
                pass
        status = re.sub(r"\*\*", "", parts[4]).lower().strip() if len(parts) > 4 else ""
        rows.append({
            "id": clean_id, "status": status, "builds_tested": builds_tested,
            "score": score, "target": parts[3] if len(parts) > 3 else "",
        })
    # Deduplicate by ID, keeping last
    seen: dict[str, dict] = {}
    for r in rows:
        seen[r["id"]] = r
    return list(seen.values())


def count_untested_hypotheses(path: Path) -> int:
    if not path.exists():
        return 0
    text = path.read_text()
    return len(re.findall(r"\*\*Status\*\*:\s*untested", text))


def extract_untested_hypothesis_ids(path: Path) -> list[str]:
    """Extract IDs of hypotheses with Status: untested."""
    if not path.exists():
        return []
    text = path.read_text()
    ids: list[str] = []
    current_id = None
    for line in text.splitlines():
        m = re.match(r"##\s+(H\S+):", line) or re.match(r"##\s+(\[N\+\d+\]):", line)
        if m:
            current_id = m.group(1)
        if "**Status**: untested" in line and current_id:
            ids.append(current_id)
    return ids


def extract_latest_score(path: Path) -> float | None:
    if not path.exists():
        return None
    text = path.read_text()
    scores = []
    for match in re.finditer(r"Score:\s*([0-9]+(?:\.[0-9]+)?)\s*/\s*5\.0", text):
        scores.append(float(match.group(1)))
    for match in re.finditer(r"^## FB\d+.*\n.*\n- Score:\s*([0-9]+(?:\.[0-9]+)?)", text, re.MULTILINE):
        scores.append(float(match.group(1)))
    return scores[-1] if scores else None


def extract_skill_variety(path: Path) -> tuple[int, int]:
    """Return (skills_used, skills_total) from skill registry.

    Only counts skills with status 'Full' as part of the denominator.
    Excludes Planned, Icebox, and Deprecated skills which are not actionable.
    """
    if not path.exists():
        return 0, 0
    text = path.read_text()
    full_skill_names: set[str] = set()
    for line in text.splitlines():
        if "|" in line and "Full" in line:
            parts = [p.strip() for p in line.split("|")]
            parts = [p for p in parts if p]
            # Pattern skill rows have 5 columns; pitfall rows have 4
            if len(parts) >= 4 and parts[0] not in ("Skill", ""):
                status = parts[-1] if len(parts) == 5 else parts[-2] if len(parts) == 4 else ""
                if status == "Full":
                    full_skill_names.add(parts[0])
    # Count used skills from skill-effectiveness-log (match registry names)
    skill_log = REFS_DIR / "skill-effectiveness-log.md"
    seen_skills: set[str] = set()
    if skill_log.exists():
        log_text = skill_log.read_text()
        for line in log_text.splitlines():
            if not line.startswith("|"):
                continue
            parts = [p.strip() for p in line.split("|")]
            parts = [p for p in parts if p]
            if len(parts) >= 3 and parts[0] in full_skill_names:
                try:
                    builds_used = int(parts[1])
                    if builds_used > 0 and parts[0] not in seen_skills:
                        seen_skills.add(parts[0])
                except ValueError:
                    pass
    return len(seen_skills), len(full_skill_names)


# ---------------------------------------------------------------------------
# Action plan generation
# ---------------------------------------------------------------------------

def generate_mutation_actions(rows: list[dict]) -> list[str]:
    actions: list[str] = []
    probationary = [r for r in rows if r["status"] == "probation"]
    monitor = [r for r in rows if r["status"] == "monitor"]

    # Demotion candidates: monitor with low score and sufficient builds
    # Threshold relaxed from >=3 to >=2 builds to catch mutations like PM3 (score 2, 2 builds)
    demotion_ready = [
        r for r in monitor
        if r["builds_tested"] >= 2 and r["score"] is not None and r["score"] <= 2
    ]
    if demotion_ready:
        actions.append(
            f"**Demote {len(demotion_ready)} monitor mutation(s) to ineffective/removed**: "
            + ", ".join(f"{r['id']} (score {r['score']}, {r['builds_tested']} builds)" for r in demotion_ready)
        )

    # Unmeasured probationary: builds=0 and no score — need fitness build validation
    unmeasured = [
        r for r in probationary
        if r["builds_tested"] == 0 and r["score"] is None
    ]
    if unmeasured:
        actions.append(
            f"**Measure {len(unmeasured)} unmeasured probationary mutation(s)**: "
            + ", ".join(f"{r['id']}" for r in unmeasured)
        )

    # Promotion candidates: probation with high score and sufficient builds
    promotion_ready = [
        r for r in probationary
        if r["builds_tested"] >= 3 and r["score"] is not None and r["score"] >= 4
    ]
    if promotion_ready:
        actions.append(
            f"**Promote {len(promotion_ready)} probationary mutation(s) to effective**: "
            + ", ".join(f"{r['id']} (score {r['score']}, {r['builds_tested']} builds)" for r in promotion_ready)
        )

    # Historical promotions: effective with >= 5 builds and score >= 4
    historical_ready = [
        r for r in rows
        if r["status"] == "effective" and r["builds_tested"] >= 5
        and r["score"] is not None and r["score"] >= 4
    ]
    if historical_ready:
        actions.append(
            f"**Move {len(historical_ready)} effective mutation(s) to historical**: "
            + ", ".join(f"{r['id']} (score {r['score']}, {r['builds_tested']} builds)" for r in historical_ready)
        )

    if not actions:
        actions.append("No autonomous promotion/demotion actions available. Manual portfolio review recommended.")

    return actions


def generate_hypothesis_actions(untested_ids: list[str], hyp_path: Path) -> list[str]:
    actions: list[str] = []
    if not untested_ids:
        return actions

    # Categorize by skimming rationale keywords
    frontend = []
    backend = []
    infra = []
    arch = []
    other = []

    if hyp_path.exists():
        text = hyp_path.read_text()
        for hid in untested_ids:
            # Find the hypothesis section
            pattern = rf"## {re.escape(hid)}:.*?(?=\n## |\Z)"
            match = re.search(pattern, text, re.DOTALL)
            section = match.group(0) if match else ""
            section_lower = section.lower()

            if any(k in section_lower for k in ["frontend", "vite", "apollo", "react", "typescript", "npm", "jsdom"]):
                frontend.append(hid)
            elif any(k in section_lower for k in ["backend", "python", "pydantic", "sqlalchemy", "fastapi", "graphql"]):
                backend.append(hid)
            elif any(k in section_lower for k in ["docker", "compose", "port", "cors", "infra", "deployment"]):
                infra.append(hid)
            elif any(k in section_lower for k in ["architect", "agent file", "yaml", "subagent", "token", "context"]):
                arch.append(hid)
            else:
                other.append(hid)

    if frontend:
        actions.append(f"**Frontend gym batch**: Test {', '.join(frontend)} in a minimal React+Vite project")
    if backend:
        actions.append(f"**Backend gym batch**: Test {', '.join(backend)} in a minimal FastAPI project")
    if infra:
        actions.append(f"**Infrastructure gym batch**: Test {', '.join(infra)} in a build with Docker/Compose")
    if arch:
        actions.append(f"**Architecture gym batch**: Test {', '.join(arch)} — evaluate agent configuration changes")
    if other:
        actions.append(f"**Miscellaneous**: Test {', '.join(other)} when opportunity arises")

    # Priority: H[N+3] and H[N+4] are low-priority architecture experiments
    low_priority = [h for h in untested_ids if "N+" in h]
    if low_priority:
        actions.append(
            f"**Low priority (optional)**: {', '.join(low_priority)} — CLI architecture experiments; "
            "defer until prompt drift or tool misuse becomes measurable"
        )

    return actions


def generate_variety_actions(used: int, total: int) -> list[str]:
    actions: list[str] = []
    if total == 0:
        return actions

    ratio = used / total
    if ratio < 0.70:
        # Identify unused skills from registry
        unused: list[str] = []
        if SKILL_REGISTRY.exists():
            text = SKILL_REGISTRY.read_text()
            for line in text.splitlines():
                if "|" in line and ("Full" in line or "Planned" in line):
                    parts = [p.strip() for p in line.split("|")]
                    parts = [p for p in parts if p]
                    if len(parts) >= 4 and parts[0] not in ("Skill", ""):
                        skill_name = parts[0]
                        # Check if used in skill-effectiveness-log
                        skill_log = REFS_DIR / "skill-effectiveness-log.md"
                        if skill_log.exists():
                            log_text = skill_log.read_text()
                            # Simple heuristic: skill name appears with builds_used > 0
                            skill_used = False
                            for log_line in log_text.splitlines():
                                if skill_name in log_line and "|" in log_line:
                                    log_parts = [p.strip() for p in log_line.split("|")]
                                    log_parts = [p for p in log_parts if p]
                                    if len(log_parts) >= 3:
                                        try:
                                            if int(log_parts[1]) > 0:
                                                skill_used = True
                                                break
                                        except ValueError:
                                            pass
                            if not skill_used:
                                unused.append(skill_name)

        if unused:
            actions.append(
                f"1. **Exercise unused skills in next fitness build**: {', '.join(unused[:5])} "
                f"({len(unused)} total unused)"
            )
        actions.append(
            "2. **Agent variety boost**: Spawn vsm_variety_engineer and vsm_learning_curator "
            "in next build to exercise underutilized S4* agents"
        )
        if ratio < 0.50:
            actions.append(
                "3. **CRITICAL variety deficit**: Halt non-urgent builds and run a gym batch "
                "covering at least 3 unused skills before next fitness build"
            )
    return actions


def main() -> int:
    parser = argparse.ArgumentParser(description="Algedonic Action Plan Generator")
    parser.add_argument("--build-dir", help="Build directory to write .kimi/ artifacts to")
    args = parser.parse_args()

    # Compute metrics
    mutation_rows = parse_mutation_rows(MUTATION_STATE)
    active_statuses = {"probation", "effective", "monitor", "ineffective"}
    active_count = len([r for r in mutation_rows if r["status"] in active_statuses])
    probationary = sum(1 for r in mutation_rows if r["status"] == "probation")
    untested_count = count_untested_hypotheses(HYPOTHESES)
    untested_ids = extract_untested_hypothesis_ids(HYPOTHESES)
    latest_score = extract_latest_score(BUILD_HISTORY)
    used_skills, total_skills = extract_skill_variety(SKILL_REGISTRY)
    skill_ratio = round(used_skills / total_skills, 2) if total_skills else 0.0

    # Determine triggered algedonics
    algedonics: list[dict] = []
    if active_count > 70:
        algedonics.append({
            "name": "Active mutation bloat",
            "value": active_count,
            "threshold": 70,
            "level": "WARNING" if active_count <= 80 else "CRITICAL",
        })
    if probationary > 12:
        algedonics.append({
            "name": "Probationary mutations",
            "value": probationary,
            "threshold": 12,
            "level": "WARNING" if probationary <= 18 else "CRITICAL",
        })
    if untested_count > 7:
        algedonics.append({
            "name": "Untested hypotheses",
            "value": untested_count,
            "threshold": 7,
            "level": "WARNING" if untested_count <= 10 else "CRITICAL",
        })
    if skill_ratio < 0.70:
        algedonics.append({
            "name": "Skill variety",
            "value": skill_ratio,
            "threshold": 0.70,
            "level": "WARNING" if skill_ratio >= 0.50 else "CRITICAL",
        })

    # Build report
    lines = [
        "# Algedonic Action Plan — Pre-computed",
        f"**Date**: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M')} UTC",
        f"**Scanner**: scripts/algedonic-action-plan.py",
        "",
        "> This file is auto-generated by `scripts/algedonic-action-plan.py`.",
        "> The vsm_variety_engineer should read this file, verify actions, and write `.kimi/variety-assessment.md`.",
        "",
        "## Triggered Algedonics",
        "",
    ]

    if not algedonics:
        lines.append("✅ No algedonic signals triggered. No immediate action required.")
        lines.append("")
    else:
        for a in algedonics:
            lines.extend([
                f"### {a['level']}: {a['name']}",
                f"**Current Value**: {a['value']}",
                f"**Threshold**: {a['threshold']}",
                f"**Blocking**: {'YES' if a['level'] == 'CRITICAL' else 'NO'}",
                "",
                "**Specific Actions**:",
            ])

            if a["name"] in ("Active mutation bloat", "Probationary mutations"):
                for action in generate_mutation_actions(mutation_rows):
                    lines.append(f"- {action}")
            elif a["name"] == "Untested hypotheses":
                for action in generate_hypothesis_actions(untested_ids, HYPOTHESES):
                    lines.append(f"- {action}")
            elif a["name"] == "Skill variety":
                for action in generate_variety_actions(used_skills, total_skills):
                    lines.append(f"- {action}")

            lines.append("")

    lines.extend([
        "## Metrics Snapshot",
        "",
        f"| Metric | Value | Target |",
        f"|---|---|---|",
        f"| Active mutations | {active_count} | ≤ 70 |",
        f"| Probationary mutations | {probationary} | ≤ 12 |",
        f"| Untested hypotheses | {untested_count} | ≤ 7 |",
        f"| Skill variety | {skill_ratio} ({used_skills}/{total_skills}) | ≥ 0.70 |",
        f"| Latest build score | {latest_score if latest_score else 'N/A'} | ≥ 3.5 |",
        "",
    ])

    report_text = "\n".join(lines)

    if args.build_dir:
        build_path = Path(args.build_dir)
        out_path = build_path / ".kimi" / "algedonic-action-plan.md"
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(report_text)

    print(report_text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
