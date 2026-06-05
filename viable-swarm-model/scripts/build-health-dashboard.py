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


def extract_score_from_build(build_dir: Path) -> float | None:
    """Extract build score from meta-report.md or fitness-report.md.
    Supports both /5.0 and /100 formats; normalizes /100 to /5.0 scale."""
    for report_name in ("meta-report.md", "fitness-report.md"):
        path = build_dir / ".kimi" / report_name
        if not path.exists():
            continue
        text = path.read_text()
        # Prefer /5.0 format
        match = re.search(r"([0-9]+(?:\.[0-9]+)?)\s*/\s*5\.0", text)
        if match:
            return float(match.group(1))
        # Fallback to /100 format (fitness-coach scores)
        match = re.search(r"([0-9]+(?:\.[0-9]+)?)\s*/\s*100", text)
        if match:
            return round(float(match.group(1)) / 20, 2)
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
    """Count BLOCKER findings from audit reports.
    Counts markdown section headings (### ... BLOCKER) rather than all
    string occurrences, which over-counts table cells and summaries."""
    count = 0
    for audit_file in [
        "foundation-audit.md",
        "implementation-audit.md",
        "re-audit-report.md",
        "security-audit.md",
        "security-report.md",
    ]:
        audit_path = path / ".kimi" / audit_file
        if audit_path.exists():
            text = audit_path.read_text()
            # Count headings like "### BLOCKER" or "### `file.py` — BLOCKER"
            # Exclude summary lines like "BLOCKER count": and "## BLOCKER Details"
            headings = re.findall(r"^#{1,3}\s+.*\bBLOCKER\b.*$", text, re.MULTILINE)
            # Filter out "BLOCKER Details" and "BLOCKER count" summary headings
            for h in headings:
                if re.search(r"BLOCKER\s+(?:Details|count)", h, re.IGNORECASE):
                    continue
                count += 1
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

        score = extract_score_from_build(fb_dir)
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
    removed = len(re.findall(r"\|\s*removed\s*\|", text, re.IGNORECASE))

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
    # Strip markdown bold markers to handle **Status**: untested
    clean_text = re.sub(r'\*+', '', text)
    untested = len(re.findall(r"Status:\s*untested", clean_text, re.IGNORECASE))

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


def predict_next_score(scores: list[float | None]) -> tuple[float | None, str]:
    """Simple linear regression on last 5 scores. Returns (prediction, alert_level)."""
    clean = [v for v in scores if v is not None]
    if len(clean) < 3:
        return None, "insufficient_data"
    n = len(clean)
    x_mean = sum(range(n)) / n
    y_mean = sum(clean) / n
    numerator = sum((i - x_mean) * (clean[i] - y_mean) for i in range(n))
    denominator = sum((i - x_mean) ** 2 for i in range(n))
    slope = numerator / denominator if denominator != 0 else 0
    intercept = y_mean - slope * x_mean
    prediction = intercept + slope * n
    prediction = max(0.0, min(5.0, prediction))
    if prediction < 3.0:
        return round(prediction, 2), "CRITICAL"
    elif prediction < 3.5:
        return round(prediction, 2), "WARNING"
    else:
        return round(prediction, 2), "OK"


def get_agent_risk_assessment() -> list[dict]:
    """Read capability matrix from mutation-state.md and flag high-risk agents."""
    mutation_state = REFS_DIR / "mutation-state.md"
    if not mutation_state.exists():
        return []
    text = mutation_state.read_text()
    risks = []
    # Find capability matrix section
    matrix_match = re.search(
        r"\| Agent \| Domain \| Success Rate \|.*?\n\|[-\s|]+\|\n(.*?)\n\n",
        text,
        re.DOTALL,
    )
    if matrix_match:
        for line in matrix_match.group(1).strip().split("\n"):
            if line.startswith("|") and "Success Rate" not in line and "---" not in line:
                parts = [p.strip() for p in line.split("|")]
                parts = [p for p in parts if p]
                if len(parts) >= 4:
                    agent = parts[0]
                    rate_str = parts[2].replace("%", "").strip()
                    try:
                        rate = float(rate_str)
                    except ValueError:
                        continue
                    if rate < 60:
                        max_lines = 200
                        risk_level = "CRITICAL"
                    elif rate < 70:
                        max_lines = 300
                        risk_level = "HIGH"
                    elif rate < 80:
                        max_lines = 400
                        risk_level = "MEDIUM"
                    else:
                        max_lines = 500
                        risk_level = "LOW"
                    risks.append({
                        "agent": agent,
                        "success_rate": rate,
                        "risk_level": risk_level,
                        "recommended_max_lines": max_lines,
                    })
    return risks


def compute_process_drift(builds: list[dict]) -> dict | None:
    """Compare latest process score to rolling average of last 5."""
    process_scores = [b["process"] for b in builds if b["process"] is not None]
    if len(process_scores) < 2:
        return None
    latest = process_scores[-1]
    rolling = process_scores[-5:-1] if len(process_scores) >= 5 else process_scores[:-1]
    avg = sum(rolling) / len(rolling)
    delta = avg - latest
    if delta > 10:
        alert = "CRITICAL"
    elif delta > 5:
        alert = "WARNING"
    else:
        alert = "OK"
    return {"latest": latest, "rolling_avg": round(avg, 1), "delta": round(delta, 1), "alert": alert}


def compute_mutation_bloat_velocity() -> dict | None:
    """Track new mutations vs removals per 5-build window."""
    mutation_log = REFS_DIR / "mutation-log.md"
    if not mutation_log.exists():
        return None
    text = mutation_log.read_text()
    # Count mutations added in last 5 builds (rough: mutations with build IDs from last 5 FBs)
    # This is approximate — we count all un-removed mutations as "active"
    mutation_state = REFS_DIR / "mutation-state.md"
    if not mutation_state.exists():
        return None
    state_text = mutation_state.read_text()
    total = len(re.findall(r"\|\s*probation\s*\|", state_text))
    total += len(re.findall(r"\|\s*effective\s*\|", state_text))
    total += len(re.findall(r"\|\s*monitor\s*\|", state_text))
    removed = len(re.findall(r"\*\*REMOVED\*\*", state_text))
    # Approximate velocity: if total growing faster than removed
    ratio = total / max(removed, 1)
    if ratio > 4:
        alert = "CRITICAL"
    elif ratio > 2:
        alert = "WARNING"
    else:
        alert = "OK"
    return {"total_active": total, "removed": removed, "ratio": round(ratio, 1), "alert": alert}


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

    # Predictive sections
    prediction, pred_alert = predict_next_score(scores)
    agent_risks = get_agent_risk_assessment()
    process_drift = compute_process_drift(builds)
    bloat = compute_mutation_bloat_velocity()

    lines.extend([
        "",
        "## Predictive Alerts",
    ])
    if prediction is not None:
        lines.append(f"| Predicted Next Score | {prediction}/5.0 | Alert: {pred_alert} |")
    if process_drift:
        lines.append(f"| Process Drift | Latest: {process_drift['latest']}, Rolling Avg: {process_drift['rolling_avg']}, Delta: {process_drift['delta']} | Alert: {process_drift['alert']} |")
    if bloat:
        lines.append(f"| Mutation Bloat | Active: {bloat['total_active']}, Removed: {bloat['removed']}, Ratio: {bloat['ratio']} | Alert: {bloat['alert']} |")
    if agent_risks:
        lines.append("")
        lines.append("### Agent Risk Assessment")
        lines.append("| Agent | Success Rate | Risk | Recommended Max Lines |")
        lines.append("|-------|-------------|------|----------------------|")
        for r in agent_risks:
            lines.append(f"| {r['agent']} | {r['success_rate']}% | {r['risk_level']} | {r['recommended_max_lines']} |")

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

    # Guard: refuse to run outside a valid build directory
    has_plan = (build_dir / "plan.md").exists()
    has_fb_id = re.search(r"FB\d+", str(build_dir)) is not None
    if not has_plan and not has_fb_id:
        print("ERROR: Not a valid build directory (no plan.md, no FB* in path).")
        print("Usage: python3 build-health-dashboard.py <build-directory>")
        sys.exit(1)

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
