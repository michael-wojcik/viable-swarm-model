#!/bin/bash
# VSM Check Zero-Defaults Hook
# Blocks commits that contain insecure os.environ.get(..., default) fallbacks.
#
# Event: PreToolUse (matcher: WriteFile|StrReplaceFile|Shell)
# If any Python file in app/ contains os.environ.get("SECURITY_VAR", "default")
# with a non-empty default for security-critical variables, this hook BLOCKS.
#
# Targets: FB33-1 — tool-enforce Zero-Default rule to replace ineffective prompt-only FB32-1

set -euo pipefail

PAYLOAD=$(cat)
FILE_PATH=$(echo "$PAYLOAD" | jq -r '.tool_input.path // .tool_input.file_path // ""')
CWD=$(echo "$PAYLOAD" | jq -r '.cwd // "/tmp"')

# Only check Python files in app/ or similar backend directories
if [[ ! "$FILE_PATH" =~ \.py$ ]]; then
    exit 0
fi

# Security-critical variable patterns that must NEVER have default fallbacks
CRITICAL_VARS=(
    "DATABASE_URL"
    "DB_URL"
    "SQLALCHEMY_DATABASE_URI"
    "REDIS_URL"
    "CELERY_BROKER_URL"
    "CELERY_RESULT_BACKEND"
    "JWT_SECRET"
    "SECRET_KEY"
    "API_KEY"
    "AUTH_TOKEN"
    "S3_BUCKET_NAME"
    "RATELIMIT_STORAGE_URI"
    "STORAGE_URL"
)

# Build grep pattern: os.environ.get("VAR", "...") for each critical var
PATTERN=""
for var in "${CRITICAL_VARS[@]}"; do
    if [[ -n "$PATTERN" ]]; then
        PATTERN="$PATTERN|"
    fi
    PATTERN="${PATTERN}os\.environ\.get\([\"']${var}[\"'],\s*[\"'][^\"']+[\"']\)"
done

# If this is a file write, check the content
if echo "$PAYLOAD" | jq -e '.tool_input.content' >/dev/null 2>&1; then
    CONTENT=$(echo "$PAYLOAD" | jq -r '.tool_input.content // ""')
    MATCH=$(echo "$CONTENT" | grep -nE "$PATTERN" 2>/dev/null || true)
    if [[ -n "$MATCH" ]]; then
        echo "[BLOCKED by check-zero-defaults.sh] Insecure default fallback detected in $FILE_PATH:"
        echo "$MATCH"
        echo ""
        echo "Security-critical environment variables must NOT have default fallbacks."
        echo "Use os.environ['VAR'] or raise RuntimeError if missing."
        echo "See: security-patterns/SKILL.md — Environment Variable Default Fallback Rule (FB33-1)"
        exit 2
    fi
fi

exit 0
