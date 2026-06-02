#!/bin/bash
# VSM Agent Performance Scorer Hook
# Heuristic scoring of subagent output → updates capability matrix in skill-state.md
#
# Event: SubagentStop
# Receives: session_id, cwd, agent_name, response

set -euo pipefail

PAYLOAD=$(cat)
SESSION_ID=$(echo "$PAYLOAD" | jq -r '.session_id // "unknown"')
CWD=$(echo "$PAYLOAD" | jq -r '.cwd // "/tmp"')
AGENT_NAME=$(echo "$PAYLOAD" | jq -r '.agent_name // "unknown"')
RESPONSE=$(echo "$PAYLOAD" | jq -r '.response // ""')

SKILL_STATE="$HOME/vsm/viable-swarm-model/references/skill-state.md"
TELEMETRY_DIR="$HOME/.vsm-telemetry"
mkdir -p "$TELEMETRY_DIR"

# Heuristic scoring from response content
SCORE=3  # neutral default
BLOCKERS=0
ISSUES=0
PASSES=0

if [[ -n "$RESPONSE" ]]; then
    # Count BLOCKERs (allow BLOCKER or BLOCKERs)
    BLOCKERS=$(echo "$RESPONSE" | grep -oiE 'BLOCKERS?' | wc -l | tr -d ' ' || true)
    # Count ISSUEs (allow ISSUE or ISSUES)
    ISSUES=$(echo "$RESPONSE" | grep -oiE 'ISSUES?' | wc -l | tr -d ' ' || true)
    # Count PASSes (allow PASS or PASSED)
    PASSES=$(echo "$RESPONSE" | grep -oiE 'PASS(ED)?' | wc -l | tr -d ' ' || true)
fi

# Calculate score (1-5 scale)
if [[ "$BLOCKERS" -gt 2 ]]; then
    SCORE=1
elif [[ "$BLOCKERS" -gt 0 ]]; then
    SCORE=2
elif [[ "$ISSUES" -gt 3 ]]; then
    SCORE=2
elif [[ "$PASSES" -gt 0 && "$ISSUES" -eq 0 && "$BLOCKERS" -eq 0 ]]; then
    SCORE=5
elif [[ "$PASSES" -gt 0 && "$ISSUES" -le 2 ]]; then
    SCORE=4
else
    SCORE=3
fi

# Log the score
ENTRY=$(jq -n -c \
    --arg ts "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
    --arg session_id "$SESSION_ID" \
    --arg agent_name "$AGENT_NAME" \
    --argjson score "$SCORE" \
    --argjson blockers "$BLOCKERS" \
    --argjson issues "$ISSUES" \
    --argjson passes "$PASSES" \
    '{ts: $ts, session_id: $session_id, agent_name: $agent_name, score: $score, blockers: $blockers, issues: $issues, passes: $passes, event: "agent_score"}')

echo "$ENTRY" >> "$TELEMETRY_DIR/agent-scores.jsonl"

# Update skill-state.md capability matrix if it exists
if [[ -f "$SKILL_STATE" ]]; then
    # Only update for known VSM agents
    if grep -q "^| $AGENT_NAME " "$SKILL_STATE" 2>/dev/null; then
        # Extract current Last 3 Scores, prepend new score, keep last 3
        CURRENT_LINE=$(grep "^| $AGENT_NAME " "$SKILL_STATE" || true)
        if [[ -n "$CURRENT_LINE" ]]; then
            CURRENT_SCORES=$(echo "$CURRENT_LINE" | awk -F'|' '{print $5}' | tr -d ' ')
            # Build new scores list (new score + previous, truncated to 3)
            if [[ "$CURRENT_SCORES" == "—" || -z "$CURRENT_SCORES" ]]; then
                NEW_SCORES="$SCORE"
            else
                NEW_SCORES="$SCORE, $CURRENT_SCORES"
            fi
            # Keep only last 3
            NEW_SCORES=$(echo "$NEW_SCORES" | tr ',' '\n' | head -3 | tr '\n' ',' | sed 's/,$//; s/,/, /g' | sed 's/^ *//; s/ *$//')

            # Replace the line in skill-state.md
            NEW_LINE=$(echo "$CURRENT_LINE" | awk -F'|' -v new_scores="$NEW_SCORES" '{
                for(i=1;i<=NF;i++) {
                    gsub(/^ +| +$/, "", $i);
                }
                printf "| %s | %s | %s | %s | %s |\n", $2, $3, $4, new_scores, $6
            }')
            # Use sed to replace the specific line
            ESCAPED_CURRENT=$(printf '%s\n' "$CURRENT_LINE" | sed 's/[[\.*^$()+?{|]/\\&/g')
            ESCAPED_NEW=$(printf '%s\n' "$NEW_LINE" | sed 's/[[\.*^$()+?{|]/\\&/g')
            sed -i.bak "s/$ESCAPED_CURRENT/$ESCAPED_NEW/" "$SKILL_STATE" 2>/dev/null || true
            rm -f "$SKILL_STATE.bak"
        fi
    fi
fi

exit 0
