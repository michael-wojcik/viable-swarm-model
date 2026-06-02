#!/bin/bash
# VSM Stop Verifier Hook
# Blocks session end if Phase 8c-ii is incomplete.
# Verifies mutations-applied.md exists and measured effects are not pending.
# Also auto-parses trainer backfill output and writes measured effects to mutation-log.md.
#
# Event: Stop
# Can block once (anti-loop protection built into kimi-cli).

set -euo pipefail

PAYLOAD=$(cat)
CWD=$(echo "$PAYLOAD" | jq -r '.cwd // "/tmp"')
STOP_HOOK_ACTIVE=$(echo "$PAYLOAD" | jq -r '.stop_hook_active // false')

# Anti-loop: if stop hook already fired once, allow exit
if [[ "$STOP_HOOK_ACTIVE" == "true" ]]; then
    exit 0
fi

KIMI_DIR="$CWD/.kimi"
MUTATIONS_FILE="$KIMI_DIR/mutations-applied.md"
MUTATION_LOG="$HOME/vsm/viable-swarm-model/references/mutation-log.md"

# --- Auto-parse trainer backfill and fill measured effects ---
# Look for trainer backfill files in .kimi/ directory
if [[ -d "$KIMI_DIR" && -f "$MUTATION_LOG" ]]; then
    for backfill_file in "$KIMI_DIR"/*backfill* "$KIMI_DIR"/trainer-output* "$KIMI_DIR"/fitness-report*; do
        [[ -f "$backfill_file" ]] || continue

        # Extract mutation effectiveness table lines
        # Pattern: | M[ID] | [effectiveness] | [notes] |
        while IFS= read -r line; do
            if echo "$line" | grep -qE '^\s*\|\s*(FB[0-9]+-[0-9]+|M[0-9]+|Mutation [0-9]+)'; then
                MUTATION_ID=$(echo "$line" | awk -F'|' '{print $2}' | tr -d ' ')
                EFFECT=$(echo "$line" | awk -F'|' '{print $3}' | sed 's/^ *//;s/ *$//')
                NOTES=$(echo "$line" | awk -F'|' '{print $4}' | sed 's/^ *//;s/ *$//')

                if [[ -n "$MUTATION_ID" && -n "$EFFECT" && "$EFFECT" != "Effectiveness" ]]; then
                    # Use awk to find the mutation block and replace PENDING within it
                    awk -v mut_id="$MUTATION_ID" -v effect="$EFFECT" -v notes="$NOTES" '
                        BEGIN { found=0 }
                        $0 ~ ("## Mutation " mut_id) { found=1 }
                        found && /Measured effect.*\[PENDING\]/ {
                            sub(/\[PENDING\]/, "[" effect "] (auto-filled from trainer backfill: " notes ")")
                            found=0
                        }
                        { print }
                    ' "$MUTATION_LOG" > "$MUTATION_LOG.tmp" && mv "$MUTATION_LOG.tmp" "$MUTATION_LOG"
                    if [[ $? -eq 0 ]]; then
                        echo "stop-verifier.sh: Auto-filled measured effect for $MUTATION_ID → $EFFECT" >&2
                    fi
                fi
            fi
        done < "$backfill_file"
    done
fi

# Only verify if this looks like a VSM build directory
if [[ ! -d "$KIMI_DIR" ]]; then
    exit 0
fi

# Check 1: mutations-applied.md must exist
if [[ ! -f "$MUTATIONS_FILE" ]]; then
    # However, don't block if this is a very early session (no build artifacts yet)
    if [[ -f "$KIMI_DIR/meta-report.md" || -f "$KIMI_DIR/lessons.md" || -f "$KIMI_DIR/security-report.md" ]]; then
        echo "STOP BLOCKED by stop-verifier.sh: Phase 8c-ii incomplete. .kimi/mutations-applied.md is missing. Every build MUST log applied mutations before completion." >&2
        echo '{"hookSpecificOutput":{"permissionDecision":"deny","permissionDecisionReason":"Phase 8c-ii incomplete: mutations-applied.md missing. Write it before stopping."}}'
        exit 0
    fi
fi

# Check 2: No PENDING measured effects in mutation-log.md
if [[ -f "$MUTATION_LOG" ]]; then
    # Count "Measured effect: [PENDING]" or "Measured effect: [pending]" entries
    # Also catch empty measured effect fields from recent sessions
    PENDING_COUNT=$(grep -ciE '\*\*Measured effect\*\*:\s*\[PENDING\]|\*\*Measured effect\*\*:\s*\[pending\]|\*\*Measured effect\*\*:\s*$|\*\*Measured effect\*\*:\s*\[.*fill.*\]' "$MUTATION_LOG" 2>/dev/null || true)
    PENDING_COUNT=${PENDING_COUNT:-0}

    # Only block if there are actual pending entries (not just template placeholders)
    # We look for entries that have a real mutation ID pattern
    if [[ "$PENDING_COUNT" -gt 0 ]]; then
        echo "STOP BLOCKED by stop-verifier.sh: $PENDING_COUNT mutation(s) have pending measured effects. Complete the mutation effectiveness audit before stopping." >&2
        echo '{"hookSpecificOutput":{"permissionDecision":"deny","permissionDecisionReason":"Measured effects pending. Complete mutation effectiveness audit before stopping."}}'
        exit 0
    fi
fi

exit 0
