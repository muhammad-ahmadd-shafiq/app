#!/usr/bin/env bash
# Post one stage result to the SecureGitOps dashboard API.
#
# Inputs (environment variables):
#   STAGE, STATUS (pass|fail|warn|skipped)            required
#   TOOL, CRITICAL, HIGH, MEDIUM, LOW, DURATION       optional
#   DETAILS_FILE                                      optional JSON file with extra details
#   ENFORCE                                           "true" (default) makes a failed stage exit 1
#   REPORT_ONLY                                       "true" never exits 1, only posts the result
#   DASHBOARD_URL, DASHBOARD_API_KEY                  where to post
# The standard GITHUB_* variables supply commit, repo, branch, actor and run id.
set -uo pipefail

: "${STAGE:?STAGE is required}"
: "${STATUS:?STATUS is required}"
: "${GITHUB_SHA:?GITHUB_SHA is required}"
: "${GITHUB_RUN_ID:?GITHUB_RUN_ID is required}"

command -v jq >/dev/null 2>&1 || { echo "ERROR: jq is not installed on this runner (sudo apt install -y jq)"; exit 1; }
command -v curl >/dev/null 2>&1 || { echo "ERROR: curl is not installed on this runner"; exit 1; }

TOOL="${TOOL:-$STAGE}"
CRITICAL="${CRITICAL:-0}"
HIGH="${HIGH:-0}"
MEDIUM="${MEDIUM:-0}"
LOW="${LOW:-0}"
DURATION="${DURATION:-0}"
FINDINGS=$((CRITICAL + HIGH + MEDIUM + LOW))

DETAILS='{}'
if [ -n "${DETAILS_FILE:-}" ] && [ -f "$DETAILS_FILE" ] && jq -e . "$DETAILS_FILE" >/dev/null 2>&1; then
  DETAILS=$(cat "$DETAILS_FILE")
fi

if [ "${ENFORCE:-true}" = "true" ]; then ENFORCED=true; else ENFORCED=false; fi

if [ -z "${DASHBOARD_URL:-}" ] || [ -z "${DASHBOARD_API_KEY:-}" ]; then
  echo "WARNING: DASHBOARD_URL or DASHBOARD_API_KEY is not set, skipping report for stage $STAGE"
else
  RUN_URL="${GITHUB_SERVER_URL:-https://github.com}/${GITHUB_REPOSITORY:-unknown}/actions/runs/${GITHUB_RUN_ID}"
  PAYLOAD=$(jq -n \
    --arg commit_sha "$GITHUB_SHA" \
    --arg run_id "$GITHUB_RUN_ID" \
    --arg repo "${GITHUB_REPOSITORY:-}" \
    --arg branch "${GITHUB_REF_NAME:-}" \
    --arg actor "${GITHUB_ACTOR:-}" \
    --arg run_url "$RUN_URL" \
    --argjson enforced "$ENFORCED" \
    --arg stage "$STAGE" \
    --arg tool "$TOOL" \
    --arg status "$STATUS" \
    --argjson findings "$FINDINGS" \
    --argjson critical "$CRITICAL" \
    --argjson high "$HIGH" \
    --argjson medium "$MEDIUM" \
    --argjson low "$LOW" \
    --argjson duration_seconds "$DURATION" \
    --argjson details "$DETAILS" \
    '{commit_sha:$commit_sha, run_id:$run_id, repo:$repo, branch:$branch, actor:$actor,
      run_url:$run_url, enforced:$enforced, stage:$stage, tool:$tool, status:$status,
      findings:$findings, critical:$critical, high:$high, medium:$medium, low:$low,
      duration_seconds:$duration_seconds, details:$details}')

  RESP=$(mktemp)
  HTTP=$(curl -sS -o "$RESP" -w '%{http_code}' --max-time 15 -X POST "${DASHBOARD_URL%/}/api/stages" \
    -H "Content-Type: application/json" \
    -H "X-API-Key: ${DASHBOARD_API_KEY}" \
    -d "$PAYLOAD") || HTTP="000"
  if [ "$HTTP" = "201" ]; then
    echo "Reported stage '$STAGE' ($STATUS) to dashboard"
  else
    # A dashboard outage must never break the pipeline itself.
    echo "WARNING: dashboard returned HTTP $HTTP for stage '$STAGE'"
    cat "$RESP" 2>/dev/null || true
    echo
  fi
  rm -f "$RESP"
fi

if [ "$STATUS" = "fail" ] && [ "$ENFORCED" = "true" ] && [ "${REPORT_ONLY:-false}" != "true" ]; then
  echo "GATE FAILED: stage '$STAGE' failed and enforcement is on."
  exit 1
fi
exit 0
