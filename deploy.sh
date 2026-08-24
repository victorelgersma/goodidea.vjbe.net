#!/usr/bin/env bash
#
# deploy.sh
#
# Deploys the dashboard application to the Hetzner host.
#

set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &>/dev/null && pwd)"

REMOTE_HOST="hetzner"
REMOTE_DIR="~/html/agoodidea"

FILES=(
    "index.php"
    "dashboard.php"
    "comments.php"
    "dashboard.json"
    "style.css"
    "data-anonymized/2026-08-03/results_anonymized.csv"
)

echo "==> Checking local files..."

for file in "${FILES[@]}"; do
    if [[ ! -f "${SCRIPT_DIR}/${file}" ]]; then
        echo "Error: missing local file: ${SCRIPT_DIR}/${file}" >&2
        exit 1
    fi
done

if [[ ! -d "${SCRIPT_DIR}/includes" ]]; then
    echo "Error: missing includes directory." >&2
    exit 1
fi

echo "==> Ensuring remote directory exists..."
ssh "$REMOTE_HOST" "mkdir -p $REMOTE_DIR/includes"

echo "==> Uploading PHP files..."
rsync -avz --inplace \
    "${SCRIPT_DIR}/index.php" \
    "${SCRIPT_DIR}/dashboard.php" \
    "${SCRIPT_DIR}/comments.php" \
    "${SCRIPT_DIR}/data-anonymized/2026-08-03/results_anonymized.csv" \
    "${REMOTE_HOST}:${REMOTE_DIR}/"

echo "==> Uploading generated data and styles..."
rsync -avz --inplace \
    "${SCRIPT_DIR}/dashboard.json" \
    "${SCRIPT_DIR}/style.css" \
    "${REMOTE_HOST}:${REMOTE_DIR}/"

echo "==> Uploading includes..."
rsync -avz --inplace \
    "${SCRIPT_DIR}/includes/" \
    "${REMOTE_HOST}:${REMOTE_DIR}/includes/"

echo "==> Deployment complete!"
echo "https://agoodidea.vjbe.net"