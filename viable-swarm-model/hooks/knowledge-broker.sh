#!/bin/bash
# VSM Knowledge Broker Hook
# Writes cross-skill digest to knowledge-broker.md on session end.
# Determines skill context from CWD and synthesizes a digest of gaps/experiments.
#
# Event: SessionEnd

set -euo pipefail

PAYLOAD=$(cat)
SESSION_ID=$(echo "$PAYLOAD" | jq -r '.session_id // "unknown"')
CWD=$(echo "$PAYLOAD" | jq -r '.cwd // "/tmp"')
REASON=$(echo "$PAYLOAD" | jq -r '.reason // "unknown"')

BROKER_FILE="$HOME/vsm/viable-swarm-model/references/knowledge-broker.md"
TIMESTAMP=$(date -u +%Y-%m-%dT%H:%M:%SZ)

# Determine skill context from CWD
SKILL_CONTEXT="unknown"
if [[ "$CWD" =~ vsm-fitness-coach ]]; then
    SKILL_CONTEXT="coach"
elif [[ "$CWD" =~ vsm-fitness-gym ]]; then
    SKILL_CONTEXT="gym"
elif [[ "$CWD" =~ viable-swarm-model ]]; then
    SKILL_CONTEXT="main"
fi

# Initialize broker file if not exists
if [[ ! -f "$BROKER_FILE" ]]; then
    mkdir -p "$(dirname "$BROKER_FILE")"
    cat > "$BROKER_FILE" << 'HEADER'
# VSM Knowledge Broker — Cross-Skill Digest
> Updated by: `knowledge-broker.sh` (SessionEnd hook)
> Read by: All three skills at Phase 0

This file bridges the three VSM skills (main, coach, gym) by explicitly
surfacing what each skill has learned, so the others can act on it.

HEADER
fi

# Build digest based on skill context
DIGEST=""

if [[ "$SKILL_CONTEXT" == "main" ]]; then
    # Extract from meta-report and process-audit if they exist
    META="$CWD/.kimi/meta-report.md"
    AUDIT="$CWD/.kimi/process-audit.md"
    GAPS=""
    if [[ -f "$META" ]]; then
        GAPS=$(grep -iE 'gap|missed|failure|bypass|BLOCKER' "$META" 2>/dev/null | head -5 | sed 's/^/  - /' || true)
    fi
    if [[ -f "$AUDIT" && -z "$GAPS" ]]; then
        GAPS=$(grep -iE 'violation|missed|non-compliant' "$AUDIT" 2>/dev/null | head -5 | sed 's/^/  - /' || true)
    fi
    if [[ -z "$GAPS" ]]; then
        GAPS="  - (no gaps extracted — meta-report may be missing)"
    fi

    DIGEST=$(cat << EOF

## [$TIMESTAMP] — Main Skill Build ($SESSION_ID)
**Skill**: viable-swarm-model
**Top gaps from meta-report/process-audit**:
$GAPS
**Suggested Coach Trap**: Design build targeting most frequent gap above
**Suggested Gym Experiment**: Test hypothesis for most frequent gap
**Status**: Build completed, awaiting coach evaluation
EOF
)

elif [[ "$SKILL_CONTEXT" == "coach" ]]; then
    # Extract from fitness report or mutation log
    MUTATION_LOG="$HOME/vsm/viable-swarm-model/references/mutation-log.md"
    FITNESS_LEDGER="$HOME/vsm/vsm-fitness-coach/references/fitness-projects.md"
    LAST_SCORE="unknown"
    if [[ -f "$FITNESS_LEDGER" ]]; then
        LAST_SCORE=$(grep -E 'FB[0-9]+.*score' "$FITNESS_LEDGER" 2>/dev/null | tail -1 | grep -oE '[0-9]\.[0-9]' | tail -1 || true)
    fi

    DIGEST=$(cat << EOF

## [$TIMESTAMP] — Coach Fitness Evaluation ($SESSION_ID)
**Skill**: vsm-fitness-coach
**Last build score**: $LAST_SCORE
**Mutation effectiveness**: See mutation-log.md for measured effects
**New mutations proposed**: Check coach mutation-log.md
**Suggested Gym Priority**: Test top-scored gap hypotheses
**Status**: Evaluation complete, mutations applied
EOF
)

elif [[ "$SKILL_CONTEXT" == "gym" ]]; then
    # Extract from experiment results
    GYM_EXPERIMENTS="$HOME/vsm/vsm-fitness-gym/references/experiments.md"
    RECENT_RESULTS=""
    if [[ -f "$GYM_EXPERIMENTS" ]]; then
        RECENT_RESULTS=$(tail -30 "$GYM_EXPERIMENTS" 2>/dev/null | grep -iE 'confirmed|rejected|inconclusive' | tail -3 | sed 's/^/  - /' || true)
    fi
    if [[ -z "$RECENT_RESULTS" ]]; then
        RECENT_RESULTS="  - (no recent results extracted)"
    fi

    DIGEST=$(cat << EOF

## [$TIMESTAMP] — Gym Experiment Results ($SESSION_ID)
**Skill**: vsm-fitness-gym
**Recent hypothesis results**:
$RECENT_RESULTS
**Suggested Main Skill Action**: Integrate confirmed patterns into pattern-library.md
**Suggested Coach Action**: Score builds using confirmed detection improvements
**Status**: Experiments complete, hypotheses updated
EOF
)
fi

# Append digest
if [[ -n "$DIGEST" ]]; then
    echo "$DIGEST" >> "$BROKER_FILE"
fi

exit 0
