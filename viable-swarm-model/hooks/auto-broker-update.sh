#!/usr/bin/env bash
# Auto-Broker-Update — Session-end knowledge broker hydration
# Replaces the broken knowledge-broker.sh hook with structured parsing
# Handles both raw session log append AND curated table updates.
#
# Usage: auto-broker-update.sh <build-directory>
# Example: auto-broker-update.sh ~/vsm-fitness-builds/coach/FB30-20260604

set -euo pipefail

BUILD_DIR="${1:-.}"
KIMI_DIR="${BUILD_DIR}/.kimi"
BROKER_FILE="${HOME}/vsm/viable-swarm-model/references/knowledge-broker.md"
MUTATION_LOG="${HOME}/vsm/viable-swarm-model/references/mutation-log.md"
ERROR_FILE="${KIMI_DIR}/broker-update-errors.md"

# --- Error fallback ---
log_error() {
    local msg="$1"
    echo "ERROR: $msg" >&2
    mkdir -p "$KIMI_DIR" 2>/dev/null || true
    echo "$(date +%Y-%m-%dT%H:%M:%S) — $msg" >> "$ERROR_FILE" 2>/dev/null || true
}

# --- Validate inputs ---
if [[ ! -d "$KIMI_DIR" ]]; then
    log_error ".kimi/ directory not found in $BUILD_DIR"
    exit 1
fi

if [[ ! -f "${BUILD_DIR}/plan.md" ]]; then
    log_error "Build directory $BUILD_DIR has no plan.md — not a valid build directory. Refusing to append UNKNOWN entry."
    exit 1
fi

if [[ ! -f "$BROKER_FILE" ]]; then
    log_error "Knowledge broker file not found at $BROKER_FILE"
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
    LEARNINGS=$(grep -v '^#' "${KIMI_DIR}/lessons.md" | grep -v '^$' | head -3 | sed 's/^/- /' || true)
fi

# Extract new mutations from mutation log (last 7 days)
NEW_MUTATIONS=""
if [[ -f "$MUTATION_LOG" ]]; then
    NEW_MUTATIONS=$(grep -B1 "^## Mutation" "$MUTATION_LOG" | grep "$DATE" | head -5 | sed 's/^/- /' || true)
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

# --- Mode selection: raw append vs curated table update ---
# If the broker contains a "## Curated Build Index" section, append to the table.
# Otherwise, append a raw session log entry.

if grep -q "## Curated Build Index" "$BROKER_FILE" 2>/dev/null; then
    # Curated table mode — append a single row to the build index table
    # Find the last table row and append after it
    TABLE_ROW="| ${BUILD_ID} | ${DATE} | ${SCORE} | ${PROCESS_SCORE} | ${DOMAIN} | ${NEW_MUTATIONS//$'\n'/ } |"
    
    # Insert before the first blank line after the table, or at end of section
    if ! sed -i.bak "/## Curated Build Index/,/^$/!b;/^$/i\\
${TABLE_ROW}" "$BROKER_FILE" 2>/dev/null; then
        # Fallback: append raw entry if table manipulation fails
        log_error "Failed to append to curated table; falling back to raw append mode"
        cat >> "$BROKER_FILE" << EOF

---

## Entry: ${BUILD_ID} — ${DATE} (fallback)

**Build**: ${BUILD_ID}
**Score**: ${SCORE}
**Process Audit**: ${PROCESS_SCORE}
**Domain**: ${DOMAIN}

### Key Learnings
${LEARNINGS:-"- (None extracted)"}

### Mutations Applied
${NEW_MUTATIONS}

### Cross-Skill Findings
- (Auto-populated — review and expand manually if needed)
EOF
    else
        rm -f "${BROKER_FILE}.bak" 2>/dev/null || true
        echo "OK: Appended curated table row for ${BUILD_ID}"
    fi
else
    # Raw session log append mode
    cat >> "$BROKER_FILE" << EOF

---

## Entry: ${BUILD_ID} — ${DATE}

**Build**: ${BUILD_ID}
**Score**: ${SCORE}
**Process Audit**: ${PROCESS_SCORE}
**Domain**: ${DOMAIN}

### Key Learnings
${LEARNINGS:-"- (None extracted)"}

### Mutations Applied
${NEW_MUTATIONS}

### Cross-Skill Findings
- (Auto-populated — review and expand manually if needed)
EOF
    echo "OK: Appended raw session entry for ${BUILD_ID}"
fi

# Update "Last updated" timestamp
if ! sed -i.bak "s/^> \*\*Last updated\*\*: .*/> **Last updated**: ${DATE}/" "$BROKER_FILE" 2>/dev/null; then
    log_error "Failed to update 'Last updated' timestamp in broker"
else
    rm -f "${BROKER_FILE}.bak" 2>/dev/null || true
fi

echo "Broker file: ${BROKER_FILE}"
