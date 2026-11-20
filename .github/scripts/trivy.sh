#!/usr/bin/env bash
# Vulnerability scan with Trivy.
# Usage: trivy.sh <fs|image> <target> <stage-name>
# CRITICAL fails the gate, HIGH gives a warn.
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MODE="$1"; TARGET="$2"; STAGE_NAME="$3"
START=$(date +%s)
OUT="trivy-${STAGE_NAME}.json"

EXTRA=()
if [ "$MODE" = "image" ]; then EXTRA+=(--ignore-unfixed); fi

if ! trivy "$MODE" --scanners vuln --format json --output "$OUT" --quiet "${EXTRA[@]}" "$TARGET"; then
  echo "Trivy failed to run (database download problem?)"
  STAGE="$STAGE_NAME" TOOL=trivy STATUS=fail bash "$HERE/report.sh"
  exit $?
fi

count() {
  jq --arg sev "$1" '[.Results[]?.Vulnerabilities[]? | select(.Severity==$sev)] | length' "$OUT"
}
CRIT=$(count CRITICAL); HIGH=$(count HIGH); MED=$(count MEDIUM); LOW=$(count LOW)

jq '{items: ([.Results[]? | .Target as $t | .Vulnerabilities[]?
      | select(.Severity=="CRITICAL" or .Severity=="HIGH")
      | {target: $t, id: .VulnerabilityID, package: .PkgName, installed: .InstalledVersion,
         fixed: .FixedVersion, severity: .Severity}] | .[:25])}' "$OUT" > "trivy-${STAGE_NAME}-details.json"

if [ "$CRIT" -gt 0 ]; then STATUS=fail; elif [ "$HIGH" -gt 0 ]; then STATUS=warn; else STATUS=pass; fi
echo "Trivy ($STAGE_NAME): critical=$CRIT high=$HIGH medium=$MED low=$LOW"

STAGE="$STAGE_NAME" TOOL=trivy STATUS=$STATUS CRITICAL=$CRIT HIGH=$HIGH MEDIUM=$MED LOW=$LOW \
  DURATION=$(( $(date +%s) - START )) DETAILS_FILE="trivy-${STAGE_NAME}-details.json" \
  bash "$HERE/report.sh"
