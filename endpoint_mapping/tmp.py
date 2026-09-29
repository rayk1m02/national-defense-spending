import requests, time
import json, zipfile
import pandas as pd

# payload = {
#     "filters": {
#         "agencies": [{"type": "awarding", "tier": "toptier", "name": "Department of Energy"}],
#         "time_period": [{"start_date": "2024-01-01", "end_date": "2024-01-31"}],
#     },
#     "spending_level": ["transactions"],
#     "columns": []  # empty = all columns
# }

# r3 = requests.post("https://api.usaspending.gov/api/v2/download/search/", json=payload, timeout=30)
# result = r3.json()
# # print(r.status_code)
# # print(json.dumps(result, indent=2))

# status_url = result["status_url"]

# # we poll status_url to know when the background generation job completes so that we can download our file_url.
# while True:
#     r4 = requests.get(status_url, timeout=30)
#     data = r4.json()
#     if data.get("status") in ("finished", "failed"):
#         break
#     time.sleep(5)

# r5 = requests.get(data["file_url"], timeout=60)
# with open("../bulk_data_samples/zip_doe_download.zip", "wb") as f:      # wb (write binary)
#     f.write(r5.content)                                                 # save those bytes to disk

# open zip without manual extraction
with zipfile.ZipFile("../bulk_data_samples/zip_doe_download.zip") as z:
    # print(z.namelist())                                                     # what files are inside (should be one csv, so confirming the name)
    csv_name = z.namelist()[0]                                              # grab the file
    with z.open(csv_name) as f:                                             # open csv in memory
        df = pd.read_csv(f)

# for i, col in enumerate(df.columns):
#     print(i, col)
DOE_DEFENSE_OFFICE_CODES = [
    "892332", "892330", "892331",                                   # NNSA
    "893033", "893035", "893031", "893042", "893034", "893032",     # EM
    "893039",                                                       # Hanford Field Office
    "893040",                                                       # Office of River Protection
]

filtered = df[df["awarding_office_code"].isin(DOE_DEFENSE_OFFICE_CODES)]

print(filtered)