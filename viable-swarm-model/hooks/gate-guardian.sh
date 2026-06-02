#!/bin/bash
# VSM Phase 4 Gate Guardian Hook
# Blocks fraudulent gate-pass documents by independently checking test results.
#
# Event: PreToolUse (matcher: WriteFile|StrReplaceFile)
# If the tool writes .kimi/phase4-gate.md claiming PASS while test logs show failures,
# this hook BLOCKS (exit 2) the WriteFile call.

set -euo pipefail

PAYLOAD=$(cat)
FILE_PATH=$(echo "$PAYLOAD" | jq -r '.tool_input.path // .tool_input.file_path // ""')
CONTENT=$(echo "$PAYLOAD" | jq -r '.tool_input.content // ""')
CWD=$(echo "$PAYLOAD" | jq -r '.cwd // "/tmp"')

# Only gatekeep phase4-gate.md
if [[ ! "$FILE_PATH" =~ phase4-gate\.md$ ]]; then
    exit 0
fi

# If gate claims PASS, verify test results
if echo "$CONTENT" | grep -qiE '\bPASS\b|\bpass\b'; then
    # Look for test output files in .kimi/
    TEST_DIR="$CWD/.kimi"
    FAIL_FOUND=false

    if [[ -d "$TEST_DIR" ]]; then
        # Check pytest output
        if find "$TEST_DIR" -maxdepth 1 -name '*pytest*' -o -name '*test*' | head -1 | grep -q .; then
            for f in "$TEST_DIR"/*pytest* "$TEST_DIR"/*test* "$TEST_DIR"/*npm*; do
                [[ -f "$f" ]] || continue
                if grep -qiE 'failed|FAIL|error|Error' "$f" 2>/dev/null; then
                    FAIL_FOUND=true
                    break
                fi
            done
        fi
    fi

    # Also check for pytest-output.log or npm-test.log in build root
    for f in "$CWD/pytest-output.log" "$CWD/npm-test.log" "$CWD/test-output.log"; do
        [[ -f "$f" ]] || continue
        if grep -qiE 'failed|FAIL' "$f" 2>/dev/null; then
            FAIL_FOUND=true
            break
        fi
    done

    if [[ "$FAIL_FOUND" == true ]]; then
        echo "FRAUDULENT GATE PASS BLOCKED by gate-guardian.sh: Test results show failures. Fix ALL tests before claiming PASS." >&2
        # Write marker for S5 to detect
        echo "BLOCKED_BY_HOOK:gate-guardian:$(date -u +%Y-%m-%dT%H:%M:%SZ)" >> "$TEST_DIR/.gate-guardian-blocks.log"
        exit 2
    fi
fi

exit 0
