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
print(json.dumps(agencies, indent=2))
'''
{
  "agencies": {
        "cfo_agencies": [                           # agencies under the Chief Financial Officers Act of 1990
        {
            "name": "Department of Commerce",
            "toptier_agency_id": 15,                # USASpend internal surrogate key
            "toptier_code": "013"                   # stable identifier
        },
        {
            "name": "Department of Defense",
            "toptier_agency_id": 126,             
            "toptier_code": "097"                 
        }, ...
        ],
        "other_agencies": [                         # agencies not on CFO Act list (smaller independent boards, commissions, offices)
        {
            "name": "Access Board",
            "toptier_agency_id": 102,
            "toptier_code": "310"
        },
        {
            "name": "Administrative Conference of the U.S.",
            "toptier_agency_id": 92,
            "toptier_code": "302"
        }, ...
        ]
    },
    "sub_agencies": []                              # only populates when specific agency is requested in api parameter
}
'''

# find DOD's toptier_code
cfo = agencies["agencies"]["cfo_agencies"]
dod = next(a for a in cfo if "Department of Defense" in a["name"])
print("DoD:", dod)  
'''
DoD: {'name': 'Department of Defense', 'toptier_agency_id': 126, 'toptier_code': '097'}
'''

# list DOD sub-agencies and offices
r1 = requests.get(f"https://api.usaspending.gov/api/v2/agency/{dod['toptier_code']}/sub_agency/", timeout=30)
with open("../bulk_data_samples/json_dod_sub_agencies.json", "w", encoding="utf-8") as f:
    json.dump(r1.json(), f, indent=2)
'''
{
    "toptier_code": "097",
    "fiscal_year": 2026,
    "page_metadata": {
    "page": 1,
    "total": 25, ...
    },
    "results": [
        {
            "abbreviation": "USN",
            "name": "Department of the Navy",               # sub-agency
            "total_obligations": 112994602496.94,
            "transaction_count": 129736,
            "new_award_count": 36678,
            "children": [                                   # offices
                {
                    "code": "N00024",
                    "name": "NAVSEA HQ",
                    "total_obligations": 37199529170.29,
                    "transaction_count": 4204,
                    "new_award_count": 935
                }, ...
            ]
        },
        {
            "abbreviation": "USA",
            "name": "Department of the Army",
            "total_obligations": 82167103841.97,
            "transaction_count": 95436,
            "new_award_count": 24934,
            "children": [ ...
            ]
        }, ...
    ],
    "messages": []
}
'''

# check DOD bulk data
r2 = requests.post(
    "https://api.usaspending.gov/api/v2/bulk_download/list_monthly_files/",
    json={"agency": dod["toptier_agency_id"], "fiscal_year": 2024, "type": "contracts"},
    timeout=30
)
print(json.dumps(r2.json(), indent=2))
'''
{
  "monthly_files": [
    {
      "fiscal_year": 2024,
      "agency_name": "Department of Defense",
      "agency_acronym": "DOD",
      "type": "contracts",
      "updated_date": "2026-09-06",
      "file_name": "FY2024_097_Contracts_Full_20260906.zip",
      "url": "https://files.usaspending.gov/award_data_archive/FY2024_097_Contracts_Full_20260906.zip"
    },
    {
      "fiscal_year": null,
      "agency_name": "Department of Defense",
      "agency_acronym": "DOD",
      "type": "contracts",
      "updated_date": "2026-09-06",
      "file_name": "FY(All)_097_Contracts_Delta_20260906.zip",
      "url": "https://files.usaspending.gov/award_data_archive/FY(All)_097_Contracts_Delta_20260906.zip"
    }
  ]
}
'''

# unzip and open generated DOD bulk full data
r3 = requests.get(r2.json()["monthly_files"][0]["url"], timeout=120)
with open("../bulk_data_samples/zip_dod_bulk_full.zip", "wb") as f:
    f.write(r3.content)

with zipfile.ZipFile("../bulk_data_samples/zip_dod_bulk_full.zip") as z:
    csv_name = [n for n in z.namelist() if n.endswith(".csv")][0]
    with z.open(csv_name) as f:
        df = pd.read_csv(f, nrows=5)

print(len(df.columns)) # 297
pd.Series(df.columns, name="column").to_csv("../bulk_data_samples/csv_dod_bulk_full_columns.csv", index=False)
'''
contract_transaction_unique_key
contract_award_unique_key
award_id_piid
modification_number
transaction_number
parent_award_agency_id
parent_award_agency_name
...
highly_compensated_officer_5_amount
usaspending_permalink
initial_report_date
last_modified_date
'''