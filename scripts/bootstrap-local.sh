#!/usr/bin/env bash

set -euo pipefail

STATE_ROOT="${PRIVATE_OS_STATE_ROOT:-$HOME/.private-os}"
DATA_DIR="${PRIVATE_OS_DATA_DIR:-$STATE_ROOT/data}"
MEMORY_DIR="${PRIVATE_OS_MEMORY_DIR:-$STATE_ROOT/memory}"
LOG_DIR="${PRIVATE_OS_LOG_DIR:-$STATE_ROOT/logs}"
WORKSPACE_DIR="${PRIVATE_OS_WORKSPACE_DIR:-$STATE_ROOT/workspace}"
DB_PATH="${PRIVATE_OS_DB_PATH:-$DATA_DIR/private_os.sqlite}"

mkdir -p "$DATA_DIR" "$MEMORY_DIR" "$LOG_DIR" "$WORKSPACE_DIR"

if [[ ! -f ".env.local" ]]; then
  cp .env.example .env.local
fi

cat > .env.local <<EOF
PRIVATE_OS_STATE_ROOT=$STATE_ROOT
PRIVATE_OS_DATA_DIR=$DATA_DIR
PRIVATE_OS_MEMORY_DIR=$MEMORY_DIR
PRIVATE_OS_LOG_DIR=$LOG_DIR
PRIVATE_OS_WORKSPACE_DIR=$WORKSPACE_DIR
PRIVATE_OS_DB_PATH=$DB_PATH
PRIVATE_OS_SAFE_MODE=true
PRIVATE_OS_ALLOWED_ROOT=.
PRIVATE_OS_LANGUAGE=it
PRIVATE_OS_BROWSER_MODE=mock
PRIVATE_OS_GMAIL_MODE=draft
PRIVATE_OS_CALENDAR_MODE=draft
PRIVATE_OS_DRIVE_MODE=mock_local
PRIVATE_OS_TELEGRAM_MODE=mock
EOF

if [[ ! -f "$STATE_ROOT/CONSTITUTION.local.md" ]]; then
  cat > "$STATE_ROOT/CONSTITUTION.local.md" <<'EOF'
# Local Constitution Overlay

## Identity

Describe the local operator identity here.

## Mission

Describe the local mission and priorities here.

## Constraints

- Keep all personal data local.
- Never commit this file.
EOF
fi

echo "Bootstrap completato."
echo "State root: $STATE_ROOT"
echo "Local env: $(pwd)/.env.local"
echo "Local constitution: $STATE_ROOT/CONSTITUTION.local.md"
