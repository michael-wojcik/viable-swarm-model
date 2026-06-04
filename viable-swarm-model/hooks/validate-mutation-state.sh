#!/bin/bash
# validate-mutation-state.sh
# Pre-session validation of mutation tracking infrastructure
# Run this before starting a build to ensure data integrity.
#
# Usage: bash ~/vsm/viable-swarm-model/hooks/validate-mutation-state.sh

set -euo pipefail

MUTATION_STATE="$HOME/vsm/viable-swarm-model/references/mutation-state.md"
MUTATION_LOG="$HOME/vsm/viable-swarm-model/references/mutation-log.md"
CEMETERY="$HOME/vsm/viable-swarm-model/references/mutation-cemetery.md"

ERRORS=0
WARNINGS=0

echo "=== Mutation State Validation ==="

# 1. Check files exist
if [ ! -f "$MUTATION_STATE" ]; then
  echo "🔴 ERROR: mutation-state.md not found"
  exit 1
fi
if [ ! -f "$MUTATION_LOG" ]; then
  echo "🔴 ERROR: mutation-log.md not found"
  exit 1
fi

# 2. Check for duplicate IDs in mutation-state.md master table
# Extract IDs from the master table — mutation IDs match patterns like FB24-1, H217, R19, A4, S5, PM3, M-FB30-1, SM1
echo "Checking for duplicate mutation IDs in state..."
DUPLICATES=$(grep -E '^\| [A-Z0-9]+[0-9-]*[A-Z0-9-]* \|' "$MUTATION_STATE" | grep -v '^| ID' | grep -v '^|--' | grep -v '^| Metric' | awk -F'|' '{print $2}' | sed 's/^ *//;s/ *$//' | sort | uniq -d)
if [ -n "$DUPLICATES" ]; then
  echo "🔴 ERROR: Duplicate mutation IDs in mutation-state.md:"
  echo "$DUPLICATES" | while read -r dup; do
    echo "  - $dup"
  done
  ERRORS=$((ERRORS + 1))
else
  echo "✅ No duplicate IDs in master table"
fi

# 3. Check for malformed table rows (wrong column count)
echo "Checking table row consistency..."
# Master table should have 10 columns
echo "$MUTATION_STATE"
# Master table rows have 12 pipe-separated fields (including leading/trailing empties)
MALFORMED=$(grep -E '^\| [A-Z0-9]+[0-9-]*[A-Z0-9-]* \|' "$MUTATION_STATE" | grep -v '^| ID' | grep -v '^|--' | grep -v '^| Metric' | awk -F'|' 'NF != 12 {print NR ": " $0}')
if [ -n "$MALFORMED" ]; then
  echo "🟡 WARNING: Potentially malformed table rows (expected 10 columns):"
  echo "$MALFORMED" | head -5
  WARNINGS=$((WARNINGS + 1))
else
  echo "✅ Table row column counts consistent"
fi

# 4. Check that every active/probation/monitor mutation has a log entry
echo "Checking log entry coverage..."
MISSING_LOGS=0
while IFS= read -r line; do
  ID=$(echo "$line" | awk -F'|' '{print $2}' | sed 's/^ *//;s/ *$//')
  STATUS=$(echo "$line" | awk -F'|' '{print $6}' | sed 's/^ *//;s/ *$//' | tr '[:upper:]' '[:lower:]')
  if [ -n "$ID" ] && [ "$ID" != "ID" ] && [ "$ID" != "**" ]; then
    if [ "$STATUS" = "probation" ] || [ "$STATUS" = "monitor" ] || [ "$STATUS" = "effective" ]; then
      if ! grep -q "^## Mutation $ID" "$MUTATION_LOG"; then
        # Allow exceptions for redesign/removed status
        if [ "$STATUS" != "removed" ] && [ "$STATUS" != "redesigned" ]; then
          echo "🟡 WARNING: $ID (status: $STATUS) has no ## Mutation block in mutation-log.md"
          MISSING_LOGS=$((MISSING_LOGS + 1))
        fi
      fi
    fi
  fi
done < <(grep -E '^\| [A-Z0-9]+[0-9-]*[A-Z0-9-]* \|' "$MUTATION_STATE" | grep -v '^| ID' | grep -v '^|--' | grep -v '^| Metric')

if [ $MISSING_LOGS -eq 0 ]; then
  echo "✅ All tracked mutations have log entries"
else
  WARNINGS=$((WARNINGS + MISSING_LOGS))
fi

# 5. Check cemetery consistency: removed mutations should be in cemetery
echo "Checking cemetery consistency..."
REMOVED_NOT_IN_CEMETERY=0
while IFS= read -r line; do
  ID=$(echo "$line" | awk -F'|' '{print $2}' | sed 's/^ *//;s/ *$//')
  STATUS=$(echo "$line" | awk -F'|' '{print $6}' | sed 's/^ *//;s/ *$//' | tr '[:upper:]' '[:lower:]')
  if [ -n "$ID" ] && [ "$ID" != "ID" ] && [ "$STATUS" = "removed" ]; then
    if ! grep -qi "$ID" "$CEMETERY" 2>/dev/null; then
      echo "🟡 WARNING: $ID status is 'removed' but not found in mutation-cemetery.md"
      REMOVED_NOT_IN_CEMETERY=$((REMOVED_NOT_IN_CEMETERY + 1))
    fi
  fi
done < <(grep -E '^\| [A-Z0-9]+[0-9-]*[A-Z0-9-]* \|' "$MUTATION_STATE" | grep -v '^| ID' | grep -v '^|--' | grep -v '^| Metric')

if [ $REMOVED_NOT_IN_CEMETERY -eq 0 ]; then
  echo "✅ All removed mutations are in cemetery"
else
  WARNINGS=$((WARNINGS + REMOVED_NOT_IN_CEMETERY))
fi

# 6. Check for probation mutations that have been untested for >3 builds
echo "Checking stale probation mutations..."
STALE_PROBATION=0
while IFS= read -r line; do
  ID=$(echo "$line" | awk -F'|' '{print $2}' | sed 's/^ *//;s/ *$//')
  STATUS=$(echo "$line" | awk -F'|' '{print $6}' | sed 's/^ *//;s/ *$//' | tr '[:upper:]' '[:lower:]')
  BUILDS=$(echo "$line" | awk -F'|' '{print $7}' | sed 's/^ *//;s/ *$//')
  if [ -n "$ID" ] && [ "$ID" != "ID" ] && [ "$STATUS" = "probation" ]; then
    if [ "$BUILDS" -gt 3 ] 2>/dev/null; then
      echo "🟡 WARNING: $ID has been in probation for $BUILDS builds without scoring"
      STALE_PROBATION=$((STALE_PROBATION + 1))
    fi
  fi
done < <(grep -E '^\| [A-Z0-9]+[0-9-]*[A-Z0-9-]* \|' "$MUTATION_STATE" | grep -v '^| ID' | grep -v '^|--' | grep -v '^| Metric')

if [ $STALE_PROBATION -eq 0 ]; then
  echo "✅ No stale probation mutations"
else
  WARNINGS=$((WARNINGS + STALE_PROBATION))
fi

# Summary
echo ""
echo "=== Validation Summary ==="
if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
  echo "✅ PASS — Mutation state is healthy."
  exit 0
else
  echo "Errors: $ERRORS | Warnings: $WARNINGS"
  if [ $ERRORS -gt 0 ]; then
    echo "🔴 FAILED — Critical data integrity issues detected."
    exit 1
  else
    echo "🟡 ISSUES — Non-critical warnings detected."
    exit 0
  fi
fi
