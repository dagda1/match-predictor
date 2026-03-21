#!/usr/bin/env bash
set -euo pipefail

bucket=$(aws s3api list-buckets \
  --query "Buckets[?starts_with(Name, 'cuttingedge-matchpredictor-data')].Name | [0]" \
  --output text)

if [ "$bucket" = "None" ] || [ -z "$bucket" ]; then
  echo "No matching bucket found" >&2
  exit 1
fi

echo "Clearing s3://${bucket}/matches/"
aws s3 rm "s3://${bucket}/matches/" --recursive
aws s3 rm "s3://${bucket}/predictions/" --recursive
aws s3 rm "s3://${bucket}/upcoming/" --recursive

echo "Uploading to s3://${bucket}/matches/"
aws s3 cp packages/etl/data/matches-2024.json "s3://${bucket}/matches/"
aws s3 cp packages/etl/data/matches-2025.json "s3://${bucket}/matches/"
aws s3 cp packages/etl/data/predictions-2026.json "s3://${bucket}/predictions/"
aws s3 cp packages/etl/data/upcoming.json "s3://${bucket}/upcoming/"
