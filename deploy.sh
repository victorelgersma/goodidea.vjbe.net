
#!/usr/bin/env bash
#
# deploy.sh
# Deploy dashboard.html to ~/html/agoodidea on the hetzner host.

set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &>/dev/null && pwd)"
LOCAL_FILE="${SCRIPT_DIR}/dashboard.html"
REMOTE_HOST="hetzner"
REMOTE_DIR="~/html/agoodidea"

if [[ ! -f "$LOCAL_FILE" ]]; then
    echo "Error: local file not found: $LOCAL_FILE" >&2
    echo "Run ./compile_dashboard.sh first to generate dashboard.html." >&2
    exit 1
fi

echo "==> Ensuring remote directory exists..."
ssh "$REMOTE_HOST" "mkdir -p $REMOTE_DIR"

echo "==> Uploading dashboard.html to $REMOTE_HOST:$REMOTE_DIR..."
rsync -avz --inplace "$LOCAL_FILE" "${REMOTE_HOST}:${REMOTE_DIR}/index.html"

echo "==> Deployment complete!"