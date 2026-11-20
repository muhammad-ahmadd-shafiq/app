#!/usr/bin/env bash
# Generate a CycloneDX SBOM with Syft.
# Usage: sbom.sh <syft-source> <stage-name>
#   syft-source examples: dir:.   docker:ghcr.io/owner/image:tag
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SOURCE="$1"; STAGE_NAME="$2"
START=$(date +%s)
OUT="sbom-${STAGE_NAME}.json"

if syft "$SOURCE" -q -o "cyclonedx-json=$OUT"; then
  COMPONENTS=$(jq '.components | length' "$OUT")
  STATUS=pass
else
  COMPONENTS=0
  STATUS=fail
fi
jq -n --argjson components "$COMPONENTS" --arg file "$OUT" \
  '{components: $components, format: "cyclonedx-json", file: $file}' > "sbom-${STAGE_NAME}-details.json"
echo "SBOM $STAGE_NAME: $COMPONENTS components"

STAGE="$STAGE_NAME" TOOL=syft STATUS=$STATUS \
  DURATION=$(( $(date +%s) - START )) DETAILS_FILE="sbom-${STAGE_NAME}-details.json" \
  bash "$HERE/report.sh"
