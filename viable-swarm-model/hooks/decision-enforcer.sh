#!/bin/bash
# VSM Decision Enforcer Hook
# Verifies decisions.md has a corresponding entry when plan.md or approval markers are written.
# Advisory only — warns to stderr but does not block (PostToolUse cannot block).
#
# Event: PostToolUse (matcher: WriteFile|StrReplaceFile)

set -euo pipefail

PAYLOAD=$(cat)
SESSION_ID=$(echo "$PAYLOAD" | jq -r '.session_id // "unknown"')
CWD=$(echo "$PAYLOAD" | jq -r '.cwd // "/tmp"')
TOOL_NAME=$(echo "$PAYLOAD" | jq -r '.tool_name // "unknown"')
FILE_PATH=$(echo "$PAYLOAD" | jq -r '.tool_input.file_path // ""')

decisions_file="$HOME/vsm/viable-swarm-model/references/decisions.md"

# Only care about plan.md writes and approval marker files
IS_PLAN=false
IS_APPROVAL=false

if [[ "$FILE_PATH" =~ plan\.md$ ]]; then
    IS_PLAN=true
fi

if [[ "$FILE_PATH" =~ \.structural-mutation-approved$ ]]; then
    IS_APPROVAL=true
fi

if [[ "$IS_PLAN" == false && "$IS_APPROVAL" == false ]]; then
    exit 0
fi

# Check if decisions.md exists and has a recent entry
if [[ ! -f "$decisions_file" ]]; then
    echo "DECISION ENFORCER WARNING: $FILE_PATH was written but decisions.md does not exist. S5 MUST log decisions at Phase 0 (plan approval) and Phase 8c (structural mutation approval)." >&2
    exit 0
fi

# Check for a recent D[N] entry (within last 7 days) referencing this session or a plan/approval decision
RECENT_ENTRY=$(grep -E '^## D\[?[0-9]+\]?\s*—' "$decisions_file" 2>/dev/null | tail -5 || true)

if [[ -z "$RECENT_ENTRY" ]]; then
    echo "DECISION ENFORCER WARNING: $FILE_PATH was written but decisions.md has no D[N] entries. S5 MUST append a decision entry with rationale before proceeding." >&2
    exit 0
fi

# Look for session_id match or plan/structural keywords in last 3 entries
LAST_ENTRIES=$(tail -30 "$decisions_file" 2>/dev/null || true)
HAS_SESSION=false
if echo "$LAST_ENTRIES" | grep -q "$SESSION_ID" 2>/dev/null; then
    HAS_SESSION=true
fi

HAS_PLAN_DECISION=false
if echo "$LAST_ENTRIES" | grep -qiE 'plan|approved|structural mutation' 2>/dev/null; then
    HAS_PLAN_DECISION=true
fi

if [[ "$HAS_SESSION" == false && "$HAS_PLAN_DECISION" == false ]]; then
    echo "DECISION ENFORCER WARNING: $FILE_PATH written but no matching D[N] entry found in decisions.md for session $SESSION_ID. S5 MUST log the decision rationale." >&2
    exit 0
fi

exit 0
