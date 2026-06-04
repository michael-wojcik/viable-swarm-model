#!/usr/bin/env python3
"""
Build Health Dashboard — Unified organism health metrics

Computes longitudinal health metrics across fitness builds and writes:
- .kimi/health-dashboard.md (per-build snapshot)
- references/build-health-history.md (append-only longitudinal record)

Usage: python3 build-health-dashboard.py <build-directory>
"""

import os
import sys
import re
import glob
from datetime import datetime, timedelta
from pathlib import Path
from collections import Counter

VSM_ROOT = Path.home() / "vsm" / "viable-swarm-model"
COACH_DIR = Path.home() / "vsm-fitness-builds" / "coach"
GYM_DIR = Path.home() / "vsm-fitness-builds" / "gym"
REFS_DIR = VSM_ROOT / "references"


def extract_score_from_meta_report(path: Path) -> float | None:
    """Extract trainer score (e.g., 4.2/5.0) from meta-report."""
    if not path.exists():
        return None
    text = path.read_text()
    match = re.search(r"([0-9]+\.[0-9]+)\s*/\s*5\.0", text)
    if match:
        return float(match.group(1))
    return None


def extract_process_score(path: Path) -> int | None:
    """Extract process audit score (e.g., 85/100) from process-audit."""
    if not path.exists():
        return None
    text = path.read_text()
    match = re.search(r"([0-9]+)\s*/\s*100", text)
    if match:
        return int(match.group(1))
    return None


def extract_timeout_count(path: Path) -> int:
    """Count agent timeouts from plan.md."""
    if not path.exists():
        return 0
    text = path.read_text()
    matches = re.findall(r"\| Phase \d+ \| \d+ \| (\d+) \|", text)
    return sum(int(m) for m in matches)


def extract_blocker_count(path: Path) -> int:
    """Count BLOCKERs from audit reports."""
    count = 0
    for audit_file in ["foundation-audit.md", "implementation-audit.md", "re-audit-report.md"]:
        audit_path = path / ".kimi" / audit_file
        if audit_path.exists():
            text = audit_path.read_text()
            count += len(re.findall(r"BLOCKER", text))
    return count


def extract_algedonic_stats(build_dir: Path) -> tuple[int, int]:
    """Extract (heeded, ignored) algedonic counts from lessons.md."""
    lessons_path = build_dir / ".kimi" / "lessons.md"
    if not lessons_path.exists():
        return 0, 0
    text = lessons_path.read_text()
    heeded = len(re.findall(r"algedonic.*heeded|heeded.*algedonic", text, re.IGNORECASE))
    ignored = len(re.findall(r"algedonic.*ignored|ignored.*algedonic", text, re.IGNORECASE))
    return heeded, ignored


def get_build_scores(limit: int = 10) -> list[dict]:
    """Collect scores from last N fitness builds."""
    builds = []
    if not COACH_DIR.exists():
        return builds

    # Find all FB directories
    fb_dirs = sorted(
        [d for d in COACH_DIR.iterdir() if d.is_dir() and re.match(r"FB\d+", d.name)],
        key=lambda d: int(re.search(r"FB(\d+)", d.name).group(1)),
        reverse=True
    )

    for fb_dir in fb_dirs[:limit]:
        build_num = int(re.search(r"FB(\d+)", fb_dir.name).group(1))
        meta_report = fb_dir / ".kimi" / "meta-report.md"
        process_audit = fb_dir / ".kimi" / "process-audit.md"
        plan_md = fb_dir / "plan.md"

        score = extract_score_from_meta_report(meta_report)
        process_score = extract_process_score(process_audit)
        timeouts = extract_timeout_count(plan_md)
        blockers = extract_blocker_count(fb_dir)
        heeded, ignored = extract_algedonic_stats(fb_dir)

        builds.append({
            "id": f"FB{build_num}",
            "score": score,
            "process": process_score,
            "timeouts": timeouts,
            "blockers": blockers,
            "algedonic_heeded": heeded,
            "algedonic_ignored": ignored,
        })

    return list(reversed(builds))  # chronological order


def get_mutation_metrics() -> dict:
    """Extract metrics from mutation-state.md."""
    mutation_state = REFS_DIR / "mutation-state.md"
    if not mutation_state.exists():
        return {}

    text = mutation_state.read_text()

    # Count statuses
    probation = len(re.findall(r"\|\s*probation\s*\|", text))
    effective = len(re.findall(r"\|\s*effective\s*\|", text))
    monitor = len(re.findall(r"\|\s*monitor\s*\|", text))
    ineffective = len(re.findall(r"\|\s*ineffective\s*\|", text))
    removed = len(re.findall(r"\|\s*removed\s*\|", text))

    total = probation + effective + monitor + ineffective
    fill_rate = 0  # Would need deeper parsing

    return {
        "total_active": total,
        "probationary": probation,
        "effective": effective,
        "monitor": monitor,
        "ineffective": ineffective,
        "removed": removed,
        "probationary_ratio": round(probation / total * 100, 1) if total > 0 else 0,
    }


def get_hypothesis_backlog() -> dict:
    """Count untested hypotheses and their age."""
    hypotheses = REFS_DIR / "hypotheses.md"
    if not hypotheses.exists():
        return {"untested": 0, "critical_age": 0}

    text = hypotheses.read_text()
    untested = len(re.findall(r"status:\s*untested", text, re.IGNORECASE))

    # Count hypotheses older than 30 days (rough estimate from dates in file)
    dates = re.findall(r"Proposed:\s*(\d{4}-\d{2}-\d{2})", text)
    old_count = 0
    today = datetime.now()
    for date_str in dates:
        try:
            proposed = datetime.strptime(date_str, "%Y-%m-%d")
            if (today - proposed).days > 30:
                old_count += 1
        except ValueError:
            continue

    return {"untested": untested, "critical_age": old_count}


def get_broker_staleness() -> int:
    """Days since knowledge broker was updated."""
    broker = REFS_DIR / "knowledge-broker.md"
    if not broker.exists():
        return 999

    text = broker.read_text()
    match = re.search(r"Last updated.*?(\d{4}-\d{2}-\d{2})", text)
    if match:
        last_update = datetime.strptime(match.group(1), "%Y-%m-%d")
        return (datetime.now() - last_update).days
    return 999


def compute_trend(values: list[float | None]) -> str:
    """Compute trend direction from a series of values."""
    clean = [v for v in values if v is not None]
    if len(clean) < 2:
        return "stable"
    if clean[-1] > clean[-2] + 0.15:
        return "improving"
    if clean[-1] < clean[-2] - 0.15:
        return "declining"
    return "stable"


def generate_dashboard(builds: list[dict], mutation_metrics: dict, hypothesis_metrics: dict, broker_days: int) -> str:
    """Generate the health dashboard markdown."""
    scores = [b["score"] for b in builds if b["score"] is not None]
    process_scores = [b["process"] for b in builds if b["process"] is not None]
    total_timeouts = sum(b["timeouts"] for b in builds)
    total_blockers = sum(b["blockers"] for b in builds)
    total_heeded = sum(b["algedonic_heeded"] for b in builds)
    total_ignored = sum(b["algedonic_ignored"] for b in builds)

    score_trend = compute_trend(scores)
    latest_score = scores[-1] if scores else "N/A"
    avg_score = round(sum(scores) / len(scores), 2) if scores else "N/A"
    avg_process = round(sum(process_scores) / len(process_scores), 1) if process_scores else "N/A"

    lines = [
        "# Build Health Dashboard",
        f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        f"**Builds Analyzed**: {len(builds)}",
        "",
        "## Score Trend",
        f"| Latest | Average | Trend |",
        f"|--------|---------|-------|",
        f"| {latest_score} | {avg_score} | {score_trend} |",
        "",
        "## Build History",
        "| Build | Score | Process | Timeouts | Blockers | Algedonic |",
        "|-------|-------|---------|----------|----------|-----------|",
    ]

    for b in builds:
        score_str = f"{b['score']:.1f}" if b["score"] is not None else "N/A"
        process_str = f"{b['process']}" if b["process"] is not None else "N/A"
        algedonic_str = f"{b['algedonic_heeded']}h/{b['algedonic_ignored']}i"
        lines.append(f"| {b['id']} | {score_str} | {process_str} | {b['timeouts']} | {b['blockers']} | {algedonic_str} |")

    lines.extend([
        "",
        "## Mutation Portfolio Health",
        f"| Metric | Value | Target | Status |",
        f"|--------|-------|--------|--------|",
        f"| Total active | {mutation_metrics.get('total_active', 'N/A')} | < 50 | {'OK' if mutation_metrics.get('total_active', 999) < 50 else 'WARNING'} |",
        f"| Probationary ratio | {mutation_metrics.get('probationary_ratio', 'N/A')}% | < 30% | {'OK' if mutation_metrics.get('probationary_ratio', 999) < 30 else 'WARNING'} |",
        f"| Ineffective count | {mutation_metrics.get('ineffective', 'N/A')} | < 5 | {'OK' if mutation_metrics.get('ineffective', 999) < 5 else 'WARNING'} |",
        "",
        "## Hypothesis Backlog",
        f"| Metric | Value | Threshold | Status |",
        f"|--------|-------|-----------|--------|",
        f"| Untested hypotheses | {hypothesis_metrics.get('untested', 'N/A')} | < 10 | {'OK' if hypothesis_metrics.get('untested', 999) < 10 else 'WARNING'} |",
        f"| >30 days old | {hypothesis_metrics.get('critical_age', 'N/A')} | < 5 | {'OK' if hypothesis_metrics.get('critical_age', 999) < 5 else 'WARNING'} |",
        "",
        "## Cross-Skill Health",
        f"| Metric | Value | Threshold | Status |",
        f"|--------|-------|-----------|--------|",
        f"| Knowledge broker staleness | {broker_days} days | < 7 days | {'OK' if broker_days < 7 else 'WARNING'} |",
        f"| Total timeouts (last {len(builds)} builds) | {total_timeouts} | < 5 | {'OK' if total_timeouts < 5 else 'WARNING'} |",
        f"| Total blockers (last {len(builds)} builds) | {total_blockers} | < 10 | {'OK' if total_blockers < 10 else 'WARNING'} |",
        f"| Algedonic heeded/ignored | {total_heeded}/{total_ignored} | — | {'OK' if total_ignored == 0 else 'WARNING'} |",
        "",
        "---",
        "*Auto-generated by build-health-dashboard.py*",
    ])

    return "\n".join(lines)


def main():
    build_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")
    kimi_dir = build_dir / ".kimi"
    kimi_dir.mkdir(parents=True, exist_ok=True)

    # Collect metrics
    builds = get_build_scores(limit=10)
    mutation_metrics = get_mutation_metrics()
    hypothesis_metrics = get_hypothesis_backlog()
    broker_days = get_broker_staleness()

    # Generate dashboard
    dashboard = generate_dashboard(builds, mutation_metrics, hypothesis_metrics, broker_days)

    # Write per-build dashboard
    dashboard_path = kimi_dir / "health-dashboard.md"
    dashboard_path.write_text(dashboard)
    print(f"Wrote: {dashboard_path}")

    # Append to longitudinal history
    history_path = REFS_DIR / "build-health-history.md"
    history_path.parent.mkdir(parents=True, exist_ok=True)

    # Add header if new file
    if not history_path.exists():
        history_path.write_text("# Build Health History\n\n> Longitudinal health metrics across all fitness builds.\n> **Updated by**: build-health-dashboard.py\n\n")

    # Append snapshot
    build_id = re.search(r"FB\d+", str(build_dir))
    build_id = build_id.group(0) if build_id else "UNKNOWN"
    snapshot = f"\n## {build_id} — {datetime.now().strftime('%Y-%m-%d')}\n\n"
    snapshot += f"- Score: {[b['score'] for b in builds if b['id'] == build_id][0] if any(b['id'] == build_id for b in builds) else 'N/A'}\n"
    snapshot += f"- Process: {[b['process'] for b in builds if b['id'] == build_id][0] if any(b['id'] == build_id for b in builds) else 'N/A'}\n"
    snapshot += f"- Mutations active: {mutation_metrics.get('total_active', 'N/A')}\n"
    snapshot += f"- Hypotheses untested: {hypothesis_metrics.get('untested', 'N/A')}\n"
    snapshot += f"- Broker staleness: {broker_days} days\n"

    with history_path.open("a") as f:
        f.write(snapshot)

    print(f"Appended to: {history_path}")
    print("OK: Dashboard generation complete")


if __name__ == "__main__":
    main()
