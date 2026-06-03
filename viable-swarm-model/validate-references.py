#!/usr/bin/env python3
"""
validate-references.py

Validates reference files in the VSM ecosystem:
1. Duplicate ID detection within each reference file
2. Cross-link validity (when file A references an ID in file B, verify it exists)
3. Gap detection in sequentially-numbered files

Run from repo root or any directory.
"""

import os
import re
import sys
from pathlib import Path
from collections import defaultdict

# --- Configuration ---
REFS_DIR = Path.home() / "vsm" / "viable-swarm-model" / "references"

FILE_CONFIG = {
    "anti-patterns.md": {
        "id_pattern": r"^###\s+(?:(?:Anti-Pattern\s+)?#)?(\d+)[:\.]",
        "id_type": int,
        "prefix": "#",
        "sequential": True,
    },
    "security-lessons.md": {
        "id_pattern": r"^###\s+(L\d+):",
        "id_type": str,
        "prefix": "L",
        "sequential": False,  # Lessons are removed over time; gaps expected
    },
    "pattern-library.md": {
        "id_pattern": r"^###\s+(\d+)\.",
        "id_type": int,
        "prefix": "#",
        "sequential": True,
    },
    "meta-reflection.md": {
        "id_pattern": r"^##\s+Entry\s+(\d+)",
        "id_type": int,
        "prefix": "Entry ",
        "sequential": True,
    },
    "hypotheses.md": {
        "id_pattern": r"^##\s+(H\d+):",
        "id_type": str,
        "prefix": "H",
        "sequential": False,
    },
    "mutation-log.md": {
        "id_pattern": r"^##\s+Mutation\s+(?:\[)?(\d+)(?:\])?",
        "id_type": int,
        "prefix": "M",
        "sequential": True,
    },
    "experiments.md": {
        "id_pattern": r"^##\s+Experiment\s+(?:E)?(\d+)",
        "id_type": int,
        "prefix": "E",
        "sequential": True,
    },
    "hypotheses-archive.md": {
        "id_pattern": r"^#{2,3}\s+(H\d+):",
        "id_type": str,
        "prefix": "H",
        "sequential": False,
    },
}

# Cross-link patterns to validate
# Map: source file -> list of (regex_pattern, target_file, id_extractor)
CROSS_LINK_PATTERNS = [
    # anti-patterns.md -> security-lessons.md L#
    (r"security-lessons\.md[`\s]+L(\d+)", "security-lessons.md", lambda m: f"L{m.group(1)}"),
    # security-lessons.md -> anti-patterns.md ##
    (r"anti-patterns\.md[`\s]+#(\d+)", "anti-patterns.md", lambda m: int(m.group(1))),
    # mutation-log.md -> pattern-library.md ##
    (r"pattern-library\.md[`\s]+#(\d+)", "pattern-library.md", lambda m: int(m.group(1))),
    # integration-checklist.md -> anti-patterns.md ##
    (r"anti-patterns(?:\.md)?[`\s]+#(\d+)", "anti-patterns.md", lambda m: int(m.group(1))),
    # integration-checklist.md -> security-lessons.md L#
    (r"security-lessons(?:\.md)?[`\s]+L(\d+)", "security-lessons.md", lambda m: f"L{m.group(1)}"),
    # Any file -> hypotheses.md H#
    (r"hypotheses\.md[`\s]+H(\d+)", "hypotheses.md", lambda m: f"H{m.group(1)}"),
    # Any file -> hypotheses-archive.md H#
    (r"hypotheses-archive\.md[`\s]+H(\d+)", "hypotheses-archive.md", lambda m: f"H{m.group(1)}"),
    # Any file -> experiments.md E#
    (r"experiments\.md[`\s]+E(\d+)", "experiments.md", lambda m: int(m.group(1))),
    # Any file -> mutation-log.md M# (or just "Mutation N")
    (r"mutation-log\.md[`\s]+(?:Mutation\s+)?#?(\d+)", "mutation-log.md", lambda m: int(m.group(1))),
]


def parse_ids(filepath: Path, config: dict) -> tuple[dict, list]:
    """Extract IDs from a file. Returns (id->line map, list of errors)."""
    ids = {}  # id_value -> line_number
    errors = []

    if not filepath.exists():
        errors.append(f"File not found: {filepath}")
        return ids, errors

    content = filepath.read_text(encoding="utf-8")
    pattern = re.compile(config["id_pattern"], re.MULTILINE)

    for match in pattern.finditer(content):
        raw_id = match.group(1)
        line_num = content[:match.start()].count("\n") + 1

        if config["id_type"] == int:
            id_val = int(raw_id)
        else:
            id_val = raw_id

        if id_val in ids:
            errors.append(
                f"  DUPLICATE {config['prefix']}{id_val} at lines {ids[id_val]} and {line_num}"
            )
        else:
            ids[id_val] = line_num

    return ids, errors


def check_gaps(ids: dict, config: dict, filename: str) -> list:
    """Check for gaps in sequential numbering."""
    errors = []
    if not config.get("sequential") or not ids:
        return errors

    if config["id_type"] != int:
        return errors

    sorted_ids = sorted(ids.keys())
    expected = list(range(1, max(sorted_ids) + 1))
    missing = [i for i in expected if i not in ids]

    if missing:
        # Report as warnings, not hard errors — some gaps may be intentional
        for m in missing:
            errors.append(
                f"  GAP: {config['prefix']}{m} is missing (between {config['prefix']}{m-1} and {config['prefix']}{m+1})"
            )

    return errors


def check_cross_links(source_path: Path, all_ids: dict) -> list:
    """Check that all cross-references in source file point to valid IDs."""
    errors = []
    content = source_path.read_text(encoding="utf-8")
    source_name = source_path.name

    for pattern_str, target_file, extractor in CROSS_LINK_PATTERNS:
        pattern = re.compile(pattern_str, re.IGNORECASE)
        target_path = REFS_DIR / target_file

        # Skip if target file doesn't exist
        if not target_path.exists():
            continue

        target_ids = all_ids.get(target_file, {})

        for match in pattern.finditer(content):
            ref_id = extractor(match)
            line_num = content[:match.start()].count("\n") + 1

            if ref_id not in target_ids:
                errors.append(
                    f"  BROKEN LINK at line {line_num}: references {target_file} {ref_id} — NOT FOUND"
                )

    return errors


def main():
    print("=" * 60)
    print("VSM Reference File Validator")
    print("=" * 60)

    if not REFS_DIR.exists():
        print(f"BLOCKER: References directory not found: {REFS_DIR}")
        sys.exit(1)

    all_ids = {}  # filename -> {id_value: line_number}
    all_errors = defaultdict(list)  # filename -> [error strings]
    total_errors = 0
    total_warnings = 0

    # Phase 1: Parse IDs from all configured files
    print("\n📋 Phase 1: Parsing IDs from reference files\n")
    for filename, config in FILE_CONFIG.items():
        filepath = REFS_DIR / filename
        ids, errors = parse_ids(filepath, config)
        all_ids[filename] = ids

        if not filepath.exists():
            print(f"  ⚠️  {filename}: FILE NOT FOUND")
            all_errors[filename].extend(errors)
            total_errors += len(errors)
            continue

        print(f"  ✅ {filename}: {len(ids)} IDs parsed")
        if errors:
            for e in errors:
                print(f"    🔴 {e}")
                all_errors[filename].append(e)
            total_errors += len(errors)

        # Check for gaps
        gap_errors = check_gaps(ids, config, filename)
        if gap_errors:
            for e in gap_errors:
                print(f"    🟡 {e}")
                all_errors[filename].append(e)
            total_warnings += len(gap_errors)

    # Phase 2: Check cross-links in ALL .md files in references/
    print("\n🔗 Phase 2: Validating cross-links\n")
    for md_file in sorted(REFS_DIR.glob("*.md")):
        if md_file.name.startswith("integration-checklist-archive"):
            continue  # Archive file may have stale links

        link_errors = check_cross_links(md_file, all_ids)
        if link_errors:
            print(f"  📄 {md_file.name}:")
            for e in link_errors:
                print(f"    🔴 {e}")
                all_errors[md_file.name].append(e)
            total_errors += len(link_errors)
        else:
            # Only print if we checked something
            content = md_file.read_text(encoding="utf-8")
            has_refs = any(
                re.search(p[0], content, re.IGNORECASE) for p in CROSS_LINK_PATTERNS
            )
            if has_refs:
                print(f"  ✅ {md_file.name}: all cross-links valid")

    # Summary
    print("\n" + "=" * 60)
    print("📊 SUMMARY")
    print("=" * 60)

    if total_errors == 0 and total_warnings == 0:
        print("\n🎉 All checks passed. Reference files are clean.")
        sys.exit(0)
    else:
        print(f"\n🔴 Errors: {total_errors}")
        print(f"🟡 Warnings (gaps): {total_warnings}")

        if all_errors:
            print("\n📋 Error breakdown by file:")
            for filename, errors in sorted(all_errors.items()):
                if errors:
                    print(f"\n  {filename}:")
                    for e in errors:
                        print(f"    {e}")

        sys.exit(1 if total_errors > 0 else 0)


if __name__ == "__main__":
    main()
