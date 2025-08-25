#!/usr/bin/env bash
set -euo pipefail

HOST=${MB_HOST:-http://localhost:3000}
USER=${MB_USER:-admin@example.com}
PASS=${MB_PASS:-password}

SESSION=$(curl -X POST -H "Content-Type: application/json" \
  -d '{"username":"'"${USER}"'","password":"'"${PASS}"'"}' \
  "$HOST/api/session" | jq -r '.id')

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SEED_DIR="$SCRIPT_DIR/../metabase/seed"

# Import collections and capture numeric IDs
if [[ -f "$SEED_DIR/collections.ndjson" ]]; then
  declare -A COLLECTIONS
  while IFS= read -r line; do
    [[ -z "$line" ]] && continue
    key=$(echo "$line" | jq -r '.id')
    payload=$(echo "$line" | jq -c 'del(.id)')
    resp=$(curl -X POST -H "Content-Type: application/json" -H "X-Metabase-Session: $SESSION" \
      -d "$payload" "$HOST/api/collection")
    cid=$(echo "$resp" | jq -r '.id')
    COLLECTIONS[$key]=$cid
    echo "Created collection '$key' as id $cid"
  done < "$SEED_DIR/collections.ndjson"
fi

# Import cards, wiring them to collections when provided
if [[ -f "$SEED_DIR/cards.ndjson" ]]; then
  while IFS= read -r line; do
    [[ -z "$line" ]] && continue
    key=$(echo "$line" | jq -r '.collection // empty')
    if [[ -n "$key" && -n "${COLLECTIONS[$key]:-}" ]]; then
      cid=${COLLECTIONS[$key]}
      payload=$(echo "$line" | jq -c --arg cid "$cid" 'del(.collection) | .collection_id=($cid|tonumber)')
    else
      payload=$(echo "$line" | jq -c 'del(.collection)')
    fi
    name=$(echo "$line" | jq -r '.name')
    curl -X POST -H "Content-Type: application/json" -H "X-Metabase-Session: $SESSION" \
      -d "$payload" "$HOST/api/card" >/dev/null
    echo "Imported card '$name'"
  done < "$SEED_DIR/cards.ndjson"
fi

echo "Metabase seed import completed."
