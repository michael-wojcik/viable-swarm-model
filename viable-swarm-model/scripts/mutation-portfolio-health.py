#!/usr/bin/env python3
"""
Mutation Portfolio Health — Pre-computation script for S5* Learning Curator.

Reads references/mutation-state.md and computes portfolio health metrics.
Outputs structured JSON that vsm_learning_curator can consume directly,
reducing its task from "read + parse + compute" to "read + review + decide".

Usage:
    python3 mutation-portfolio-health.py [--build-dir <dir>]

If --build-dir is provided, writes:
    <build-dir>/.kimi/mutation-portfolio-health.json
    <build-dir>/.kimi/mutation-portfolio-health.md   (human-readable summary)

Always prints JSON to stdout.
"""

import argparse
import json
import re
import sys
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Optional

VSM_ROOT = Path.home() / "vsm" / "viable-swarm-model"
DEFAULT_MUTATION_STATE = VSM_ROOT / "references" / "mutation-state.md"


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


@dataclass
class PortfolioHealth:
    total_active: int
    probationary_count: int
    probationary_ratio: float
    effective_count: int
    monitor_count: int
    ineffective_count: int
    removed_count: int
    historical_effective_count: int
    measured_fill_rate_scored: float
    measured_fill_rate_any: float
    promotions_ready: list
    demotions_ready: list
    monitor_promotions_ready: list
    monitor_removals_ready: list
    historical_promotions_ready: list
    consolidations_suggested: list
    removal_rate_last_5: int
    data_integrity_errors: list
    computed_at: str


def parse_mutation_state(path: Path) -> tuple[list[MutationRow], list[str]]:
    """Parse the master mutation table from mutation-state.md.

    The file may contain multiple table blocks separated by section headers.
    Schema v2.0 allows rows to be updated in place; we deduplicate by ID,
    keeping the last occurrence.
    """
    rows: list[MutationRow] = []
    errors: list[str] = []

    if not path.exists():
        errors.append(f"mutation-state.md not found at {path}")
        return rows, errors

    text = path.read_text()
    lines = text.splitlines()

    for line in lines:
        stripped = line.strip()

        # Skip divider rows, blank lines, and non-table lines
        if not stripped.startswith("|") or stripped.startswith("|---|"):
            continue

        parts = [p.strip() for p in line.split("|")]
        parts = [p for p in parts if p]
        if len(parts) < 6:
            continue

        # Skip header rows and section labels
        if parts[0].startswith("**") or parts[0] == "ID":
            continue

        # Skip rows where Source column is empty or a header label
        if parts[1] in ("Source", "", "—"):
            continue

        # Clean strikethrough IDs: ~~FB28-S5~~ → FB28-S5
        raw_id = parts[0]
        clean_id = re.sub(r"^~~(.+)~~$", r"\1", raw_id)

        # Parse builds tested
        builds_raw = parts[5] if len(parts) > 5 else "0"
        try:
            builds_tested = int(builds_raw) if builds_raw not in ("", "—") else 0
        except ValueError:
            builds_tested = 0

        # Parse score
        score_raw = parts[6] if len(parts) > 6 else ""
        score: Optional[int] = None
        if score_raw and score_raw not in ("—", ""):
            try:
                score = int(score_raw)
            except ValueError:
                pass

        # Parse status — handle **REMOVED** and **REDESIGNED** formatting
        status_raw = parts[4].lower() if len(parts) > 4 else ""
        status_raw = re.sub(r"\*\*", "", status_raw).strip()

        row = MutationRow(
            id=clean_id,
            source=parts[1],
            type=parts[2] if len(parts) > 2 else "",
            target_failure=parts[3] if len(parts) > 3 else "",
            status=status_raw,
            builds_tested=builds_tested,
            score=score,
            hypothesis=parts[7] if len(parts) > 7 else "",
            experiment=parts[8] if len(parts) > 8 else "",
            next_review=parts[9] if len(parts) > 9 else "",
        )
        rows.append(row)

    # Deduplicate by ID (keep last occurrence — Schema v2.0 updates rows in place)
    seen: dict[str, MutationRow] = {}
    for row in rows:
        seen[row.id] = row
    rows = list(seen.values())

    return rows, errors


def compute_portfolio_health(rows: list[MutationRow]) -> PortfolioHealth:
    from datetime import datetime, timezone

    total_active = 0
    probationary = 0
    effective = 0
    monitor = 0
    ineffective = 0
    removed = 0
    historical_effective = 0
    tracked_count = 0
    scored_count = 0
    any_entry_count = 0

    promotions = []
    demotions = []
    monitor_promotions = []
    monitor_removals = []
    historical_promotions = []

    for row in rows:
        # Only count recognized mutation statuses for fill rate denominator.
        # Skip capability matrix rows and other non-mutation tables that happen
        # to have 6+ pipe-separated fields.
        if row.status not in ("probation", "effective", "monitor", "ineffective",
                               "removed", "historical", "redesigned"):
            continue
        tracked_count += 1

        # Categorize by status
        if row.status in ("probation", "effective", "monitor", "ineffective"):
            total_active += 1
        if row.status == "probation":
            probationary += 1
        elif row.status == "effective":
            effective += 1
        elif row.status == "monitor":
            monitor += 1
        elif row.status == "ineffective":
            ineffective += 1
        elif row.status in ("removed", "redesigned"):
            removed += 1
        elif row.status == "historical":
            historical_effective += 1

        # Measured fill rate
        if row.score is not None:
            scored_count += 1
        if row.builds_tested > 0 or row.score is not None:
            any_entry_count += 1

        # Promotion / demotion rules
        if row.status == "probation" and row.builds_tested >= 3:
            if row.score is not None and row.score >= 4:
                promotions.append({
                    "id": row.id,
                    "new_status": "effective",
                    "rationale": f"{row.builds_tested} builds tested, score {row.score}",
                })
            elif row.score == 3:
                demotions.append({
                    "id": row.id,
                    "new_status": "monitor",
                    "rationale": f"{row.builds_tested} builds tested, score {row.score}",
                })
            elif row.score is not None and row.score <= 2:
                demotions.append({
                    "id": row.id,
                    "new_status": "ineffective",
                    "rationale": f"{row.builds_tested} builds tested, score {row.score}",
                })

        if row.status == "monitor" and row.builds_tested >= 5:
            if row.score is not None and row.score >= 4:
                monitor_promotions.append({
                    "id": row.id,
                    "new_status": "effective",
                    "rationale": f"{row.builds_tested} builds tested, score {row.score}",
                })
            elif row.score is not None and row.score <= 2:
                monitor_removals.append({
                    "id": row.id,
                    "new_status": "ineffective",
                    "rationale": f"{row.builds_tested} builds tested, score {row.score}",
                })

        # Historical promotion: effective mutations with ≥5 builds and score ≥4
        if row.status == "effective" and row.builds_tested >= 5:
            if row.score is not None and row.score >= 4:
                historical_promotions.append({
                    "id": row.id,
                    "new_status": "historical",
                    "rationale": f"{row.builds_tested} builds tested, score {row.score} — proven effective, move to historical",
                })

    # Consolidation suggestion: if multiple probationary mutations target same failure mode
    failure_mode_groups: dict[str, list[str]] = {}
    for row in rows:
        if row.status in ("probation", "effective", "monitor"):
            fm = row.target_failure.lower()
            failure_mode_groups.setdefault(fm, []).append(row.id)

    consolidations = []
    for fm, ids in failure_mode_groups.items():
        if len(ids) >= 2:
            consolidations.append({
                "target_failure": fm,
                "mutation_ids": ids,
                "rationale": f"{len(ids)} mutations target same failure mode",
            })

    # Probationary ratio
    prob_ratio = round((probationary / total_active) * 100, 1) if total_active > 0 else 0.0

    # Measured fill rates — denominator is tracked mutations only, not all parsed rows
    scored_rate = round((scored_count / tracked_count) * 100, 1) if tracked_count else 0.0
    any_rate = round((any_entry_count / tracked_count) * 100, 1) if tracked_count else 0.0

    # Removal rate last 5 builds — count removed mutations with source from recent builds
    # Heuristic: look for "FB30", "FB31", "FB32", etc. in source or build-derived IDs
    recent_removed = sum(
        1 for r in rows
        if r.status in ("removed", "redesigned") and any(b in r.source for b in ("FB28", "FB29", "FB30", "FB31", "FB32"))
    )

    return PortfolioHealth(
        total_active=total_active,
        probationary_count=probationary,
        probationary_ratio=prob_ratio,
        effective_count=effective,
        monitor_count=monitor,
        ineffective_count=ineffective,
        removed_count=removed,
        historical_effective_count=historical_effective,
        measured_fill_rate_scored=scored_rate,
        measured_fill_rate_any=any_rate,
        promotions_ready=promotions,
        demotions_ready=demotions,
        monitor_promotions_ready=monitor_promotions,
        monitor_removals_ready=monitor_removals,
        historical_promotions_ready=historical_promotions,
        consolidations_suggested=consolidations,
        removal_rate_last_5=recent_removed,
        data_integrity_errors=[],
        computed_at=datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    )


def write_health_markdown(health: PortfolioHealth, build_dir: Path) -> None:
    """Write a human-readable summary for S5 and learning curator."""
    path = build_dir / ".kimi" / "mutation-portfolio-health.md"
    path.parent.mkdir(parents=True, exist_ok=True)

    status = lambda v, target, op="lt": "✅ OK" if (v < target if op == "lt" else v >= target) else "⚠️ WARNING"

    lines = [
        "# Mutation Portfolio Health — Pre-computed",
        f"**Computed at**: {health.computed_at}",
        "",
        "> This file is auto-generated by `scripts/mutation-portfolio-health.py`.",
        "> The vsm_learning_curator should read this file first, then verify and write `.kimi/mutation-portfolio-review.md`.",
        "",
        "## Portfolio Health Metrics",
        "",
        "| Metric | Value | Target | Status |",
        "|---|---|---|---|",
        f"| Total active mutations | {health.total_active} | < 60 | {status(health.total_active, 60)} |",
        f"| Probationary ratio | {health.probationary_ratio}% | < 30% | {status(health.probationary_ratio, 30)} |",
        f"| Measured effect fill rate (scored) | {health.measured_fill_rate_scored}% | ≥ 80% | {status(health.measured_fill_rate_scored, 80, 'ge')} |",
        f"| Measured effect fill rate (any) | {health.measured_fill_rate_any}% | ≥ 80% | {status(health.measured_fill_rate_any, 80, 'ge')} |",
        f"| Removal rate (last 5 builds) | {health.removal_rate_last_5} | ≥ 2 | {status(health.removal_rate_last_5, 2, 'ge')} |",
        "",
        f"- **Effective mutations**: {health.effective_count}",
        f"- **Monitor mutations**: {health.monitor_count}",
        f"- **Ineffective mutations**: {health.ineffective_count}",
        f"- **Removed mutations**: {health.removed_count}",
        f"- **Historical effective**: {health.historical_effective_count}",
        "",
    ]

    if health.promotions_ready:
        lines.extend([
            "## Promotions Ready (Autonomous)",
            "",
            "| Mutation ID | New Status | Rationale |",
            "|---|---|---|",
        ])
        for p in health.promotions_ready:
            lines.append(f"| {p['id']} | {p['new_status']} | {p['rationale']} |")
        lines.append("")

    if health.demotions_ready:
        lines.extend([
            "## Demotions Ready",
            "",
            "| Mutation ID | New Status | Rationale |",
            "|---|---|---|",
        ])
        for d in health.demotions_ready:
            lines.append(f"| {d['id']} | {d['new_status']} | {d['rationale']} |")
        lines.append("")

    if health.monitor_promotions_ready:
        lines.extend([
            "## Monitor → Effective Promotions",
            "",
            "| Mutation ID | New Status | Rationale |",
            "|---|---|---|",
        ])
        for p in health.monitor_promotions_ready:
            lines.append(f"| {p['id']} | {p['new_status']} | {p['rationale']} |")
        lines.append("")

    if health.monitor_removals_ready:
        lines.extend([
            "## Monitor → Ineffective Removals",
            "",
            "| Mutation ID | New Status | Rationale |",
            "|---|---|---|",
        ])
        for p in health.monitor_removals_ready:
            lines.append(f"| {p['id']} | {p['new_status']} | {p['rationale']} |")
        lines.append("")

    if health.historical_promotions_ready:
        lines.extend([
            "## Effective → Historical Promotions (Autonomous)",
            "",
            "| Mutation ID | New Status | Rationale |",
            "|---|---|---|",
        ])
        for p in health.historical_promotions_ready:
            lines.append(f"| {p['id']} | {p['new_status']} | {p['rationale']} |")
        lines.append("")

    if health.consolidations_suggested:
        lines.extend([
            "## Consolidation Suggestions",
            "",
            "| Target Failure | Mutation IDs | Rationale |",
            "|---|---|---|",
        ])
        for c in health.consolidations_suggested[:5]:  # Cap at 5
            ids_str = ", ".join(c["mutation_ids"])
            lines.append(f"| {c['target_failure']} | {ids_str} | {c['rationale']} |")
        lines.append("")

    # Spot-check guidance for the learning curator agent
    lines.extend([
        "## Spot-Check Guidance (for vsm_learning_curator)",
        "",
        "If you are the learning curator agent, follow this guidance:",
        "- For metrics marked ✅ OK: No spot-check needed. Trust the pre-computed result.",
        "- For metrics marked ⚠️ WARNING: Verify the specific rows in mutation-state.md.",
        "- For promotion/demotion candidates: Read the specific mutation row in mutation-state.md to confirm builds_tested and score.",
        "",
        "| Check | If suspicious, verify this | What to look for |",
        "|---|---|---|",
        "| Total active mutations | `references/mutation-state.md` master table | Count of active rows matches |",
        "| Promotions ready | Specific mutation rows | builds_tested ≥ 3, score ≥ 4 |",
        "| Demotions ready | Specific mutation rows | builds_tested ≥ 3, score ≤ 2 |",
        "| Historical promotions | Specific mutation rows | builds_tested ≥ 5, score ≥ 4 |",
        "| Consolidations | `references/mutation-log.md` | Overlapping failure modes |",
        "",
        "**Limit**: Maximum 3 spot-checks. If more than 3 candidates, verify the 3 most impactful.",
        "",
    ])

    if health.data_integrity_errors:
        lines.extend([
            "## ⚠️ Data Integrity Errors",
            "",
        ] + [f"- {e}" for e in health.data_integrity_errors] + [""])

    path.write_text("\n".join(lines))


def main() -> int:
    parser = argparse.ArgumentParser(description="Mutation Portfolio Health Calculator")
    parser.add_argument("--build-dir", help="Build directory to write .kimi/ artifacts to")
    parser.add_argument("--mutation-state", help="Path to mutation-state.md (default: ~/vsm/viable-swarm-model/references/mutation-state.md)")
    args = parser.parse_args()

    state_path = Path(args.mutation_state) if args.mutation_state else DEFAULT_MUTATION_STATE
    rows, errors = parse_mutation_state(state_path)
    health = compute_portfolio_health(rows)
    health.data_integrity_errors = errors

    # Serialize for stdout
    health_dict = asdict(health)
    print(json.dumps(health_dict, indent=2))

    if args.build_dir:
        build_path = Path(args.build_dir)
        json_path = build_path / ".kimi" / "mutation-portfolio-health.json"
        json_path.parent.mkdir(parents=True, exist_ok=True)
        json_path.write_text(json.dumps(health_dict, indent=2))
        write_health_markdown(health, build_path)

    return 0


if __name__ == "__main__":
    sys.exit(main())
