#!/usr/bin/env bash
# Static analysis. Semgrep ERROR fails the gate, WARNING gives a warn.
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
START=$(date +%s)

semgrep scan --config p/default --metrics=off --json --output semgrep-report.json --quiet . || true
if [ ! -s semgrep-report.json ]; then
  echo "Semgrep produced no report"
  STAGE=semgrep TOOL=semgrep STATUS=fail bash "$HERE/report.sh"
  exit $?
fi

ERRS=$(jq '[.results[] | select(.extra.severity=="ERROR")] | length' semgrep-report.json)
WARNS=$(jq '[.results[] | select(.extra.severity=="WARNING")] | length' semgrep-report.json)
INFOS=$(jq '[.results[] | select(.extra.severity=="INFO")] | length' semgrep-report.json)
jq '{items: ([.results[] | {rule: .check_id, severity: .extra.severity, file: .path, line: .start.line}] | .[:25])}' \
  semgrep-report.json > semgrep-details.json

if [ "$ERRS" -gt 0 ]; then STATUS=fail; elif [ "$WARNS" -gt 0 ]; then STATUS=warn; else STATUS=pass; fi
echo "Semgrep: error=$ERRS warning=$WARNS info=$INFOS"

STAGE=semgrep TOOL=semgrep STATUS=$STATUS HIGH=$ERRS MEDIUM=$WARNS LOW=$INFOS \
  DURATION=$(( $(date +%s) - START )) DETAILS_FILE=semgrep-details.json \
  bash "$HERE/report.sh"
