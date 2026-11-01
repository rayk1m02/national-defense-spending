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

FIRST_FISCAL_YEAR = 2017

# The environment variables are not actually set yet so it defaults to dev, nds-extract-dev, and downloads. 
# This is a design choice so that prod can be selected later by simply setting NDS_ENV=prod and without needing to change any code.