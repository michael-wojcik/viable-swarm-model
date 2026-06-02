#!/bin/bash
# VSM Subagent Counter Hook
# Tracks every subagent spawn for the capability matrix.
# Appends to ~/.vsm-telemetry/subagents.jsonl
#
# Event: SubagentStart

set -euo pipefail

PAYLOAD=$(cat)
SESSION_ID=$(echo "$PAYLOAD" | jq -r '.session_id // "unknown"')
CWD=$(echo "$PAYLOAD" | jq -r '.cwd // "/tmp"')
AGENT_NAME=$(echo "$PAYLOAD" | jq -r '.agent_name // "unknown"')
PROMPT=$(echo "$PAYLOAD" | jq -r '.prompt // ""')

# Truncate prompt for logging (first 200 chars)
PROMPT_TRUNC="${PROMPT:0:200}"

TELEMETRY_DIR="$HOME/.vsm-telemetry"
mkdir -p "$TELEMETRY_DIR"

ENTRY=$(jq -n \
    --arg ts "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
    --arg session_id "$SESSION_ID" \
    --arg cwd "$CWD" \
    --arg agent_name "$AGENT_NAME" \
    --arg prompt_trunc "$PROMPT_TRUNC" \
    '{ts: $ts, session_id: $session_id, cwd: $cwd, agent_name: $agent_name, prompt_trunc: $prompt_trunc, event: "subagent_start"}')

echo "$ENTRY" >> "$TELEMETRY_DIR/subagents.jsonl"

exit 0
