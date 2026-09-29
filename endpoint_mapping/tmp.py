import requests, time
import json, zipfile
import pandas as pd

# list all the agencies
r = requests.post(
    "https://api.usaspending.gov/api/v2/bulk_download/list_agencies/",
    json={"type": "award_agencies"},
    timeout=30
)
agencies = r.json()


# find DOE's toptier_code
cfo = agencies["agencies"]["cfo_agencies"]
doe = next(a for a in cfo if "Department of Energy" in a["name"])


# check DOE bulk data
r2 = requests.post(
    "https://api.usaspending.gov/api/v2/bulk_download/list_monthly_files/",
    json={"agency": doe["toptier_agency_id"], "fiscal_year": 2024, "type": "contracts"},
    timeout=30
)


r3 = requests.get("https://files.usaspending.gov/award_data_archive/FY2024_089_Contracts_Full_20260906.zip", timeout=120)
with open("../bulk_data_samples/doe_bulk_full.zip", "wb") as f:
    f.write(r3.content)

with zipfile.ZipFile("../bulk_data_samples/doe_bulk_full.zip") as z:
    csv_name = [n for n in z.namelist() if n.endswith(".csv")][0]
    with z.open(csv_name) as f:
        df = pd.read_csv(f, nrows=5)

# print(len(df.columns))
# print(df.columns.tolist())

pd.Series(df.columns, name="column").to_csv("../bulk_data_samples/doe_bulk_full_columns.csv", index=False)