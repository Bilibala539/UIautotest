#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"
python3 -m pytest "${1:-tests/}" -v

echo "Test run completed. Local reports, when enabled, are in output/."
