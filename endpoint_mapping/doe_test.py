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

# find DOE's toptier_code
cfo = agencies["agencies"]["cfo_agencies"]
doe = next(a for a in cfo if "Department of Energy" in a["name"])
print("DoE:", doe)  
'''
DoE: {'name': 'Department of Energy', 'toptier_agency_id': 78, 'toptier_code': '089'}
'''

# list DOE sub-agencies and offices
r1 = requests.get(f"https://api.usaspending.gov/api/v2/agency/{doe['toptier_code']}/sub_agency/", timeout=30)
with open("../bulk_data_samples/json_doe_sub_agencies.json", "w", encoding="utf-8") as f:
    json.dump(r1.json(), f, indent=2)
'''
{
    "toptier_code": "089",
    "fiscal_year": 2026,
    "page_metadata": {
    ...
    "hasPrevious": false
    },
    "results": [
        {
            "abbreviation": "DOE",
            "name": "Department of Energy",
            "total_obligations": 58274713926.8,
            "transaction_count": 20350,
            "new_award_count": 2425,
            "children": [
                {
                "code": "892332",
                "name": "NNSA MO CONTRACTING",
                "total_obligations": 25632313666.86,
                "transaction_count": 281,
                "new_award_count": 0
                },
                {
                "code": "892432",
                "name": "IDAHO OPERATIONS OFFICE",
                "total_obligations": 5840548305.36,
                "transaction_count": 525,
                "new_award_count": 130
                },
                ..
            ]
        },
        {
            "abbreviation": "FERC",
            "name": "Federal Energy Regulatory Commission",
            "total_obligations": 158560780.76,
            "transaction_count": 483,
            "new_award_count": 86,
            "children": [
                {
                "code": "896030",
                "name": "FEDERAL ENERGY REGULATORY COMM",
                "total_obligations": 158560780.76,
                "transaction_count": 483,
                "new_award_count": 86
                }
            ]
        }
    ],
    "messages": []
}
'''

# check DOE bulk data
r2 = requests.post(
    "https://api.usaspending.gov/api/v2/bulk_download/list_monthly_files/",
    json={"agency": doe["toptier_agency_id"], "fiscal_year": 2024, "type": "contracts"},
    timeout=30
)
print(json.dumps(r2.json(), indent=2))
'''
{
  "monthly_files": [
    {
      "fiscal_year": 2024,
      "agency_name": "Department of Energy",
      "agency_acronym": "DOE",
      "type": "contracts",
      "updated_date": "2026-09-06",
      "file_name": "FY2024_089_Contracts_Full_20260906.zip",
      "url": "https://files.usaspending.gov/award_data_archive/FY2024_089_Contracts_Full_20260906.zip"
    },
    {
      "fiscal_year": null,
      "agency_name": "Department of Energy",
      "agency_acronym": "DOE",
      "type": "contracts",
      "updated_date": "2026-09-06",
      "file_name": "FY(All)_089_Contracts_Delta_20260906.zip",
      "url": "https://files.usaspending.gov/award_data_archive/FY(All)_089_Contracts_Delta_20260906.zip"
    }
  ]
}
'''

# unzip and open generated DOE bulk full data
r3 = requests.get("https://files.usaspending.gov/award_data_archive/FY2024_089_Contracts_Full_20260906.zip", timeout=120)
with open("../bulk_data_samples/zip_doe_bulk_full.zip", "wb") as f:
    f.write(r3.content)

with zipfile.ZipFile("../bulk_data_samples/zip_doe_bulk_full.zip") as z:
    csv_name = [n for n in z.namelist() if n.endswith(".csv")][0]
    with z.open(csv_name) as f:
        df = pd.read_csv(f, nrows=5)

print(len(df.columns)) #297
pd.Series(df.columns, name="column").to_csv("../bulk_data_samples/csv_doe_bulk_full_columns.csv", index=False)
'''
contract_transaction_unique_key
contract_award_unique_key
award_id_piid
modification_number
transaction_number
parent_award_agency_id
parent_award_agency_name
parent_award_id_piid
parent_award_modification_number
federal_action_obligation
total_dollars_obligated
...

'''