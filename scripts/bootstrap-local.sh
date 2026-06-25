#!/usr/bin/env bash

set -euo pipefail

STATE_ROOT="${VITADEX_STATE_ROOT:-$HOME/.vitadex}"
DATA_DIR="${VITADEX_DATA_DIR:-$STATE_ROOT/data}"
MEMORY_DIR="${VITADEX_MEMORY_DIR:-$STATE_ROOT/memory}"
LOG_DIR="${VITADEX_LOG_DIR:-$STATE_ROOT/logs}"
WORKSPACE_DIR="${VITADEX_WORKSPACE_DIR:-$STATE_ROOT/workspace}"
DB_PATH="${VITADEX_DB_PATH:-$DATA_DIR/vitadex.sqlite}"

mkdir -p "$DATA_DIR" "$MEMORY_DIR" "$LOG_DIR" "$WORKSPACE_DIR"

if [[ ! -f ".env.local" ]]; then
  cp .env.example .env.local
fi

cat > .env.local <<EOF
VITADEX_STATE_ROOT=$STATE_ROOT
VITADEX_DATA_DIR=$DATA_DIR
VITADEX_MEMORY_DIR=$MEMORY_DIR
VITADEX_LOG_DIR=$LOG_DIR
VITADEX_WORKSPACE_DIR=$WORKSPACE_DIR
VITADEX_DB_PATH=$DB_PATH
VITADEX_SAFE_MODE=true
VITADEX_ALLOWED_ROOT=.
VITADEX_LANGUAGE=it
VITADEX_BROWSER_MODE=mock
VITADEX_GMAIL_MODE=draft
VITADEX_CALENDAR_MODE=draft
VITADEX_DRIVE_MODE=mock_local
VITADEX_TELEGRAM_MODE=mock
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
