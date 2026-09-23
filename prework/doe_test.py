import requests, time
import json, zipfile
import pandas as pd

# scoping DOE sub-agencies
# get real agency IDs
# check if pre-generated files exist for DOE and if we can filter by office
# figuring out DOE office codes

### ----------------------------------------------------------------------------------------------------------------------------- ###

# scoping DOE sub-agencies (we assume 089 is the National Nuclear Security Administration). 
# we see that NNSA makes up about half of DOE's total spending. The rest are non-defense energy programs.
r = requests.get("https://api.usaspending.gov/api/v2/agency/089/sub_agency/", timeout=30)
print(r.status_code)
print(json.dumps(r.json(), indent=2))

### ----------------------------------------------------------------------------------------------------------------------------- ###

# get real agency IDs
r = requests.post(
    "https://api.usaspending.gov/api/v2/bulk_download/list_agencies/",
    json={"type": "award_agencies"},
    timeout=30
)
print(r.status_code)
agencies = r.json()

cfo = agencies["agencies"]["cfo_agencies"]
doe = next(a for a in cfo if "Energy" in a["name"])     # next() pulls first item out of iterator, then raises StopIteration
dod = next(a for a in cfo if "Defense" in a["name"])
print("DOE:", doe)                                      # {'name': 'Department of Energy', 'toptier_agency_id': 78, 'toptier_code': '089'}
print("DoD:", dod)                                      # 097

# see DOE's break down by sub-agency (how much is NNSA). This component mirros block 1, but we use and verify with the official agency ID here.
r1 = requests.get(f"https://api.usaspending.gov/api/v2/agency/{doe['toptier_code']}/sub_agency/", timeout=30)
print(r1.status_code)
print(json.dumps(r1.json(), indent=2))

# check if DOE has pre-generated files and if we can filter by office
# we cannot, as we infer (and confirmed separately in a temp file) from the api response structure that it only takes the fields agency_*, fiscal_year, and type, and does not allow for filtering by awarding_office-* (NNSA)
# given that, we will need to use /api/v2/download/* instead of /api/v2/bulk_download/* for DOE data
r2 = requests.post(
    "https://api.usaspending.gov/api/v2/bulk_download/list_monthly_files/",
    json={"agency": doe["toptier_agency_id"], "fiscal_year": 2024, "type": "contracts"},
    timeout=30
)
print(r2.status_code)
print(json.dumps(r2.json(), indent=2))

### ----------------------------------------------------------------------------------------------------------------------------- ###

# figuring out DOE office codes

payload = {
    "filters": {
        "agencies": [{"type": "awarding", "tier": "toptier", "name": "Department of Energy"}],
        "time_period": [{"start_date": "2024-01-01", "end_date": "2024-01-31"}],
    },
    "spending_level": ["transactions"],
    "columns": []  # empty = all columns
}

r3 = requests.post("https://api.usaspending.gov/api/v2/download/search/", json=payload, timeout=30)
result = r3.json()
# print(r.status_code)
print(json.dumps(result, indent=2))

status_url = result["status_url"]

# we poll status_url to know when the background generation job completes so that we can download our file_url.
while True:
    r4 = requests.get(status_url, timeout=30)
    data = r4.json()
    if data.get("status") in ("finished", "failed"):
        break
    time.sleep(5)

# grab the generated zip
# note: the status response (data) also contains file_url, and it matches result["file_url"]
r5 = requests.get(data["file_url"], timeout=60)
with open("doe_test.zip", "wb") as f:   # wb (write binary)
    f.write(r5.content)                 # save those bytes to disk

# open zip without manual extraction
with zipfile.ZipFile("doe_test.zip") as z:
    print(z.namelist())                 # what files are inside (should be one csv, so confirming the name)
    csv_name = z.namelist()[0]          # grab the file
    with z.open(csv_name) as f:         # open csv in memory
        df = pd.read_csv(f)

for i, col in enumerate(df.columns):
    print(i, col)

print(df["awarding_sub_agency_name"].unique())
print(df["awarding_office_name"].nunique())
for name in sorted(df["awarding_office_name"].unique()):
    print(name)

office_map = df[["awarding_office_code", "awarding_office_name"]].drop_duplicates().sort_values("awarding_office_name")
print(office_map.to_string(index=False))

DOE_DEFENSE_OFFICE_CODES = [
    "892332", "892330", "892331",                                   # NNSA
    "893033", "893035", "893031", "893042", "893034", "893032",     # EM
    "893039",                                                       # Hanford Field Office
    "893040",                                                       # Office of River Protection
]

filtered = df[df["awarding_office_code"].isin(DOE_DEFENSE_OFFICE_CODES)]