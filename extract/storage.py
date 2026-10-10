import boto3
from extract import settings
from extract.settings import BUCKET

# to communicate to S3 using nds-extract-dev
def get_client():
    session = boto3.Session(profile_name=settings.AWS_PROFILE)
    return session.client("s3")

# based on the file, it returns its S3 address
# prefix - raw/prestaged
# source_name - SOURCES key (dod, doe, ...)
# file - monthly_files[]
# filename- FYXXX_XXX_Contracts_Full_XXXXXXXX.zip (if zip not prestaged)
# # raw/dod/full/fiscal_year=2025/FY2025_097_Contracts_Full_20260906.zip
def build_key(prefix, source_name, file, filename): 
    if file["fiscal_year"] is None:
        partition = f"delta/load_date={file['updated_date']}"
    else:
        partition = f"full/fiscal_year={file['fiscal_year']}"
    return f"{prefix}/{source_name}/{partition}/{filename}"

# put the local file at that address
def upload(client, local_path, key):
    client.upload_file(local_path, settings.BUCKET, key)

# does this file already exist
def exists(client, key):
    resp = client.list_objects_v2(Bucket=settings.BUCKET, Prefix=key)
    return any(obj["Key"] == key for obj in resp.get("Contents", []))

# check whether a partition has objects
def has_objects(client, prefix):
    resp = client.list_objects_v2(Bucket=settings.BUCKET, Prefix=prefix, MaxKeys=1)
    return resp.get("KeyCount", 0) > 0

# return every key under a prefix
def list_keys(client, prefix):
    paginator = client.get_paginator("list_objects_v2")
    keys = []
    for page in paginator.paginate(Bucket=BUCKET, Prefix=prefix):
        for obj in page.get("Contents", []):
            keys.append(obj["Key"])
    return keys