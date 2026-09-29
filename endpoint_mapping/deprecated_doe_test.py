import requests, time
import json, zipfile
import pandas as pd

# get agency ID
r = requests.post(
    "https://api.usaspending.gov/api/v2/bulk_download/list_agencies/",
    json={"type": "award_agencies"},
    timeout=30
)
print(r.status_code)
agencies = r.json()

cfo = agencies["agencies"]["cfo_agencies"]
doe = next(a for a in cfo if "Energy" in a["name"])     # next() pulls next item out of itereator. If no default is set, raises StopIteration exception
print("DOE:", doe)                                      # {'name': 'Department of Energy', 'toptier_agency_id': 78, 'toptier_code': '089'}

# see DOE's break down by sub-agency (how much is NNSA).
r1 = requests.get(f"https://api.usaspending.gov/api/v2/agency/{doe['toptier_code']}/sub_agency/", timeout=30)
print(r1.status_code)
print(json.dumps(r1.json(), indent=2))

# check if DOE has pre-generated files and if we can filter by office
r2 = requests.post(
    "https://api.usaspending.gov/api/v2/bulk_download/list_monthly_files/",
    json={"agency": doe["toptier_agency_id"], "fiscal_year": 2024, "type": "contracts"},
    timeout=30
)
print(r2.status_code)
print(json.dumps(r2.json(), indent=2))

# api response structure only takes the fields agency_*, fiscal_year, and type, and does not allow for filtering by awarding_office-* (NNSA)
# given that, we will need to use /api/v2/download/* instead of /api/v2/bulk_download/* for DOE data
# REVIST: this finding was incorrect, and we can in fact use /api/v2/bulk_download/*. But see below the /api/v2/download/* extraction path used to obtain the same results

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
'''
{
  "status_url": "https://api.usaspending.gov/api/v2/download/status?file_name=PrimeAwardsTransactionsAndSubawards_2026-09-29_H04M23S33732497.zip",
  "file_name": "PrimeAwardsTransactionsAndSubawards_2026-09-29_H04M23S33732497.zip",
  "file_url": "https://files.usaspending.gov/generated_downloads/PrimeAwardsTransactionsAndSubawards_2026-09-29_H04M23S33732497.zip",
  "download_request": {
    "download_types": [
      "elasticsearch_transactions"
    ],
    "file_format": "csv",
    "filters": {
      "agencies": [
        {
          "name": "Department of Energy",
          "tier": "toptier",
          "type": "awarding"
        }
      ],
      "award_type_codes": [
        "-1",
        "02",
        "03",
'''

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
with open("../bulk_data_samples/zip_doe_download.zip", "wb") as f:      # wb (write binary)
    f.write(r5.content)                                                 # save those bytes to disk

# open zip without manual extraction
with zipfile.ZipFile("../bulk_data_samples/zip_doe_download.zip") as z:
    print(z.namelist())                                                     # what files are inside
    # ['Contracts_PrimeTransactions_2026-09-29_H04M23S36_1.csv', 'Assistance_PrimeTransactions_2026-09-29_H04M24S33_1.csv']
    csv_name = z.namelist()[0]                                              # grab the file
    with z.open(csv_name) as f:                                             # open csv in memory
        df = pd.read_csv(f)

for i, col in enumerate(df.columns):
    print(i, col)

print(df["awarding_sub_agency_name"].unique())
'''
<StringArray>
['Department of Energy', 'Federal Energy Regulatory Commission']
Length: 2, dtype: str
'''

office_map = df[["awarding_office_code", "awarding_office_name"]].drop_duplicates().sort_values("awarding_office_name")
print(office_map.to_string(index=False))
'''
 awarding_office_code                         awarding_office_name
               897030            ADVANCED RSRCH PROJ AGENCY ARPA-E
               893032                                  EM-CARLSBAD
               893033            EM-ENVIRONMENTAL MGMT CON BUS CTR
               893042                                     EM-IDAHO
               893034                                EM-LOS ALAMOS
               893035                                 EM-OAK RIDGE
               893031            EM-PORTSMOUTH/PADUCAH PROJECT OFC
               896030               FEDERAL ENERGY REGULATORY COMM
               892434                          GOLDEN FIELD OFFICE
               893039                         HANFORD FIELD OFFICE
               893030            HEADQUARTERS PROCUREMENT SERVICES
               892432                      IDAHO OPERATIONS OFFICE
               892433        NATIONAL ENERGY TECHNOLOGY LABORATORY
               892332                          NNSA MO CONTRACTING
               892330           NNSA NAVAL REACTORS LAB FLD OFFICE
               892331                 NNSA NON-MO CNTRCTNG OPS DIV
               892436 OFFICE OF CLEAN ENERGY DEMONSTRATIONS (OCED)
               893040                   OFFICE OF RIVER PROTECTION
               893037             SAVANNAH RIVER OPERATIONS OFFICE
               892430                    SC CHICAGO SERVICE CENTER
               892431                          SC OAK RIDGE OFFICE
               895035            SOUTHEASTERN POWER ADMINISTRATION
               895036            SOUTHWESTERN POWER ADMINISTRATION
               892435                  STRATEGIC PETROLEUM RESERVE
               895030            WESTERN-CORPORATE SERVICES OFFICE
               895031              WESTERN-DESERT SOUTHWEST REGION
               895032                WESTERN-ROCKY MOUNTAIN REGION
               895033                 WESTERN-SIERRA NEVADA REGION
               895034            WESTERN-UPPER GREAT PLAINS REGION
'''

DOE_DEFENSE_OFFICE_CODES = [
    "892332", "892330", "892331",                                   # NNSA
    "893033", "893035", "893031", "893042", "893034", "893032",     # EM
    "893039",                                                       # Hanford Field Office
    "893040",                                                       # Office of River Protection
]

filtered = df[df["awarding_office_code"].isin(DOE_DEFENSE_OFFICE_CODES)]