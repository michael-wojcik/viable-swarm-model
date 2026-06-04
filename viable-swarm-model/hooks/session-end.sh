#!/bin/bash
# VSM Session End Hook
# Parses telemetry logs and updates skill-state.md with efficiency baselines.
# Clears per-session telemetry after processing.
#
# Event: SessionEnd

set -euo pipefail

PAYLOAD=$(cat)
SESSION_ID=$(echo "$PAYLOAD" | jq -r '.session_id // "unknown"')
CWD=$(echo "$PAYLOAD" | jq -r '.cwd // "/tmp"')
REASON=$(echo "$PAYLOAD" | jq -r '.reason // "unknown"')

TELEMETRY_DIR="$HOME/.vsm-telemetry"
SKILL_STATE="$HOME/vsm/viable-swarm-model/references/skill-state.md"

# Only process if we have telemetry
if [[ ! -d "$TELEMETRY_DIR" ]]; then
    exit 0
fi

# Count file writes for this session
FILE_WRITES=0
if [[ -f "$TELEMETRY_DIR/file-writes.jsonl" ]]; then
    FILE_WRITES=$(grep -c "$SESSION_ID" "$TELEMETRY_DIR/file-writes.jsonl" 2>/dev/null || true)
    FILE_WRITES=${FILE_WRITES:-0}
fi

# Count subagents spawned for this session
SUBAGENT_COUNT=0
if [[ -f "$TELEMETRY_DIR/subagents.jsonl" ]]; then
    SUBAGENT_COUNT=$(grep -c "$SESSION_ID" "$TELEMETRY_DIR/subagents.jsonl" 2>/dev/null || true)
    SUBAGENT_COUNT=${SUBAGENT_COUNT:-0}
fi

# Count unique agent types
AGENT_TYPES=""
if [[ -f "$TELEMETRY_DIR/subagents.jsonl" ]]; then
    AGENT_TYPES=$(grep "$SESSION_ID" "$TELEMETRY_DIR/subagents.jsonl" 2>/dev/null | jq -r '.agent_name' | sort -u | tr '\n' ',' | sed 's/,$//')
fi

# Calculate session duration from session log
SESSION_START=""
SESSION_END="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
DURATION_MIN="unknown"
if [[ -f "$TELEMETRY_DIR/sessions.jsonl" ]]; then
    SESSION_START=$(grep "$SESSION_ID" "$TELEMETRY_DIR/sessions.jsonl" 2>/dev/null | head -1 | jq -r '.ts // ""')
    if [[ -n "$SESSION_START" && "$SESSION_START" != "null" ]]; then
        START_EPOCH=$(date -j -f "%Y-%m-%dT%H:%M:%SZ" "$SESSION_START" +%s 2>/dev/null || date -d "$SESSION_START" +%s 2>/dev/null || echo "")
        END_EPOCH=$(date -j -f "%Y-%m-%dT%H:%M:%SZ" "$SESSION_END" +%s 2>/dev/null || date -d "$SESSION_END" +%s 2>/dev/null || echo "")
        if [[ -n "$START_EPOCH" && -n "$END_EPOCH" ]]; then
            DURATION_SEC=$((END_EPOCH - START_EPOCH))
            DURATION_MIN=$((DURATION_SEC / 60))
        fi
    fi
fi

# ── Background Agent Bypass Audit ──
# Hooks do NOT fire for background subagents. Scan for evidence of bypasses.
AUDIT_WARNINGS=""

# Check 1: Unverified phase4-gate.md with PASS
if [[ -f "$CWD/.kimi/phase4-gate.md" ]] && grep -qi "PASS" "$CWD/.kimi/phase4-gate.md" 2>/dev/null; then
    if [[ ! -f "$CWD/.kimi/.gate-guardian-verified" ]]; then
        AUDIT_WARNINGS="${AUDIT_WARNINGS}- phase4-gate.md contains PASS but no hook verification marker. Possible background agent bypass.\n"
    fi
else
    if [[ -f "$CWD/.kimi/meta-report.md" || -f "$CWD/.kimi/security-report.md" ]]; then
        AUDIT_WARNINGS="${AUDIT_WARNINGS}- CRITICAL: Build reached Phase 5+ without phase4-gate.md PASS. This is a process violation.\n"
    fi
fi

# Check 2: Boundary window violations
if [[ -f "$CWD/.kimi/synthesis-integration.md" ]] && [[ ! -f "$CWD/.kimi/re-audit-report.md" ]]; then
    AUDIT_WARNINGS="${AUDIT_WARNINGS}- Boundary window open (synthesis-integration.md exists, re-audit-report.md missing). Review for inline fixes.\n"
fi

# Check 3: Unapproved structural changes
if [[ ! -f "$CWD/.kimi/.structural-mutation-approved" ]]; then
    if [[ -f "$CWD/SKILL.md" ]] && [[ -f "$TELEMETRY_DIR/sessions.jsonl" ]]; then
        AUDIT_WARNINGS="${AUDIT_WARNINGS}- No structural mutation approval marker. If SKILL.md or agents/ were modified this session, it was unapproved.\n"
    fi
fi

# Check 4: Missing mutations-applied.md in completed builds
if [[ -f "$CWD/.kimi/meta-report.md" || -f "$CWD/.kimi/process-audit.md" ]]; then
    if [[ ! -f "$CWD/.kimi/mutations-applied.md" ]]; then
        AUDIT_WARNINGS="${AUDIT_WARNINGS}- CRITICAL: Phase 8b complete but mutations-applied.md missing. Phase 8c-ii bypassed.\n"
    fi
fi

# Check 5: Missing lessons.md in completed builds
if [[ -f "$CWD/.kimi/meta-report.md" && ! -f "$CWD/.kimi/lessons.md" ]]; then
    AUDIT_WARNINGS="${AUDIT_WARNINGS}- Phase 8b complete but lessons.md missing. Phase 8 reflection bypassed.\n"
fi

# Check 6: Missing process-audit.md in completed builds
if [[ -f "$CWD/.kimi/meta-report.md" && ! -f "$CWD/.kimi/process-audit.md" ]]; then
    AUDIT_WARNINGS="${AUDIT_WARNINGS}- Phase 8b complete but process-audit.md missing. Process auditor not spawned.\n"
fi

# Check 7: knowledge-broker.md consumption check
if [[ -f "$CWD/plan.md" ]]; then
    if ! grep -qi "knowledge-broker\|Active Constraints\|broker trap" "$CWD/plan.md" 2>/dev/null; then
        AUDIT_WARNINGS="${AUDIT_WARNINGS}- plan.md has no knowledge broker references. Phase 0 broker read likely skipped.\n"
    fi
fi

# ── Auto-update mutation state (H213 safety net) ──
# If mutations-applied.md exists but mutation-state.md was not updated during
# Phase 8c-ii (S5 forgot to run update-mutation-state.sh), update it now.
UPDATE_SCRIPT="$HOME/vsm/viable-swarm-model/hooks/update-mutation-state.sh"
if [[ -f "$CWD/.kimi/mutations-applied.md" && -f "$UPDATE_SCRIPT" ]]; then
    echo "Auto-updating mutation state from $CWD/.kimi/mutations-applied.md ..."
    bash "$UPDATE_SCRIPT" "$CWD" >/dev/null 2>&1 || echo "Mutation state auto-update failed (non-fatal)"
fi

# Build telemetry block — write to EPHEMERAL .kimi/ file, NOT tracked skill-state.md
SESSION_TELEMETRY_FILE="$CWD/.kimi/session-telemetry.md"

TELEMETRY_BLOCK=$(cat << EOF
# Session Telemetry — $SESSION_END

| Metric | Value |
|--------|-------|
| Session ID | $SESSION_ID |
| File writes | $FILE_WRITES |
| Subagents spawned | $SUBAGENT_COUNT |
| Agent types | $AGENT_TYPES |
| Duration (min) | $DURATION_MIN |
| Stop reason | $REASON |
EOF
)

# Append audit warnings if any
if [[ -n "$AUDIT_WARNINGS" ]]; then
    TELEMETRY_BLOCK="${TELEMETRY_BLOCK}

## Bypass Audit Warnings
${AUDIT_WARNINGS}"
fi

echo "$TELEMETRY_BLOCK" >> "$SESSION_TELEMETRY_FILE"

# NOTE: S5 updates references/skill-state.md during Phase 8 by reading this file.
# Hooks MUST NOT modify tracked reference files.

# ── Self-Healing Hook Diagnostic — verify infrastructure ──
# Run diagnostic-router in test mode to ensure the self-healing layer is functional.
DIAGNOSTIC_ROUTER="$HOME/vsm/viable-swarm-model/hooks/diagnostic-router.sh"
if [[ -f "$DIAGNOSTIC_ROUTER" ]]; then
    bash "$DIAGNOSTIC_ROUTER" --test >/dev/null 2>&1 || {
        echo "WARNING: diagnostic-router.sh self-test failed. Self-healing infrastructure may be compromised." >&2
    }
fi

# Clean up per-session telemetry files (keep aggregated logs)
# We keep the jsonl files as they accumulate across sessions for rolling averages
# But mark session as processed
if [[ -f "$TELEMETRY_DIR/sessions.jsonl" ]]; then
    # Remove processed session start entry to keep file from growing infinitely
    grep -v "$SESSION_ID" "$TELEMETRY_DIR/sessions.jsonl" > "$TELEMETRY_DIR/sessions.jsonl.tmp" 2>/dev/null || true
    mv "$TELEMETRY_DIR/sessions.jsonl.tmp" "$TELEMETRY_DIR/sessions.jsonl" 2>/dev/null || true
fi

exit 0
