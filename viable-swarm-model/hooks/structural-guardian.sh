#!/bin/bash
# VSM Structural Mutation Guardian Hook
# Blocks unapproved structural mutations (SKILL.md, agent architecture changes).
# Structural mutations require a .kimi/.structural-mutation-approved marker file.
#
# Event: PreToolUse (matcher: WriteFile|StrReplaceFile)

set -euo pipefail

PAYLOAD=$(cat)
FILE_PATH=$(echo "$PAYLOAD" | jq -r '.tool_input.file_path // ""')
CWD=$(echo "$PAYLOAD" | jq -r '.cwd // "/tmp"')

# Check if this is a structural mutation target
IS_STRUCTURAL=false

# SKILL.md changes
if [[ "$FILE_PATH" =~ SKILL\.md$ ]]; then
    IS_STRUCTURAL=true
fi

# Agent registry changes
if [[ "$FILE_PATH" =~ vsm-main\.yaml$ ]]; then
    IS_STRUCTURAL=true
fi

# Agent file creation/deletion
if [[ "$FILE_PATH" =~ /agents/ && "$FILE_PATH" =~ \.md$ ]]; then
    IS_STRUCTURAL=true
fi

# Reference files that are architecture-level (flow diagrams, role maps)
if [[ "$FILE_PATH" =~ /references/ ]]; then
    if [[ "$FILE_PATH" =~ flow-diagram || "$FILE_PATH" =~ role-map || "$FILE_PATH" =~ orchestration ]]; then
        IS_STRUCTURAL=true
    fi
fi

if [[ "$IS_STRUCTURAL" == false ]]; then
    exit 0
fi

# Check for approval marker
MARKER="$CWD/.kimi/.structural-mutation-approved"
if [[ ! -f "$MARKER" ]]; then
    echo "STRUCTURAL MUTATION BLOCKED by structural-guardian.sh: Changes to $FILE_PATH require explicit user approval. To approve, create: $MARKER (e.g., 'touch .kimi/.structural-mutation-approved')." >&2
    mkdir -p "$CWD/.kimi"
    echo "BLOCKED_BY_HOOK:structural-guardian:$(date -u +%Y-%m-%dT%H:%M:%SZ):$FILE_PATH" >> "$CWD/.kimi/.structural-guardian-blocks.log"
    exit 2
fi

exit 0
