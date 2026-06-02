#!/bin/bash
# VSM Hook Validation Test Suite
# Simulates hook events and verifies correct behavior.
# Run with: bash ~/vsm/viable-swarm-model/hooks/test-hooks.sh

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PASSED=0
FAILED=0

TMPDIR=$(mktemp -d)
trap "rm -rf $TMPDIR" EXIT

# Helper: run a hook script with JSON payload
# Returns the hook's exit code without triggering set -e
run_hook() {
    local script="$1"
    local payload="$2"
    local rc
    bash "$script" <<< "$payload" || rc=$?
    if [[ -z "${rc:-}" ]]; then
        rc=0
    fi
    return $rc
}

echo "========================================"
echo "VSM Hook Validation Test Suite"
echo "========================================"
echo ""

# --- Test 1: gate-guardian blocks fraudulent PASS ---
echo "Test 1: gate-guardian blocks fraudulent phase4-gate.md PASS..."
mkdir -p "$TMPDIR/.kimi"
echo "test_foo.py::test_bar FAILED" > "$TMPDIR/.kimi/pytest-output.log"
PAYLOAD=$(jq -n \
    --arg cwd "$TMPDIR" \
    --arg file_path "$TMPDIR/.kimi/phase4-gate.md" \
    --arg content "## Phase 4 Gate\nStatus: PASS\nAll tests passing." \
    '{cwd: $cwd, tool_input: {file_path: $file_path, content: $content}}')

if run_hook "$SCRIPT_DIR/gate-guardian.sh" "$PAYLOAD"; then
    echo "  ❌ FAILED: Should have blocked fraudulent PASS"
    ((FAILED++))
else
    echo "  ✅ PASSED: Correctly blocked fraudulent PASS"
    ((PASSED++))
fi

# --- Test 2: gate-guardian allows legitimate PASS ---
echo "Test 2: gate-guardian allows legitimate phase4-gate.md PASS..."
rm -f "$TMPDIR/.kimi/pytest-output.log"
echo "test_foo.py::test_bar PASSED" > "$TMPDIR/.kimi/pytest-output.log"
PAYLOAD=$(jq -n \
    --arg cwd "$TMPDIR" \
    --arg file_path "$TMPDIR/.kimi/phase4-gate.md" \
    --arg content "## Phase 4 Gate\nStatus: PASS\nAll tests passing." \
    '{cwd: $cwd, tool_input: {file_path: $file_path, content: $content}}')

if run_hook "$SCRIPT_DIR/gate-guardian.sh" "$PAYLOAD"; then
    echo "  ✅ PASSED: Correctly allowed legitimate PASS"
    ((PASSED++))
else
    echo "  ❌ FAILED: Should have allowed legitimate PASS"
    ((FAILED++))
fi

# --- Test 3: boundary-guardian blocks inline fix ---
echo "Test 3: boundary-guardian blocks inline fix during Phase 6/7..."
mkdir -p "$TMPDIR/.kimi"
touch "$TMPDIR/.kimi/synthesis-integration.md"
PAYLOAD=$(jq -n \
    --arg cwd "$TMPDIR" \
    --arg file_path "$TMPDIR/src/main.py" \
    --arg content "print('fix')" \
    '{cwd: $cwd, tool_input: {file_path: $file_path, content: $content}}')

if run_hook "$SCRIPT_DIR/boundary-guardian.sh" "$PAYLOAD"; then
    echo "  ❌ FAILED: Should have blocked inline fix"
    ((FAILED++))
else
    echo "  ✅ PASSED: Correctly blocked inline fix"
    ((PASSED++))
fi

# --- Test 4: boundary-guardian allows fix after re-audit ---
echo "Test 4: boundary-guardian allows fix after re-audit..."
touch "$TMPDIR/.kimi/re-audit-report.md"
if run_hook "$SCRIPT_DIR/boundary-guardian.sh" "$PAYLOAD"; then
    echo "  ✅ PASSED: Correctly allowed fix after re-audit"
    ((PASSED++))
else
    echo "  ❌ FAILED: Should have allowed fix after re-audit"
    ((FAILED++))
fi

# --- Test 5: structural-guardian blocks unapproved SKILL.md change ---
echo "Test 5: structural-guardian blocks unapproved SKILL.md change..."
PAYLOAD=$(jq -n \
    --arg cwd "$TMPDIR" \
    --arg file_path "$TMPDIR/SKILL.md" \
    --arg content "# Updated skill" \
    '{cwd: $cwd, tool_input: {file_path: $file_path, content: $content}}')

if run_hook "$SCRIPT_DIR/structural-guardian.sh" "$PAYLOAD"; then
    echo "  ❌ FAILED: Should have blocked unapproved structural mutation"
    ((FAILED++))
else
    echo "  ✅ PASSED: Correctly blocked unapproved structural mutation"
    ((PASSED++))
fi

# --- Test 6: structural-guardian allows approved change ---
echo "Test 6: structural-guardian allows approved SKILL.md change..."
mkdir -p "$TMPDIR/.kimi"
touch "$TMPDIR/.kimi/.structural-mutation-approved"
if run_hook "$SCRIPT_DIR/structural-guardian.sh" "$PAYLOAD"; then
    echo "  ✅ PASSED: Correctly allowed approved structural mutation"
    ((PASSED++))
else
    echo "  ❌ FAILED: Should have allowed approved structural mutation"
    ((FAILED++))
fi

# --- Test 7: session-start creates skill-state.md if missing ---
echo "Test 7: session-start creates skill-state.md if missing..."
export HOME="$TMPDIR"
PAYLOAD=$(jq -n \
    --arg session_id "test-session" \
    --arg cwd "$TMPDIR" \
    --arg source "startup" \
    '{session_id: $session_id, cwd: $cwd, source: $source}')

run_hook "$SCRIPT_DIR/session-start.sh" "$PAYLOAD"
if [[ -f "$TMPDIR/vsm/viable-swarm-model/references/skill-state.md" ]]; then
    echo "  ✅ PASSED: Created skill-state.md template"
    ((PASSED++))
else
    echo "  ❌ FAILED: Did not create skill-state.md"
    ((FAILED++))
fi
unset HOME

echo ""
echo "========================================"
echo "Results: $PASSED passed, $FAILED failed"
echo "========================================"

if [[ "$FAILED" -gt 0 ]]; then
    exit 1
fi
exit 0
