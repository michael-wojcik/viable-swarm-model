#!/bin/bash
# VSM Telemetry Logger Hook
# Logs every file write for efficiency tracking.
# Appends to ~/.vsm-telemetry/file-writes.jsonl
#
# Event: PostToolUse (matcher: WriteFile|StrReplaceFile)

set -euo pipefail

PAYLOAD=$(cat)
SESSION_ID=$(echo "$PAYLOAD" | jq -r '.session_id // "unknown"')
CWD=$(echo "$PAYLOAD" | jq -r '.cwd // "/tmp"')
TOOL_NAME=$(echo "$PAYLOAD" | jq -r '.tool_name // "unknown"')
FILE_PATH=$(echo "$PAYLOAD" | jq -r '.tool_input.file_path // ""')

# Create telemetry directory
TELEMETRY_DIR="$HOME/.vsm-telemetry"
mkdir -p "$TELEMETRY_DIR"

# Log the file write
ENTRY=$(jq -n \
    --arg ts "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
    --arg session_id "$SESSION_ID" \
    --arg cwd "$CWD" \
    --arg tool_name "$TOOL_NAME" \
    --arg file_path "$FILE_PATH" \
    '{ts: $ts, session_id: $session_id, cwd: $cwd, tool_name: $tool_name, file_path: $file_path, event: "file_write"}')

echo "$ENTRY" >> "$TELEMETRY_DIR/file-writes.jsonl"

exit 0
