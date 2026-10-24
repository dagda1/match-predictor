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

for path in packages/etl/data/matches-*.json; do
  file=$(basename "$path")
  python3 -c "
import json, sys
with open(sys.argv[1]) as f:
    for obj in json.load(f):
        print(json.dumps(obj))
" "$path" > "$tmp/$file"
done

for file in predictions.json upcoming.json; do
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
for path in "$tmp"/matches-*.json; do
  aws s3 cp "$path" "s3://${bucket}/matches/"
done
aws s3 cp "$tmp/predictions.json" "s3://${bucket}/predictions/"
aws s3 cp "$tmp/upcoming.json" "s3://${bucket}/upcoming/"
