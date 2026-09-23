import requests, time
import json, zipfile
import pandas as pd

# list agencies
r = requests.post(
    "https://api.usaspending.gov/api/v2/bulk_download/list_agencies/",
    json={"type": "award_agencies"},
    timeout=30
)
agencies = r.json()

# find DOD toptier_code
cfo = agencies["agencies"]["cfo_agencies"]
dod = next(a for a in cfo if "Defense" in a["name"])
print("DoD:", dod) # 097

# see DOD sub-agency breakdown
r1 = requests.get(f"https://api.usaspending.gov/api/v2/agency/{dod['toptier_code']}/sub_agency/", timeout=30)
# print(json.dumps(r1.json(), indent=2))

# check DOD pre-generated files
r2 = requests.post(
    "https://api.usaspending.gov/api/v2/bulk_download/list_monthly_files/",
    json={"agency": dod["toptier_agency_id"], "fiscal_year": 2024, "type": "contracts"},
    timeout=30
)
# print(json.dumps(r2.json(), indent=2))

# generated file url for full data
r3 = requests.get("https://files.usaspending.gov/award_data_archive/FY2024_097_Contracts_Full_20260906.zip", timeout=120)
with open("dod_test.zip", "wb") as f:
    f.write(r3.content)

with zipfile.ZipFile("dod_test.zip") as z:
    csv_name = [n for n in z.namelist() if n.endswith(".csv")][0]
    with z.open(csv_name) as f:
        df = pd.read_csv(f, nrows=5)

# check columns and see if it matches 297 columns like DOE
print(len(df.columns))
# print(df.columns.tolist())

