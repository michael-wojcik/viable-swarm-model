#!/usr/bin/bash
# Update-Causal-Index — Auto-link hypotheses, experiments, mutations, and builds
#
# Usage: update-causal-index.sh <build-directory>
# This script scans recent changes to hypotheses, experiments, and mutation logs
# and appends/updates causal chain entries in causal-index.md

set -euo pipefail

BUILD_DIR="${1:-.}"
REFS_DIR="${HOME}/vsm/viable-swarm-model/references"
CAUSAL_INDEX="${REFS_DIR}/causal-index.md"
HYPOTHESES="${REFS_DIR}/hypotheses.md"
EXPERIMENTS="${REFS_DIR}/experiments.md"
MUTATION_LOG="${REFS_DIR}/mutation-log.md"
MUTATION_STATE="${REFS_DIR}/mutation-state.md"

# Extract build ID
BUILD_ID=""
if [[ "$BUILD_DIR" =~ FB[0-9]+ ]]; then
    BUILD_ID="${BASH_REMATCH[0]}"
else
    BUILD_ID="MANUAL"
fi

DATE=$(date +%Y-%m-%d)

# Find recently updated hypotheses (status changed to confirmed/rejected in last 7 days)
# We look for hypotheses that have a "Tested by" or "Result" field updated
RECENT_HYPOTHESES=$(grep -B5 -A5 "Tested by.*FB" "$HYPOTHESES" 2>/dev/null | grep "^## H" | sed 's/## //' | head -10 || true)

# Find recently added mutations (last 7 days in mutation log)
RECENT_MUTATIONS=$(grep -B2 "^## Mutation.*${DATE}" "$MUTATION_LOG" 2>/dev/null | grep "^## Mutation" | sed 's/## Mutation //' | head -10 || true)

# Find recently completed experiments
RECENT_EXPERIMENTS=$(grep -B2 "^## E[0-9]" "$EXPERIMENTS" 2>/dev/null | grep "^## E" | sed 's/## //' | head -10 || true)

# Only update if there's something new
if [[ -z "$RECENT_HYPOTHESES" && -z "$RECENT_MUTATIONS" && -z "$RECENT_EXPERIMENTS" ]]; then
    echo "INFO: No recent changes to hypotheses, experiments, or mutations. Causal index unchanged."
    exit 0
fi

# Ensure causal-index.md exists with header
if [[ ! -f "$CAUSAL_INDEX" ]]; then
    cat > "$CAUSAL_INDEX" << 'EOF'
# Causal Index — Hypothesis → Experiment → Mutation → Build Chains

> **Purpose**: Unified causal tracing across the VSM ecosystem.
> **Updated by**: `update-causal-index.sh` at session end
> **Schema version**: 1.0

---

EOF
fi

# Generate new causal chain entries for each recent mutation that links to a hypothesis
while IFS= read -r mut_line; do
    [[ -z "$mut_line" ]] && continue
    MUT_ID=$(echo "$mut_line" | awk '{print $1}')
    
    # Try to find linked hypothesis in mutation log
    HYPOTHESIS_LINK=$(grep -A20 "^## Mutation ${MUT_ID}" "$MUTATION_LOG" 2>/dev/null | grep -oE 'H[0-9]+' | head -1 || true)
    
    # Try to find linked experiment
    EXPERIMENT_LINK=$(grep -A20 "^## Mutation ${MUT_ID}" "$MUTATION_LOG" 2>/dev/null | grep -oE 'E[0-9]+' | head -1 || true)
    
    # Try to find target failure mode
    TARGET_FAILURE=$(grep -A20 "^## Mutation ${MUT_ID}" "$MUTATION_LOG" 2>/dev/null | grep "Target failure mode" | head -1 | sed 's/.*Target failure mode.*: *//' || echo "Unknown")
    
    # Check if this chain already exists
    if grep -q "## CC-.*${MUT_ID}" "$CAUSAL_INDEX" 2>/dev/null; then
        # Update existing chain with new build ID
        sed -i.bak "/## CC-.*${MUT_ID}/,/^---$/s/Builds Tested:.*/& ${BUILD_ID}/" "$CAUSAL_INDEX" && rm -f "${CAUSAL_INDEX}.bak"
        echo "UPDATED: Causal chain for ${MUT_ID} with build ${BUILD_ID}"
    else
        # Create new chain
        CC_NUM=$(grep -c "^## CC-" "$CAUSAL_INDEX" 2>/dev/null || true)
        CC_NUM=${CC_NUM:-0}
        CC_NUM=$((CC_NUM + 1))
        
        cat >> "$CAUSAL_INDEX" << EOF

## CC-${CC_NUM}
**Hypothesis**: ${HYPOTHESIS_LINK:-N/A}
**Experiment**: ${EXPERIMENT_LINK:-N/A}
**Mutation**: ${MUT_ID}
**Target Failure**: ${TARGET_FAILURE}
**Builds Tested**: ${BUILD_ID}
**Result**: [pending — update after measurement]
**Score Trend**: [pending]

EOF
        echo "CREATED: New causal chain CC-${CC_NUM} for ${MUT_ID}"
    fi
done <<< "$RECENT_MUTATIONS"

echo "OK: Causal index updated for build ${BUILD_ID}"
