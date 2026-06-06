#!/usr/bin/env python3
"""
Increment builds_tested for S5 iteration mutations.

Two modes:
1. --backfill: Compute builds_tested from the number of subsequent S5 iterations
   documented in mutation-state.md (one-time correction).
2. Default: Increment builds_tested by 1 for all effective S5 iteration mutations.

Usage:
    python3 increment-s5-iteration-counter.py --backfill
    python3 increment-s5-iteration-counter.py
"""

import argparse
import re
import sys
from pathlib import Path

DEFAULT_MUTATION_STATE = Path.home() / "vsm" / "viable-swarm-model" / "references" / "mutation-state.md"


def read_file(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_file(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")


def parse_s5_mutations(text: str) -> list[dict]:
    """Extract S5 iteration mutation rows from the master table."""
    mutations = []
    in_s5_section = False
    for line in text.splitlines():
        if "**S5 ITERATION MUTATIONS" in line:
            in_s5_section = True
            continue
        if in_s5_section and line.startswith("| **") and "S5" not in line:
            # Next section header
            in_s5_section = False
            continue
        if in_s5_section and line.startswith("|") and "---" not in line:
            parts = [p.strip() for p in line.split("|")]
            parts = [p for p in parts if p]
            if len(parts) >= 7 and parts[0] not in ("ID", "**id**"):
                try:
                    builds_tested = int(parts[5])
                except ValueError:
                    builds_tested = 0
                mutations.append({
                    "id": parts[0],
                    "source": parts[1],
                    "type": parts[2],
                    "target_failure": parts[3],
                    "status": parts[4].strip("*"),
                    "builds_tested": builds_tested,
                    "score": parts[6] if len(parts) > 6 else "—",
                    "line": line,
                })
    return mutations


def backfill_builds_tested(text: str, mutations: list[dict]) -> str:
    """Set builds_tested based on position: 1 + number of subsequent S5 mutations."""
    if not mutations:
        return text

    # Mutations are in chronological order in the file
    # Each mutation's builds_tested = 1 + count of mutations after it
    total = len(mutations)
    new_text = text
    for i, m in enumerate(mutations):
        expected = total - i
        if m["builds_tested"] != expected:
            old_line = m["line"]
            parts = [p.strip() for p in old_line.split("|")]
            parts = [p for p in parts if p]
            if len(parts) >= 7:
                parts[5] = str(expected)
                new_line = "| " + " | ".join(parts) + " |"
                new_text = new_text.replace(old_line, new_line)
    return new_text


def increment_builds_tested(text: str, mutations: list[dict]) -> str:
    """Increment builds_tested by 1 for all effective S5 iteration mutations."""
    new_text = text
    for m in mutations:
        if m["status"].lower() != "effective":
            continue
        old_line = m["line"]
        parts = [p.strip() for p in old_line.split("|")]
        parts = [p for p in parts if p]
        if len(parts) >= 7:
            try:
                current = int(parts[5])
            except ValueError:
                current = 0
            parts[5] = str(current + 1)
            new_line = "| " + " | ".join(parts) + " |"
            new_text = new_text.replace(old_line, new_line)
    return new_text


def main() -> int:
    parser = argparse.ArgumentParser(description="Increment S5 iteration mutation counters")
    parser.add_argument("--mutation-state", type=Path, default=DEFAULT_MUTATION_STATE)
    parser.add_argument("--backfill", action="store_true", help="One-time backfill based on file order")
    parser.add_argument("--dry-run", action="store_true", help="Print changes without writing")
    args = parser.parse_args()

    if not args.mutation_state.exists():
        print(f"ERROR: {args.mutation_state} not found", file=sys.stderr)
        return 1

    text = read_file(args.mutation_state)
    mutations = parse_s5_mutations(text)

    if not mutations:
        print("No S5 iteration mutations found.")
        return 0

    if args.backfill:
        new_text = backfill_builds_tested(text, mutations)
        mode = "backfill"
    else:
        new_text = increment_builds_tested(text, mutations)
        mode = "increment"

    if new_text == text:
        print(f"No changes needed ({mode} mode).")
        return 0

    # Report changes
    old_muts = parse_s5_mutations(text)
    new_muts = parse_s5_mutations(new_text)
    print(f"S5 iteration mutation updates ({mode} mode):")
    for old, new in zip(old_muts, new_muts):
        if old["builds_tested"] != new["builds_tested"]:
            print(f"  {old['id']}: builds_tested {old['builds_tested']} -> {new['builds_tested']}")

    if args.dry_run:
        print("(dry-run: no files modified)")
        return 0

    write_file(args.mutation_state, new_text)
    print(f"Updated {args.mutation_state}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
