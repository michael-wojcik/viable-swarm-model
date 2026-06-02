#!/bin/bash
# VSM Session End Hook
# Parses telemetry logs and updates skill-state.md with efficiency baselines.
# Clears per-session telemetry after processing.
#
# Event: SessionEnd

set -euo pipefail

PAYLOAD=$(cat)
SESSION_ID=$(echo "$PAYLOAD" | jq -r '.session_id // "unknown"')
CWD=$(echo "$PAYLOAD" | jq -r '.cwd // "/tmp"')
REASON=$(echo "$PAYLOAD" | jq -r '.reason // "unknown"')

TELEMETRY_DIR="$HOME/.vsm-telemetry"
SKILL_STATE="$HOME/vsm/viable-swarm-model/references/skill-state.md"

# Only process if we have telemetry
if [[ ! -d "$TELEMETRY_DIR" ]]; then
    exit 0
fi

# Count file writes for this session
FILE_WRITES=0
if [[ -f "$TELEMETRY_DIR/file-writes.jsonl" ]]; then
    FILE_WRITES=$(grep -c "$SESSION_ID" "$TELEMETRY_DIR/file-writes.jsonl" 2>/dev/null || true)
    FILE_WRITES=${FILE_WRITES:-0}
fi

# Count subagents spawned for this session
SUBAGENT_COUNT=0
if [[ -f "$TELEMETRY_DIR/subagents.jsonl" ]]; then
    SUBAGENT_COUNT=$(grep -c "$SESSION_ID" "$TELEMETRY_DIR/subagents.jsonl" 2>/dev/null || true)
    SUBAGENT_COUNT=${SUBAGENT_COUNT:-0}
fi

# Count unique agent types
AGENT_TYPES=""
if [[ -f "$TELEMETRY_DIR/subagents.jsonl" ]]; then
    AGENT_TYPES=$(grep "$SESSION_ID" "$TELEMETRY_DIR/subagents.jsonl" 2>/dev/null | jq -r '.agent_name' | sort -u | tr '\n' ',' | sed 's/,$//')
fi

# Calculate session duration from session log
SESSION_START=""
SESSION_END="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
DURATION_MIN="unknown"
if [[ -f "$TELEMETRY_DIR/sessions.jsonl" ]]; then
    SESSION_START=$(grep "$SESSION_ID" "$TELEMETRY_DIR/sessions.jsonl" 2>/dev/null | head -1 | jq -r '.ts // ""')
    if [[ -n "$SESSION_START" && "$SESSION_START" != "null" ]]; then
        START_EPOCH=$(date -j -f "%Y-%m-%dT%H:%M:%SZ" "$SESSION_START" +%s 2>/dev/null || date -d "$SESSION_START" +%s 2>/dev/null || echo "")
        END_EPOCH=$(date -j -f "%Y-%m-%dT%H:%M:%SZ" "$SESSION_END" +%s 2>/dev/null || date -d "$SESSION_END" +%s 2>/dev/null || echo "")
        if [[ -n "$START_EPOCH" && -n "$END_EPOCH" ]]; then
            DURATION_SEC=$((END_EPOCH - START_EPOCH))
            DURATION_MIN=$((DURATION_SEC / 60))
        fi
    fi
fi

# Build telemetry update block
UPDATE_BLOCK=$(cat << EOF

## Session Telemetry — $SESSION_END
| Metric | Value |
|--------|-------|
| Session ID | $SESSION_ID |
| File writes | $FILE_WRITES |
| Subagents spawned | $SUBAGENT_COUNT |
| Agent types | $AGENT_TYPES |
| Duration (min) | $DURATION_MIN |
| Stop reason | $REASON |
EOF
)

# Append to skill-state.md if it exists
if [[ -f "$SKILL_STATE" ]]; then
    # Check if there's a "## Session Telemetry" section; append or create
    if grep -q "## Session Telemetry" "$SKILL_STATE"; then
        # Append after the last Session Telemetry entry, before any final marker
        echo "$UPDATE_BLOCK" >> "$SKILL_STATE"
    else
        echo -e "\n## Session Telemetry Log\n$UPDATE_BLOCK" >> "$SKILL_STATE"
    fi
fi

# Clean up per-session telemetry files (keep aggregated logs)
# We keep the jsonl files as they accumulate across sessions for rolling averages
# But mark session as processed
if [[ -f "$TELEMETRY_DIR/sessions.jsonl" ]]; then
    # Remove processed session start entry to keep file from growing infinitely
    grep -v "$SESSION_ID" "$TELEMETRY_DIR/sessions.jsonl" > "$TELEMETRY_DIR/sessions.jsonl.tmp" 2>/dev/null || true
    mv "$TELEMETRY_DIR/sessions.jsonl.tmp" "$TELEMETRY_DIR/sessions.jsonl" 2>/dev/null || true
fi

exit 0
