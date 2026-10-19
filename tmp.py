import requests, time
import json, zipfile
import pandas as pd
import os
from extract.prestage import prestage
from extract.sources import SOURCES
from extract.columns import COLUMNS
from extract.bulkfiles import list_monthly_files, download_monthly_files
from extract.prestage import filter_mask

import redshift_connector
from dotenv import load_dotenv

from extract.settings import PRESTAGED_PREFIX
from extract.storage import get_client, list_keys

dhs = SOURCES["dhs"]
for fy in (2026, 2027):
    files = list_monthly_files(dhs["agency_id"], fy)
    print(fy)
    for f in files:
        print("  ", f["file_name"], f["updated_date"])