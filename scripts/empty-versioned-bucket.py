#!/usr/bin/env python3
import subprocess
import sys

try:
    import boto3
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "--break-system-packages", "boto3"])
    import boto3

bucket = sys.argv[1]
s3 = boto3.client("s3")
versions = s3.list_object_versions(Bucket=bucket)
while True:
    objects = [{"Key": v["Key"], "VersionId": v["VersionId"]} for v in versions.get("Versions", [])]
    objects += [{"Key": d["Key"], "VersionId": d["VersionId"]} for d in versions.get("DeleteMarkers", [])]
    if not objects:
        break
    s3.delete_objects(Bucket=bucket, Delete={"Objects": objects[:1000]})
    if not versions.get("IsTruncated"):
        break
    versions = s3.list_object_versions(Bucket=bucket, KeyMarker=versions["NextKeyMarker"], VersionIdMarker=versions["NextVersionIdMarker"])
print(f"emptied {bucket}")
