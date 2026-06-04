#!/bin/bash
# VSM Stop Verifier Hook
# Blocks session end if Phase 8c-ii is incomplete.
# Verifies mutations-applied.md exists and measured effects are not pending.
# Also auto-parses trainer backfill output and writes measured effects to mutation-log.md.
#
# Event: Stop
# Can block once (anti-loop protection built into kimi-cli).

set -euo pipefail

PAYLOAD=$(cat)
CWD=$(echo "$PAYLOAD" | jq -r '.cwd // "/tmp"')
STOP_HOOK_ACTIVE=$(echo "$PAYLOAD" | jq -r '.stop_hook_active // false')

# Anti-loop: if stop hook already fired once, allow exit
if [[ "$STOP_HOOK_ACTIVE" == "true" ]]; then
    exit 0
fi

KIMI_DIR="$CWD/.kimi"
MUTATIONS_FILE="$KIMI_DIR/mutations-applied.md"
MUTATION_LOG="$HOME/vsm/viable-swarm-model/references/mutation-log.md"

# --- Auto-parse trainer backfill and write to ephemeral file ---
# Hooks MUST NOT modify tracked reference files. Extract backfill data and
# write it to .kimi/mutation-backfill.md for S5 to apply during Phase 8c-ii.
BACKFILL_FILE="$KIMI_DIR/mutation-backfill.md"

if [[ -d "$KIMI_DIR" && -f "$MUTATION_LOG" ]]; then
    for source_file in "$KIMI_DIR"/*backfill* "$KIMI_DIR"/trainer-output* "$KIMI_DIR"/fitness-report*; do
        [[ -f "$source_file" ]] || continue

        # Extract mutation effectiveness table lines
        while IFS= read -r line; do
            if echo "$line" | grep -qE '^\s*\|\s*(FB[0-9]+-[0-9]+|M[0-9]+|Mutation [0-9]+)'; then
                MUTATION_ID=$(echo "$line" | awk -F'|' '{print $2}' | tr -d ' ')
                EFFECT=$(echo "$line" | awk -F'|' '{print $3}' | sed 's/^ *//;s/ *$//')
                NOTES=$(echo "$line" | awk -F'|' '{print $4}' | sed 's/^ *//;s/ *$//')

                if [[ -n "$MUTATION_ID" && -n "$EFFECT" && "$EFFECT" != "Effectiveness" ]]; then
                    echo "- $MUTATION_ID | $EFFECT | $NOTES" >> "$BACKFILL_FILE"
                    echo "stop-verifier.sh: Extracted backfill for $MUTATION_ID → $EFFECT" >&2
                fi
            fi
        done < "$source_file"
    done
fi

# NOTE: S5 applies backfill to references/mutation-log.md during Phase 8c-ii.
# Hooks MUST NOT modify tracked reference files.

# Only verify if this looks like a VSM build directory
if [[ ! -d "$KIMI_DIR" ]]; then
    exit 0
fi

# Check 1: mutations-applied.md must exist AND have content for THIS build
# A retroactively-created empty file does not satisfy Phase 8c-ii.
MUTATIONS_VALID=false
if [[ -f "$MUTATIONS_FILE" ]]; then
    # Must contain a Build ID entry and at least one mutation block
    if grep -qE '^## Build |^\*\*Build ID\*\*|^\*\*Mutation\*\*|Applied|Effectiveness' "$MUTATIONS_FILE" 2>/dev/null; then
        MUTATIONS_VALID=true
    fi
fi

if [[ "$MUTATIONS_VALID" != "true" ]]; then
    # Only enforce if this looks like a completed build (has meta, lessons, or security report)
    if [[ -f "$KIMI_DIR/meta-report.md" || -f "$KIMI_DIR/lessons.md" || -f "$KIMI_DIR/security-report.md" || -f "$KIMI_DIR/process-audit.md" ]]; then
        echo "STOP BLOCKED by stop-verifier.sh: Phase 8c-ii incomplete. .kimi/mutations-applied.md is missing or empty. Every build MUST log applied mutations with measured effects before completion." >&2
        echo '{"hookSpecificOutput":{"permissionDecision":"deny","permissionDecisionReason":"Phase 8c-ii incomplete: mutations-applied.md missing or empty. Write it with build ID and measured effects before stopping."}}'
        exit 0
    fi
fi

# Check 1b: Retroactive creation detection
# If mutations-applied.md was created AFTER meta-report.md or process-audit.md,
# it was written retroactively and the checkpoint was still bypassed. Block and warn.
if [[ "$MUTATIONS_VALID" == "true" ]]; then
    MUT_MTIME=$(stat -f%m "$MUTATIONS_FILE" 2>/dev/null || stat -c%Y "$MUTATIONS_FILE" 2>/dev/null || echo 0)
    LATEST_ARTIFACT=0
    for artifact in "$KIMI_DIR/meta-report.md" "$KIMI_DIR/process-audit.md" "$KIMI_DIR/lessons.md"; do
        if [[ -f "$artifact" ]]; then
            ART_MTIME=$(stat -f%m "$artifact" 2>/dev/null || stat -c%Y "$artifact" 2>/dev/null || echo 0)
            if [[ "$ART_MTIME" -gt "$LATEST_ARTIFACT" ]]; then
                LATEST_ARTIFACT=$ART_MTIME
            fi
        fi
    done
    if [[ "$LATEST_ARTIFACT" -gt 0 && "$MUT_MTIME" -gt "$LATEST_ARTIFACT" ]]; then
        echo "STOP BLOCKED by stop-verifier.sh: mutations-applied.md was created AFTER meta-report.md/process-audit.md. Phase 8c-ii must be completed BEFORE Phase 8b, not retroactively. Reorder the workflow." >&2
        echo '{"hookSpecificOutput":{"permissionDecision":"deny","permissionDecisionReason":"Retroactive mutations-applied.md detected. Write it BEFORE meta-report and process-audit."}}'
        exit 0
    fi
fi

# Check 2: No PENDING measured effects in mutation-log.md
if [[ -f "$MUTATION_LOG" ]]; then
    # Count "Measured effect: [PENDING]" or "Measured effect: [pending]" entries
    # Also catch empty measured effect fields from recent sessions
    # Match: [PENDING], **PENDING**, [pending], **Pending**, plain PENDING/Pending
    # Count "PENDING" measured effects — but exclude "AWAITING_BUILD" which is
    # the expected status for mutations applied in the current session that will
    # be measured in the NEXT build.
    PENDING_COUNT=$(grep -ciE '\*\*Measured effect\*\*:\s*(\*\*|\[)?PENDING(\*\*|\])?|\*\*Measured effect\*\*:\s*(\*\*|\[)?pending(\*\*|\])?|Measured effect:\s*(\*\*|\[)?PENDING(\*\*|\])?|Measured effect:\s*(\*\*|\[)?pending(\*\*|\])?' "$MUTATION_LOG" 2>/dev/null || true)
    PENDING_COUNT=${PENDING_COUNT:-0}

    AWAITING_COUNT=$(grep -ciE 'AWAITING_BUILD|awaiting.*build' "$MUTATION_LOG" 2>/dev/null || true)
    AWAITING_COUNT=${AWAITING_COUNT:-0}

    # Effective pending = PENDING entries minus AWAITING_BUILD entries
    EFFECTIVE_PENDING=$((PENDING_COUNT - AWAITING_COUNT))
    if [[ "$EFFECTIVE_PENDING" -lt 0 ]]; then
        EFFECTIVE_PENDING=0
    fi

    if [[ "$EFFECTIVE_PENDING" -gt 0 ]]; then
        echo "STOP BLOCKED by stop-verifier.sh: $EFFECTIVE_PENDING mutation(s) have pending measured effects (excluding $AWAITING_COUNT awaiting next build). Complete the mutation effectiveness audit before stopping." >&2
        echo '{"hookSpecificOutput":{"permissionDecision":"deny","permissionDecisionReason":"Measured effects pending. Complete mutation effectiveness audit before stopping."}}'
        exit 0
    fi
fi

# Check 3: Process auditor MUST exist and be non-retroactive (FB29-sourced PM1)
# Detect if process-audit.md was produced during the build or retroactively
if [[ -f "$KIMI_DIR/process-audit.md" ]]; then
    PA_MTIME=$(stat -f%m "$KIMI_DIR/process-audit.md" 2>/dev/null || stat -c%Y "$KIMI_DIR/process-audit.md" 2>/dev/null || echo 0)
    # If process-audit.md is newer than lessons.md or meta-report.md, it's retroactive
    for artifact in "$KIMI_DIR/lessons.md" "$KIMI_DIR/meta-report.md"; do
        if [[ -f "$artifact" ]]; then
            ART_MTIME=$(stat -f%m "$artifact" 2>/dev/null || stat -c%Y "$artifact" 2>/dev/null || echo 0)
            if [[ "$ART_MTIME" -gt 0 && "$PA_MTIME" -gt "$ART_MTIME" ]]; then
                echo "STOP BLOCKED by stop-verifier.sh: process-audit.md was created AFTER other Phase 8 artifacts. Process auditor must be spawned DURING the build, not retroactively." >&2
                echo '{"hookSpecificOutput":{"permissionDecision":"deny","permissionDecisionReason":"Retroactive process-audit.md detected. Spawn vsm_process_auditor during Phase 8b, not after."}}'
                exit 0
            fi
        fi
    done
else
    # process-audit.md is missing entirely — block if this looks like a completed build
    if [[ -f "$KIMI_DIR/meta-report.md" || -f "$KIMI_DIR/lessons.md" ]]; then
        echo "STOP BLOCKED by stop-verifier.sh: process-audit.md is missing. Spawn vsm_process_auditor during Phase 8b before completing the build." >&2
        echo '{"hookSpecificOutput":{"permissionDecision":"deny","permissionDecisionReason":"process-audit.md missing. Spawn vsm_process_auditor during Phase 8b."}}'
        exit 0
    fi
fi

# Check 4: mutation-state.md MUST contain current build ID (FB29-sourced PM3)
# Extract build ID from mutations-applied.md
BUILD_ID=""
if [[ -f "$MUTATIONS_FILE" ]]; then
    BUILD_ID=$(grep -oE 'FB[0-9]+' "$MUTATIONS_FILE" | head -1)
fi
if [[ -n "$BUILD_ID" && -f "$HOME/vsm/viable-swarm-model/references/mutation-state.md" ]]; then
    if ! grep -q "$BUILD_ID" "$HOME/vsm/viable-swarm-model/references/mutation-state.md"; then
        echo "STOP BLOCKED by stop-verifier.sh: mutation-state.md does not contain build ID $BUILD_ID. Run update-mutation-state.sh before stopping." >&2
        echo '{"hookSpecificOutput":{"permissionDecision":"deny","permissionDecisionReason":"mutation-state.md missing build ID. Run update-mutation-state.sh ."}}'
        exit 0
    fi
fi

# Check 5: process-audit.md MUST NOT contain HARD BLOCK (2026-06-04 structural mutation)
if [[ -f "$KIMI_DIR/process-audit.md" ]]; then
    if grep -q "HARD BLOCK" "$KIMI_DIR/process-audit.md"; then
        echo "STOP BLOCKED by stop-verifier.sh: process-audit.md contains HARD BLOCK. Build compliance is below threshold. Address violations before stopping." >&2
        echo '{"hookSpecificOutput":{"permissionDecision":"deny","permissionDecisionReason":"process-audit.md contains HARD BLOCK. Address process violations before stopping."}}'
        exit 0
    fi
fi

# Check 6: mutation-portfolio-review.md MUST exist if this is a fitness build (2026-06-04 structural mutation)
if [[ -f "$KIMI_DIR/meta-report.md" && -f "$KIMI_DIR/mutations-applied.md" ]]; then
    if [[ ! -f "$KIMI_DIR/mutation-portfolio-review.md" ]]; then
        echo "STOP BLOCKED by stop-verifier.sh: mutation-portfolio-review.md is missing. Spawn vsm_learning_curator during Phase 8c-iii before completing." >&2
        echo '{"hookSpecificOutput":{"permissionDecision":"deny","permissionDecisionReason":"mutation-portfolio-review.md missing. Spawn vsm_learning_curator during Phase 8c-iii."}}'
        exit 0
    fi
fi

exit 0
