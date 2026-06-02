#!/usr/bin/env python3
"""
Validate reference files for ID uniqueness and cross-link validity.

Checks:
1. anti-patterns.md has unique anti-pattern IDs
2. security-lessons.md has unique lesson IDs
3. Cross-links (See also) point to IDs that exist

Run from the agents/ directory or repo root:
    python3 agents/validate-references.py
"""

import os
import re
import sys

REFS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "references")


def check_anti_patterns():
    errors = []
    path = os.path.join(REFS_DIR, "anti-patterns.md")
    if not os.path.exists(path):
        errors.append("anti-patterns.md not found")
        return errors

    with open(path) as f:
        content = f.read()

    # Match "### N. Title" or "### Anti-Pattern #N: Title"
    ids = re.findall(r"^### (?:Anti-Pattern #)?(\d+)[.:]", content, re.MULTILINE)
    seen = {}
    for ap_id in ids:
        if ap_id in seen:
            errors.append(f"anti-patterns.md: duplicate ID #{ap_id}")
        seen[ap_id] = True

    # Check for gaps (optional warning)
    numeric_ids = sorted(int(x) for x in ids)
    if numeric_ids:
        for i in range(1, numeric_ids[-1]):
            if i not in numeric_ids:
                # This is just a warning, not an error — gaps are allowed
                pass

    return errors


def check_security_lessons():
    errors = []
    path = os.path.join(REFS_DIR, "security-lessons.md")
    if not os.path.exists(path):
        errors.append("security-lessons.md not found")
        return errors

    with open(path) as f:
        content = f.read()

    ids = re.findall(r"^### L(\d+):", content, re.MULTILINE)
    seen = {}
    for lesson_id in ids:
        if lesson_id in seen:
            errors.append(f"security-lessons.md: duplicate ID L{lesson_id}")
        seen[lesson_id] = True

    return errors


def check_cross_links():
    errors = []
    path = os.path.join(REFS_DIR, "anti-patterns.md")
    if not os.path.exists(path):
        return errors

    with open(path) as f:
        content = f.read()

    # Check "See also: `security-lessons.md` LNN" references
    refs = re.findall(r"`security-lessons\.md` L(\d+)", content)
    sl_path = os.path.join(REFS_DIR, "security-lessons.md")
    if os.path.exists(sl_path):
        with open(sl_path) as f:
            sl_content = f.read()
        valid_ids = set(re.findall(r"^### L(\d+):", sl_content, re.MULTILINE))
        for ref_id in refs:
            if ref_id not in valid_ids:
                errors.append(f"anti-patterns.md: cross-link to security-lessons.md L{ref_id} does not exist")

    return errors


def main():
    errors = check_anti_patterns() + check_security_lessons() + check_cross_links()

    if errors:
        print("ERRORS:", file=sys.stderr)
        for e in errors:
            print(f"  ❌ {e}", file=sys.stderr)
        return 1
    else:
        print("✅ All reference files validated successfully.")
        return 0


if __name__ == "__main__":
    sys.exit(main())
