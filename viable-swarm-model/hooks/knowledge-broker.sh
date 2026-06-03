#!/bin/bash
# VSM Knowledge Broker Hook
# Writes cross-skill digest to knowledge-broker.md on session end.
# Fixed 2026-06-02: regex patterns now match actual build directory paths.
#
# Event: SessionEnd

set -euo pipefail

PAYLOAD=$(cat)
SESSION_ID=$(echo "$PAYLOAD" | jq -r '.session_id // "unknown"')
CWD=$(echo "$PAYLOAD" | jq -r '.cwd // "/tmp"')
REASON=$(echo "$PAYLOAD" | jq -r '.reason // "unknown"')

BROKER_FILE="$HOME/vsm/viable-swarm-model/references/knowledge-broker.md"
TIMESTAMP=$(date -u +%Y-%m-%dT%H:%M:%SZ)

# Determine skill context from CWD — FIXED: match actual directory structures
SKILL_CONTEXT="unknown"
if [[ "$CWD" =~ vsm-fitness-builds/coach || "$CWD" =~ vsm-fitness-coach ]]; then
    SKILL_CONTEXT="coach"
elif [[ "$CWD" =~ vsm-fitness-builds/gym || "$CWD" =~ vsm-fitness-gym ]]; then
    SKILL_CONTEXT="gym"
elif [[ "$CWD" =~ viable-swarm-model || "$CWD" =~ vsm-fitness-builds ]]; then
    SKILL_CONTEXT="main"
fi

# If CWD doesn't have .kimi/, try to find the most recent build directory
BUILD_DIR="$CWD"
if [[ ! -d "$BUILD_DIR/.kimi" ]]; then
    if [[ "$SKILL_CONTEXT" == "main" ]]; then
        LATEST=$(find "$HOME/vsm-fitness-builds/coach" -maxdepth 1 -name 'FB*' -type d 2>/dev/null | sort | tail -1)
        if [[ -n "$LATEST" && -d "$LATEST/.kimi" ]]; then
            BUILD_DIR="$LATEST"
        fi
    fi
fi

# Build digest based on skill context
DIGEST=""

if [[ "$SKILL_CONTEXT" == "main" ]]; then
    META="$BUILD_DIR/.kimi/meta-report.md"
    AUDIT="$BUILD_DIR/.kimi/process-audit.md"
    GAPS=""
    if [[ -f "$META" ]]; then
        GAPS=$(grep -iE 'gap|missed|failure|bypass|BLOCKER' "$META" 2>/dev/null | head -5 | sed 's/^/  - /' || true)
    fi
    if [[ -f "$AUDIT" && -z "$GAPS" ]]; then
        GAPS=$(grep -iE 'violation|missed|non-compliant' "$AUDIT" 2>/dev/null | head -5 | sed 's/^/  - /' || true)
    fi
    if [[ -z "$GAPS" ]]; then
        GAPS="  - (no gaps extracted — build artifacts may be in $BUILD_DIR)"
    fi

    DIGEST=$(cat << EOF
- [$TIMESTAMP] Main Build ($SESSION_ID): Gaps — $GAPS
EOF
)

elif [[ "$SKILL_CONTEXT" == "coach" ]]; then
    FITNESS_LEDGER="$HOME/vsm/vsm-fitness-coach/references/fitness-projects.md"
    LAST_SCORE="unknown"
    if [[ -f "$FITNESS_LEDGER" ]]; then
        LAST_SCORE=$(grep -E 'FB[0-9]+.*score' "$FITNESS_LEDGER" 2>/dev/null | tail -1 | grep -oE '[0-9]\.[0-9]' | tail -1 || true)
    fi
    DIGEST=$(cat << EOF
- [$TIMESTAMP] Coach Eval ($SESSION_ID): Last score $LAST_SCORE
EOF
)

elif [[ "$SKILL_CONTEXT" == "gym" ]]; then
    GYM_EXPERIMENTS="$HOME/vsm/vsm-fitness-gym/references/experiments.md"
    RECENT_RESULTS=""
    if [[ -f "$GYM_EXPERIMENTS" ]]; then
        RECENT_RESULTS=$(tail -30 "$GYM_EXPERIMENTS" 2>/dev/null | grep -iE 'confirmed|rejected|inconclusive' | tail -3 | tr '\n' '; ' || true)
    fi
    if [[ -z "$RECENT_RESULTS" ]]; then
        RECENT_RESULTS="(no recent results)"
    fi
    DIGEST=$(cat << EOF
- [$TIMESTAMP] Gym Results ($SESSION_ID): $RECENT_RESULTS
EOF
)
fi

# Append to Session Append Log section if it exists; otherwise append to file
if [[ -n "$DIGEST" ]]; then
    if grep -q "## Session Append Log" "$BROKER_FILE" 2>/dev/null; then
        # Append after the marker line
        sed -i '' "/## Session Append Log/a\\
$DIGEST" "$BROKER_FILE" 2>/dev/null || echo "$DIGEST" >> "$BROKER_FILE"
    else
        echo "" >> "$BROKER_FILE"
        echo "## Session Append Log" >> "$BROKER_FILE"
        echo "" >> "$BROKER_FILE"
        echo "$DIGEST" >> "$BROKER_FILE"
    fi
fi

exit 0
