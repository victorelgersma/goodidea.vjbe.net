#!/usr/bin/env bash
#
# compile_dashboard.sh
#
# Builds dashboard JSON data from a Qualtrics survey CSV export.
# Excludes "Survey Preview" rows and rows under 50% progress.
#
# Usage:
#   ./compile_dashboard.sh <survey_export.csv> [output.json]
#
# Requires:
#   bash >= 4
#   python3

set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &>/dev/null && pwd)"

if (( BASH_VERSINFO[0] < 4 )); then
    echo "Error: this script requires bash 4+ (found ${BASH_VERSION})." >&2
    exit 1
fi

if [[ $# -lt 1 || $# -gt 2 ]]; then
    echo "Usage: $(basename "$0") <survey_export.csv> [output.json]" >&2
    exit 1
fi

input_csv="$1"
output_json="${2:-dashboard.json}"

if [[ ! -f "$input_csv" ]]; then
    echo "Error: input file not found: $input_csv" >&2
    exit 1
fi

if ! command -v python3 &>/dev/null; then
    echo "Error: python3 is required but was not found on PATH." >&2
    exit 1
fi

echo "==> Generating dashboard JSON..."
python3 "$SCRIPT_DIR/generate_dashboard.py" "$input_csv" "$output_json"

echo "Done. Generated $output_json"