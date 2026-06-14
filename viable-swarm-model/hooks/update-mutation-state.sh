#!/bin/bash
# update-mutation-state.sh
# Auto-update mutation-state.md and mutation-log.md from build artifacts
# Called by session-end.sh or run manually by S5 during Phase 8c-ii
#
# Usage: bash ~/vsm/viable-swarm-model/hooks/update-mutation-state.sh <build-directory> [--dry-run]

set -euo pipefail

# Resolve the real Python interpreter once to avoid pyenv shim overhead.
if [ -z "${PYTHON3:-}" ]; then
    if command -v pyenv >/dev/null 2>&1; then
        PYTHON3=$(pyenv which python3 2>/dev/null || command -v python3)
    else
        PYTHON3=$(command -v python3)
    fi
fi

BUILD_DIR="${1:-.}"
DRY_RUN=false
if [ "${2:-}" = "--dry-run" ]; then
  DRY_RUN=true
  echo "[DRY-RUN] No files will be modified."
fi

MUTATION_STATE="$HOME/vsm/viable-swarm-model/references/mutation-state.md"
MUTATIONS_APPLIED="$BUILD_DIR/.kimi/mutations-applied.md"
MUTATION_LOG="$HOME/vsm/viable-swarm-model/references/mutation-log.md"
ERROR_LOG="$BUILD_DIR/.kimi/mutation-update-errors.md"

# Fallback error logging
log_error() {
  echo "[$(date -Iseconds)] $1" >> "$ERROR_LOG"
}

if [ ! -f "$MUTATIONS_APPLIED" ]; then
  MSG="ERROR: $MUTATIONS_APPLIED not found. Cannot auto-update mutation state."
  echo "$MSG"
  log_error "$MSG"
  # Write a fallback reminder to the build directory so S5 sees it
  echo "$MSG" > "$BUILD_DIR/.kimi/mutation-update-reminder.md"
  exit 1
fi

if [ ! -f "$MUTATION_STATE" ]; then
  MSG="ERROR: $MUTATION_STATE not found."
  echo "$MSG"
  log_error "$MSG"
  exit 1
fi

if [ ! -f "$MUTATION_LOG" ]; then
  MSG="ERROR: $MUTATION_LOG not found."
  echo "$MSG"
  log_error "$MSG"
  exit 1
fi

# Extract mutation IDs and measured effects from mutations-applied.md
echo "Scanning $MUTATIONS_APPLIED for measured effects..."

# For each mutation in mutations-applied.md, update mutation-log.md and mutation-state.md
while IFS= read -r line; do
  if echo "$line" | grep -qE '^\| [^|]+ \|'; then
    MUTATION_ID=$(echo "$line" | awk -F'|' '{print $3}' | sed 's/^ *//;s/ *$//')
    STATUS=$(echo "$line" | awk -F'|' '{print $6}' | sed 's/^ *//;s/ *$//')
    EVIDENCE=$(echo "$line" | awk -F'|' '{print $7}' | sed 's/^ *//;s/ *$//')

    # Skip header row
    if [ -n "$MUTATION_ID" ] && [ "$MUTATION_ID" != "Mutation ID" ] && [ "$MUTATION_ID" != "---" ]; then
      echo "Processing: $MUTATION_ID (status: $STATUS)"

      # Escape regex special characters in MUTATION_ID for safe embedding in Python regex
      SAFE_ID=$(printf '%s' "$MUTATION_ID" | sed 's/[[\.*^$()+?{|]/\\&/g')

      # Update mutation-log.md: replace **PENDING** with measured effect
      if grep -q "^## Mutation $MUTATION_ID" "$MUTATION_LOG"; then
        # Check if measured effect is still pending (supports **PENDING**, [PENDING], PENDING)
        # Scoped to the mutation block; look for PENDING in measured effect line.
        # The line may have markdown bold: **Measured effect**: [PENDING]
        MEASURED_EFFECT_LINE=$(grep -A30 "^## Mutation $MUTATION_ID" "$MUTATION_LOG" | grep -i 'Measured effect' | head -1 || true)
        if echo "$MEASURED_EFFECT_LINE" | grep -qi 'PENDING'; then
          # Extract the score from evidence or default to Effective
          if echo "$EVIDENCE" | grep -qi "ineffective"; then
            EFFECT="Ineffective (Score: 1–2) — $EVIDENCE"
          elif echo "$EVIDENCE" | grep -qi "partial"; then
            EFFECT="Partial (Score: 3) — $EVIDENCE"
          elif echo "$EVIDENCE" | grep -qi "monitor"; then
            EFFECT="Monitor (Score: 3) — $EVIDENCE"
          else
            EFFECT="Effective (Score: 4–5) — $EVIDENCE"
          fi

          if [ "$DRY_RUN" = true ]; then
            echo "  [DRY-RUN] Would update mutation-log.md: $MUTATION_ID -> '$EFFECT'"
          else
            # Use Python for precise block-scoped replacement
            "$PYTHON3" -c "
import re
with open('$MUTATION_LOG', 'r') as f:
    content = f.read()

# Find the mutation block and replace PENDING in measured effect
# Match **PENDING**, [PENDING], or bare PENDING with optional surrounding markdown
pattern = r'(## Mutation $SAFE_ID.*?(?:\*\*)?Measured effect(?:\*\*)?:[ \t]*)((?:\*\*)?\[?PENDING\]?(?:\*\*)?(?:[ \t]*—[ \t]*awaiting[^\n]*)?)'

def repl(m):
    return m.group(1) + '$EFFECT'

new_content, count = re.subn(pattern, repl, content, flags=re.DOTALL)
if count == 0:
    print('  Warning: PENDING pattern not found for $MUTATION_ID')
else:
    with open('$MUTATION_LOG', 'w') as f:
        f.write(new_content)
    print('  Updated mutation-log.md: $MUTATION_ID')
"
          fi
        else
          echo "  Measured effect already filled for $MUTATION_ID"
        fi
      else
        echo "  Warning: Mutation $MUTATION_ID not found in mutation-log.md"
      fi

      # Update mutation-state.md: increment Builds Tested, update score
      if grep -q "^| $MUTATION_ID " "$MUTATION_STATE"; then
        if [ "$DRY_RUN" = true ]; then
          echo "  [DRY-RUN] Would increment Builds Tested for $MUTATION_ID in mutation-state.md"
        else
          "$PYTHON3" -c "
import re
with open('$MUTATION_STATE', 'r') as f:
    content = f.read()

# Find the row for this mutation and increment Builds Tested
# Match: | ID | Source | Type | Target | Status | N | ...
# Uses [^|]*\| to match each column boundary precisely.
pattern = r'(\| $SAFE_ID \|[^|]*\|[^|]*\|[^|]*\|[^|]*\|)([0-9]+)( \|)'

def increment(match):
    return match.group(1) + str(int(match.group(2)) + 1) + match.group(3)

new_content, count = re.subn(pattern, increment, content)
if count == 0:
    print('  Warning: Could not increment Builds Tested for $MUTATION_ID')
else:
    with open('$MUTATION_STATE', 'w') as f:
        f.write(new_content)
    print('  Incremented Builds Tested: $MUTATION_ID')
"
        fi
      else
        echo "  Warning: Mutation $MUTATION_ID not found in mutation-state.md"
      fi
    fi
  fi
done < "$MUTATIONS_APPLIED"

echo "Mutation state auto-update complete."
if [ "$DRY_RUN" = true ]; then
  echo "[DRY-RUN] No files were modified."
fi
