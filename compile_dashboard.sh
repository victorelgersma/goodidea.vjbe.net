#!/usr/bin/env bash
#
# compile_dashboard.sh
#
# Builds an HTML results dashboard from a Qualtrics survey CSV export.
# Excludes "Survey Preview" rows and rows under 50% progress, then renders
# charts (Chart.js) and comment lists for every question.
#
# Usage:
#   ./compile_dashboard.sh <survey_export.csv> [output.html]
#
# Requires: bash >= 4 (associative arrays not actually used, but written
#           against bash 5), python3 (standard library only, no deps).

set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &>/dev/null && pwd)"

if (( BASH_VERSINFO[0] < 4 )); then
    echo "Error: this script requires bash 4+ (found ${BASH_VERSION})." >&2
    exit 1
fi

if [[ $# -lt 1 || $# -gt 2 ]]; then
    echo "Usage: $(basename "$0") <survey_export.csv> [output.html]" >&2
    exit 1
fi

input_csv="$1"
output_html="${2:-dashboard.html}"

if [[ ! -f "$input_csv" ]]; then
    echo "Error: input file not found: $input_csv" >&2
    exit 1
fi

if ! command -v python3 &>/dev/null; then
    echo "Error: python3 is required but was not found on PATH." >&2
    exit 1
fi

python3 "$SCRIPT_DIR/generate_dashboard.py" "$input_csv" "$output_html"

echo "Done. Open $output_html in a browser to view the dashboard."
