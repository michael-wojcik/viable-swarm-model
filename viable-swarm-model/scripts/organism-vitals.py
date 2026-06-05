#!/usr/bin/env python3
"""
Organism Vitals — Unified S4* health scanner for vsm_variety_engineer.

Pre-computes all variety metrics, algedonic thresholds, and proactive
recommendations so the variety engineer can verify rather than compute.

Reads:
- references/mutation-state.md (portfolio health)
- references/hypotheses.md (untested count)
- references/knowledge-broker.md (staleness)
- references/build-health-history.md (score trend)
- vsm-fitness-builds/coach/ (days since last build)

Usage:
    python3 organism-vitals.py [--build-dir <dir>]

If --build-dir is provided, writes:
    <build-dir>/.kimi/organism-vitals.md
"""

import argparse
import json
import re
import sys
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional

VSM_ROOT = Path.home() / "vsm" / "viable-swarm-model"
COACH_DIR = Path.home() / "vsm-fitness-builds" / "coach"
REFS_DIR = VSM_ROOT / "references"

MUTATION_STATE = REFS_DIR / "mutation-state.md"
HYPOTHESES = REFS_DIR / "hypotheses.md"
BROKER = REFS_DIR / "knowledge-broker.md"
BUILD_HISTORY = REFS_DIR / "build-health-history.md"


# ---------------------------------------------------------------------------
# Mutation state parsing (replicated from mutation-portfolio-health.py)
# ---------------------------------------------------------------------------

@dataclass
class MutationRow:
    id: str
    source: str
    type: str
    target_failure: str
    status: str
    builds_tested: int
    score: Optional[int]
    hypothesis: str
    experiment: str
    next_review: str


def parse_mutation_state(path: Path) -> list[MutationRow]:
    rows: list[MutationRow] = []
    if not path.exists():
        return rows
    text = path.read_text()
    for line in text.splitlines():
        stripped = line.strip()
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
        clean_id = re.sub(r"^~~(.+)~~$", r"\1", parts[0])
        builds_raw = parts[5] if len(parts) > 5 else "0"
        try:
            builds_tested = int(builds_raw) if builds_raw not in ("", "—") else 0
        except ValueError:
            builds_tested = 0
        score_raw = parts[6] if len(parts) > 6 else ""
        score: Optional[int] = None
        if score_raw and score_raw not in ("—", ""):
            try:
                score = int(score_raw)
            except ValueError:
                pass
        status_raw = parts[4].lower() if len(parts) > 4 else ""
        status_raw = re.sub(r"\*\*", "", status_raw).strip()
        rows.append(MutationRow(
            id=clean_id, source=parts[1], type=parts[2] if len(parts) > 2 else "",
            target_failure=parts[3] if len(parts) > 3 else "",
            status=status_raw, builds_tested=builds_tested, score=score,
            hypothesis=parts[7] if len(parts) > 7 else "",
            experiment=parts[8] if len(parts) > 8 else "",
            next_review=parts[9] if len(parts) > 9 else "",
        ))
    seen: dict[str, MutationRow] = {}
    for row in rows:
        seen[row.id] = row
    return list(seen.values())


# ---------------------------------------------------------------------------
# Hypotheses
# ---------------------------------------------------------------------------

def count_untested_hypotheses(path: Path) -> int:
    if not path.exists():
        return 0
    text = path.read_text()
    # Count occurrences of "untested" in status lines
    return len(re.findall(r"\*\*Status\*\*:\s*untested", text))


# ---------------------------------------------------------------------------
# Knowledge broker staleness
# ---------------------------------------------------------------------------

def broker_staleness_days(path: Path) -> int:
    if not path.exists():
        return 999
    text = path.read_text()
    match = re.search(r"\*\*Last updated\*\*:\s*(\d{4}-\d{2}-\d{2})", text)
    if not match:
        return 999
    try:
        updated = datetime.strptime(match.group(1), "%Y-%m-%d").date()
        return (datetime.now(timezone.utc).date() - updated).days
    except ValueError:
        return 999


# ---------------------------------------------------------------------------
# Build health history — latest score and trend
# ---------------------------------------------------------------------------

def extract_latest_score(path: Path) -> tuple[Optional[float], Optional[float]]:
    """Return (latest_score, previous_score) from build-health-history.md."""
    if not path.exists():
        return None, None
    text = path.read_text()
    scores = []
    for match in re.finditer(r"Score:\s*([0-9]+(?:\.[0-9]+)?)\s*/\s*5\.0", text):
        scores.append(float(match.group(1)))
    # Also look for inline scores like "3.85" in FB32 summary lines
    for match in re.finditer(r"^## FB\d+.*\n.*\n- Score:\s*([0-9]+(?:\.[0-9]+)?)", text, re.MULTILINE):
        scores.append(float(match.group(1)))
    if len(scores) >= 2:
        return scores[-1], scores[-2]
    if len(scores) == 1:
        return scores[0], None
    return None, None


def days_since_last_fitness_build() -> int:
    """Find the most recent build directory under vsm-fitness-builds/coach/."""
    if not COACH_DIR.exists():
        return 999
    latest = None
    for d in COACH_DIR.iterdir():
        if d.is_dir():
            # Parse date from directory name or look at mtime
            mtime = datetime.fromtimestamp(d.stat().st_mtime).date()
            if latest is None or mtime > latest:
                latest = mtime
    if latest is None:
        return 999
    return (datetime.utcnow().date() - latest).days


# ---------------------------------------------------------------------------
# Variety score computation
# ---------------------------------------------------------------------------

def compute_variety_score(
    agent_variety: float,
    hypothesis_variety: float,
    skill_variety: float,
    temporal_variety: float,
) -> float:
    return round(
        (agent_variety * 0.25)
        + (hypothesis_variety * 0.25)
        + (skill_variety * 0.30)
        + (temporal_variety * 0.20),
        2,
    )


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(description="Organism Vitals Scanner")
    parser.add_argument("--build-dir", help="Build directory to write .kimi/ artifacts to")
    args = parser.parse_args()

    # --- Mutation portfolio ---
    mutation_rows = parse_mutation_state(MUTATION_STATE)
    total_mutations = len(mutation_rows)
    active = sum(1 for r in mutation_rows if r.status in ("probation", "effective", "monitor", "ineffective"))
    probationary = sum(1 for r in mutation_rows if r.status == "probation")
    monitor_count = sum(1 for r in mutation_rows if r.status == "monitor")
    removed = sum(1 for r in mutation_rows if r.status == "removed")
    scored = sum(1 for r in mutation_rows if r.score is not None)
    fill_rate = round((scored / total_mutations) * 100, 1) if total_mutations else 0.0

    # --- Hypotheses ---
    untested = count_untested_hypotheses(HYPOTHESES)
    total_hypotheses = 0
    if HYPOTHESES.exists():
        text = HYPOTHESES.read_text()
        total_hypotheses = len(re.findall(r"\*\*Status\*\*:", text))
    hypothesis_variety = round((total_hypotheses - untested) / total_hypotheses, 2) if total_hypotheses else 0.0

    # --- Broker ---
    broker_age = broker_staleness_days(BROKER)

    # --- Build scores ---
    latest_score, prev_score = extract_latest_score(BUILD_HISTORY)
    score_drop = round(prev_score - latest_score, 2) if latest_score is not None and prev_score is not None else 0.0

    # --- Days since last fitness build ---
    days_since_build = days_since_last_fitness_build()

    # --- Agent variety (from mutation state capability matrix if present, else heuristic) ---
    # Heuristic: count unique agent types referenced in mutation state
    agent_refs = set()
    if MUTATION_STATE.exists():
        text = MUTATION_STATE.read_text()
        for match in re.finditer(r"vsm_\w+", text):
            agent_refs.add(match.group(0))
    # 14 custom agent types exist; we count how many are referenced
    known_agents = {
        "vsm_architect", "vsm_auditor", "vsm_backend_coder", "vsm_backend_fix_agent",
        "vsm_backend_tester", "vsm_coordinator", "vsm_devops_coder", "vsm_explore",
        "vsm_frontend_coder", "vsm_frontend_fix_agent", "vsm_frontend_tester",
        "vsm_meta", "vsm_process_auditor", "vsm_product", "vsm_security",
        "vsm_variety_engineer", "vsm_learning_curator", "vsm_synthesizer", "vsm_wiring",
    }
    agent_variety = round(len(agent_refs & known_agents) / len(known_agents), 2)

    # --- Skill variety (heuristic from skill-effectiveness-log) ---
    skill_log = REFS_DIR / "skill-effectiveness-log.md"
    skills_used = 0
    skills_total = 0
    if skill_log.exists():
        text = skill_log.read_text()
        for line in text.splitlines():
            if "|" in line and "pitfalls" in line or "patterns" in line or "migration" in line:
                parts = [p.strip() for p in line.split("|")]
                parts = [p for p in parts if p]
                if len(parts) >= 3 and parts[1].replace(".", "").isdigit():
                    builds_used = int(parts[1])
                    if builds_used > 0:
                        skills_used += 1
                    skills_total += 1
    skill_variety = round(skills_used / skills_total, 2) if skills_total else 0.0

    # --- Temporal variety (unique build domains in last 5 builds) ---
    temporal_variety = 0.6  # Default heuristic; hard to compute without build metadata
    if COACH_DIR.exists():
        dirs = sorted([d for d in COACH_DIR.iterdir() if d.is_dir()], key=lambda d: d.stat().st_mtime, reverse=True)[:5]
        if len(dirs) >= 3:
            temporal_variety = 1.0
        elif len(dirs) >= 2:
            temporal_variety = 0.8
        elif len(dirs) >= 1:
            temporal_variety = 0.6

    # --- Compute variety score ---
    variety_score = compute_variety_score(agent_variety, hypothesis_variety, skill_variety, temporal_variety)

    # --- Algedonic checks ---
    def status(value, warning, critical, mode="gt"):
        if mode == "gt":
            if value > critical:
                return "CRITICAL"
            if value > warning:
                return "WARNING"
        else:
            if value < critical:
                return "CRITICAL"
            if value < warning:
                return "WARNING"
        return "OK"

    checks = [
        ("Probationary mutations", probationary, 12, 18, "gt"),
        ("Untested hypotheses", untested, 7, 10, "gt"),
        ("Score drop", score_drop, 0.2, 0.3, "gt"),
        ("Knowledge broker age", broker_age, 5, 7, "gt"),
        ("Days since last fitness build", days_since_build, 5, 7, "gt"),
        ("Measured effect fill rate", fill_rate, 75, 60, "lt"),
        ("Variety Score", variety_score, 0.70, 0.50, "lt"),
    ]

    algedonics = []
    for name, value, warn, crit, mode in checks:
        st = status(value, warn, crit, mode)
        if st in ("WARNING", "CRITICAL"):
            algedonics.append({
                "name": name,
                "value": value,
                "threshold": crit if st == "CRITICAL" else warn,
                "status": st,
                "mode": mode,
            })

    # --- Build report ---
    lines = [
        "# Organism Vitals — Pre-computed",
        f"**Date**: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M')} UTC",
        f"**Scanner**: scripts/organism-vitals.py",
        "",
        "> This file is auto-generated by `scripts/organism-vitals.py`.",
        "> The vsm_variety_engineer should read this file first, then verify and write `.kimi/variety-assessment.md`.",
        "",
        "## Health Metrics",
        "",
        "| Metric | Value | Threshold | Status |",
        "|---|---|---|---|",
        f"| Probationary mutations | {probationary} | > 12 | {status(probationary, 12, 18, 'gt')} |",
        f"| Untested hypotheses | {untested} | > 7 | {status(untested, 7, 10, 'gt')} |",
        f"| Score drop (last→current) | {score_drop} | > 0.2 | {status(score_drop, 0.2, 0.3, 'gt')} |",
        f"| Knowledge broker age | {broker_age} days | > 5 days | {status(broker_age, 5, 7, 'gt')} |",
        f"| Days since last fitness build | {days_since_build} | > 5 days | {status(days_since_build, 5, 7, 'gt')} |",
        f"| Measured effect fill rate | {fill_rate}% | < 75% | {status(fill_rate, 75, 60, 'lt')} |",
        f"| Variety Score | {variety_score} | < 0.70 | {status(variety_score, 0.70, 0.50, 'lt')} |",
        "",
        "## Portfolio Snapshot",
        f"- **Total mutations tracked**: {total_mutations}",
        f"- **Active mutations**: {active}",
        f"- **Monitor mutations**: {monitor_count}",
        f"- **Removed mutations**: {removed}",
        f"- **Agent variety**: {agent_variety} ({len(agent_refs & known_agents)}/{len(known_agents)} agents referenced)",
        f"- **Skill variety**: {skill_variety} ({skills_used}/{skills_total} skills exercised)",
        f"- **Temporal variety**: {temporal_variety}",
        "",
    ]

    if algedonics:
        lines.extend([
            "## Algedonic Signals",
            "",
        ])
        for a in algedonics:
            blocking = "YES" if a["status"] == "CRITICAL" else "NO"
            lines.extend([
                f"### {a['status']}: {a['name']}",
                f"**Metric**: {a['name']}",
                f"**Current Value**: {a['value']}",
                f"**Threshold**: {a['threshold']}",
                f"**Recommendation**: Address {a['name'].lower()} before proceeding with next build.",
                f"**Blocking**: {blocking}",
                "",
            ])
    else:
        lines.extend([
            "## Algedonic Signals",
            "",
            "✅ All metrics within acceptable thresholds. No algedonic signals triggered.",
            "",
        ])

    # Spot-check guidance for the variety engineer agent
    lines.extend([
        "## Spot-Check Guidance (for vsm_variety_engineer)",
        "",
        "If you are the variety engineer agent, follow this guidance:",
        "- For metrics within thresholds: No spot-check needed. Trust the pre-computed result.",
        "- For WARNING/CRITICAL algedonics: Read the specific source file to add qualitative depth.",
        "",
        "| Algedonic | If triggered, verify this | What to look for |",
        "|---|---|---|",
        "| Probationary mutations | `references/mutation-state.md` | Which mutations are probationary and why |",
        "| Untested hypotheses | `references/hypotheses.md` | Domain distribution of untested hypotheses |",
        "| Score drop | `references/build-health-history.md` | Which phase or agent caused the drop |",
        "| Broker stale | `references/knowledge-broker.md` | Last updated date and content quality |",
        "| Variety deficit | `references/skill-effectiveness-log.md` | Which skills are unused |",
        "",
        "**Limit**: Maximum 3 spot-checks. If more than 3 algedonics triggered, verify the 3 most severe.",
        "",
    ])

    lines.extend([
        "## Proactive Recommendations",
        "",
    ])

    if probationary > 12:
        lines.append(f"1. **Mutation consolidation needed**: {probationary} probationary mutations exceed threshold. Trigger portfolio review.")
    if untested > 7:
        lines.append(f"2. **Gym batch needed**: {untested} untested hypotheses. Run vsm-fitness-gym to validate backlog.")
    if broker_age > 5:
        lines.append(f"3. **Broker update needed**: Knowledge broker is {broker_age} days stale. Run auto-broker-update.sh.")
    if variety_score < 0.70:
        lines.append(f"4. **Variety deficit**: Score {variety_score} < 0.70. Consider spawning underutilized agents or running gym experiments.")
    if not any([probationary > 12, untested > 7, broker_age > 5, variety_score < 0.70]):
        lines.append("1. No proactive actions required. Organism health is stable.")

    lines.append("")

    report_text = "\n".join(lines)

    if args.build_dir:
        build_path = Path(args.build_dir)
        out_path = build_path / ".kimi" / "organism-vitals.md"
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(report_text)

    print(report_text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
