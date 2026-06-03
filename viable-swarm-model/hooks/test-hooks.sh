#!/bin/bash
# VSM Hook Validation Test Suite
# Simulates hook events and verifies correct behavior.
# Run with: bash ~/vsm/viable-swarm-model/hooks/test-hooks.sh

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REAL_HOME="${HOME:-}"
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
echo "NOTE: These tests validate hook scripts in isolation."
echo "They do NOT test kimi-cli integration. Empirically confirmed"
echo "(2026-06-02): ALL subagents — background, foreground, AND"
echo "parallel foreground — bypass ALL hooks. This is EXPECTED"
echo "behavior, not a bug. BackgroundAgentRunner and parallel"
echo "asyncio.create_task() do not propagate the hook engine."
echo "Primary enforcement is Layer 1: prompt-hardened structural"
echo "gate rules in every agent system prompt. Hooks are a"
echo "secondary safety net for S5 ONLY."
echo ""
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
export HOME="$REAL_HOME"

# --- Test 8: decision-enforcer warns when decisions.md missing ---
echo "Test 8: decision-enforcer warns when decisions.md missing on plan.md write..."
# Ensure decisions.md does NOT exist
rm -f "$TMPDIR/vsm/viable-swarm-model/references/decisions.md"
export HOME="$TMPDIR"
mkdir -p "$TMPDIR/vsm/viable-swarm-model/references"
PAYLOAD=$(jq -n \
    --arg session_id "test-session-8" \
    --arg cwd "$TMPDIR" \
    --arg file_path "$TMPDIR/plan.md" \
    --arg content "# Plan" \
    '{session_id: $session_id, cwd: $cwd, tool_name: "WriteFile", tool_input: {file_path: $file_path, content: $content}}')

WARN_OUTPUT=$(bash "$SCRIPT_DIR/decision-enforcer.sh" <<< "$PAYLOAD" 2>&1 >/dev/null)
if echo "$WARN_OUTPUT" | grep -qi "DECISION ENFORCER WARNING"; then
    echo "  ✅ PASSED: Correctly warned about missing decisions.md"
    ((PASSED++))
else
    echo "  ❌ FAILED: Did not warn about missing decisions.md"
    ((FAILED++))
fi
export HOME="$REAL_HOME"

# --- Test 10: context-pressure warns when >200k tokens ---
echo "Test 9: context-pressure warns when >200k tokens..."
export HOME="$TMPDIR"
PAYLOAD=$(jq -n \
    --arg session_id "test-session-9" \
    --arg cwd "$TMPDIR" \
    --arg trigger "ratio" \
    --argjson token_count 210000 \
    '{session_id: $session_id, cwd: $cwd, trigger: $trigger, token_count: $token_count}')

WARN_OUTPUT=$(bash "$SCRIPT_DIR/context-pressure.sh" <<< "$PAYLOAD" 2>&1 >/dev/null)
if echo "$WARN_OUTPUT" | grep -qi "CONTEXT PRESSURE ALERT"; then
    echo "  ✅ PASSED: Correctly warned about context pressure"
    ((PASSED++))
else
    echo "  ❌ FAILED: Did not warn about context pressure"
    ((FAILED++))
fi
export HOME="$REAL_HOME"

# --- Test 9: stop-verifier auto-fills measured effects from trainer backfill ---
echo "Test 10: stop-verifier auto-fills measured effects from trainer backfill..."
# Create a mock mutation-log.md with a PENDING entry
mkdir -p "$TMPDIR/.kimi"
mkdir -p "$TMPDIR/vsm/viable-swarm-model/references"
cat > "$TMPDIR/vsm/viable-swarm-model/references/mutation-log.md" << 'MUTLOG'
# Mutation Log

## Mutation FB25-1 — 2026-06-02
**Session**: Test session
**File**: `references/security-lessons.md`
**Type**: append
**Target failure mode**: Phase 4 bypass when 1 test fails
**Rationale**: Hook enforcement needed
**Expected effect**: Zero bypasses in next build
**Measured effect**: [PENDING]
MUTLOG

# Create a mock trainer backfill file
cat > "$TMPDIR/.kimi/trainer-backfill.md" << 'BACKFILL'
# Trainer Mutation Effectiveness Backfill

| Mutation ID | Effectiveness | Notes |
|-------------|--------------|-------|
| FB25-1 | Effective | Zero bypasses observed |
| FB25-2 | Ineffective | Still occurring |
BACKFILL

export HOME="$TMPDIR"
PAYLOAD=$(jq -n \
    --arg cwd "$TMPDIR" \
    --argjson stop_hook_active false \
    '{cwd: $cwd, stop_hook_active: $stop_hook_active}')

run_hook "$SCRIPT_DIR/stop-verifier.sh" "$PAYLOAD"
# Check if backfill file was created (hook does NOT modify tracked mutation-log.md;
# it writes ephemeral backfill for S5 to apply during Phase 8c-ii)
if [[ -f "$TMPDIR/.kimi/mutation-backfill.md" ]] && grep -q "FB25-1 | Effective" "$TMPDIR/.kimi/mutation-backfill.md" 2>/dev/null; then
    echo "  ✅ PASSED: Extracted trainer backfill to ephemeral mutation-backfill.md"
    ((PASSED++))
else
    echo "  ❌ FAILED: Did not extract trainer backfill"
    ls -la "$TMPDIR/.kimi/" 2>/dev/null || echo "No .kimi directory"
    ((FAILED++))
fi
export HOME="$REAL_HOME"

echo ""
echo "========================================"
echo "Results: $PASSED passed, $FAILED failed"
echo "========================================"

if [[ "$FAILED" -gt 0 ]]; then
    exit 1
fi
exit 0
