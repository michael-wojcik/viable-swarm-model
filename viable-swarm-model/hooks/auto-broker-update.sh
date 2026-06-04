#!/usr/bin/bash
# Auto-Broker-Update — Session-end knowledge broker hydration
# Replaces the broken knowledge-broker.sh hook with structured parsing
#
# Usage: auto-broker-update.sh <build-directory>
# Example: auto-broker-update.sh ~/vsm-fitness-builds/coach/FB30-20260604

set -euo pipefail

BUILD_DIR="${1:-.}"
KIMI_DIR="${BUILD_DIR}/.kimi"
BROKER_FILE="${HOME}/vsm/viable-swarm-model/references/knowledge-broker.md"
MUTATION_LOG="${HOME}/vsm/viable-swarm-model/references/mutation-log.md"

if [[ ! -d "$KIMI_DIR" ]]; then
    echo "ERROR: .kimi/ directory not found in $BUILD_DIR" >&2
    exit 1
fi

if [[ ! -f "$BROKER_FILE" ]]; then
    echo "ERROR: Knowledge broker file not found at $BROKER_FILE" >&2
    exit 1
fi

# Extract build ID from directory name or from plan.md
BUILD_ID=""
if [[ "$BUILD_DIR" =~ FB[0-9]+ ]]; then
    BUILD_ID="${BASH_REMATCH[0]}"
elif [[ -f "${BUILD_DIR}/plan.md" ]]; then
    BUILD_ID=$(grep -m1 -oE 'FB[0-9]+' "${BUILD_DIR}/plan.md" || echo "UNKNOWN")
else
    BUILD_ID="UNKNOWN"
fi

DATE=$(date +%Y-%m-%d)

# Extract score from meta-report if available
SCORE="N/A"
if [[ -f "${KIMI_DIR}/meta-report.md" ]]; then
    SCORE=$(grep -m1 -oE '[0-9]+\.[0-9]+/5\.0' "${KIMI_DIR}/meta-report.md" || echo "N/A")
fi

# Extract process audit score if available
PROCESS_SCORE="N/A"
if [[ -f "${KIMI_DIR}/process-audit.md" ]]; then
    PROCESS_SCORE=$(grep -m1 -oE '[0-9]+/100' "${KIMI_DIR}/process-audit.md" || echo "N/A")
fi

# Extract key learnings from lessons.md
LEARNINGS=""
if [[ -f "${KIMI_DIR}/lessons.md" ]]; then
    # Get first 3 non-empty, non-header lines as key learnings
    LEARNINGS=$(grep -v '^#' "${KIMI_DIR}/lessons.md" | grep -v '^$' | head -3 | sed 's/^/- /')
fi

# Extract new mutations from mutation log (last 7 days)
NEW_MUTATIONS=""
if [[ -f "$MUTATION_LOG" ]]; then
    NEW_MUTATIONS=$(grep -B1 "^## Mutation" "$MUTATION_LOG" | grep "$DATE" | head -5 | sed 's/^/- /')
    if [[ -z "$NEW_MUTATIONS" ]]; then
        NEW_MUTATIONS="- (No mutations applied today)"
    fi
else
    NEW_MUTATIONS="- (Mutation log not found)"
fi

# Extract domain from plan.md if available
DOMAIN="N/A"
if [[ -f "${BUILD_DIR}/plan.md" ]]; then
    DOMAIN=$(grep -m1 -i 'domain\|project\|build.*:' "${BUILD_DIR}/plan.md" | head -1 | cut -d: -f2- | sed 's/^ *//' | head -c 80 || echo "N/A")
fi

# Append entry to broker
cat >> "$BROKER_FILE" << EOF

---

## Entry: ${BUILD_ID} — ${DATE}

**Build**: ${BUILD_ID}
**Score**: ${SCORE}
**Process Audit**: ${PROCESS_SCORE}
**Domain**: ${DOMAIN}

### Key Learnings
${LEARNINGS}

### Mutations Applied
${NEW_MUTATIONS}

### Cross-Skill Findings
- (Auto-populated — review and expand manually if needed)
EOF

# Update "Last updated" timestamp
sed -i.bak "s/^> \*\*Last updated\*\*: .*/> **Last updated**: ${DATE}/" "$BROKER_FILE" && rm -f "${BROKER_FILE}.bak"

echo "OK: Knowledge broker updated for ${BUILD_ID} on ${DATE}"
echo "Broker file: ${BROKER_FILE}"
