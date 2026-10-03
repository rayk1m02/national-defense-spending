import os

ACCOUNT_ID = "381492047455"
REGION = "us-east-1"

ENV = os.environ.get("NDS_ENV", "dev") # read NDS_ENV variable, if not set, return "dev"
if ENV not in ("dev", "prod"):
    raise ValueError(f"NDS_ENV must be 'dev' or 'prod', got {ENV!r}")

BUCKET = f"national-defense-spending-{ENV}-{ACCOUNT_ID}-{REGION}-an"
AWS_PROFILE = os.environ.get("AWS_PROFILE", f"nds-extract-{ENV}")

RAW_PREFIX = "raw"
PRESTAGED_PREFIX = "prestaged"

DOWNLOAD_DIR = os.environ.get("NDS_DOWNLOAD_DIR", "downloads")

FIRST_FISCAL_YEAR = 2008