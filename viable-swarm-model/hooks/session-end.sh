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

# Telemetry is optional; process what exists, default to zero/unknown
FILE_WRITES=0
if [[ -f "$TELEMETRY_DIR/file-writes.jsonl" ]]; then
    FILE_WRITES=$(grep -c "$SESSION_ID" "$TELEMETRY_DIR/file-writes.jsonl" 2>/dev/null || true)
    FILE_WRITES=${FILE_WRITES:-0}
fi

SUBAGENT_COUNT=0
if [[ -f "$TELEMETRY_DIR/subagents.jsonl" ]]; then
    SUBAGENT_COUNT=$(grep -c "$SESSION_ID" "$TELEMETRY_DIR/subagents.jsonl" 2>/dev/null || true)
    SUBAGENT_COUNT=${SUBAGENT_COUNT:-0}
fi

AGENT_TYPES=""
if [[ -f "$TELEMETRY_DIR/subagents.jsonl" ]]; then
    AGENT_TYPES=$(grep "$SESSION_ID" "$TELEMETRY_DIR/subagents.jsonl" 2>/dev/null | jq -r '.agent_name' | sort -u | tr '\n' ',' | sed 's/,$//')
fi

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

# Check 7: knowledge-broker.md consumption check
if [[ -f "$CWD/plan.md" ]]; then
    if ! grep -qi "knowledge-broker\|Active Constraints\|broker trap" "$CWD/plan.md" 2>/dev/null; then
        AUDIT_WARNINGS="${AUDIT_WARNINGS}- plan.md has no knowledge broker references. Phase 0 broker read likely skipped.\n"
    fi
fi

# Check 8: Mutation portfolio review completion (NEW — closes S4→S5 learning loop)
# If build reached Phase 8 (meta-report.md exists) but portfolio review was never done,
# flag the omission and auto-generate pre-computed health data as fallback.
if [[ -f "$CWD/.kimi/meta-report.md" && ! -f "$CWD/.kimi/mutation-portfolio-review.md" ]]; then
    AUDIT_WARNINGS="${AUDIT_WARNINGS}- Phase 8b complete but mutation-portfolio-review.md missing. vsm_learning_curator not spawned.\n"
    # Auto-generate pre-computed portfolio health so S5 has data even without curator
    PORTFOLIO_SCRIPT="$HOME/vsm/viable-swarm-model/scripts/mutation-portfolio-health.py"
    if [[ -f "$PORTFOLIO_SCRIPT" ]]; then
        python3 "$PORTFOLIO_SCRIPT" --build-dir "$CWD" >/dev/null 2>&1 || {
            echo "WARNING: mutation-portfolio-health.py failed. Portfolio metrics not pre-computed." >&2
        }
    fi
fi

# Check 9: Variety assessment completion (NEW — closes S4* environmental scanning gap)
# If build reached Phase 8 but variety assessment was never done, flag and auto-generate.
if [[ -f "$CWD/.kimi/meta-report.md" && ! -f "$CWD/.kimi/variety-assessment.md" ]]; then
    AUDIT_WARNINGS="${AUDIT_WARNINGS}- Phase 8b complete but variety-assessment.md missing. vsm_variety_engineer not spawned.\n"
    VITALS_SCRIPT="$HOME/vsm/viable-swarm-model/scripts/organism-vitals.py"
    if [[ -f "$VITALS_SCRIPT" ]]; then
        python3 "$VITALS_SCRIPT" --build-dir "$CWD" >/dev/null 2>&1 || {
            echo "WARNING: organism-vitals.py failed. Variety metrics not pre-computed." >&2
        }
    fi
fi

# Check 10: Process audit completion (NEW — closes S3* audit gap)
# If build reached Phase 8 but process audit was never done, flag and auto-generate.
if [[ -f "$CWD/.kimi/meta-report.md" && ! -f "$CWD/.kimi/process-audit.md" ]]; then
    AUDIT_WARNINGS="${AUDIT_WARNINGS}- Phase 8b complete but process-audit.md missing. vsm_process_auditor not spawned or timed out.\n"
    COMPLIANCE_SCRIPT="$HOME/vsm/viable-swarm-model/scripts/process-compliance-precompute.py"
    if [[ -f "$COMPLIANCE_SCRIPT" ]]; then
        python3 "$COMPLIANCE_SCRIPT" "$CWD" >/dev/null 2>&1 || {
            echo "WARNING: process-compliance-precompute.py failed. Compliance metrics not pre-computed." >&2
        }
    fi
fi

# Check 11: Security gate completion (NEW — closes S3→S1 security bypass gap)
# If build reached Phase 8, contains security-relevant code, but security-report.md
# is missing, the security gate was bypassed. This is a CRITICAL process violation.
# FB30 demonstrated this bypass: manual audit was used instead of vsm_security agent.
if [[ -f "$CWD/.kimi/meta-report.md" && ! -f "$CWD/.kimi/security-report.md" ]]; then
    # Detect security-relevant surface area in source files
    HAS_SECURITY_SURFACE="no"
    if [[ -d "$CWD" ]]; then
        # Grep for auth, GraphQL, WebSocket, CORS, rate limiting patterns
        if grep -riE \
            '\bjwt\b|\bJWT\b|\bbcrypt\b|\bpasslib\b|\bOAuth\b|get_current_user|require_role|auth_depend|\\bpassword\\b|\\bhash\\b' \
            "$CWD" --include='*.py' --include='*.ts' --include='*.tsx' --include='*.js' >/dev/null 2>&1; then
            HAS_SECURITY_SURFACE="yes"
        elif grep -riE \
            '\bstrawberry\b|\bGraphQL\b|\bgraphql\b|GraphQLRouter' \
            "$CWD" --include='*.py' --include='*.ts' --include='*.tsx' --include='*.js' >/dev/null 2>&1; then
            HAS_SECURITY_SURFACE="yes"
        elif grep -riE \
            '\bsocketio\b|\bsio\\.\b|\bwebsocket\b|\bWebSocket\b' \
            "$CWD" --include='*.py' --include='*.ts' --include='*.tsx' --include='*.js' >/dev/null 2>&1; then
            HAS_SECURITY_SURFACE="yes"
        elif grep -riE \
            'CORSMiddleware|\bRateLimit\b|\bSlowAPI\b|rate_limit|allow_origins' \
            "$CWD" --include='*.py' --include='*.ts' --include='*.tsx' --include='*.js' >/dev/null 2>&1; then
            HAS_SECURITY_SURFACE="yes"
        fi
    fi
    if [[ "$HAS_SECURITY_SURFACE" == "yes" ]]; then
        AUDIT_WARNINGS="${AUDIT_WARNINGS}- CRITICAL: Phase 8b complete but security-report.md missing. vsm_security agent bypassed despite security-relevant code present.\n"
    fi
fi

# Check 12: Product brief completion (NEW — closes S4→S5 intelligence gap)
# Tier 2+ builds require a product brief to prevent architect scope creep.
# H[N+1] confirmed: product briefs reduce scope creep by 80%+.
# If plan.md indicates Tier 2+ but product-brief.md is missing, flag the omission.
if [[ -f "$CWD/plan.md" && ! -f "$CWD/product-brief.md" && ! -f "$CWD/.kimi/product-brief.md" ]]; then
    IS_TIER2PLUS="no"
    if grep -qiE '\*\*Tier\*\*.*[23]|Tier:[[:space:]]*[23]' "$CWD/plan.md" 2>/dev/null; then
        IS_TIER2PLUS="yes"
    fi
    if [[ "$IS_TIER2PLUS" == "yes" ]]; then
        AUDIT_WARNINGS="${AUDIT_WARNINGS}- Tier 2+ build missing product-brief.md. vsm_product agent not spawned. Architect scope creep risk elevated.\n"
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

# ── Build Health Dashboard ──
# Generate longitudinal health metrics for S4 intelligence layer.
# This populates build-health-history.md so variety engineer and S5
# have accurate trend data for proactive health assessment.
DASHBOARD_SCRIPT="$HOME/vsm/viable-swarm-model/scripts/build-health-dashboard.py"
if [[ -f "$CWD/plan.md" && -f "$DASHBOARD_SCRIPT" ]]; then
    python3 "$DASHBOARD_SCRIPT" "$CWD" >/dev/null 2>&1 || {
        echo "WARNING: build-health-dashboard.py failed. Longitudinal health metrics not updated." >&2
    }
fi

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
