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

# load_dotenv()

# conn = redshift_connector.connect(
#     host=os.environ["NDS_REDSHIFT_HOST"],
#     port=int(os.environ["NDS_REDSHIFT_PORT"]),
#     database=os.environ["NDS_REDSHIFT_DATABASE"],
#     user=os.environ["NDS_REDSHIFT_USER"],
#     password=os.environ["NDS_REDSHIFT_PASSWORD"],
# )
# cursor = conn.cursor()
# cursor.execute("SELECT current_user, current_database()")
# print(cursor.fetchone())
# conn.close()

keys = list_keys(get_client(), f"{PRESTAGED_PREFIX}/")
for key in keys:
    print(key)
print(len(keys))