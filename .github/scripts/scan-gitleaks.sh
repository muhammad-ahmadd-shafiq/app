#!/usr/bin/env bash
# Secret scan over the full git history. Any finding is critical and fails the gate.
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
START=$(date +%s)

gitleaks detect --source . --report-format json --report-path gitleaks-report.json \
  --redact --no-banner --exit-code 0
[ -f gitleaks-report.json ] || echo '[]' > gitleaks-report.json

COUNT=$(jq 'length' gitleaks-report.json)
jq '{items: [.[] | {rule: .RuleID, file: .File, line: .StartLine, commit: .Commit}]}' \
  gitleaks-report.json > gitleaks-details.json

if [ "$COUNT" -gt 0 ]; then STATUS=fail; else STATUS=pass; fi
echo "Gitleaks findings: $COUNT"

STAGE=gitleaks TOOL=gitleaks STATUS=$STATUS CRITICAL=$COUNT \
  DURATION=$(( $(date +%s) - START )) DETAILS_FILE=gitleaks-details.json \
  bash "$HERE/report.sh"
