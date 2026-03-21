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

echo "Uploading to s3://${bucket}/matches/"
aws s3 sync packages/etl/data/ "s3://${bucket}/matches/"
