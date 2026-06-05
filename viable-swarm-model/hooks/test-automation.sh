#!/bin/bash
# VSM Automation Infrastructure Test Suite
# Tests update-mutation-state.sh, validate-mutation-state.sh,
# auto-broker-update.sh, update-causal-index.sh, build-health-dashboard.py
#
# Run with: bash ~/vsm/viable-swarm-model/hooks/test-automation.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REAL_HOME="${HOME:-}"
PASSED=0
FAILED=0

TMPDIR=$(mktemp -d)
trap 'rm -rf "$TMPDIR"' EXIT

export HOME="$TMPDIR"

# Create base directory structures used by multiple tests
mkdir -p "$TMPDIR/vsm/viable-swarm-model/references"
mkdir -p "$TMPDIR/vsm-fitness-builds/coach"

# ---------- Helpers ----------
pass() {
    PASSED=$((PASSED + 1))
    echo "PASS"
}

fail() {
    FAILED=$((FAILED + 1))
    echo "FAIL: $1"
}

# ============================================================================
# Preliminary: Syntax checks for all .sh scripts in this directory
# ============================================================================

echo -n "TEST: Syntax check update-mutation-state.sh ... "
if bash -n "$SCRIPT_DIR/update-mutation-state.sh"; then
    pass
else
    fail "syntax error detected"
fi

echo -n "TEST: Syntax check validate-mutation-state.sh ... "
if bash -n "$SCRIPT_DIR/validate-mutation-state.sh"; then
    pass
else
    fail "syntax error detected"
fi

echo -n "TEST: Syntax check auto-broker-update.sh ... "
if bash -n "$SCRIPT_DIR/auto-broker-update.sh"; then
    pass
else
    fail "syntax error detected"
fi

echo -n "TEST: Syntax check update-causal-index.sh ... "
if bash -n "$SCRIPT_DIR/update-causal-index.sh"; then
    pass
else
    fail "syntax error detected"
fi

# ============================================================================
# Test 1: update-mutation-state.sh — dry-run mode
# ============================================================================

echo -n "TEST: update-mutation-state.sh dry-run processes PENDING entries ... "

mkdir -p "$TMPDIR/build1/.kimi"

cat > "$TMPDIR/vsm/viable-swarm-model/references/mutation-state.md" << 'EOF'
# Mutation State

| ID | Source | Type | Target Failure | Status | Builds Tested | Score | Hypothesis | Experiment | Next Review |
|---|---|---|---|---|---|---|---|---|---|
| T1 | Test | append-only | Test failure | probation | 1 | 3 | H1 | E1 | — |
| T2 | Test | append-only | Test failure | effective | 5 | 4 | — | — | — |
EOF

cat > "$TMPDIR/vsm/viable-swarm-model/references/mutation-log.md" << 'EOF'
# Mutation Log

## Mutation T1 — 2026-06-04

**Session**: Test session
**File**: `test.md`
**Type**: append-only
**Target failure mode**: Test failure
**Rationale**: Testing
**Expected effect**: Fix tests

Measured effect: [PENDING]

---

## Mutation T2 — 2026-06-04

**Session**: Test session
**File**: `test.md`
**Type**: append-only
**Target failure mode**: Test failure
**Rationale**: Testing
**Expected effect**: Fix tests

Measured effect: Effective (Score: 4–5) — Already measured
EOF

cat > "$TMPDIR/build1/.kimi/mutations-applied.md" << 'EOF'
# Mutations Applied

| # | Mutation ID | Classification | Target File(s) | Status | Evidence |
|---|---|---|---|---|---|
| 1 | T1 | append-only | test.md | **PENDING** | Evidence of effectiveness |
EOF

OUTPUT=$(bash "$SCRIPT_DIR/update-mutation-state.sh" "$TMPDIR/build1" --dry-run 2>&1) || true

if echo "$OUTPUT" | grep -q "Would update mutation-log.md: T1" && \
   echo "$OUTPUT" | grep -q "Would increment Builds Tested for T1"; then
    # Verify no changes were made to tracked files
    if grep -q "Measured effect: \[PENDING\]" "$TMPDIR/vsm/viable-swarm-model/references/mutation-log.md" && \
       grep -q "| T1 | Test | append-only | Test failure | probation | 1 |" "$TMPDIR/vsm/viable-swarm-model/references/mutation-state.md"; then
        pass
    else
        fail "files were modified during dry-run"
    fi
else
    fail "dry-run did not report expected actions"
fi

# ============================================================================
# Test 2: update-mutation-state.sh — real run replaces PENDING
# ============================================================================

echo -n "TEST: update-mutation-state.sh real run replaces PENDING in mutation-log.md ... "

OUTPUT=$(bash "$SCRIPT_DIR/update-mutation-state.sh" "$TMPDIR/build1" 2>&1) || true

if grep -q "Effective (Score: 4–5) — Evidence of effectiveness" "$TMPDIR/vsm/viable-swarm-model/references/mutation-log.md"; then
    pass
else
    fail "PENDING not replaced in mutation-log.md"
fi

# ============================================================================
# Test 3: validate-mutation-state.sh — catches corrupted state
# ============================================================================

echo -n "TEST: validate-mutation-state.sh detects duplicate IDs and malformed rows ... "

cat > "$TMPDIR/vsm/viable-swarm-model/references/mutation-state.md" << 'EOF'
# Mutation State

| ID | Source | Type | Target Failure | Status | Builds Tested | Score | Hypothesis | Experiment | Next Review |
|---|---|---|---|---|---|---|---|---|---|
| T1 | Test | append-only | Test failure | probation | 1 | 3 | H1 | E1 | — |
| T1 | Test | append-only | Test failure | probation | 1 | 3 | H1 | E1 | — |
| T2 | Test | append-only | Test failure | effective | 5 | 4 |
EOF

cat > "$TMPDIR/vsm/viable-swarm-model/references/mutation-log.md" << 'EOF'
# Mutation Log

## Mutation T1 — 2026-06-04

**Measured effect**: [PENDING]
EOF

cat > "$TMPDIR/vsm/viable-swarm-model/references/mutation-cemetery.md" << 'EOF'
# Mutation Cemetery
EOF

RC=0
OUTPUT=$(bash "$SCRIPT_DIR/validate-mutation-state.sh" 2>&1) || RC=$?

if [ "$RC" -ne 0 ] && \
   echo "$OUTPUT" | grep -qi "duplicate" && \
   echo "$OUTPUT" | grep -qi "malformed"; then
    pass
else
    fail "did not detect corruption (rc=$RC)"
fi

# ============================================================================
# Test 4: validate-mutation-state.sh — passes clean state
# ============================================================================

echo -n "TEST: validate-mutation-state.sh passes clean state ... "

cat > "$TMPDIR/vsm/viable-swarm-model/references/mutation-state.md" << 'EOF'
# Mutation State

| ID | Source | Type | Target Failure | Status | Builds Tested | Score | Hypothesis | Experiment | Next Review |
|---|---|---|---|---|---|---|---|---|---|
| T1 | Test | append-only | Test failure | probation | 2 | 3 | H1 | E1 | — |
| T2 | Test | append-only | Test failure | effective | 5 | 4 | — | — | — |
EOF

cat > "$TMPDIR/vsm/viable-swarm-model/references/mutation-log.md" << 'EOF'
# Mutation Log

## Mutation T1 — 2026-06-04

**Measured effect**: Effective

---

## Mutation T2 — 2026-06-04

**Measured effect**: Effective
EOF

RC=0
OUTPUT=$(bash "$SCRIPT_DIR/validate-mutation-state.sh" 2>&1) || RC=$?

if [ "$RC" -eq 0 ] && echo "$OUTPUT" | grep -q "PASS"; then
    pass
else
    fail "clean state failed validation (rc=$RC)"
fi

# ============================================================================
# Test 5: auto-broker-update.sh — appends entry for valid build directory
# ============================================================================

echo -n "TEST: auto-broker-update.sh appends entry and updates timestamp ... "

mkdir -p "$TMPDIR/build5/.kimi"

cat > "$TMPDIR/build5/plan.md" << 'EOF'
# Build Plan — FB99
Domain: Test Automation
EOF

cat > "$TMPDIR/vsm/viable-swarm-model/references/knowledge-broker.md" << 'EOF'
# VSM Knowledge Broker

> **Last updated**: 2026-01-01

## Curated Build Index

| Build | Date | Score | Process | Domain | Mutations |
|-------|------|-------|---------|--------|-----------|

EOF

BROKER_BEFORE=$(wc -l < "$TMPDIR/vsm/viable-swarm-model/references/knowledge-broker.md")

bash "$SCRIPT_DIR/auto-broker-update.sh" "$TMPDIR/build5" >/dev/null 2>&1 || true

BROKER_AFTER=$(wc -l < "$TMPDIR/vsm/viable-swarm-model/references/knowledge-broker.md")
BROKER_LINES_ADDED=$((BROKER_AFTER - BROKER_BEFORE))

if grep -q "FB99" "$TMPDIR/vsm/viable-swarm-model/references/knowledge-broker.md" && \
   grep -q "Last updated.*$(date +%Y-%m-%d)" "$TMPDIR/vsm/viable-swarm-model/references/knowledge-broker.md" && \
   [ "$BROKER_LINES_ADDED" -ge 1 ]; then
    pass
else
    fail "broker file not updated correctly (before=$BROKER_BEFORE, after=$BROKER_AFTER)"
fi

# ============================================================================
# Test 6: auto-broker-update.sh — rejects directory without plan.md
# ============================================================================

echo -n "TEST: auto-broker-update.sh rejects directory without plan.md ... "

mkdir -p "$TMPDIR/build6/.kimi"
# Intentionally omit plan.md

RC=0
bash "$SCRIPT_DIR/auto-broker-update.sh" "$TMPDIR/build6" >/dev/null 2>&1 || RC=$?

if [ "$RC" -ne 0 ]; then
    pass
else
    fail "should have rejected missing plan.md"
fi

# ============================================================================
# Test 7: update-causal-index.sh — dry-run mode
# ============================================================================

echo -n "TEST: update-causal-index.sh dry-run reports correctly ... "

mkdir -p "$TMPDIR/build7/.kimi"

cat > "$TMPDIR/build7/.kimi/mutations-applied.md" << 'EOF'
# Mutations Applied

| ID | Name | Status | Hypothesis | Experiment |
|---|---|---|---|---|
| M1 | Test Mutation | effective | H1 | E1 |
EOF

cat > "$TMPDIR/vsm/viable-swarm-model/references/hypotheses.md" << 'EOF'
# Hypotheses
H1 exists here
EOF

cat > "$TMPDIR/vsm/viable-swarm-model/references/experiments.md" << 'EOF'
# Experiments
E1 exists here
EOF

OUTPUT=$(bash "$SCRIPT_DIR/update-causal-index.sh" --dry-run "$TMPDIR/build7" 2>&1) || true

if echo "$OUTPUT" | grep -q "Would create new causal chain CC-1 for M1" && \
   echo "$OUTPUT" | grep -q "DRY-RUN"; then
    pass
else
    fail "dry-run did not report expected actions"
fi

# ============================================================================
# Test 8: build-health-dashboard.py — generates dashboard for valid build
# ============================================================================

echo -n "TEST: build-health-dashboard.py generates dashboard and history ... "

mkdir -p "$TMPDIR/vsm-fitness-builds/coach/FB95/.kimi"
mkdir -p "$TMPDIR/vsm-fitness-builds/coach/FB96/.kimi"
mkdir -p "$TMPDIR/build8/.kimi"

cat > "$TMPDIR/vsm-fitness-builds/coach/FB95/plan.md" << 'EOF'
# Build Plan — FB95
| Phase 1 | 5 | 0 |
| Phase 2 | 3 | 1 |
EOF
cat > "$TMPDIR/vsm-fitness-builds/coach/FB95/.kimi/meta-report.md" << 'EOF'
Trainer score: 4.2/5.0
EOF
cat > "$TMPDIR/vsm-fitness-builds/coach/FB95/.kimi/process-audit.md" << 'EOF'
Process score: 85/100
EOF

cat > "$TMPDIR/vsm-fitness-builds/coach/FB96/plan.md" << 'EOF'
# Build Plan — FB96
| Phase 1 | 4 | 0 |
EOF
cat > "$TMPDIR/vsm-fitness-builds/coach/FB96/.kimi/meta-report.md" << 'EOF'
Trainer score: 3.8/5.0
EOF
cat > "$TMPDIR/vsm-fitness-builds/coach/FB96/.kimi/process-audit.md" << 'EOF'
Process score: 90/100
EOF

cat > "$TMPDIR/build8/plan.md" << 'EOF'
# Build Plan — FB99
EOF

cat > "$TMPDIR/vsm/viable-swarm-model/references/mutation-state.md" << 'EOF'
# Mutation State
| ID | Source | Type | Target Failure | Status | Builds Tested | Score | Hypothesis | Experiment | Next Review |
|---|---|---|---|---|---|---|---|---|---|
| T1 | Test | append-only | Test failure | probation | 1 | 3 | H1 | E1 | — |
EOF

cat > "$TMPDIR/vsm/viable-swarm-model/references/hypotheses.md" << 'EOF'
# Hypotheses
**Status**: untested
Proposed: 2026-01-01
EOF

cat > "$TMPDIR/vsm/viable-swarm-model/references/knowledge-broker.md" << 'EOF'
# Broker
> **Last updated**: 2026-06-01
EOF

RC=0
python3 "$SCRIPT_DIR/../scripts/build-health-dashboard.py" "$TMPDIR/build8" >/dev/null 2>&1 || RC=$?

if [ "$RC" -eq 0 ] && \
   [ -f "$TMPDIR/build8/.kimi/health-dashboard.md" ] && \
   [ -f "$TMPDIR/vsm/viable-swarm-model/references/build-health-history.md" ] && \
   grep -q "Build Health Dashboard" "$TMPDIR/build8/.kimi/health-dashboard.md"; then
    pass
else
    fail "dashboard or history not generated (rc=$RC)"
fi

# ============================================================================
# Test 9: build-health-dashboard.py — rejects non-build directory
# ============================================================================

echo -n "TEST: build-health-dashboard.py rejects non-build directory ... "

mkdir -p "$TMPDIR/notabuild"

RC=0
python3 "$SCRIPT_DIR/../scripts/build-health-dashboard.py" "$TMPDIR/notabuild" >/dev/null 2>&1 || RC=$?

if [ "$RC" -ne 0 ]; then
    pass
else
    fail "should have rejected non-build directory"
fi

# ============================================================================
# Test 10: build-health-dashboard.py — score extraction handles /100 format
# ============================================================================

echo -n "TEST: build-health-dashboard.py normalizes /100 scores to /5.0 ... "

mkdir -p "$TMPDIR/vsm-fitness-builds/coach/FB97/.kimi"
mkdir -p "$TMPDIR/build10/.kimi"

cat > "$TMPDIR/vsm-fitness-builds/coach/FB97/plan.md" << 'EOF'
# Build Plan — FB97
EOF
cat > "$TMPDIR/vsm-fitness-builds/coach/FB97/.kimi/meta-report.md" << 'EOF'
Trainer score: 77/100
EOF

cat > "$TMPDIR/build10/plan.md" << 'EOF'
# Build Plan — FB97
EOF

RC=0
python3 "$SCRIPT_DIR/../scripts/build-health-dashboard.py" "$TMPDIR/build10" >/dev/null 2>&1 || RC=$?

if [ "$RC" -eq 0 ] && \
   grep -q "3.85" "$TMPDIR/build10/.kimi/health-dashboard.md"; then
    pass
else
    fail "/100 score not normalized to /5.0 in dashboard"
fi

# ============================================================================
# Test 11: build-health-dashboard.py — agent risk excludes non-agent rows
# ============================================================================

echo -n "TEST: build-health-dashboard.py agent risk excludes efficiency baselines ... "

mkdir -p "$TMPDIR/build11/.kimi"

cat > "$TMPDIR/build11/plan.md" << 'EOF'
# Build Plan — FB98
EOF

cat > "$TMPDIR/vsm/viable-swarm-model/references/mutation-state.md" << 'EOF'
# Mutation State

| ID | Source | Type | Target Failure | Status | Builds Tested | Score | Hypothesis | Experiment | Next Review |
|---|---|---|---|---|---|---|---|---|---|
| T1 | Test | append-only | Test failure | effective | 5 | 4 | — | — | — |

### Capability Matrix
| Agent | Domain | Success Rate | Last 3 Scores | Known Failure Modes | Recommended Max Task Size |
|-------|--------|-------------|---------------|---------------------|--------------------------|
| vsm_backend_coder | Python | 85% | 4,4,4 | None | 500 lines |
| Context compactions | 4.0% | — | — | — | 200 lines |

### Known Unknowns
| Hypothesis | Confidence |
|---|---|
| H1 | HIGH |
EOF

RC=0
python3 "$SCRIPT_DIR/../scripts/build-health-dashboard.py" "$TMPDIR/build11" >/dev/null 2>&1 || RC=$?

if [ "$RC" -eq 0 ] && \
   grep -q "vsm_backend_coder" "$TMPDIR/build11/.kimi/health-dashboard.md" && \
   ! grep -q "Context compactions" "$TMPDIR/build11/.kimi/health-dashboard.md"; then
    pass
else
    fail "efficiency baseline row incorrectly listed as agent risk"
fi

# ============================================================================
# Test 12: build-health-dashboard.py — blocker count uses headings not strings
# ============================================================================

echo -n "TEST: build-health-dashboard.py counts BLOCKER headings not all occurrences ... "

mkdir -p "$TMPDIR/vsm-fitness-builds/coach/FB98/.kimi"
mkdir -p "$TMPDIR/vsm-fitness-builds/coach/FB99/.kimi"
mkdir -p "$TMPDIR/FB100/.kimi"

cat > "$TMPDIR/vsm-fitness-builds/coach/FB98/plan.md" << 'EOF'
# Build Plan — FB98
EOF
cat > "$TMPDIR/vsm-fitness-builds/coach/FB98/.kimi/meta-report.md" << 'EOF'
Score: 4.0/5.0
EOF

cat > "$TMPDIR/vsm-fitness-builds/coach/FB99/plan.md" << 'EOF'
# Build Plan — FB99
EOF
cat > "$TMPDIR/vsm-fitness-builds/coach/FB99/.kimi/meta-report.md" << 'EOF'
Score: 4.0/5.0
EOF
cat > "$TMPDIR/vsm-fitness-builds/coach/FB99/.kimi/security-audit.md" << 'EOF'
# Security Audit

- **BLOCKER count**: 5

## Executive Summary
Some text with BLOCKER mentioned again.

### BLOCKER
Actual finding here.

### BLOCKER
Another actual finding.
EOF

cat > "$TMPDIR/FB100/plan.md" << 'EOF'
# Build Plan — FB100
EOF

RC=0
python3 "$SCRIPT_DIR/../scripts/build-health-dashboard.py" "$TMPDIR/FB100" >/dev/null 2>&1 || RC=$?

# Extract blocker count from the Build History table in the dashboard
BLOCKER_VAL=$(grep "FB99" "$TMPDIR/FB100/.kimi/health-dashboard.md" | grep -oE '\| [0-9]+ \| [0-9]+h/[0-9]+i' | awk '{print $2}')

if [ "$RC" -eq 0 ] && [ "$BLOCKER_VAL" = "2" ]; then
    pass
else
    fail "blocker count should be 2 (headings only), got: $BLOCKER_VAL"
fi

# ============================================================================
# Test 13: build-health-dashboard.py — removed count handles **REMOVED**
# ============================================================================

echo -n "TEST: build-health-dashboard.py counts **REMOVED** mutations correctly ... "

mkdir -p "$TMPDIR/build13/.kimi"

cat > "$TMPDIR/build13/plan.md" << 'EOF'
# Build Plan — FB100
EOF

cat > "$TMPDIR/vsm/viable-swarm-model/references/mutation-state.md" << 'EOF'
# Mutation State
| ID | Source | Type | Target Failure | Status | Builds Tested | Score | Hypothesis | Experiment | Next Review |
|---|---|---|---|---|---|---|---|---|---|
| T1 | Test | append-only | Test failure | effective | 5 | 4 | — | — | — |
| T2 | Test | structural | Test bypass | **REMOVED** | 1 | 1 | — | — | — |
| T3 | Test | refinement | Test gap | **REMOVED** | 2 | 2 | — | — | — |
EOF

RC=0
python3 "$SCRIPT_DIR/../scripts/build-health-dashboard.py" "$TMPDIR/build13" >/dev/null 2>&1 || RC=$?

if [ "$RC" -eq 0 ] && \
   grep -q "Removed: 2" "$TMPDIR/build13/.kimi/health-dashboard.md"; then
    pass
else
    fail "**REMOVED** mutations not counted correctly"
fi

# ============================================================================
# Test 14: mutation-portfolio-health.py — basic computation and JSON output
# ============================================================================

echo -n "TEST: mutation-portfolio-health.py computes portfolio metrics correctly ... "

mkdir -p "$TMPDIR/build14/.kimi"

cat > "$TMPDIR/vsm/viable-swarm-model/references/mutation-state.md" << 'EOF'
# Mutation State
| ID | Source | Type | Target Failure | Status | Builds Tested | Score | Hypothesis | Experiment | Next Review |
|---|---|---|---|---|---|---|---|---|---|
| T1 | Test | append-only | Test failure | effective | 5 | 4 | — | — | — |
| T2 | Test | structural | Test bypass | probation | 1 | 3 | — | — | — |
| T3 | Test | refinement | Test gap | monitor | 5 | 2 | — | — | — |
| T4 | Test | append-only | Auth bug | probation | 3 | 5 | — | — | — |
| T5 | Test | structural | Config drift | **REMOVED** | 1 | 1 | — | — | — |
EOF

cat > "$TMPDIR/build14/plan.md" << 'EOF'
# Build Plan — FB101
EOF

RC=0
python3 "$SCRIPT_DIR/../scripts/mutation-portfolio-health.py" --build-dir "$TMPDIR/build14" >/dev/null 2>&1 || RC=$?

if [ "$RC" -eq 0 ] && \
   [ -f "$TMPDIR/build14/.kimi/mutation-portfolio-health.json" ] && \
   [ -f "$TMPDIR/build14/.kimi/mutation-portfolio-health.md" ] && \
   grep -q '"total_active": 4' "$TMPDIR/build14/.kimi/mutation-portfolio-health.json" && \
   grep -q '"probationary_count": 2' "$TMPDIR/build14/.kimi/mutation-portfolio-health.json" && \
   grep -q '"promotions_ready"' "$TMPDIR/build14/.kimi/mutation-portfolio-health.json"; then
    pass
else
    fail "portfolio health output incorrect or missing"
fi

# ============================================================================
# Test 15: mutation-portfolio-health.py — promotion detection
# ============================================================================

echo -n "TEST: mutation-portfolio-health.py detects promotion-ready mutations ... "

mkdir -p "$TMPDIR/build15/.kimi"

cat > "$TMPDIR/vsm/viable-swarm-model/references/mutation-state.md" << 'EOF'
# Mutation State
| ID | Source | Type | Target Failure | Status | Builds Tested | Score | Hypothesis | Experiment | Next Review |
|---|---|---|---|---|---|---|---|---|---|
| T4 | Test | append-only | Auth bug | probation | 3 | 5 | — | — | — |
EOF

cat > "$TMPDIR/build15/plan.md" << 'EOF'
# Build Plan — FB102
EOF

RC=0
python3 "$SCRIPT_DIR/../scripts/mutation-portfolio-health.py" --build-dir "$TMPDIR/build15" >/dev/null 2>&1 || RC=$?

if [ "$RC" -eq 0 ] && \
   grep -q '"id": "T4"' "$TMPDIR/build15/.kimi/mutation-portfolio-health.json" && \
   grep -q '"new_status": "effective"' "$TMPDIR/build15/.kimi/mutation-portfolio-health.json"; then
    pass
else
    fail "promotion-ready mutation not detected"
fi

# ============================================================================
# Test 16: mutation-portfolio-health.py — demotion detection
# ============================================================================

echo -n "TEST: mutation-portfolio-health.py detects demotion-ready mutations ... "

mkdir -p "$TMPDIR/build16/.kimi"

cat > "$TMPDIR/vsm/viable-swarm-model/references/mutation-state.md" << 'EOF'
# Mutation State
| ID | Source | Type | Target Failure | Status | Builds Tested | Score | Hypothesis | Experiment | Next Review |
|---|---|---|---|---|---|---|---|---|---|
| T3 | Test | refinement | Test gap | probation | 3 | 2 | — | — | — |
EOF

cat > "$TMPDIR/build16/plan.md" << 'EOF'
# Build Plan — FB103
EOF

RC=0
python3 "$SCRIPT_DIR/../scripts/mutation-portfolio-health.py" --build-dir "$TMPDIR/build16" >/dev/null 2>&1 || RC=$?

if [ "$RC" -eq 0 ] && \
   grep -q '"id": "T3"' "$TMPDIR/build16/.kimi/mutation-portfolio-health.json" && \
   grep -q '"new_status": "ineffective"' "$TMPDIR/build16/.kimi/mutation-portfolio-health.json"; then
    pass
else
    fail "demotion-ready mutation not detected"
fi

# ============================================================================
# Test 17: mutation-portfolio-health.py — session-end hook auto-invocation
# ============================================================================

echo -n "TEST: session-end.sh auto-generates portfolio health when review missing ... "

mkdir -p "$TMPDIR/build17/.kimi"
mkdir -p "$TMPDIR/vsm/viable-swarm-model/scripts"

# Copy scripts into TMPDIR so session-end.sh can find them via $HOME
cp "$SCRIPT_DIR/../scripts/mutation-portfolio-health.py" "$TMPDIR/vsm/viable-swarm-model/scripts/"

cat > "$TMPDIR/build17/plan.md" << 'EOF'
# Build Plan — FB104
EOF

cat > "$TMPDIR/build17/.kimi/meta-report.md" << 'EOF'
# Meta Report
Score: 4.0/5.0
EOF

cat > "$TMPDIR/vsm/viable-swarm-model/references/mutation-state.md" << 'EOF'
# Mutation State
| ID | Source | Type | Target Failure | Status | Builds Tested | Score | Hypothesis | Experiment | Next Review |
|---|---|---|---|---|---|---|---|---|---|
| T1 | Test | append-only | Test failure | effective | 5 | 4 | — | — | — |
EOF

# Simulate session-end payload
PAYLOAD='{"session_id":"test-session-17","cwd":"'$TMPDIR/build17'","reason":"stop"}'
RC=0
echo "$PAYLOAD" | bash "$SCRIPT_DIR/session-end.sh" >/dev/null 2>&1 || RC=$?

if [ "$RC" -eq 0 ] && \
   [ -f "$TMPDIR/build17/.kimi/mutation-portfolio-health.json" ] && \
   grep -q "mutation-portfolio-review.md missing" "$TMPDIR/build17/.kimi/session-telemetry.md" 2>/dev/null; then
    pass
else
    fail "session-end did not auto-generate portfolio health or flag missing review"
fi

# ============================================================================
# Summary
# ============================================================================

echo ""
echo "========================================"
echo "Results: $PASSED passed, $FAILED failed"
echo "========================================"

if [ "$FAILED" -gt 0 ]; then
    exit 1
fi
exit 0
