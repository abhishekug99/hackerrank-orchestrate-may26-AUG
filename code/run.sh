#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
python -S code/main.py --input support_tickets/support_tickets.csv --output support_tickets/output.csv "$@"
