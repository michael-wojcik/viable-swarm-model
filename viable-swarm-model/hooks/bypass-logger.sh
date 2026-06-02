#!/bin/bash
# VSM Bypass Logger Hook
# Logs every tool use failure as a potential "bypass attempt" for behavioral analysis.
# Helps detect patterns where S5 repeatedly tries blocked operations.
#
# Event: PostToolUseFailure

set -euo pipefail

PAYLOAD=$(cat)
SESSION_ID=$(echo "$PAYLOAD" | jq -r '.session_id // "unknown"')
CWD=$(echo "$PAYLOAD" | jq -r '.cwd // "/tmp"')
TOOL_NAME=$(echo "$PAYLOAD" | jq -r '.tool_name // "unknown"')
FILE_PATH=$(echo "$PAYLOAD" | jq -r '.tool_input.path // .tool_input.file_path // ""')
ERROR=$(echo "$PAYLOAD" | jq -r '.error // ""')

TELEMETRY_DIR="$HOME/.vsm-telemetry"
mkdir -p "$TELEMETRY_DIR"

# Determine if this looks like a hook block (exit code 2 from a PreToolUse hook)
IS_HOOK_BLOCK=false
if echo "$ERROR" | grep -qiE 'blocked|exit code 2|permission denied|FRAUDULENT|INLINE FIX|STRUCTURAL MUTATION'; then
    IS_HOOK_BLOCK=true
fi

# Determine if this is a retry pattern (same tool + file in quick succession)
RETRY_COUNT=0
if [[ -f "$TELEMETRY_DIR/bypass-attempts.jsonl" ]]; then
    RETRY_COUNT=$(grep -c "\"session_id\":\"$SESSION_ID\".*\"file_path\":\"$FILE_PATH\".*\"tool_name\":\"$TOOL_NAME\"" "$TELEMETRY_DIR/bypass-attempts.jsonl" 2>/dev/null || true)
    RETRY_COUNT=${RETRY_COUNT:-0}
fi

# Build log entry
ENTRY=$(jq -n -c \
    --arg ts "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
    --arg session_id "$SESSION_ID" \
    --arg cwd "$CWD" \
    --arg tool_name "$TOOL_NAME" \
    --arg file_path "$FILE_PATH" \
    --arg error "$ERROR" \
    --argjson is_hook_block "$([[ "$IS_HOOK_BLOCK" == true ]] && echo true || echo false)" \
    --argjson retry_count "$RETRY_COUNT" \
    '{ts: $ts, session_id: $session_id, cwd: $cwd, tool_name: $tool_name, file_path: $file_path, error: $error, is_hook_block: $is_hook_block, retry_count: $retry_count, event: "bypass_attempt"}')

echo "$ENTRY" >> "$TELEMETRY_DIR/bypass-attempts.jsonl"

# If this is a retry (>2 attempts on same file), escalate warning
if [[ "$RETRY_COUNT" -ge 2 ]]; then
    echo "BYPASS PATTERN ALERT: Tool '$TOOL_NAME' on '$FILE_PATH' has failed $((RETRY_COUNT + 1)) times this session. This may indicate S5 is trying to circumvent enforcement. Review bypass-attempts.jsonl for pattern analysis." >&2
fi

exit 0
