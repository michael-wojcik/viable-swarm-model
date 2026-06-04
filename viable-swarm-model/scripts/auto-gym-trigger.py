#!/usr/bin/env python3
"""
Auto-Gym Trigger

Automatically trigger gym experiments when:
1. The hypothesis backlog grows beyond 10 untested hypotheses AND
   no gym experiment has run in the last 7 days.
2. Any monitor-status mutation has Builds Tested >= 3.

Reads:
  - ~/vsm/viable-swarm-model/references/hypotheses.md
  - ~/vsm/viable-swarm-model/references/mutation-state.md
  - ~/vsm-fitness-builds/gym/ (directory mtime for last experiment)

Writes:
  - ~/vsm/viable-swarm-model/.kimi/auto-gym-trigger.md
"""

from __future__ import annotations

import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
HOME = Path.home()
HYPOTHESES_PATH = HOME / "vsm" / "viable-swarm-model" / "references" / "hypotheses.md"
MUTATION_STATE_PATH = HOME / "vsm" / "viable-swarm-model" / "references" / "mutation-state.md"
GYM_DIR = HOME / "vsm-fitness-builds" / "gym"
OUTPUT_PATH = HOME / "vsm" / "viable-swarm-model" / ".kimi" / "auto-gym-trigger.md"

HYPOTHESIS_BACKLOG_THRESHOLD = 10
GYM_COOLDOWN_DAYS = 7
MONITOR_BUILDS_TESTED_THRESHOLD = 3


def eprint(msg: str) -> None:
    print(msg, file=sys.stderr)


# ---------------------------------------------------------------------------
# Hypothesis parsing
# ---------------------------------------------------------------------------

def parse_hypotheses(path: Path) -> list[dict]:
    """Parse hypotheses.md and return a list of untested hypothesis dicts."""
    if not path.exists():
        eprint(f"WARNING: {path} not found; returning empty hypothesis list.")
        return []

    text = path.read_text(encoding="utf-8")
    hypotheses = []

    # Each main hypothesis section starts with ## H<identifier>: <claim>
    # Update subsections start with ### and should be ignored for counting.
    sections = re.split(r"\n## ", text)
    for section in sections:
        # Skip table-of-contents lines and update subsections
        if not section.strip() or section.startswith("# "):
            continue
        header_match = re.match(r"(H[\w+\-]+)\s*:\s*(.+)", section.strip(), re.IGNORECASE)
        if not header_match:
            continue

        hid = header_match.group(1).strip()
        claim = header_match.group(2).strip()

        status_match = re.search(r"\*\*Status\*\*\s*:\s*(\S+)", section, re.IGNORECASE)
        status = status_match.group(1).lower() if status_match else "unknown"

        if status not in ("untested", "testing"):
            continue

        proposed_match = re.search(r"\*\*Proposed\*\*\s*:\s*(\d{4}-\d{2}-\d{2})", section)
        proposed_str = proposed_match.group(1) if proposed_match else None

        # Extract experiment design (first paragraph after **Experiment**)
        experiment_match = re.search(
            r"\*\*Experiment\*\*\s*:\s*(.+?)(?:\n\n|\n\*\*)", section, re.DOTALL
        )
        experiment = experiment_match.group(1).strip().replace("\n", " ") if experiment_match else ""

        hypotheses.append({
            "id": hid,
            "claim": claim,
            "status": status,
            "proposed": proposed_str,
            "experiment": experiment,
            "confidence": None,  # populated later via cross-reference
            "priority": None,
        })

    # Apply status updates from `### H[ID] Update` subsections anywhere in the file.
    # The final status is the right-hand side of `→` if present, else the single value.
    update_pattern = re.compile(
        r"###\s*(H[\w+\-]+)\s*Update.*?\*\*Status\*\*\s*:\s*(.+?)(?:\n\n|\n## |\n### |$)",
        re.DOTALL | re.IGNORECASE,
    )
    for m in update_pattern.finditer(text):
        hid = m.group(1).strip()
        status_line = m.group(2).strip().lower()
        # Handle "testing → monitor" format: take the final status
        if "→" in status_line:
            status_line = status_line.split("→")[-1].strip()
        for h in hypotheses:
            if h["id"] == hid:
                h["status"] = status_line
                break

    # Filter out any that are no longer untested/testing after updates
    hypotheses = [h for h in hypotheses if h["status"] in ("untested", "testing")]

    return hypotheses


def cross_reference_confidence(hypotheses: list[dict], mutation_state_path: Path) -> None:
    """Cross-reference mutation-state.md Known Unknowns table for confidence/priority."""
    if not mutation_state_path.exists():
        eprint(f"WARNING: {mutation_state_path} not found; skipping confidence cross-reference.")
        return

    text = mutation_state_path.read_text(encoding="utf-8")

    # Known Unknowns table columns: Hypothesis | Confidence | Last Tested | Priority | Status
    in_table = False
    for line in text.splitlines():
        if "| Hypothesis | Confidence |" in line:
            in_table = True
            continue
        if in_table:
            if not line.startswith("|"):
                break
            if line.strip().startswith("|---|"):
                continue
            parts = [p.strip() for p in line.split("|")]
            parts = [p for p in parts if p]
            if len(parts) >= 4:
                hypo_text = parts[0]
                confidence = parts[1]
                priority = parts[3] if len(parts) > 3 else ""
                # Extract ID like H150 from "H150: ..."
                m = re.match(r"(H[\w+\-]+)", hypo_text)
                if m:
                    hid = m.group(1)
                    for h in hypotheses:
                        if h["id"] == hid:
                            h["confidence"] = confidence
                            h["priority"] = priority
                            break

    # Fallback: scan hypothesis text itself for priority keywords
    for h in hypotheses:
        if h["priority"]:
            continue
        # Check if the claim or experiment mentions priority
        combined = f"{h['claim']} {h.get('experiment', '')}".lower()
        if "critical" in combined:
            h["priority"] = "CRITICAL"
        elif "high" in combined:
            h["priority"] = "HIGH"
        elif "low" in combined:
            h["priority"] = "LOW"
        else:
            h["priority"] = "MEDIUM"
        h["confidence"] = h["priority"]  # mirror priority as confidence if unknown


# ---------------------------------------------------------------------------
# Mutation-state parsing
# ---------------------------------------------------------------------------

def parse_monitor_mutations(path: Path) -> list[dict]:
    """Return monitor-status mutations with Builds Tested >= threshold."""
    if not path.exists():
        eprint(f"WARNING: {path} not found; returning empty mutation list.")
        return []

    text = path.read_text(encoding="utf-8")
    mutations = []

    # Master table and subsequent build tables share the same schema.
    # Look for rows where Status contains 'monitor' (case-insensitive) and
    # Builds Tested is a digit >= threshold.
    for line in text.splitlines():
        if not line.strip().startswith("|"):
            continue
        parts = [p.strip() for p in line.split("|")]
        parts = [p for p in parts if p]
        if len(parts) < 6:
            continue
        # Skip header / separator rows
        if parts[0].lower() in ("id", "**id**", "---") or "---" in parts[0]:
            continue

        status = parts[4].lower().strip("*")
        builds_tested_str = parts[5].strip("*")
        try:
            builds_tested = int(builds_tested_str)
        except ValueError:
            continue

        if "monitor" in status and builds_tested >= MONITOR_BUILDS_TESTED_THRESHOLD:
            mutations.append({
                "id": parts[0].strip("*~"),
                "source": parts[1],
                "type": parts[2],
                "target_failure": parts[3],
                "status": status,
                "builds_tested": builds_tested,
                "score": parts[6] if len(parts) > 6 else "—",
            })

    return mutations


# ---------------------------------------------------------------------------
# Gym directory date check
# ---------------------------------------------------------------------------

def days_since_last_gym_experiment(gym_dir: Path) -> float | None:
    """Return days since the most recently modified subdirectory in gym_dir."""
    if not gym_dir.exists():
        eprint(f"WARNING: {gym_dir} not found; assuming no recent experiments.")
        return None

    latest_mtime: float | None = None
    for entry in gym_dir.iterdir():
        if entry.is_dir():
            mtime = entry.stat().st_mtime
            if latest_mtime is None or mtime > latest_mtime:
                latest_mtime = mtime

    if latest_mtime is None:
        return None

    now = datetime.now(timezone.utc).timestamp()
    return (now - latest_mtime) / 86400.0


# ---------------------------------------------------------------------------
# Prioritization
# ---------------------------------------------------------------------------

def priority_rank(p: str) -> int:
    mapping = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
    return mapping.get((p or "").upper(), 2)


def compute_age_days(proposed_str: str | None) -> int:
    if not proposed_str:
        return 0
    try:
        proposed = datetime.strptime(proposed_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    except ValueError:
        return 0
    now = datetime.now(timezone.utc)
    return max(0, (now - proposed).days)


def select_top_hypotheses(hypotheses: list[dict], n: int = 3) -> list[dict]:
    """Select top N by priority rank descending, then age descending."""
    for h in hypotheses:
        h["age_days"] = compute_age_days(h.get("proposed"))

    sorted_h = sorted(
        hypotheses,
        key=lambda h: (priority_rank(h.get("priority") or h.get("confidence")), -h["age_days"]),
    )
    return sorted_h[:n]


# ---------------------------------------------------------------------------
# Output generation
# ---------------------------------------------------------------------------

def build_report(
    trigger_reason: str,
    hypotheses: list[dict],
    monitor_mutations: list[dict],
) -> str:
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    lines = [
        "# Auto-Gym Trigger",
        f"**Date**: {today}",
        f"**Reason**: {trigger_reason}",
        "",
        "## Recommended Hypotheses",
        "| Priority | ID | Claim | Confidence | Age (days) |",
        "|----------|----|-------|------------|------------|",
    ]
    for h in hypotheses:
        claim = h['claim'].replace('|', '\\|')
        lines.append(
            f"| {h.get('priority', 'MEDIUM')} | {h['id']} | {claim} | "
            f"{h.get('confidence', '—')} | {h['age_days']} |"
        )

    lines.extend(["", "## Suggested Experiments"])
    for i, h in enumerate(hypotheses, 1):
        design = h.get("experiment", "")
        if not design:
            design = "Run a minimal reproduction to verify the claim."
        # Truncate very long designs
        if len(design) > 200:
            design = design[:197] + "..."
        lines.append(f"{i}. **{h['id']}**: {design}")

    ids = ", ".join(h["id"] for h in hypotheses)
    lines.extend([
        "",
        "## Recommended Invocation",
        f"/flow:vsm-fitness-gym Test {ids}",
    ])

    if monitor_mutations:
        lines.extend([
            "",
            "## Monitor Mutations Requiring Experiments",
            "| Mutation ID | Target Failure | Builds Tested | Score |",
            "|-------------|----------------|---------------|-------|",
        ])
        for m in monitor_mutations:
            tf = m['target_failure'].replace('|', '\\|')
            lines.append(
                f"| {m['id']} | {tf} | {m['builds_tested']} | {m['score']} |"
            )
        mut_ids = ", ".join(m["id"] for m in monitor_mutations)
        lines.append(f"\n**Suggested**: /flow:vsm-fitness-gym Evaluate mutations {mut_ids}")

    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    eprint("[auto-gym-trigger] Starting analysis...")

    hypotheses = parse_hypotheses(HYPOTHESES_PATH)
    eprint(f"[auto-gym-trigger] Found {len(hypotheses)} untested hypotheses.")

    cross_reference_confidence(hypotheses, MUTATION_STATE_PATH)

    monitor_mutations = parse_monitor_mutations(MUTATION_STATE_PATH)
    eprint(f"[auto-gym-trigger] Found {len(monitor_mutations)} monitor mutations with >= {MONITOR_BUILDS_TESTED_THRESHOLD} builds tested.")

    days_since = days_since_last_gym_experiment(GYM_DIR)
    if days_since is not None:
        eprint(f"[auto-gym-trigger] Days since last gym experiment: {days_since:.1f}")
    else:
        eprint("[auto-gym-trigger] No gym experiment directories found.")

    triggered = False
    reasons: list[str] = []

    if len(hypotheses) > HYPOTHESIS_BACKLOG_THRESHOLD:
        if days_since is None or days_since > GYM_COOLDOWN_DAYS:
            triggered = True
            reasons.append("hypothesis backlog")
        else:
            eprint(f"[auto-gym-trigger] Hypothesis backlog > {HYPOTHESIS_BACKLOG_THRESHOLD} but gym ran recently ({days_since:.1f} days ago); not triggering.")

    if monitor_mutations:
        triggered = True
        reasons.append("monitor mutations")

    if not triggered:
        eprint("[auto-gym-trigger] No trigger conditions met. Exiting without writing report.")
        return 0

    top_hypotheses = select_top_hypotheses(hypotheses, n=3)
    reason_str = " + ".join(reasons) if len(reasons) > 1 else reasons[0]

    report = build_report(reason_str, top_hypotheses, monitor_mutations)

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(report, encoding="utf-8")
    eprint(f"[auto-gym-trigger] Wrote trigger report to {OUTPUT_PATH}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
