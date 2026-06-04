#!/bin/bash
# update-mutation-state.sh
# Auto-update mutation-state.md from build artifacts
# Called by session-end.sh or run manually by S5 during Phase 8c-ii
#
# Usage: bash ~/vsm/viable-swarm-model/hooks/update-mutation-state.sh <build-directory>

BUILD_DIR="${1:-.}"
MUTATION_STATE="$HOME/vsm/viable-swarm-model/references/mutation-state.md"
MUTATIONS_APPLIED="$BUILD_DIR/.kimi/mutations-applied.md"
MUTATION_LOG="$HOME/vsm/viable-swarm-model/references/mutation-log.md"

if [ ! -f "$MUTATIONS_APPLIED" ]; then
  echo "ERROR: $MUTATIONS_APPLIED not found. Cannot auto-update mutation state."
  exit 1
fi

if [ ! -f "$MUTATION_STATE" ]; then
  echo "ERROR: $MUTATION_STATE not found."
  exit 1
fi

# Extract mutation IDs and measured effects from mutations-applied.md
echo "Scanning $MUTATIONS_APPLIED for measured effects..."

# For each mutation in mutations-applied.md, update mutation-log.md and mutation-state.md
while IFS= read -r line; do
  if echo "$line" | grep -qE '^\| [0-9]+ \|'; then
    MUTATION_ID=$(echo "$line" | awk -F'|' '{print $3}' | tr -d ' ')
    STATUS=$(echo "$line" | awk -F'|' '{print $6}' | tr -d ' ')
    EVIDENCE=$(echo "$line" | awk -F'|' '{print $7}' | sed 's/^ *//;s/ *$//')

    if [ -n "$MUTATION_ID" ] && [ "$MUTATION_ID" != "Mutation ID" ]; then
      echo "Processing: $MUTATION_ID (status: $STATUS)"

      # Update mutation-log.md: replace [PENDING] with measured effect
      if grep -q "^## Mutation $MUTATION_ID" "$MUTATION_LOG"; then
        # Check if measured effect is already filled
        if grep -A20 "^## Mutation $MUTATION_ID" "$MUTATION_LOG" | grep -qE "Measured effect: \*?\[?PENDING\]?\*?"; then
          # Extract the score from evidence or default to Effective
          if echo "$EVIDENCE" | grep -qi "ineffective"; then
            EFFECT="Ineffective (Score: 1-2) — $EVIDENCE"
          elif echo "$EVIDENCE" | grep -qi "partial"; then
            EFFECT="Partial (Score: 3) — $EVIDENCE"
          else
            EFFECT="Effective (Score: 4-5) — $EVIDENCE"
          fi

          # Use sed to replace [PENDING] in the mutation block
          # This is tricky because we need to scope to the specific mutation block
          # Use a Python one-liner for precision
          python3 -c "
import re
with open('$MUTATION_LOG', 'r') as f:
    content = f.read()

# Find the mutation block and replace [PENDING] in measured effect
pattern = r'(## Mutation $MUTATION_ID.*?Measured effect: )\\*?\[?PENDING\]?\\*?'
replacement = r'\1$EFFECT'
content = re.sub(pattern, replacement, content, flags=re.DOTALL)

with open('$MUTATION_LOG', 'w') as f:
    f.write(content)
" 2>/dev/null || echo "  Python replacement failed for $MUTATION_ID"
          echo "  Updated mutation-log.md: $MUTATION_ID"
        fi
      fi

      # Update mutation-state.md: increment Builds Tested, update score
      if grep -q "^| $MUTATION_ID " "$MUTATION_STATE"; then
        # Increment builds tested
        python3 -c "
import re
with open('$MUTATION_STATE', 'r') as f:
    content = f.read()

# Find the row and increment Builds Tested
pattern = r'(\| $MUTATION_ID \|[^\n]*\|[^\n]*\|[^\n]*\|[^\n]*\|)([0-9]+)( \|)'

def increment(match):
    return match.group(1) + str(int(match.group(2)) + 1) + match.group(3)

content = re.sub(pattern, increment, content)

with open('$MUTATION_STATE', 'w') as f:
    f.write(content)
" 2>/dev/null || echo "  Python replacement failed for $MUTATION_ID in state"
        echo "  Updated mutation-state.md: $MUTATION_ID"
      fi
    fi
  fi
done < "$MUTATIONS_APPLIED"

echo "Mutation state auto-update complete."

