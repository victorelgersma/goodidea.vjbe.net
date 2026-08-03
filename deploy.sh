#!/usr/bin/env bash
#
# deploy.sh
# Deploy dashboard.html and logo.html to ~/html/agoodidea on the hetzner host.

set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &>/dev/null && pwd)"
LOCAL_DASHBOARD="${SCRIPT_DIR}/dashboard.html"
LOCAL_LOGO="${SCRIPT_DIR}/logo.html"
REMOTE_HOST="hetzner"
REMOTE_DIR="~/html/agoodidea"

# Verify both local files exist before deploying
missing_files=0

if [[ ! -f "$LOCAL_DASHBOARD" ]]; then
    echo "Error: local file not found: $LOCAL_DASHBOARD" >&2
    echo "Run ./compile_dashboard.sh first to generate dashboard.html." >&2
    missing_files=1
fi

if [[ ! -f "$LOCAL_LOGO" ]]; then
    echo "Error: local file not found: $LOCAL_LOGO" >&2
    missing_files=1
fi

if [[ "$missing_files" -eq 1 ]]; then
    exit 1
fi

echo "==> Ensuring remote directory exists..."
ssh "$REMOTE_HOST" "mkdir -p $REMOTE_DIR"

echo "==> Uploading files to $REMOTE_HOST:$REMOTE_DIR..."
rsync -avz --inplace "$LOCAL_DASHBOARD" "${REMOTE_HOST}:${REMOTE_DIR}/index.html"
rsync -avz --inplace "$LOCAL_LOGO" "${REMOTE_HOST}:${REMOTE_DIR}/logo.html"

echo "==> Deployment complete!"