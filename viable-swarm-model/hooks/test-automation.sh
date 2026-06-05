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

echo -n "TEST: Syntax check stop-verifier.sh ... "
if bash -n "$SCRIPT_DIR/stop-verifier.sh"; then
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
# Test 18: organism-vitals.py — basic vitals computation
# ============================================================================

echo -n "TEST: organism-vitals.py computes variety metrics and algedonics ... "

mkdir -p "$TMPDIR/build18/.kimi"
mkdir -p "$TMPDIR/vsm-fitness-builds/coach/FB99/.kimi"
mkdir -p "$TMPDIR/vsm/viable-swarm-model/scripts"

cp "$SCRIPT_DIR/../scripts/organism-vitals.py" "$TMPDIR/vsm/viable-swarm-model/scripts/"

cat > "$TMPDIR/vsm/viable-swarm-model/references/mutation-state.md" << 'EOF'
# Mutation State
| ID | Source | Type | Target Failure | Status | Builds Tested | Score | Hypothesis | Experiment | Next Review |
|---|---|---|---|---|---|---|---|---|---|
| T1 | Test | append-only | Test failure | effective | 5 | 4 | — | — | — |
| T2 | Test | structural | Test bypass | probation | 1 | 3 | — | — | — |
| T3 | Test | refinement | Test gap | monitor | 5 | 2 | — | — | — |
EOF

cat > "$TMPDIR/vsm/viable-swarm-model/references/hypotheses.md" << 'EOF'
# Hypotheses
## H1: Test
**Status**: untested
## H2: Test
**Status**: confirmed
## H3: Test
**Status**: untested
EOF

cat > "$TMPDIR/vsm/viable-swarm-model/references/knowledge-broker.md" << 'EOF'
# Broker
> **Last updated**: 2026-06-01
EOF

cat > "$TMPDIR/vsm/viable-swarm-model/references/build-health-history.md" << 'EOF'
# Build Health History
## 2026-06-01 — FB99
- Score: 4.0/5.0
## 2026-06-02 — FB100
- Score: 3.8/5.0
EOF

cat > "$TMPDIR/build18/plan.md" << 'EOF'
# Build Plan — FB105
EOF

RC=0
python3 "$SCRIPT_DIR/../scripts/organism-vitals.py" --build-dir "$TMPDIR/build18" >/dev/null 2>&1 || RC=$?

if [ "$RC" -eq 0 ] && \
   [ -f "$TMPDIR/build18/.kimi/organism-vitals.md" ] && \
   grep -q "Probationary mutations" "$TMPDIR/build18/.kimi/organism-vitals.md" && \
   grep -q "Variety Score" "$TMPDIR/build18/.kimi/organism-vitals.md"; then
    pass
else
    fail "organism vitals output incorrect or missing"
fi

# ============================================================================
# Test 19: organism-vitals.py — CRITICAL algedonic detection
# ============================================================================

echo -n "TEST: organism-vitals.py detects CRITICAL untested hypotheses ... "

mkdir -p "$TMPDIR/build19/.kimi"

cat > "$TMPDIR/vsm/viable-swarm-model/references/mutation-state.md" << 'EOF'
# Mutation State
| ID | Source | Type | Target Failure | Status | Builds Tested | Score | Hypothesis | Experiment | Next Review |
|---|---|---|---|---|---|---|---|---|---|
| T1 | Test | append-only | Test failure | effective | 5 | 4 | — | — | — |
EOF

cat > "$TMPDIR/vsm/viable-swarm-model/references/hypotheses.md" << 'EOF'
# Hypotheses
## H1
**Status**: untested
## H2
**Status**: untested
## H3
**Status**: untested
## H4
**Status**: untested
## H5
**Status**: untested
## H6
**Status**: untested
## H7
**Status**: untested
## H8
**Status**: untested
## H9
**Status**: untested
## H10
**Status**: untested
## H11
**Status**: untested
EOF

cat > "$TMPDIR/vsm/viable-swarm-model/references/knowledge-broker.md" << 'EOF'
# Broker
> **Last updated**: 2026-06-01
EOF

cat > "$TMPDIR/vsm/viable-swarm-model/references/build-health-history.md" << 'EOF'
# Build Health History
EOF

cat > "$TMPDIR/build19/plan.md" << 'EOF'
# Build Plan — FB106
EOF

RC=0
python3 "$SCRIPT_DIR/../scripts/organism-vitals.py" --build-dir "$TMPDIR/build19" >/dev/null 2>&1 || RC=$?

if [ "$RC" -eq 0 ] && \
   grep -q "CRITICAL: Untested hypotheses" "$TMPDIR/build19/.kimi/organism-vitals.md" && \
   grep -q "Blocking.*YES" "$TMPDIR/build19/.kimi/organism-vitals.md"; then
    pass
else
    fail "CRITICAL algedonic for untested hypotheses not detected"
fi

# ============================================================================
# Test 20: organism-vitals.py — session-end hook auto-invocation
# ============================================================================

echo -n "TEST: session-end.sh auto-generates organism vitals when assessment missing ... "

mkdir -p "$TMPDIR/build20/.kimi"

cat > "$TMPDIR/build20/plan.md" << 'EOF'
# Build Plan — FB107
EOF

cat > "$TMPDIR/build20/.kimi/meta-report.md" << 'EOF'
# Meta Report
Score: 4.0/5.0
EOF

cat > "$TMPDIR/vsm/viable-swarm-model/references/mutation-state.md" << 'EOF'
# Mutation State
| ID | Source | Type | Target Failure | Status | Builds Tested | Score | Hypothesis | Experiment | Next Review |
|---|---|---|---|---|---|---|---|---|---|
| T1 | Test | append-only | Test failure | effective | 5 | 4 | — | — | — |
EOF

cat > "$TMPDIR/vsm/viable-swarm-model/references/hypotheses.md" << 'EOF'
# Hypotheses
## H1
**Status**: confirmed
EOF

cat > "$TMPDIR/vsm/viable-swarm-model/references/knowledge-broker.md" << 'EOF'
# Broker
> **Last updated**: 2026-06-05
EOF

cat > "$TMPDIR/vsm/viable-swarm-model/references/build-health-history.md" << 'EOF'
# Build Health History
EOF

# Simulate session-end payload
PAYLOAD='{"session_id":"test-session-20","cwd":"'$TMPDIR/build20'","reason":"stop"}'
RC=0
echo "$PAYLOAD" | bash "$SCRIPT_DIR/session-end.sh" >/dev/null 2>&1 || RC=$?

if [ "$RC" -eq 0 ] && \
   [ -f "$TMPDIR/build20/.kimi/organism-vitals.md" ] && \
   grep -q "variety-assessment.md missing" "$TMPDIR/build20/.kimi/session-telemetry.md" 2>/dev/null; then
    pass
else
    fail "session-end did not auto-generate organism vitals or flag missing assessment"
fi

# ============================================================================
# Test 21: process-compliance-precompute.py — basic compliance scoring
# ============================================================================

echo -n "TEST: process-compliance-precompute.py scores compliance correctly ... "

mkdir -p "$TMPDIR/build21/.kimi"
mkdir -p "$TMPDIR/vsm/viable-swarm-model/scripts"

cp "$SCRIPT_DIR/../scripts/process-compliance-precompute.py" "$TMPDIR/vsm/viable-swarm-model/scripts/"

cat > "$TMPDIR/build21/plan.md" << 'EOF'
# Build Plan — FB108
EOF

cat > "$TMPDIR/build21/.kimi/phase4-gate.md" << 'EOF'
# Phase 4 Gate
PASS
EOF

cat > "$TMPDIR/build21/.kimi/re-audit-report.md" << 'EOF'
# Re-Audit Report
Files modified: auth.py
Verdict: PASS
No regressions.
EOF

cat > "$TMPDIR/build21/.kimi/lessons.md" << 'EOF'
# Lessons
Learned.
EOF

cat > "$TMPDIR/build21/.kimi/meta-report.md" << 'EOF'
# Meta Report
## Agent Performance Scores
## Phase Audit
## Hypotheses Generated
## Mutations Proposed
EOF

cat > "$TMPDIR/build21/.kimi/mutations-applied.md" << 'EOF'
# Mutations Applied
| ID | Status |
| M1 | Applied |
EOF

cat > "$TMPDIR/vsm/viable-swarm-model/references/knowledge-broker.md" << 'EOF'
# Broker
> **Last updated**: 2026-06-05
EOF

RC=0
python3 "$SCRIPT_DIR/../scripts/process-compliance-precompute.py" "$TMPDIR/build21" >/dev/null 2>&1 || RC=$?

if [ "$RC" -eq 0 ] && \
   [ -f "$TMPDIR/build21/.kimi/process-compliance-precomputed.json" ] && \
   [ -f "$TMPDIR/build21/.kimi/process-compliance-precomputed.md" ] && \
   grep -q "Phase 4 Gate Compliance" "$TMPDIR/build21/.kimi/process-compliance-precomputed.md"; then
    pass
else
    fail "compliance precompute output incorrect or missing"
fi

# ============================================================================
# Test 22: process-compliance-precompute.py — HARD BLOCK on low score
# ============================================================================

echo -n "TEST: process-compliance-precompute.py emits HARD BLOCK below 50 ... "

mkdir -p "$TMPDIR/build22/.kimi"

cat > "$TMPDIR/build22/plan.md" << 'EOF'
# Build Plan — FB109
EOF

RC=0
python3 "$SCRIPT_DIR/../scripts/process-compliance-precompute.py" "$TMPDIR/build22" >/dev/null 2>&1 || RC=$?

if [ "$RC" -eq 0 ] && \
   grep -q "HARD BLOCK" "$TMPDIR/build22/.kimi/process-compliance-precomputed.md" && \
   grep -qE "[0-9]+ / 100 \([0-9]+\.[0-9]+%\)" "$TMPDIR/build22/.kimi/process-compliance-precomputed.md"; then
    pass
else
    fail "HARD BLOCK not emitted for empty build directory"
fi

# ============================================================================
# Test 23: process-compliance-precompute.py — session-end hook auto-invocation
# ============================================================================

echo -n "TEST: session-end.sh auto-generates compliance when audit missing ... "

mkdir -p "$TMPDIR/build23/.kimi"

cat > "$TMPDIR/build23/plan.md" << 'EOF'
# Build Plan — FB110
EOF

cat > "$TMPDIR/build23/.kimi/meta-report.md" << 'EOF'
# Meta Report
Score: 4.0/5.0
EOF

cat > "$TMPDIR/vsm/viable-swarm-model/references/knowledge-broker.md" << 'EOF'
# Broker
> **Last updated**: 2026-06-05
EOF

# Simulate session-end payload
PAYLOAD='{"session_id":"test-session-23","cwd":"'$TMPDIR/build23'","reason":"stop"}'
RC=0
echo "$PAYLOAD" | bash "$SCRIPT_DIR/session-end.sh" >/dev/null 2>&1 || RC=$?

if [ "$RC" -eq 0 ] && \
   [ -f "$TMPDIR/build23/.kimi/process-compliance-precomputed.md" ] && \
   grep -q "process-audit.md missing" "$TMPDIR/build23/.kimi/session-telemetry.md" 2>/dev/null; then
    pass
else
    fail "session-end did not auto-generate compliance or flag missing audit"
fi

# ============================================================================
# Test 24: test-split-orchestrator.py — backend multi-domain split
# ============================================================================

echo -n "TEST: test-split-orchestrator.py splits backend domains correctly ... "

RC=0
OUTPUT=$(python3 "$SCRIPT_DIR/../scripts/test-split-orchestrator.py" \
    --domains "auth,courses,uploads,graphql,users,recipes,ingredients" \
    --tier 2 --backend 2>&1) || RC=$?

if [ "$RC" -eq 0 ] && \
   echo "$OUTPUT" | grep -q "Recommended spawns" && \
   echo "$OUTPUT" | grep -q "auth, graphql, uploads" && \
   echo "$OUTPUT" | grep -q "vsm_backend_tester"; then
    pass
else
    fail "backend split plan incorrect"
fi

# ============================================================================
# Test 25: test-split-orchestrator.py — frontend JSON output
# ============================================================================

echo -n "TEST: test-split-orchestrator.py outputs valid frontend JSON ... "

RC=0
OUTPUT=$(python3 "$SCRIPT_DIR/../scripts/test-split-orchestrator.py" \
    --domains "auth,home,courses,graphql,uploads" \
    --tier 2 --frontend --json 2>&1) || RC=$?

if [ "$RC" -eq 0 ] && \
   echo "$OUTPUT" | grep -q '"stack": "frontend"' && \
   echo "$OUTPUT" | grep -q '"spawn_count":' && \
   echo "$OUTPUT" | grep -q '"total_estimated_lines":'; then
    pass
else
    fail "frontend JSON output incorrect"
fi

# ============================================================================
# Test 26: test-split-orchestrator.py — writes plan to build directory
# ============================================================================

echo -n "TEST: test-split-orchestrator.py writes plan to build dir ... "

mkdir -p "$TMPDIR/build26/.kimi"

RC=0
python3 "$SCRIPT_DIR/../scripts/test-split-orchestrator.py" \
    --domains "auth,users" --tier 1 --backend --build-dir "$TMPDIR/build26" \
    >/dev/null 2>&1 || RC=$?

if [ "$RC" -eq 0 ] && \
   [ -f "$TMPDIR/build26/.kimi/test-spawn-plan.md" ] && \
   grep -q "Backend Spawn Plan" "$TMPDIR/build26/.kimi/test-spawn-plan.md"; then
    pass
else
    fail "build-dir plan file not written correctly"
fi

# ============================================================================
# Test 27: session-end.sh — flags missing security-report.md when auth code present
# ============================================================================

echo -n "TEST: session-end.sh flags security bypass when auth code present ... "

mkdir -p "$TMPDIR/build27/.kimi"
mkdir -p "$TMPDIR/build27/backend"

cat > "$TMPDIR/build27/plan.md" << 'EOF'
# Build Plan — FB111
EOF

cat > "$TMPDIR/build27/.kimi/meta-report.md" << 'EOF'
# Meta Report
Score: 4.0/5.0
EOF

cat > "$TMPDIR/build27/backend/auth.py" << 'EOF'
import jwt
from passlib.context import CryptContext
EOF

cat > "$TMPDIR/vsm/viable-swarm-model/references/mutation-state.md" << 'EOF'
# Mutation State
| ID | Source | Type | Target Failure | Status | Builds Tested | Score | Hypothesis | Experiment | Next Review |
|---|---|---|---|---|---|---|---|---|---|
| T1 | Test | append-only | Test failure | effective | 5 | 4 | — | — | — |
EOF

cat > "$TMPDIR/vsm/viable-swarm-model/references/hypotheses.md" << 'EOF'
# Hypotheses
## H1
**Status**: confirmed
EOF

cat > "$TMPDIR/vsm/viable-swarm-model/references/knowledge-broker.md" << 'EOF'
# Broker
> **Last updated**: 2026-06-05
EOF

cat > "$TMPDIR/vsm/viable-swarm-model/references/build-health-history.md" << 'EOF'
# Build Health History
EOF

# Simulate session-end payload
PAYLOAD='{"session_id":"test-session-27","cwd":"'$TMPDIR/build27'","reason":"stop"}'
RC=0
echo "$PAYLOAD" | bash "$SCRIPT_DIR/session-end.sh" >/dev/null 2>&1 || RC=$?

if [ "$RC" -eq 0 ] && \
   grep -q "security-report.md missing" "$TMPDIR/build27/.kimi/session-telemetry.md" 2>/dev/null && \
   grep -q "CRITICAL" "$TMPDIR/build27/.kimi/session-telemetry.md" 2>/dev/null; then
    pass
else
    fail "session-end did not flag CRITICAL security bypass"
fi

# ============================================================================
# Test 28: session-end.sh — no security flag when build has no security surface
# ============================================================================

echo -n "TEST: session-end.sh does NOT flag security bypass for static site ... "

mkdir -p "$TMPDIR/build28/.kimi"

cat > "$TMPDIR/build28/plan.md" << 'EOF'
# Build Plan — FB112
EOF

cat > "$TMPDIR/build28/.kimi/meta-report.md" << 'EOF'
# Meta Report
Score: 4.0/5.0
EOF

cat > "$TMPDIR/build28/index.html" << 'EOF'
<!DOCTYPE html>
<html><body>Hello</body></html>
EOF

PAYLOAD='{"session_id":"test-session-28","cwd":"'$TMPDIR/build28'","reason":"stop"}'
RC=0
echo "$PAYLOAD" | bash "$SCRIPT_DIR/session-end.sh" >/dev/null 2>&1 || RC=$?

if [ "$RC" -eq 0 ] && \
   ! grep -q "security-report.md missing" "$TMPDIR/build28/.kimi/session-telemetry.md" 2>/dev/null; then
    pass
else
    fail "session-end falsely flagged security bypass for static site"
fi

# ============================================================================
# Test 29: session-end.sh — no security flag when security-report.md exists
# ============================================================================

echo -n "TEST: session-end.sh does NOT flag when security-report.md present ... "

mkdir -p "$TMPDIR/build29/.kimi"
mkdir -p "$TMPDIR/build29/backend"

cat > "$TMPDIR/build29/plan.md" << 'EOF'
# Build Plan — FB113
EOF

cat > "$TMPDIR/build29/.kimi/meta-report.md" << 'EOF'
# Meta Report
Score: 4.0/5.0
EOF

cat > "$TMPDIR/build29/.kimi/security-report.md" << 'EOF'
# Security Report
Zero findings.
EOF

cat > "$TMPDIR/build29/backend/auth.py" << 'EOF'
import jwt
EOF

PAYLOAD='{"session_id":"test-session-29","cwd":"'$TMPDIR/build29'","reason":"stop"}'
RC=0
echo "$PAYLOAD" | bash "$SCRIPT_DIR/session-end.sh" >/dev/null 2>&1 || RC=$?

if [ "$RC" -eq 0 ] && \
   ! grep -q "security-report.md missing" "$TMPDIR/build29/.kimi/session-telemetry.md" 2>/dev/null; then
    pass
else
    fail "session-end falsely flagged security bypass when report exists"
fi

# ============================================================================
# Test 30: integration-test-closeout.py — all closeout scripts run together
# ============================================================================

echo -n "TEST: integration-test-closeout.py exercises full closeout pipeline ... "

RC=0
python3 "$SCRIPT_DIR/../scripts/integration-test-closeout.py" >/dev/null 2>&1 || RC=$?

if [ "$RC" -eq 0 ]; then
    pass
else
    fail "integration test for closeout pipeline failed"
fi

# ============================================================================
# Test 31: session-end.sh — Tier 2+ build missing product-brief.md flagged
# ============================================================================

echo -n "TEST: session-end.sh flags missing product-brief.md for Tier 2 ... "

mkdir -p "$TMPDIR/build31/.kimi"

cat > "$TMPDIR/build31/plan.md" << 'EOF'
# Build Plan — FB115
**Tier**: 2
EOF

cat > "$TMPDIR/build31/.kimi/meta-report.md" << 'EOF'
# Meta Report
Score: 4.0/5.0
EOF

PAYLOAD='{"session_id":"test-session-31","cwd":"'$TMPDIR/build31'","reason":"stop"}'
RC=0
echo "$PAYLOAD" | bash "$SCRIPT_DIR/session-end.sh" >/dev/null 2>&1 || RC=$?

if [ "$RC" -eq 0 ] && \
   grep -q "product-brief.md" "$TMPDIR/build31/.kimi/session-telemetry.md" 2>/dev/null && \
   grep -q "vsm_product agent not spawned" "$TMPDIR/build31/.kimi/session-telemetry.md" 2>/dev/null; then
    pass
else
    fail "session-end did not flag missing product brief for Tier 2"
fi

# ============================================================================
# Test 32: session-end.sh — Tier 1 build missing product-brief.md NOT flagged
# ============================================================================

echo -n "TEST: session-end.sh does NOT flag missing product-brief.md for Tier 1 ... "

mkdir -p "$TMPDIR/build32/.kimi"

cat > "$TMPDIR/build32/plan.md" << 'EOF'
# Build Plan — FB116
**Tier**: 1
EOF

cat > "$TMPDIR/build32/.kimi/meta-report.md" << 'EOF'
# Meta Report
Score: 4.0/5.0
EOF

PAYLOAD='{"session_id":"test-session-32","cwd":"'$TMPDIR/build32'","reason":"stop"}'
RC=0
echo "$PAYLOAD" | bash "$SCRIPT_DIR/session-end.sh" >/dev/null 2>&1 || RC=$?

if [ "$RC" -eq 0 ] && \
   ! grep -q "product-brief.md" "$TMPDIR/build32/.kimi/session-telemetry.md" 2>/dev/null; then
    pass
else
    fail "session-end falsely flagged missing product brief for Tier 1"
fi

# ============================================================================
# Test 33: session-end.sh — Tier 2+ with product-brief.md present NOT flagged
# ============================================================================

echo -n "TEST: session-end.sh does NOT flag when product-brief.md present ... "

mkdir -p "$TMPDIR/build33/.kimi"

cat > "$TMPDIR/build33/plan.md" << 'EOF'
# Build Plan — FB117
**Tier**: 3
EOF

cat > "$TMPDIR/build33/.kimi/meta-report.md" << 'EOF'
# Meta Report
Score: 4.0/5.0
EOF

cat > "$TMPDIR/build33/product-brief.md" << 'EOF'
# Product Brief

## Problem
Users need Z.

## Out of Scope
- Auth subsystem
- Real-time sync
EOF

PAYLOAD='{"session_id":"test-session-33","cwd":"'$TMPDIR/build33'","reason":"stop"}'
RC=0
echo "$PAYLOAD" | bash "$SCRIPT_DIR/session-end.sh" >/dev/null 2>&1 || RC=$?

if [ "$RC" -eq 0 ] && \
   ! grep -q "product-brief.md" "$TMPDIR/build33/.kimi/session-telemetry.md" 2>/dev/null; then
    pass
else
    fail "session-end falsely flagged product brief when present"
fi

# ============================================================================
# Test 34: meta-metrics-precompute.py — extracts metrics from mock artifacts
# ============================================================================

echo -n "TEST: meta-metrics-precompute.py extracts metrics from mock build ... "

mkdir -p "$TMPDIR/build34/.kimi"

cat > "$TMPDIR/build34/.kimi/phase4-gate.md" << 'EOF'
# Phase 4 Gate

| Check | Result | Details |
|---|---|---|
| Backend tests | PASS | 42/42 passed, 0 failed, 0 errors |
| Frontend tests | PASS | 15/15 passed, 0 failed, 0 errors |
| Frontend build | PASS | No errors |

## Security Status (Post-Fix Wave)
- BLOCKER: 0
- CRITICAL: 0
- HIGH: 1
- MEDIUM: 2
- LOW: 0
EOF

cat > "$TMPDIR/build34/.kimi/security-report.md" << 'EOF'
# Security Audit

## Executive Summary
- **Verdict**: ISSUES
- **BLOCKER count**: 0
- **CRITICAL count**: 0
- **HIGH count**: 3
- **MEDIUM count**: 5
- **LOW count**: 1
EOF

cat > "$TMPDIR/build34/.kimi/foundation-audit.md" << 'EOF'
# Foundation Audit

- **BLOCKER**: Missing auth router
- **ISSUE**: Lazy engine pattern not applied
EOF

cat > "$TMPDIR/build34/.kimi/lessons.md" << 'EOF'
# Lessons

## Lesson 1
Foo

## Lesson 2
Bar

## Lesson 3
Baz
EOF

cat > "$TMPDIR/build34/.kimi/mutations-applied.md" << 'EOF'
# Mutations Applied

- **M1**: Fix auth
- **M2**: Fix engine
- **M3**: Fix config
EOF

RC=0
python3 "$SCRIPT_DIR/../scripts/meta-metrics-precompute.py" --build-dir "$TMPDIR/build34" >/dev/null 2>&1 || RC=$?

if [ "$RC" -eq 0 ] && \
   [ -f "$TMPDIR/build34/.kimi/meta-metrics-precomputed.md" ] && \
   grep -q "backend_tests_passed: 42" "$TMPDIR/build34/.kimi/meta-metrics-precomputed.md" && \
   grep -q "security_high: 3" "$TMPDIR/build34/.kimi/meta-metrics-precomputed.md" && \
   grep -q "lessons_count: 3" "$TMPDIR/build34/.kimi/meta-metrics-precomputed.md" && \
   grep -q "mutations_count: 3" "$TMPDIR/build34/.kimi/meta-metrics-precomputed.md" && \
   grep -q "blocker_count: 1" "$TMPDIR/build34/.kimi/meta-metrics-precomputed.md"; then
    pass
else
    fail "meta-metrics-precompute.py did not extract expected metrics"
fi

# ============================================================================
# Test 35: meta-metrics-precompute.py — rejects nonexistent build directory
# ============================================================================

echo -n "TEST: meta-metrics-precompute.py rejects nonexistent directory ... "

RC=0
python3 "$SCRIPT_DIR/../scripts/meta-metrics-precompute.py" --build-dir "$TMPDIR/nonexistent" >/dev/null 2>&1 || RC=$?

if [ "$RC" -ne 0 ]; then
    pass
else
    fail "meta-metrics-precompute.py should fail on nonexistent directory"
fi

# ============================================================================
# Test 36: meta-metrics-precompute.py — handles empty .kimi directory
# ============================================================================

echo -n "TEST: meta-metrics-precompute.py handles empty .kimi directory ... "

mkdir -p "$TMPDIR/build36/.kimi"

RC=0
python3 "$SCRIPT_DIR/../scripts/meta-metrics-precompute.py" --build-dir "$TMPDIR/build36" >/dev/null 2>&1 || RC=$?

if [ "$RC" -eq 0 ] && \
   [ -f "$TMPDIR/build36/.kimi/meta-metrics-precomputed.md" ] && \
   grep -q "Artifacts found" "$TMPDIR/build36/.kimi/meta-metrics-precomputed.md" && \
   grep "Artifacts found" "$TMPDIR/build36/.kimi/meta-metrics-precomputed.md" | grep -q "0"; then
    pass
else
    fail "meta-metrics-precompute.py did not handle empty .kimi correctly"
fi

# ============================================================================
# Test 37: session-end.sh — Tier 2+ build missing test-spawn-plan.md flagged
# ============================================================================

echo -n "TEST: session-end.sh flags missing test-spawn-plan.md for Tier 2 ... "

mkdir -p "$TMPDIR/build37/.kimi"

cat > "$TMPDIR/build37/plan.md" << 'EOF'
# Build Plan — FB118
**Tier**: 2
EOF

cat > "$TMPDIR/build37/.kimi/meta-report.md" << 'EOF'
# Meta Report
Score: 4.0/5.0
EOF

PAYLOAD='{"session_id":"test-session-37","cwd":"'$TMPDIR/build37'","reason":"stop"}'
RC=0
echo "$PAYLOAD" | bash "$SCRIPT_DIR/session-end.sh" >/dev/null 2>&1 || RC=$?

if [ "$RC" -eq 0 ] && \
   grep -q "test-spawn-plan.md" "$TMPDIR/build37/.kimi/session-telemetry.md" 2>/dev/null && \
   grep -q "test-split-orchestrator.py not run" "$TMPDIR/build37/.kimi/session-telemetry.md" 2>/dev/null; then
    pass
else
    fail "session-end did not flag missing test spawn plan for Tier 2"
fi

# ============================================================================
# Test 38: session-end.sh — Tier 1 build missing test-spawn-plan.md NOT flagged
# ============================================================================

echo -n "TEST: session-end.sh does NOT flag missing test-spawn-plan.md for Tier 1 ... "

mkdir -p "$TMPDIR/build38/.kimi"

cat > "$TMPDIR/build38/plan.md" << 'EOF'
# Build Plan — FB119
**Tier**: 1
EOF

cat > "$TMPDIR/build38/.kimi/meta-report.md" << 'EOF'
# Meta Report
Score: 4.0/5.0
EOF

PAYLOAD='{"session_id":"test-session-38","cwd":"'$TMPDIR/build38'","reason":"stop"}'
RC=0
echo "$PAYLOAD" | bash "$SCRIPT_DIR/session-end.sh" >/dev/null 2>&1 || RC=$?

if [ "$RC" -eq 0 ] && \
   ! grep -q "test-spawn-plan.md" "$TMPDIR/build38/.kimi/session-telemetry.md" 2>/dev/null; then
    pass
else
    fail "session-end falsely flagged missing test spawn plan for Tier 1"
fi

# ============================================================================
# Test 39: session-end.sh — Tier 2+ with test-spawn-plan.md present NOT flagged
# ============================================================================

echo -n "TEST: session-end.sh does NOT flag when test-spawn-plan.md present ... "

mkdir -p "$TMPDIR/build39/.kimi"

cat > "$TMPDIR/build39/plan.md" << 'EOF'
# Build Plan — FB120
**Tier**: 3
EOF

cat > "$TMPDIR/build39/.kimi/meta-report.md" << 'EOF'
# Meta Report
Score: 4.0/5.0
EOF

cat > "$TMPDIR/build39/.kimi/test-spawn-plan.md" << 'EOF'
# Test Spawn Plan

## Spawn 1
- auth, graphql
EOF

PAYLOAD='{"session_id":"test-session-39","cwd":"'$TMPDIR/build39'","reason":"stop"}'
RC=0
echo "$PAYLOAD" | bash "$SCRIPT_DIR/session-end.sh" >/dev/null 2>&1 || RC=$?

if [ "$RC" -eq 0 ] && \
   ! grep -q "test-spawn-plan.md" "$TMPDIR/build39/.kimi/session-telemetry.md" 2>/dev/null; then
    pass
else
    fail "session-end falsely flagged test spawn plan when present"
fi

# ============================================================================
# Test 40: mutation-portfolio-health.py — detects effective→historical promotions
# ============================================================================

echo -n "TEST: mutation-portfolio-health.py detects effective->historical promotions ... "

cat > "$TMPDIR/mock-mutation-state.md" << 'EOF'
# Mutation State

| ID | Source | Type | Target Failure | Status | Builds Tested | Score | Hypothesis | Experiment | Next Review |
|---|---|---|---|---|---|---|---|---|---|
| E1 | Test | append-only | Test failure | effective | 5 | 5 | — | — | — |
| E2 | Test | append-only | Test failure | effective | 6 | 4 | — | — | — |
| E3 | Test | append-only | Test failure | effective | 3 | 5 | — | — | — |
| P1 | Test | append-only | Test failure | probation | 3 | 4 | — | — | — |
| P2 | Test | append-only | Test failure | probation | 3 | 2 | — | — | — |
| M1 | Test | append-only | Test failure | monitor | 5 | 4 | — | — | — |
EOF

RC=0
python3 "$SCRIPT_DIR/../scripts/mutation-portfolio-health.py" \
  --build-dir "$TMPDIR/build40" \
  --mutation-state "$TMPDIR/mock-mutation-state.md" >/dev/null 2>&1 || RC=$?

if [ "$RC" -eq 0 ] && \
   [ -f "$TMPDIR/build40/.kimi/mutation-portfolio-health.md" ] && \
   grep -q "Effective → Historical Promotions" "$TMPDIR/build40/.kimi/mutation-portfolio-health.md" && \
   grep -q "E1" "$TMPDIR/build40/.kimi/mutation-portfolio-health.md" && \
   grep -q "E2" "$TMPDIR/build40/.kimi/mutation-portfolio-health.md" && \
   ! grep -A5 "Effective → Historical Promotions" "$TMPDIR/build40/.kimi/mutation-portfolio-health.md" | grep -q "E3"; then
    pass
else
    fail "mutation-portfolio-health.py did not detect expected historical promotions"
fi

# ============================================================================
# Test 41: stop-verifier.sh — blocks when mutations-applied.md missing
# ============================================================================

echo -n "TEST: stop-verifier.sh blocks stop when mutations-applied.md missing ... "

mkdir -p "$TMPDIR/build41/.kimi"
mkdir -p "$TMPDIR/vsm/viable-swarm-model/references"

# Create empty mutation-log.md so Check 2 doesn't interfere
touch "$TMPDIR/vsm/viable-swarm-model/references/mutation-log.md"

# Create a completed build artifact but no mutations-applied.md
cat > "$TMPDIR/build41/.kimi/meta-report.md" << 'EOF'
# Meta Report
Score: 4.0/5.0
EOF

PAYLOAD='{"session_id":"test-session-41","cwd":"'$TMPDIR/build41'","reason":"stop","stop_hook_active":false}'
RC=0
OUTPUT=$(echo "$PAYLOAD" | bash "$SCRIPT_DIR/stop-verifier.sh" 2>/dev/null) || RC=$?

if echo "$OUTPUT" | grep -q '"permissionDecision":"deny"' && \
   echo "$OUTPUT" | grep -q "mutations-applied.md"; then
    pass
else
    fail "stop-verifier did not block for missing mutations-applied.md"
fi

# ============================================================================
# Test 42: stop-verifier.sh — allows stop when all artifacts present
# ============================================================================

echo -n "TEST: stop-verifier.sh allows stop when all artifacts present ... "

mkdir -p "$TMPDIR/build42/.kimi"
mkdir -p "$TMPDIR/vsm/viable-swarm-model/references"

# Create empty mutation-log.md
touch "$TMPDIR/vsm/viable-swarm-model/references/mutation-log.md"

# Create mutation-state.md with build ID
cat > "$TMPDIR/vsm/viable-swarm-model/references/mutation-state.md" << 'EOF'
# Mutation State
| ID | Source | Type | Target Failure | Status | Builds Tested | Score | Hypothesis | Experiment | Next Review |
|---|---|---|---|---|---|---|---|---|---|
| T1 | FB42 Build | append-only | Test | effective | 5 | 5 | — | — | — |
EOF

# Create all required artifacts
cat > "$TMPDIR/build42/.kimi/mutations-applied.md" << 'EOF'
## Build ID: FB42
**Mutation**: M1
**Effectiveness**: 5/5
EOF

cat > "$TMPDIR/build42/.kimi/meta-report.md" << 'EOF'
# Meta Report
Score: 4.0/5.0
EOF

cat > "$TMPDIR/build42/.kimi/process-audit.md" << 'EOF'
# Process Audit
Score: 85/100
All checks passed.
EOF

cat > "$TMPDIR/build42/.kimi/mutation-portfolio-review.md" << 'EOF'
# Mutation Portfolio Review
All good.
EOF

# Touch files to ensure mtimes are reasonable (process-audit not retroactive)
touch "$TMPDIR/build42/.kimi/mutations-applied.md"
touch "$TMPDIR/build42/.kimi/meta-report.md"
touch "$TMPDIR/build42/.kimi/process-audit.md"

PAYLOAD='{"session_id":"test-session-42","cwd":"'$TMPDIR/build42'","reason":"stop","stop_hook_active":false}'
RC=0
OUTPUT=$(echo "$PAYLOAD" | bash "$SCRIPT_DIR/stop-verifier.sh" 2>/dev/null) || RC=$?

if [ "$RC" -eq 0 ] && ! echo "$OUTPUT" | grep -q '"permissionDecision":"deny"'; then
    pass
else
    fail "stop-verifier blocked despite all artifacts present"
fi

# ============================================================================
# Test 43: stop-verifier.sh — blocks when portfolio-review.md missing
# ============================================================================

echo -n "TEST: stop-verifier.sh blocks stop when portfolio-review.md missing ... "

mkdir -p "$TMPDIR/build43/.kimi"
mkdir -p "$TMPDIR/vsm/viable-swarm-model/references"

# Create empty mutation-log.md
touch "$TMPDIR/vsm/viable-swarm-model/references/mutation-log.md"

# Create mutation-state.md with build ID
cat > "$TMPDIR/vsm/viable-swarm-model/references/mutation-state.md" << 'EOF'
# Mutation State
| ID | Source | Type | Target Failure | Status | Builds Tested | Score | Hypothesis | Experiment | Next Review |
|---|---|---|---|---|---|---|---|---|---|
| T1 | FB43 Build | append-only | Test | effective | 5 | 5 | — | — | — |
EOF

cat > "$TMPDIR/build43/.kimi/mutations-applied.md" << 'EOF'
## Build ID: FB43
**Mutation**: M1
**Effectiveness**: 5/5
EOF

cat > "$TMPDIR/build43/.kimi/meta-report.md" << 'EOF'
# Meta Report
Score: 4.0/5.0
EOF

cat > "$TMPDIR/build43/.kimi/process-audit.md" << 'EOF'
# Process Audit
Score: 85/100
All checks passed.
EOF

# NO mutation-portfolio-review.md — this should trigger Check 6

touch "$TMPDIR/build43/.kimi/mutations-applied.md"
touch "$TMPDIR/build43/.kimi/meta-report.md"
touch "$TMPDIR/build43/.kimi/process-audit.md"

PAYLOAD='{"session_id":"test-session-43","cwd":"'$TMPDIR/build43'","reason":"stop","stop_hook_active":false}'
RC=0
OUTPUT=$(echo "$PAYLOAD" | bash "$SCRIPT_DIR/stop-verifier.sh" 2>/dev/null) || RC=$?

if echo "$OUTPUT" | grep -q '"permissionDecision":"deny"' && \
   echo "$OUTPUT" | grep -q "mutation-portfolio-review.md"; then
    pass
else
    fail "stop-verifier did not block for missing mutation-portfolio-review.md"
fi

# ============================================================================
# Test 44: hypothesis-backlog-curator.py — archives confirmed hypotheses
# ============================================================================

echo -n "TEST: hypothesis-backlog-curator.py archives confirmed hypotheses ... "

mkdir -p "$TMPDIR/curator-test"

cat > "$TMPDIR/curator-test/hypotheses.md" << 'EOF'
# Hypotheses

## Index
| Hypothesis | Status |
|---|---|
| H1 | untested |
| H2 | confirmed |
| H3 | untested |

---

## H1: Test hypothesis one
**Status**: untested
**Proposed**: 2026-06-01
**Rationale**: Test.

---

## H2: Test hypothesis two
**Status**: confirmed
**Tested by**: FB99
**Result**: CONFIRMED.

---

## H3: Test hypothesis three
**Status**: untested
**Proposed**: 2026-06-01
**Rationale**: Test.
EOF

python3 "$SCRIPT_DIR/../scripts/hypothesis-backlog-curator.py" \
    --hypotheses "$TMPDIR/curator-test/hypotheses.md" \
    --archive "$TMPDIR/curator-test/archive.md" 2>/dev/null

# Check that H2 was archived
if grep -q "H2: Test hypothesis two" "$TMPDIR/curator-test/archive.md"; then
    :
else
    fail "H2 not archived"
fi

# Check that H1 and H3 remain
if grep -q "## H1:" "$TMPDIR/curator-test/hypotheses.md" && \
   grep -q "## H3:" "$TMPDIR/curator-test/hypotheses.md"; then
    :
else
    fail "H1 or H3 missing from hypotheses.md"
fi

# Check that H2 was removed from hypotheses.md
if grep -q "## H2:" "$TMPDIR/curator-test/hypotheses.md"; then
    fail "H2 still present in hypotheses.md"
fi

# Check index was updated
if grep -q "| H1 | untested |" "$TMPDIR/curator-test/hypotheses.md" && \
   grep -q "| H3 | untested |" "$TMPDIR/curator-test/hypotheses.md"; then
    pass
else
    fail "index not updated correctly"
fi

# ============================================================================
# Test 45: hypothesis-backlog-curator.py — picks latest status from update section
# ============================================================================

echo -n "TEST: hypothesis-backlog-curator.py picks latest status from update section ... "

mkdir -p "$TMPDIR/curator-test2"

cat > "$TMPDIR/curator-test2/hypotheses.md" << 'EOF'
# Hypotheses

## Index
| Hypothesis | Status |
|---|---|
| H1 | untested |

---

## H1: Test hypothesis
**Status**: untested
**Proposed**: 2026-06-01
**Rationale**: Test.

---

## FB99 Updates

### H1: Test hypothesis update
**Status**: confirmed
**Tested by**: FB99
**Result**: CONFIRMED.
EOF

python3 "$SCRIPT_DIR/../scripts/hypothesis-backlog-curator.py" \
    --hypotheses "$TMPDIR/curator-test2/hypotheses.md" \
    --archive "$TMPDIR/curator-test2/archive.md" 2>/dev/null

# H1 should be archived because latest status is confirmed
if grep -q "H1: Test hypothesis" "$TMPDIR/curator-test2/archive.md"; then
    pass
else
    fail "H1 not archived despite confirmed update section"
fi

# ============================================================================
# Test 46: hypothesis-backlog-curator.py — dry-run makes no changes
# ============================================================================

echo -n "TEST: hypothesis-backlog-curator.py dry-run makes no changes ... "

mkdir -p "$TMPDIR/curator-test3"

cat > "$TMPDIR/curator-test3/hypotheses.md" << 'EOF'
# Hypotheses

## Index
| Hypothesis | Status |
|---|---|
| H1 | confirmed |

---

## H1: Test hypothesis
**Status**: confirmed
**Tested by**: FB99
**Result**: CONFIRMED.
EOF

BEFORE=$(md5 -q "$TMPDIR/curator-test3/hypotheses.md")

python3 "$SCRIPT_DIR/../scripts/hypothesis-backlog-curator.py" \
    --dry-run \
    --hypotheses "$TMPDIR/curator-test3/hypotheses.md" \
    --archive "$TMPDIR/curator-test3/archive.md" 2>/dev/null

AFTER=$(md5 -q "$TMPDIR/curator-test3/hypotheses.md")

if [ "$BEFORE" = "$AFTER" ] && [ ! -f "$TMPDIR/curator-test3/archive.md" ]; then
    pass
else
    fail "dry-run modified files"
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
