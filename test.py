import requests, time, json
import zipfile
import pandas as pd

### ----------------------------------------------------------------------------------------------------------------------------- ###

# testing the /api/v2/download/* API for DOE, and viewing name search for NNSA through zip file

payload = {
    "filters": {
        "agencies": [{"type": "awarding", "tier": "toptier", "name": "Department of Energy"}],
        "time_period": [{"start_date": "2024-01-01", "end_date": "2024-01-31"}],
    },
    "spending_level": ["transactions"],
    "columns": []  # empty = all columns
}

r = requests.post("https://api.usaspending.gov/api/v2/download/search/", json=payload, timeout=30)
result = r.json()
print(r.status_code)
# print(json.dumps(result, indent=2))

status_url = result["status_url"]

while True:
    r = requests.get(status_url, timeout=30)
    data = r.json()
    if data.get("status") in ("finished", "failed"):
        break
    time.sleep(5)

# print(json.dumps(data, indent=2))

# grab the zip
r1 = requests.get(data["file_url"], timeout=60)
with open("nnsa_test.zip", "wb") as f:              # wb (write binary)
    f.write(r1.content)                             # save those bytes to disk

# open it without manually extracting
with zipfile.ZipFile("nnsa_test.zip") as z:
    print(z.namelist())             # what files are inside (should be one csv, so confirming the name)
    csv_name = z.namelist()[0]      # grab the file
    with z.open(csv_name) as f:     # open csv in memory
        df = pd.read_csv(f)

# for i, col in enumerate(df.columns):
#     print(i, col)

# print(df["awarding_sub_agency_name"].unique())
# print(df["awarding_office_name"].unique())

# print(df["awarding_office_name"].nunique())
# for name in sorted(df["awarding_office_name"].unique()):
#     print(name)

# office_map = df[["awarding_office_code", "awarding_office_name"]].drop_duplicates().sort_values("awarding_office_name")
# print(office_map.to_string(index=False))

DOE_DEFENSE_OFFICE_CODES = [
    "892332", "892330", "892331",   # NNSA
    "893033", "893035", "893031", "893042", "893034", "893032",  # EM
    "893039",  # Hanford Field Office
    "893040",  # Office of River Protection
]

filtered = df[df["awarding_office_code"].isin(DOE_DEFENSE_OFFICE_CODES)]

### ----------------------------------------------------------------------------------------------------------------------------- ###

# r2 = requests.get(f"https://api.usaspending.gov/api/v2/agency/089/sub_agency/", timeout=30)
# print(r2.status_code)
# print(json.dumps(r2.json(), indent=2))

### ----------------------------------------------------------------------------------------------------------------------------- ###