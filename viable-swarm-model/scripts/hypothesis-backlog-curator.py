#!/usr/bin/env python3
"""
Hypothesis Backlog Curator — Autonomous S4* curation for vsm_learning_curator.

Reads hypotheses.md, identifies hypotheses with confirmed/rejected/superseded status
(from main entries or FB update sections), moves them to hypotheses-archive.md,
updates the index, and reports remaining untested count.

Usage:
    python3 hypothesis-backlog-curator.py [--dry-run]

Without --dry-run:
    - Writes cleaned hypotheses.md
    - Appends to hypotheses-archive.md (creates if missing)
    - Prints summary to stdout
"""

import argparse
import re
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

VSM_ROOT = Path.home() / "vsm" / "viable-swarm-model"
REFS_DIR = VSM_ROOT / "references"

HYPOTHESES = REFS_DIR / "hypotheses.md"
ARCHIVE = REFS_DIR / "hypotheses-archive.md"


@dataclass
class Hypothesis:
    hid: str
    title: str
    statuses: list[tuple[str, str]] = field(default_factory=list)
    # Each status is (source_section, status_value)
    body_lines: list[str] = field(default_factory=list)

    def latest_status(self) -> tuple[str, str] | None:
        if not self.statuses:
            return None
        # If there's an FB update section, it's the last status added
        # Otherwise it's the main entry status
        return self.statuses[-1]

    def is_closed(self) -> bool:
        latest = self.latest_status()
        if not latest:
            return False
        return latest[1] in ("confirmed", "rejected", "superseded")


def parse_hypotheses(path: Path) -> tuple[list[Hypothesis], list[str]]:
    """Parse hypotheses.md into Hypothesis objects and preamble lines."""
    if not path.exists():
        return [], []

    text = path.read_text()
    lines = text.splitlines()

    hypotheses: dict[str, Hypothesis] = {}
    preamble: list[str] = []
    current_hid: str | None = None
    current_section: str = "preamble"

    i = 0
    while i < len(lines):
        line = lines[i]

        # Detect section headers
        if line.startswith("## H") or line.startswith("## ["):
            m = re.match(r"##\s+(H\S+):\s*(.*)", line)
            if m:
                current_hid = m.group(1)
                current_section = "main"
                if current_hid not in hypotheses:
                    hypotheses[current_hid] = Hypothesis(hid=current_hid, title=m.group(2).strip())
                hypotheses[current_hid].body_lines.append(line)
                i += 1
                continue

        if line.startswith("### H") or line.startswith("### ["):
            m = re.match(r"###\s+(H\S+):\s*(.*)", line)
            if m:
                current_hid = m.group(1)
                current_section = f"update_{current_hid}"
                if current_hid not in hypotheses:
                    hypotheses[current_hid] = Hypothesis(hid=current_hid, title=m.group(2).strip())
                hypotheses[current_hid].body_lines.append(line)
                i += 1
                continue

        # Detect status lines
        status_match = re.search(r"\*\*Status\*\*:\s*(\S+)", line)
        if status_match and current_hid:
            status_val = status_match.group(1).lower().strip(".")
            hypotheses[current_hid].statuses.append((current_section, status_val))

        # Accumulate body lines for current hypothesis
        if current_hid and current_section != "preamble":
            hypotheses[current_hid].body_lines.append(line)
        elif current_hid is None:
            preamble.append(line)

        i += 1

    return list(hypotheses.values()), preamble


def extract_index(text: str) -> list[str]:
    """Extract the index table from hypotheses.md."""
    lines = text.splitlines()
    in_index = False
    index_lines: list[str] = []
    for line in lines:
        if line.startswith("| Hypothesis"):
            in_index = True
        if in_index:
            index_lines.append(line)
            if line.startswith("|---|"):
                continue
            if not line.startswith("|"):
                break
    return index_lines


def build_index(hypotheses: list[Hypothesis]) -> list[str]:
    """Build a fresh index from hypothesis objects."""
    lines = [
        "| Hypothesis | Status |",
        "|---|---|",
    ]
    for h in sorted(hypotheses, key=lambda x: x.hid):
        latest = h.latest_status()
        status = latest[1] if latest else "unknown"
        lines.append(f"| {h.hid} | {status} |")
    return lines


def archive_hypotheses(archive_path: Path, to_archive: list[Hypothesis]) -> None:
    """Append archived hypotheses to hypotheses-archive.md."""
    lines: list[str] = []
    if not archive_path.exists():
        lines.append("# Hypotheses Archive\n")
        lines.append("> Confirmed, rejected, and superseded hypotheses. "
                     "Moved here by hypothesis-backlog-curator.py.\n")

    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    for h in to_archive:
        lines.append(f"\n---\n\n## {h.hid}: {h.title}")
        lines.append(f"**Archived**: {now}")
        latest = h.latest_status()
        if latest:
            lines.append(f"**Final Status**: {latest[1]} (from {latest[0]})")
        for body_line in h.body_lines:
            lines.append(body_line)

    if lines:
        with open(archive_path, "a") as f:
            f.write("\n".join(lines) + "\n")


def rebuild_hypotheses_file(preamble: list[str], remaining: list[Hypothesis]) -> str:
    """Rebuild hypotheses.md with only remaining (open) hypotheses."""
    # Find where the index starts and ends in preamble
    index_start = -1
    index_end = -1
    for i, line in enumerate(preamble):
        if line.startswith("| Hypothesis"):
            index_start = i
        if index_start >= 0 and not line.startswith("|") and line.strip():
            index_end = i
            break
    if index_end < 0:
        index_end = len(preamble)

    # Build new index
    new_index = build_index(remaining)

    # Reconstruct: preamble before index + new index + preamble after index + body
    before_index = preamble[:index_start] if index_start >= 0 else preamble
    after_index = preamble[index_end:] if index_end >= 0 else []

    lines = list(before_index) + new_index + list(after_index)

    # Add remaining hypothesis bodies
    for h in remaining:
        lines.append("")
        lines.append("---")
        lines.append("")
        for body_line in h.body_lines:
            lines.append(body_line)

    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Hypothesis Backlog Curator")
    parser.add_argument("--dry-run", action="store_true", help="Preview changes without writing")
    parser.add_argument("--hypotheses", help="Path to hypotheses.md")
    parser.add_argument("--archive", help="Path to hypotheses-archive.md")
    args = parser.parse_args()

    hyp_path = Path(args.hypotheses) if args.hypotheses else HYPOTHESES
    archive_path = Path(args.archive) if args.archive else ARCHIVE

    hypotheses, preamble = parse_hypotheses(hyp_path)

    to_archive = [h for h in hypotheses if h.is_closed()]
    remaining = [h for h in hypotheses if not h.is_closed()]

    untested_count = sum(
        1 for h in remaining
        if h.latest_status() and h.latest_status()[1] == "untested"
    )

    print(f"Total hypotheses: {len(hypotheses)}")
    print(f"To archive (confirmed/rejected/superseded): {len(to_archive)}")
    print(f"Remaining: {len(remaining)}")
    print(f"  - Untested: {untested_count}")
    print(f"  - Testing/monitor/partially confirmed: {len(remaining) - untested_count}")

    if to_archive:
        print("\nArchiving:")
        for h in to_archive:
            latest = h.latest_status()
            print(f"  {h.hid}: {latest[1] if latest else 'unknown'}")

    if args.dry_run:
        print("\n[Dry run — no files modified]")
        return 0

    # Write archive
    if to_archive:
        archive_hypotheses(archive_path, to_archive)
        print(f"\nAppended {len(to_archive)} hypotheses to {archive_path}")

    # Write cleaned hypotheses.md
    new_content = rebuild_hypotheses_file(preamble, remaining)
    hyp_path.write_text(new_content)
    print(f"Wrote {len(remaining)} hypotheses to {hyp_path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
