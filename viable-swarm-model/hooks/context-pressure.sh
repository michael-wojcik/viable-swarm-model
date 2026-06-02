#!/bin/bash
# VSM Context Pressure Hook
# Warns when context compaction is imminent (>200k tokens).
# Advisory — warns to stderr so S5 sees it in context.
#
# Event: PreCompact
# Payload: session_id, cwd, trigger, token_count

set -euo pipefail

PAYLOAD=$(cat)
SESSION_ID=$(echo "$PAYLOAD" | jq -r '.session_id // "unknown"')
CWD=$(echo "$PAYLOAD" | jq -r '.cwd // "/tmp"')
TRIGGER=$(echo "$PAYLOAD" | jq -r '.trigger // "unknown"')
TOKEN_COUNT=$(echo "$PAYLOAD" | jq -r '.token_count // 0')

TELEMETRY_DIR="$HOME/.vsm-telemetry"
mkdir -p "$TELEMETRY_DIR"

# Log the compaction event
ENTRY=$(jq -n -c \
    --arg ts "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
    --arg session_id "$SESSION_ID" \
    --arg cwd "$CWD" \
    --arg trigger "$TRIGGER" \
    --argjson token_count "$TOKEN_COUNT" \
    '{ts: $ts, session_id: $session_id, cwd: $cwd, trigger: $trigger, token_count: $token_count, event: "context_compaction"}')

echo "$ENTRY" >> "$TELEMETRY_DIR/context-compactions.jsonl"

# Warn if tokens exceed threshold
THRESHOLD=200000
if [[ "$TOKEN_COUNT" -gt "$THRESHOLD" ]]; then
    echo "CONTEXT PRESSURE ALERT: Context at $TOKEN_COUNT tokens (threshold: $THRESHOLD). Compaction trigger: $TRIGGER. S5 should reduce file reads, spawn synthesizers, or checkpoint progress before losing state." >&2
fi

exit 0
