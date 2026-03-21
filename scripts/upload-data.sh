#!/usr/bin/env bash
set -euo pipefail

bucket=$(aws s3api list-buckets \
  --query "Buckets[?starts_with(Name, 'cuttingedge-matchpredictor-data')].Name | [0]" \
  --output text)

if [ "$bucket" = "None" ] || [ -z "$bucket" ]; then
  echo "No matching bucket found" >&2
  exit 1
fi

# Athena requires one JSON object per line (not pretty-printed arrays).
# Convert to line-delimited JSON in a tmp dir, upload that, keep originals readable.
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT

for file in matches-2024.json matches-2025.json; do
  python3 -c "
import json, sys
with open(sys.argv[1]) as f:
    for obj in json.load(f):
        print(json.dumps(obj))
" "packages/etl/data/$file" > "$tmp/$file"
done

for file in predictions-2026.json upcoming.json; do
  python3 -c "
import json, sys
with open(sys.argv[1]) as f:
    for obj in json.load(f):
        print(json.dumps(obj))
" "packages/etl/data/$file" > "$tmp/$file"
done

echo "Clearing s3://${bucket}/"
aws s3 rm "s3://${bucket}/matches/" --recursive
aws s3 rm "s3://${bucket}/predictions/" --recursive
aws s3 rm "s3://${bucket}/upcoming/" --recursive

echo "Uploading to s3://${bucket}/"
aws s3 cp "$tmp/matches-2024.json" "s3://${bucket}/matches/"
aws s3 cp "$tmp/matches-2025.json" "s3://${bucket}/matches/"
aws s3 cp "$tmp/predictions-2026.json" "s3://${bucket}/predictions/"
aws s3 cp "$tmp/upcoming.json" "s3://${bucket}/upcoming/"
