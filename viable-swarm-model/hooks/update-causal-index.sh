#!/usr/bin/env bash
# Update-Causal-Index — Auto-link hypotheses, experiments, mutations, and builds
#
# Usage: update-causal-index.sh [--dry-run] <build-directory>
# This script reads mutations-applied.md from a build directory and appends a
# structured causal trace entry to causal-index.md.
# It validates that Experiment IDs and Hypothesis IDs exist in their respective
# files before linking them.

set -euo pipefail

DRY_RUN=false
if [[ "${1:-}" == "--dry-run" ]]; then
    DRY_RUN=true
    shift
fi

BUILD_DIR="${1:-.}"
REFS_DIR="${HOME}/vsm/viable-swarm-model/references"
CAUSAL_INDEX="${REFS_DIR}/causal-index.md"
HYPOTHESES="${REFS_DIR}/hypotheses.md"
EXPERIMENTS="${REFS_DIR}/experiments.md"
MUTATION_LOG="${REFS_DIR}/mutation-log.md"
MUTATION_STATE="${REFS_DIR}/mutation-state.md"
MUTATIONS_APPLIED="${BUILD_DIR}/.kimi/mutations-applied.md"

# Extract build ID
BUILD_ID=""
if [[ "$BUILD_DIR" =~ FB[0-9]+ ]]; then
    BUILD_ID="${BASH_REMATCH[0]}"
else
    BUILD_ID="MANUAL"
fi

DATE=$(date +%Y-%m-%d)

# --- Helper: validate that an ID exists in a file ---
validate_id() {
    local id="$1"
    local file="$2"
    local type_name="$3"
    if [[ -z "$id" || "$id" == "N/A" ]]; then
        return 0
    fi
    if [[ ! -f "$file" ]]; then
        echo "WARNING: $type_name file not found: $file" >&2
        return 1
    fi
    if ! grep -q "$id" "$file" 2>/dev/null; then
        echo "WARNING: $type_name ID '$id' not found in $(basename "$file")" >&2
        return 1
    fi
    return 0
}

# --- Read mutations from build directory ---
if [[ ! -f "$MUTATIONS_APPLIED" ]]; then
    echo "INFO: mutations-applied.md not found in ${BUILD_DIR}/.kimi/. Causal index unchanged."
    exit 0
fi

# Parse mutations-applied.md for structured entries
# Expected format: | ID | Name | Status | Hypothesis | Experiment |
MUTATION_ENTRIES=()
while IFS='|' read -r _ id name status hypothesis experiment _; do
    id=$(echo "$id" | sed 's/^ *//;s/ *$//')
    name=$(echo "$name" | sed 's/^ *//;s/ *$//')
    status=$(echo "$status" | sed 's/^ *//;s/ *$//')
    hypothesis=$(echo "$hypothesis" | sed 's/^ *//;s/ *$//')
    experiment=$(echo "$experiment" | sed 's/^ *//;s/ *$//')
    # Skip header and separator rows
    [[ "$id" == "ID" || "$id" == "-"* || -z "$id" ]] && continue
    MUTATION_ENTRIES+=("$id|$name|$status|$hypothesis|$experiment")
done < <(grep '^|' "$MUTATIONS_APPLIED" 2>/dev/null || true)

if [[ ${#MUTATION_ENTRIES[@]} -eq 0 ]]; then
    echo "INFO: No structured mutation entries found in mutations-applied.md."
    exit 0
fi

# --- Ensure causal-index.md exists with header ---
if [[ ! -f "$CAUSAL_INDEX" ]]; then
    HEADER=$(cat << 'EOF'
# Causal Index — Hypothesis → Experiment → Mutation → Build Chains

> **Purpose**: Unified causal tracing across the VSM ecosystem.
> **Updated by**: `update-causal-index.sh` at session end
> **Schema version**: 1.0

---

EOF
)
    if [[ "$DRY_RUN" == true ]]; then
        echo "[DRY-RUN] Would create causal-index.md with header"
    else
        echo "$HEADER" > "$CAUSAL_INDEX"
        echo "CREATED: causal-index.md with header"
    fi
fi

# --- Process each mutation entry ---
for entry in "${MUTATION_ENTRIES[@]}"; do
    IFS='|' read -r MUT_ID MUT_NAME MUT_STATUS HYPOTHESIS_LINK EXPERIMENT_LINK <<< "$entry"
    
    # Validate linked IDs before creating chain
    HYP_VALID=true
    EXP_VALID=true
    if [[ -n "$HYPOTHESIS_LINK" && "$HYPOTHESIS_LINK" != "N/A" ]]; then
        if ! validate_id "$HYPOTHESIS_LINK" "$HYPOTHESES" "Hypothesis"; then
            HYP_VALID=false
        fi
    fi
    if [[ -n "$EXPERIMENT_LINK" && "$EXPERIMENT_LINK" != "N/A" ]]; then
        if ! validate_id "$EXPERIMENT_LINK" "$EXPERIMENTS" "Experiment"; then
            EXP_VALID=true
        fi
    fi
    
    # Try to find target failure mode from mutation log or mutation state
    TARGET_FAILURE="Unknown"
    if [[ -f "$MUTATION_LOG" ]]; then
        TARGET_FAILURE=$(grep -A20 "^## Mutation ${MUT_ID}" "$MUTATION_LOG" 2>/dev/null | grep "Target failure mode" | head -1 | sed 's/.*Target failure mode.*: *//' || echo "Unknown")
    fi
    if [[ "$TARGET_FAILURE" == "Unknown" && -f "$MUTATION_STATE" ]]; then
        TARGET_FAILURE=$(grep "^| ${MUT_ID} |" "$MUTATION_STATE" 2>/dev/null | awk -F'|' '{print $5}' | sed 's/^ *//;s/ *$//' || echo "Unknown")
    fi
    
    # Check if this chain already exists
    if [[ -f "$CAUSAL_INDEX" ]] && grep -q "## CC-.*${MUT_ID}" "$CAUSAL_INDEX" 2>/dev/null; then
        if [[ "$DRY_RUN" == true ]]; then
            echo "[DRY-RUN] Would update causal chain for ${MUT_ID} with build ${BUILD_ID}"
        else
            # Update existing chain with new build ID (avoid duplicate build IDs)
            if ! grep -A10 "## CC-.*${MUT_ID}" "$CAUSAL_INDEX" | grep -q "${BUILD_ID}"; then
                sed -i.bak "/## CC-.*${MUT_ID}/,/^---$/s/Builds Tested:.*/& ${BUILD_ID}/" "$CAUSAL_INDEX" && rm -f "${CAUSAL_INDEX}.bak"
            fi
            echo "UPDATED: Causal chain for ${MUT_ID} with build ${BUILD_ID}"
        fi
    else
        if [[ -f "$CAUSAL_INDEX" ]]; then
            CC_NUM=$(grep -c "^## CC-" "$CAUSAL_INDEX" 2>/dev/null || true)
        else
            CC_NUM=0
        fi
        CC_NUM=${CC_NUM:-0}
        CC_NUM=$((CC_NUM + 1))
        
        CHAIN_ENTRY=$(cat << EOF

## CC-${CC_NUM}
**Mutation**: ${MUT_ID}
**Name**: ${MUT_NAME}
**Status**: ${MUT_STATUS}
**Hypothesis**: ${HYPOTHESIS_LINK:-N/A} $(if [[ "$HYP_VALID" == false ]]; then echo "(UNVALIDATED)"; fi)
**Experiment**: ${EXPERIMENT_LINK:-N/A} $(if [[ "$EXP_VALID" == false ]]; then echo "(UNVALIDATED)"; fi)
**Target Failure**: ${TARGET_FAILURE}
**Builds Tested**: ${BUILD_ID}
**Result**: [pending — update after measurement]
**Score Trend**: [pending]

---
EOF
)
        if [[ "$DRY_RUN" == true ]]; then
            echo "[DRY-RUN] Would create new causal chain CC-${CC_NUM} for ${MUT_ID}"
        else
            echo "$CHAIN_ENTRY" >> "$CAUSAL_INDEX"
            echo "CREATED: New causal chain CC-${CC_NUM} for ${MUT_ID}"
        fi
    fi
done

if [[ "$DRY_RUN" == true ]]; then
    echo "[DRY-RUN] Causal index update complete for build ${BUILD_ID}"
else
    echo "OK: Causal index updated for build ${BUILD_ID}"
fi
