#!/bin/bash
# VSM Phase 6/7 Boundary Guardian Hook
# Blocks inline fixes during integration verification.
# If synthesis-integration.md exists but re-audit-report.md does NOT exist,
# any write to source files is blocked.
#
# Event: PreToolUse (matcher: WriteFile|StrReplaceFile)

set -euo pipefail

PAYLOAD=$(cat)
FILE_PATH=$(echo "$PAYLOAD" | jq -r '.tool_input.file_path // ""')
CWD=$(echo "$PAYLOAD" | jq -r '.cwd // "/tmp"')

# Only check source code files
if [[ ! "$FILE_PATH" =~ \.(py|ts|tsx|js|jsx|go|rs|java|kt|swift)$ ]]; then
    exit 0
fi

KIMI_DIR="$CWD/.kimi"
SYNTHESIS="$KIMI_DIR/synthesis-integration.md"
REAUDIT="$KIMI_DIR/re-audit-report.md"

# If Phase 6 synthesis exists but Phase 7b re-audit does NOT exist → BLOCK
if [[ -f "$SYNTHESIS" && ! -f "$REAUDIT" ]]; then
    echo "INLINE FIX BLOCKED by boundary-guardian.sh: Phase 6 integration complete but Phase 7b re-audit not done. Spawn vsm_backend_fix_agent and complete re-audit before modifying source files." >&2
    echo "BLOCKED_BY_HOOK:boundary-guardian:$(date -u +%Y-%m-%dT%H:%M:%SZ):$FILE_PATH" >> "$KIMI_DIR/.boundary-guardian-blocks.log"
    exit 2
fi

exit 0
