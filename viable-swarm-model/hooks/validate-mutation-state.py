#!/usr/bin/env python3
"""validate-mutation-state.py

Fast Python replacement for validate-mutation-state.sh.
Pre-session validation of mutation tracking infrastructure.
"""
import os
import re
import sys

HOME = os.path.expanduser("~")
MUTATION_STATE = os.path.join(HOME, "vsm", "viable-swarm-model", "references", "mutation-state.md")
MUTATION_LOG = os.path.join(HOME, "vsm", "viable-swarm-model", "references", "mutation-log.md")
CEMETERY = os.path.join(HOME, "vsm", "viable-swarm-model", "references", "mutation-cemetery.md")


def main():
    errors = 0
    warnings = 0

    print("=== Mutation State Validation ===")

    # 1. Check files exist
    if not os.path.isfile(MUTATION_STATE):
        print("ERROR: mutation-state.md not found")
        sys.exit(1)
    if not os.path.isfile(MUTATION_LOG):
        print("ERROR: mutation-log.md not found")
        sys.exit(1)

    # Read mutation-state.md and extract master table rows
    with open(MUTATION_STATE, "r", encoding="utf-8") as f:
        state_content = f.read()

    # Mutation ID pattern: FB24-1, H217, R19, A4, S5, PM3, M-FB30-1, SM1
    id_re = re.compile(r"^\| ([A-Z0-9]+[0-9-]*[A-Z0-9-]*) \|")
    rows = []
    for line in state_content.splitlines():
        m = id_re.match(line)
        if not m:
            continue
        mid = m.group(1)
        if mid in ("ID", "**") or mid.startswith("Metric"):
            continue
        fields = [field.strip() for field in line.split("|")]
        # fields[0] is empty before leading pipe; fields[1] is ID
        rows.append({
            "id": mid,
            "fields": fields,
            "status": fields[6].lower() if len(fields) > 6 else "",
            "builds": fields[7].strip() if len(fields) > 7 else "",
        })

    # 2. Check duplicate IDs
    print("Checking for duplicate mutation IDs in state...")
    seen = set()
    duplicates = []
    for row in rows:
        if row["id"] in seen:
            duplicates.append(row["id"])
        seen.add(row["id"])
    if duplicates:
        print("ERROR: Duplicate mutation IDs in mutation-state.md:")
        for dup in duplicates:
            print(f"  - {dup}")
        errors += 1
    else:
        print("OK No duplicate IDs in master table")

    # 3. Check malformed table rows
    print("Checking table row consistency...")
    malformed = [row for row in rows if len(row["fields"]) != 12]
    if malformed:
        print("WARNING: Potentially malformed table rows (expected 10 columns):")
        for row in malformed[:5]:
            print(f"  {row['id']}: {len(row['fields'])} fields")
        warnings += 1
    else:
        print("OK Table row column counts consistent")

    # Pre-load log IDs and cemetery content
    with open(MUTATION_LOG, "r", encoding="utf-8") as f:
        log_content = f.read()
    log_ids = set(re.findall(r"^## Mutation (\S+)", log_content, re.MULTILINE))

    cemetery_content = ""
    if os.path.isfile(CEMETERY):
        with open(CEMETERY, "r", encoding="utf-8") as f:
            cemetery_content = f.read()

    # 4. Check log entry coverage
    print("Checking log entry coverage...")
    missing_logs = 0
    for row in rows:
        status = row["status"]
        if status in ("probation", "monitor", "effective"):
            if row["id"] not in log_ids:
                print(f"WARNING: {row['id']} (status: {status}) has no ## Mutation block in mutation-log.md")
                missing_logs += 1
    if missing_logs == 0:
        print("OK All tracked mutations have log entries")
    else:
        warnings += missing_logs

    # 5. Check cemetery consistency
    print("Checking cemetery consistency...")
    removed_not_in_cemetery = 0
    for row in rows:
        if row["status"] == "removed":
            if row["id"] not in cemetery_content:
                print(f"WARNING: {row['id']} status is 'removed' but not found in mutation-cemetery.md")
                removed_not_in_cemetery += 1
    if removed_not_in_cemetery == 0:
        print("OK All removed mutations are in cemetery")
    else:
        warnings += removed_not_in_cemetery

    # 6. Check stale probation mutations
    print("Checking stale probation mutations...")
    stale_probation = 0
    for row in rows:
        if row["status"] == "probation":
            try:
                builds = int(row["builds"])
            except ValueError:
                continue
            if builds > 3:
                print(f"WARNING: {row['id']} has been in probation for {builds} builds without scoring")
                stale_probation += 1
    if stale_probation == 0:
        print("OK No stale probation mutations")
    else:
        warnings += stale_probation

    # Summary
    print("")
    print("=== Validation Summary ===")
    if errors == 0 and warnings == 0:
        print("PASS — Mutation state is healthy.")
        sys.exit(0)
    else:
        print(f"Errors: {errors} | Warnings: {warnings}")
        if errors > 0:
            print("FAILED — Critical data integrity issues detected.")
            sys.exit(1)
        else:
            print("ISSUES — Non-critical warnings detected.")
            sys.exit(0)


if __name__ == "__main__":
    main()
