#!/usr/bin/env bash
# diagnostic-router.sh — Self-healing hook diagnostic router for the VSM organism
# Usage: diagnostic-router.sh <hook-name> <exit-code> [error-message]
#        diagnostic-router.sh --list-known
#        diagnostic-router.sh --test
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VSM_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
DIAG_DIR="$VSM_ROOT/.kimi"
DIAG_FILE="$DIAG_DIR/hook-diagnostic.md"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

log_stderr() {
    printf '%s\n' "$*" >&2
}

ensure_diag_dir() {
    if [[ ! -d "$DIAG_DIR" ]]; then
        mkdir -p "$DIAG_DIR" 2>/dev/null || {
            log_stderr "WARNING: Could not create $DIAG_DIR"
            return 1
        }
    fi
}

write_diagnostic() {
    local date_str hook_name exit_code diagnosis action priority next_steps
    date_str="$(date '+%Y-%m-%d %H:%M')"
    hook_name="$1"
    exit_code="$2"
    diagnosis="$3"
    action="$4"
    priority="$5"
    next_steps="$6"

    local content
    content="# Hook Diagnostic Report
**Date**: ${date_str}
**Hook**: ${hook_name}
**Exit Code**: ${exit_code}

## Diagnosis
${diagnosis}

## Recommended Action
${action}

## Priority
${priority}

## Next Steps
${next_steps}
"

    if ! ensure_diag_dir; then
        log_stderr "WARNING: Diagnostic report could not be written to $DIAG_FILE"
        return 0
    fi

    if ! printf '%s\n' "$content" > "$DIAG_FILE" 2>/dev/null; then
        log_stderr "WARNING: Failed to write diagnostic report to $DIAG_FILE"
    fi
}

# ---------------------------------------------------------------------------
# Known-failure lookup
# Returns via globals: _DIAGNOSIS, _ACTION, _PRIORITY, _NEXT_STEPS
# ---------------------------------------------------------------------------

lookup_failure() {
    local hook="$1"
    local code="$2"

    # Reset globals
    _DIAGNOSIS=""
    _ACTION=""
    _PRIORITY=""
    _NEXT_STEPS=""

    if [[ "$code" -eq 0 ]]; then
        _DIAGNOSIS="Exit code 0 indicates success. No failure detected."
        _ACTION="None required."
        _PRIORITY="LOW"
        _NEXT_STEPS="1. Continue normal operation."
        return 0
    fi

    if [[ "$code" -eq 2 ]]; then
        _DIAGNOSIS="Block signal (exit code 2). The hook intentionally blocked an operation."
        _ACTION="Review the operation that triggered the block; the hook is functioning as designed."
        _PRIORITY="LOW"
        _NEXT_STEPS="1. Determine whether the blocked operation was legitimate.\n2. If legitimate, adjust context or data to satisfy the hook's guard condition.\n3. Re-run the operation."
        return 0
    fi

    case "$hook" in
        session-start.sh)
            _DIAGNOSIS="Hook DEPRECATED. session-start.sh has been removed from the supported hook set."
            _ACTION="Use Phase 0 manual checklist instead."
            _PRIORITY="LOW"
            _NEXT_STEPS=$'1. Open the Phase 0 manual checklist.\n2. Execute pre-session setup steps manually.\n3. Remove session-start.sh from ~/.kimi/config.toml if still present.'
            ;;
        auto-broker-update.sh)
            _DIAGNOSIS="auto-broker-update.sh encountered an error during broker update."
            _ACTION="Check auto-broker-update.sh logs for pipefail or grep errors."
            _PRIORITY="MEDIUM"
            _NEXT_STEPS=$'1. Check hooks/auto-broker-update.sh for syntax errors.\n2. Verify mutation-log.md exists and is readable.\n3. Run auto-broker-update.sh manually to reproduce.'
            ;;
        update-mutation-state.sh)
            _DIAGNOSIS="Possible format mismatch in mutation-state update."
            _ACTION="Run test-automation.sh to verify."
            _PRIORITY="HIGH"
            _NEXT_STEPS=$'1. Inspect ~/.kimi/mutation-state.md for formatting errors (duplicate IDs, malformed tables).\n2. Run test-automation.sh --validate-mutations.\n3. If mismatch persists, manually correct mutation-state.md and re-run the hook.'
            ;;
        stop-verifier.sh)
            _DIAGNOSIS="Mutation checkpoint may be incomplete."
            _ACTION="Check .kimi/mutations-applied.md exists and is non-empty."
            _PRIORITY="CRITICAL"
            _NEXT_STEPS=$'1. Verify '"$VSM_ROOT"$'/.kimi/mutations-applied.md exists.\n2. If missing, re-run the mutation tracking step from Phase 8c-ii.\n3. If empty, inspect the build log for truncation or timeout.\n4. Do not end session until checkpoint is complete.'
            ;;
        gate-guardian.sh)
            _DIAGNOSIS="Phase 4 gate verification failed."
            _ACTION="Check .kimi/phase4-gate.md for test results."
            _PRIORITY="CRITICAL"
            _NEXT_STEPS=$'1. Open '"$VSM_ROOT"$'/.kimi/phase4-gate.md.\n2. Verify test output shows ZERO failures.\n3. If failures exist, route to Phase 7 fix protocol.\n4. Do not proceed to Phase 5 until gate passes.'
            ;;
        boundary-guardian.sh)
            _DIAGNOSIS="Phase 6/7 boundary violation detected."
            _ACTION="Check for inline fixes in source code."
            _PRIORITY="CRITICAL"
            _NEXT_STEPS=$'1. Inspect recently modified source files (*.py, *.ts, *.tsx, *.js, *.jsx) for unplanned changes.\n2. If inline fix found, revert it and route through proper Phase 7 fix wave.\n3. Verify .kimi/re-audit-report.md exists before any re-audit.\n4. Update process log with violation details.'
            ;;
        structural-guardian.sh)
            # Listed in context but not in the explicit known-failure registry;
            # falls through to the unknown-failure default.
            ;&
        *)
            _DIAGNOSIS="Unknown failure."
            _ACTION="Check hook logs and re-run."
            _PRIORITY="MEDIUM"
            _NEXT_STEPS=$'1. Inspect ~/.kimi/logs/ or stdout/stderr for the hook.\n2. Verify hook script syntax with bash -n.\n3. Re-run the operation that triggered the hook.\n4. If reproducible, file a hypothesis in the mutation backlog.'
            ;;
    esac
}

# ---------------------------------------------------------------------------
# --list-known
# ---------------------------------------------------------------------------

cmd_list_known() {
    printf '%s\n' "Known VSM Hook Failure Registry"
    printf '%s\n' "================================"
    printf '%-28s %-10s %s\n' "Hook" "Priority" "Diagnosis"
    printf '%s\n' "----------------------------------------"

    local hooks=(
        "session-start.sh:LOW:Hook DEPRECATED"
        "auto-broker-update.sh:MEDIUM:auto-broker-update.sh encountered an error during broker update"
        "update-mutation-state.sh:HIGH:Possible format mismatch"
        "stop-verifier.sh:CRITICAL:Mutation checkpoint may be incomplete"
        "gate-guardian.sh:CRITICAL:Phase 4 gate verification failed"
        "boundary-guardian.sh:CRITICAL:Phase 6/7 boundary violation detected"
    )

    for entry in "${hooks[@]}"; do
        IFS=':' read -r hook prio diag <<< "$entry"
        printf '%-28s %-10s %s\n' "$hook" "$prio" "$diag"
    done
}

# ---------------------------------------------------------------------------
# --test
# ---------------------------------------------------------------------------

cmd_test() {
    local failures=0
    local tmp_stderr
    tmp_stderr="$(mktemp)"

    # Use a temporary diagnostic file so self-test does not overwrite real reports.
    local DIAG_FILE
    DIAG_FILE="$(mktemp)"

    # Helper to run one case
    run_case() {
        local hook="$1"
        local code="$2"
        local expected_diag="$3"
        local expected_prio="$4"

        # Clear previous stderr capture
        : > "$tmp_stderr"

        # Invoke lookup + write in a subshell so set -e doesn't kill us on expected paths
        (
            lookup_failure "$hook" "$code"
            write_diagnostic "$hook" "$code" "$_DIAGNOSIS" "$_ACTION" "$_PRIORITY" "$_NEXT_STEPS"
            log_stderr "[$hook exit=$code] $_DIAGNOSIS"
            log_stderr "Priority: $_PRIORITY"
        ) 2>> "$tmp_stderr"

        if ! grep -q "$expected_diag" "$tmp_stderr"; then
            log_stderr "TEST FAIL: $hook (code=$code) — expected diagnosis '$expected_diag' not found in stderr"
            ((failures++)) || true
        fi

        if ! grep -q "$expected_prio" "$tmp_stderr"; then
            log_stderr "TEST FAIL: $hook (code=$code) — expected priority '$expected_prio' not found in stderr"
            ((failures++)) || true
        fi

        # Verify report file was written (unless we know it can't be, e.g., in CI without dir)
        if [[ -f "$DIAG_FILE" ]]; then
            if ! grep -q "$expected_diag" "$DIAG_FILE"; then
                log_stderr "TEST FAIL: $hook (code=$code) — diagnosis not written to $DIAG_FILE"
                ((failures++)) || true
            fi
        fi
    }

    log_stderr "Running diagnostic-router self-test..."

    # Known hooks — simulate non-zero failure
    run_case "session-start.sh" 1 "Hook DEPRECATED" "LOW"
    run_case "auto-broker-update.sh" 1 "auto-broker-update.sh encountered" "MEDIUM"
    run_case "update-mutation-state.sh" 1 "Possible format mismatch" "HIGH"
    run_case "stop-verifier.sh" 1 "Mutation checkpoint may be incomplete" "CRITICAL"
    run_case "gate-guardian.sh" 1 "Phase 4 gate verification failed" "CRITICAL"
    run_case "boundary-guardian.sh" 1 "Phase 6/7 boundary violation detected" "CRITICAL"
    run_case "structural-guardian.sh" 1 "Unknown failure" "MEDIUM"

    # Unknown hook
    run_case "telemetry-logger.sh" 1 "Unknown failure" "MEDIUM"

    # Exit code 0 — should report success
    (
        lookup_failure "session-end.sh" 0
        log_stderr "[session-end.sh exit=0] $_DIAGNOSIS"
    ) 2> "$tmp_stderr"
    if ! grep -q "Exit code 0 indicates success" "$tmp_stderr"; then
        log_stderr "TEST FAIL: session-end.sh (code=0) — expected success message"
        ((failures++)) || true
    fi

    # Exit code 2 — block signal
    (
        lookup_failure "gate-guardian.sh" 2
        log_stderr "[gate-guardian.sh exit=2] $_DIAGNOSIS"
    ) 2> "$tmp_stderr"
    if ! grep -q "Block signal" "$tmp_stderr"; then
        log_stderr "TEST FAIL: gate-guardian.sh (code=2) — expected block-signal handling"
        ((failures++)) || true
    fi

    rm -f "$tmp_stderr" "$DIAG_FILE"

    if [[ "$failures" -gt 0 ]]; then
        log_stderr ""
        log_stderr "TEST RESULT: $failures failure(s)."
        exit 1
    fi

    log_stderr "TEST RESULT: All tests passed."
    exit 0
}

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

main() {
    if [[ "${1:-}" == "--list-known" ]]; then
        cmd_list_known
        exit 0
    fi

    if [[ "${1:-}" == "--test" ]]; then
        cmd_test
        exit 0
    fi

    if [[ $# -lt 2 ]]; then
        log_stderr "Usage: $0 <hook-name> <exit-code> [error-message]"
        log_stderr "       $0 --list-known"
        log_stderr "       $0 --test"
        exit 1
    fi

    local hook_name="$1"
    local exit_code="$2"
    local error_message="${3:-}"

    # Validate exit code is numeric
    if ! [[ "$exit_code" =~ ^-?[0-9]+$ ]]; then
        log_stderr "ERROR: exit-code must be an integer, got '$exit_code'"
        exit 1
    fi

    lookup_failure "$hook_name" "$exit_code"

    # Build next-steps with optional error message injection
    local next_steps="$_NEXT_STEPS"
    if [[ -n "$error_message" ]]; then
        next_steps="0. Raw error message: $error_message"$'\n'"$next_steps"
    fi

    # Write report (non-fatal on failure)
    write_diagnostic "$hook_name" "$exit_code" "$_DIAGNOSIS" "$_ACTION" "$_PRIORITY" "$next_steps"

    # Print diagnosis to stderr
    log_stderr ""
    log_stderr "=== VSM Hook Diagnostic ==="
    log_stderr "Hook:       $hook_name"
    log_stderr "Exit Code:  $exit_code"
    log_stderr "Diagnosis:  $_DIAGNOSIS"
    log_stderr "Action:     $_ACTION"
    log_stderr "Priority:   $_PRIORITY"
    log_stderr "==========================="
    log_stderr ""

    # Return 0 so the caller can continue processing the routed fix protocol
    exit 0
}

main "$@"
