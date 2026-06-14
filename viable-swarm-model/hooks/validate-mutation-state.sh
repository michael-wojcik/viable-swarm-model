#!/bin/bash
# validate-mutation-state.sh
# Pre-session validation of mutation tracking infrastructure.
# The validation logic lives in validate-mutation-state.py for speed.
#
# Usage: bash ~/vsm/viable-swarm-model/hooks/validate-mutation-state.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Resolve the real Python interpreter once to avoid pyenv shim overhead.
if [ -z "${PYTHON3:-}" ]; then
    if command -v pyenv >/dev/null 2>&1; then
        PYTHON3=$(pyenv which python3 2>/dev/null || command -v python3)
    else
        PYTHON3=$(command -v python3)
    fi
fi

"$PYTHON3" "$SCRIPT_DIR/validate-mutation-state.py" "$@"
