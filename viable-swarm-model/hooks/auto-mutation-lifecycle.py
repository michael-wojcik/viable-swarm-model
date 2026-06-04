#!/usr/bin/env python3
"""
auto-mutation-lifecycle.py
Robust auto-update for mutation lifecycle files.
Replaces update-mutation-state.sh (which had format mismatch bugs).

Usage: python3 auto-mutation-lifecycle.py <build-directory> [--dry-run]
"""
import sys
import os
import re
import argparse

MUTATION_STATE = os.path.expanduser("~/vsm/viable-swarm-model/references/mutation-state.md")
MUTATION_LOG = os.path.expanduser("~/vsm/viable-swarm-model/references/mutation-log.md")


def parse_mutations_applied(path: str) -> list[dict]:
    """Extract mutation table from mutations-applied.md."""
    with open(path, 'r') as f:
        content = f.read()

    rows = []
    for line in content.split('\n'):
        line = line.strip()
        if not line.startswith('|') or line.startswith('|---') or '| #' in line or '| # ' in line:
            continue
        parts = [p.strip() for p in line.split('|')]
        parts = [p for p in parts if p]
        if len(parts) >= 5 and parts[1] not in ('#', 'Mutation ID', 'Num'):
            rows.append({
                'id': parts[1],
                'target': parts[2],
                'proposed_by': parts[3],
                'status': parts[4],
                'evidence': parts[5] if len(parts) > 5 else ''
            })
    return rows


def determine_effect(evidence: str, status: str) -> str:
    """Determine measured effect from evidence string."""
    ev_lower = evidence.lower()
    if 'ineffective' in ev_lower or 'score: 1' in ev_lower or 'score: 2' in ev_lower:
        return f"Ineffective (Score: 1–2) — {evidence}"
    if 'partial' in ev_lower or 'score: 3' in ev_lower:
        return f"Partial (Score: 3) — {evidence}"
    if 'effective' in ev_lower or 'score: 4' in ev_lower or 'score: 5' in ev_lower:
        return f"Effective (Score: 4–5) — {evidence}"
    if 'pending' in status.lower():
        return "PENDING"
    return f"Measured — {evidence}"


def update_mutation_log(log_path: str, mutations: list[dict]) -> tuple[str, list[str], list[str]]:
    """Update mutation-log.md measured effects. Returns (new_content, updates, errors)."""
    with open(log_path, 'r') as f:
        content = f.read()

    updates = []
    errors = []
    changed = False

    for row in mutations:
        mut_id = row['id']
        effect = determine_effect(row['evidence'], row['status'])

        if effect == "PENDING":
            continue

        # Pattern: match mutation header block and Measured effect line
        # Handles: [PENDING], **PENDING**, plain PENDING
        pattern = rf'(## Mutation {re.escape(mut_id)}.*?Measured effect:\s*)\\*?\[?PENDING\]?\\*?'

        match = re.search(pattern, content, re.DOTALL)
        if match:
            replacement = match.group(1) + effect
            content = content[:match.start()] + replacement + content[match.end():]
            changed = True
            updates.append(f"  mutation-log.md: {mut_id} ← {effect[:60]}...")
        elif re.search(rf'## Mutation {re.escape(mut_id)}', content):
            updates.append(f"  mutation-log.md: {mut_id} already has measured effect")
        else:
            errors.append(f"  WARNING: {mut_id} not found in mutation-log.md")

    return content, updates, errors


def update_mutation_state(state_path: str, mutations: list[dict]) -> tuple[str, list[str], list[str]]:
    """Increment Builds Tested for each mutation. Returns (new_content, updates, errors)."""
    with open(state_path, 'r') as f:
        content = f.read()

    updates = []
    errors = []
    changed = False

    lines = content.split('\n')
    new_lines = []

    for line in lines:
        # Match mutation ID in first column of table row
        # Format: | ID | ... | ... | Status | N | Score | ...
        match = re.match(r'^(\|\s*(?:~~)?)([A-Za-z0-9/_-]+)(\s*(?:~~)?\s+\|)', line)
        if not match:
            new_lines.append(line)
            continue

        mut_id = match.group(2)
        row_mutations = [m for m in mutations if m['id'] == mut_id]
        if not row_mutations:
            new_lines.append(line)
            continue

        parts = [p.strip() for p in line.split('|')]
        parts = [p for p in parts if p]

        # Schema: | ID | Source | Type | Target | Status | Builds | Score | Hypothesis | Experiment | Next Review |
        if len(parts) >= 10:
            try:
                current = int(parts[5])
                new_val = current + 1
                parts[5] = str(new_val)
                # Update status if it was probation and now has builds
                if parts[4].lower() == 'probation' and new_val >= 3:
                    parts[4] = 'monitor'
                    updates.append(f"  mutation-state.md: {mut_id} Builds {current}→{new_val}, status probation→monitor")
                else:
                    updates.append(f"  mutation-state.md: {mut_id} Builds {current}→{new_val}")
                new_line = '| ' + ' | '.join(parts) + ' |'
                new_lines.append(new_line)
                changed = True
                continue
            except (ValueError, IndexError):
                errors.append(f"  Could not parse Builds Tested for {mut_id}")

        new_lines.append(line)

    return '\n'.join(new_lines), updates, errors


def main():
    parser = argparse.ArgumentParser(description='Auto-update mutation lifecycle files')
    parser.add_argument('build_dir', help='Build directory containing .kimi/mutations-applied.md')
    parser.add_argument('--dry-run', action='store_true', help='Show changes without writing')
    args = parser.parse_args()

    mutations_applied = os.path.join(args.build_dir, '.kimi', 'mutations-applied.md')

    if not os.path.isfile(mutations_applied):
        print(f"ERROR: {mutations_applied} not found")
        sys.exit(1)
    if not os.path.isfile(MUTATION_STATE):
        print(f"ERROR: {MUTATION_STATE} not found")
        sys.exit(1)
    if not os.path.isfile(MUTATION_LOG):
        print(f"ERROR: {MUTATION_LOG} not found")
        sys.exit(1)

    print("=== Auto-Mutation-Lifecycle ===")
    print(f"Build dir: {args.build_dir}")
    print(f"Dry run: {args.dry_run}")

    mutations = parse_mutations_applied(mutations_applied)
    print(f"Found {len(mutations)} mutation entries")

    # Update mutation-log.md
    log_content, log_updates, log_errors = update_mutation_log(MUTATION_LOG, mutations)
    if log_updates or log_errors:
        print(f"\nmutation-log.md: {len(log_updates)} updates, {len(log_errors)} errors")
        for u in log_updates:
            print(u)
        for e in log_errors:
            print(e)

    # Update mutation-state.md
    state_content, state_updates, state_errors = update_mutation_state(MUTATION_STATE, mutations)
    if state_updates or state_errors:
        print(f"\nmutation-state.md: {len(state_updates)} updates, {len(state_errors)} errors")
        for u in state_updates:
            print(u)
        for e in state_errors:
            print(e)

    # Write changes
    if not args.dry_run:
        if log_updates:
            with open(MUTATION_LOG, 'w') as f:
                f.write(log_content)
            print("\nWrote mutation-log.md")
        if state_updates:
            with open(MUTATION_STATE, 'w') as f:
                f.write(state_content)
            print("Wrote mutation-state.md")
    else:
        print("\n[DRY RUN] No files modified")

    total_errors = len(log_errors) + len(state_errors)
    print(f"\n=== Summary ===")
    print(f"Mutations processed: {len(mutations)}")
    print(f"Total updates: {len(log_updates) + len(state_updates)}")
    print(f"Total errors: {total_errors}")

    if total_errors > 0:
        sys.exit(1)


if __name__ == '__main__':
    main()
