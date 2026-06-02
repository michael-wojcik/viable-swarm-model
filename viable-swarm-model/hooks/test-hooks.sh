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
echo "They do NOT test kimi-cli integration. A known limitation"
echo "(confirmed 2026-06-02): Background subagents bypass hooks"
echo "because BackgroundAgentRunner does not propagate hook_engine."
echo "Primary enforcement is prompt-hardened rules in agent files."
echo "Hooks remain as secondary safety net for S5 + foreground."
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

# --- Test 8: agent-performance-scorer updates capability matrix ---
echo "Test 8: agent-performance-scorer updates capability matrix..."
# Create a mock skill-state.md with a capability matrix
mkdir -p "$TMPDIR/vsm/viable-swarm-model/references"
cp "$REAL_HOME/vsm/viable-swarm-model/references/skill-state.md" "$TMPDIR/vsm/viable-swarm-model/references/skill-state.md" 2>/dev/null || cat > "$TMPDIR/vsm/viable-swarm-model/references/skill-state.md" << 'MOCK'
# VSM Skill State

## Capability Matrix
| Agent | Domain | Success Rate | Last 3 Scores | Known Failure Modes |
|-------|--------|-------------|---------------|---------------------|
| vsm_backend_coder | Python/FastAPI | 85% | 4, 4, 3 | Import loops |
| vsm_frontend_coder | React/TS | 65% | 3, 2, 2 | Stub pages |

## Current Mood
- **Recent pattern**: "No data yet"
MOCK

export HOME="$TMPDIR"
PAYLOAD=$(jq -n \
    --arg session_id "test-session-8" \
    --arg cwd "$TMPDIR" \
    --arg agent_name "vsm_backend_coder" \
    --arg response "Audit complete. PASS verdict. Zero critical findings. 2 minor notes." \
    '{session_id: $session_id, cwd: $cwd, agent_name: $agent_name, response: $response}')

run_hook "$SCRIPT_DIR/agent-performance-scorer.sh" "$PAYLOAD"
# Check that agent-scores.jsonl was written
if [[ -f "$TMPDIR/.vsm-telemetry/agent-scores.jsonl" ]]; then
    SCORE_ENTRY=$(grep "vsm_backend_coder" "$TMPDIR/.vsm-telemetry/agent-scores.jsonl" | tail -1)
    if echo "$SCORE_ENTRY" | grep -qE '"score"\s*:\s*5'; then
        echo "  ✅ PASSED: Scored agent correctly and logged score"
        ((PASSED++))
    else
        echo "  ❌ FAILED: Score not logged correctly (expected 5, got $SCORE_ENTRY)"
        ((FAILED++))
    fi
else
    echo "  ❌ FAILED: agent-scores.jsonl not created"
    ((FAILED++))
fi
unset HOME

# --- Test 9: decision-enforcer warns when decisions.md missing ---
echo "Test 9: decision-enforcer warns when decisions.md missing on plan.md write..."
# Ensure decisions.md does NOT exist
rm -f "$TMPDIR/vsm/viable-swarm-model/references/decisions.md"
export HOME="$TMPDIR"
mkdir -p "$TMPDIR/vsm/viable-swarm-model/references"
PAYLOAD=$(jq -n \
    --arg session_id "test-session-9" \
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
echo "Test 10: context-pressure warns when >200k tokens..."
export HOME="$TMPDIR"
PAYLOAD=$(jq -n \
    --arg session_id "test-session-10" \
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

# --- Test 11: bypass-logger logs hook block failures ---
echo "Test 11: bypass-logger logs tool use failures..."
export HOME="$TMPDIR"
PAYLOAD=$(jq -n \
    --arg session_id "test-session-11" \
    --arg cwd "$TMPDIR" \
    --arg tool_name "WriteFile" \
    --arg file_path "$TMPDIR/.kimi/phase4-gate.md" \
    --arg error "FRAUDULENT GATE PASS BLOCKED by gate-guardian.sh" \
    '{session_id: $session_id, cwd: $cwd, tool_name: $tool_name, tool_input: {file_path: $file_path}, error: $error}')

run_hook "$SCRIPT_DIR/bypass-logger.sh" "$PAYLOAD"
if [[ -f "$TMPDIR/.vsm-telemetry/bypass-attempts.jsonl" ]]; then
    BYPASS_ENTRY=$(grep "test-session-11" "$TMPDIR/.vsm-telemetry/bypass-attempts.jsonl" | tail -1)
    if echo "$BYPASS_ENTRY" | grep -qE '"is_hook_block"\s*:\s*true'; then
        echo "  ✅ PASSED: Correctly logged hook block as bypass attempt"
        ((PASSED++))
    else
        echo "  ❌ FAILED: Bypass entry missing is_hook_block flag"
        ((FAILED++))
    fi
else
    echo "  ❌ FAILED: bypass-attempts.jsonl not created"
    ((FAILED++))
fi
export HOME="$REAL_HOME"

# --- Test 12: stop-verifier auto-fills measured effects from trainer backfill ---
echo "Test 12: stop-verifier auto-fills measured effects from trainer backfill..."
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
# Check if mutation-log.md was updated
if grep -q "Effective (auto-filled from trainer backfill" "$TMPDIR/vsm/viable-swarm-model/references/mutation-log.md" 2>/dev/null; then
    echo "  ✅ PASSED: Auto-filled measured effect from trainer backfill"
    ((PASSED++))
else
    # Check if it was filled at all (sed may have worked differently)
    if grep -q "Measured effect.*Effective" "$TMPDIR/vsm/viable-swarm-model/references/mutation-log.md" 2>/dev/null; then
        echo "  ✅ PASSED: Auto-filled measured effect from trainer backfill"
        ((PASSED++))
    else
        echo "  ❌ FAILED: Did not auto-fill measured effect"
        cat "$TMPDIR/vsm/viable-swarm-model/references/mutation-log.md"
        ((FAILED++))
    fi
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
