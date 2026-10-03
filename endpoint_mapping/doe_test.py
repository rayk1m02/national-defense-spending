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
r3 = requests.get(r2.json()["monthly_files"][0]["url"], timeout=120)
with open("../bulk_data_samples/zip_2024_doe_bulk_full.zip", "wb") as f:
    f.write(r3.content)

with zipfile.ZipFile("../bulk_data_samples/zip_2024_doe_bulk_full.zip") as z:
    csv_name = [n for n in z.namelist() if n.endswith(".csv")][0]
    with z.open(csv_name) as f:
       #  df = pd.read_csv(f, nrows=5)
        df = pd.read_csv(f, low_memory=False, dtype={"awarding_office_code": str}) # this column is int64, so converting it for our scope work

print(len(df.columns)) #297
pd.Series(df.columns, name="column").to_csv("../bulk_data_samples/csv_2024_doe_bulk_full_columns.csv", index=False)
'''
contract_transaction_unique_key
contract_award_unique_key
award_id_piid
...
awarding_office_code
awarding_office_name
...
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


# Other Scoping Work - similar to dra_scope.py, we are taking the filter by funding federal account route to check DOE

# list out the agencies under budget subfunction 053 and their spend
r4 = requests.post(
    "https://api.usaspending.gov/api/v2/spending/",
    json={"type": "agency", "filters": {"fy": "2024", "quarter": 4, "budget_subfunction": "053"}},
    timeout=120
)
print(json.dumps(r4.json(), indent=2))
'''
{
  "total": 41156563299.52,
  "end_date": "2024-09-30T00:00:00Z",
  "results": [
    {
      "id": "930",
      "code": "089",
      "type": "agency",
      "name": "Department of Energy",
      "amount": 37934827435.6,
      "link": true
    },
    {
      "id": "267",
      "code": "1601",
      "type": "agency",
      "name": "Department of Labor",
      "amount": 2865834796.95,
      "link": true
    },
    {
      "id": "1412",
      "code": "096",
      "type": "agency",
      "name": "Corps of Engineers - Civil Works",
      "amount": 311715936.11,
      "link": true
    },
    {
      "id": "1137",
      "code": "347",
      "type": "agency",
      "name": "Defense Nuclear Facilities Safety Board",
      "amount": 44185130.86,
      "link": true
    }
  ]
}
'''

# each agencies federal account and associated spend
for agency_id, agency_name in [("930", "DOE"), ("267", "DOL"), ("1412", "COE"), ("1137", "DNFSB"), ("1143", "PCLOB")]:
    r = requests.post(
        "https://api.usaspending.gov/api/v2/spending/",
        json={
            "type": "federal_account",
            "filters": {"fy": "2024", "quarter": 4, "budget_subfunction": "053", "agency": agency_id}
        },
        timeout=120
    )
    print(f"{agency_name}")
    for acnt in sorted(r.json()["results"], key=lambda x: x["amount"], reverse=True):       # returns new sorted list. sorted(iterable, key=use each agencies amount, descending)
        print(f"{acnt['name']:<120} {acnt['amount']:<20,.2f} {acnt['account_number']}")     # '<' left-align with minimum X characters
    print() 
'''
DOE
Weapons Activities, National Nuclear Security Administration, Energy                                                     23,637,473,396.00    089-0240
Defense Environmental Cleanup, Environmental and Other Defense Activities, Energy                                        7,634,560,443.26     089-0251
Defense Nuclear Nonproliferation, National Nuclear Security Administration, Energy                                       2,638,684,171.05     089-0309
Naval Reactors, National Nuclear Security Administration, Energy                                                         1,859,189,504.77     089-0314
Other Defense Activities, Environmental and Other Defense Activities, Energy                                             1,652,767,010.37     089-0243
Federal Salaries and Expenses, National Nuclear Security Administration, Energy                                          512,152,910.15       089-0313
Defense Nuclear Waste Disposal, Environmental and Other Defense Activities, Energy                                       0.00                 089-0244
Defense Environmental Services, Energy                                                                                   0.00                 089-0249

DOL
Energy Employees Occupational Illness Compensation Fund, Labor                                                           2,721,135,306.31     016-1523
Administrative Expenses, Energy Employees Occupational Illness Compensation Fund, Office of Workers' Compensation Programs, Labor 144,699,490.64       016-1524

COE
Formerly Utilized Sites Remedial Action Program, Corps of Engineers, Civil                                               311,715,936.11       096-3130

DNFSB
Salaries and Expenses, Defense Nuclear Facilities Safety Board                                                           44,185,130.86        347-3900

PCLOB
'''

DOE_053_ACCOUNTS = {"089-0240", "089-0251", "089-0309", "089-0314", "089-0243", "089-0313", "089-0244", "089-0249"}

def funded_by(value, target_accounts):
    if pd.isna(value):
        return False
    tokens = [t.strip() for t in value.split(";")]     # tokens will be a clean list of federal accounts
    return any(t in target_accounts for t in tokens)   # any() - eg. an award funded by three accounts, only one of which is in our target, will still count  

print(df["awarding_office_code"].dtype)                 # int64, so we convert it during pd.read_csv() up top
idaho = df[df["awarding_office_code"] == "892432"]      # from our bulk file up top

is_053 = idaho["federal_accounts_funding_this_award"].apply(lambda v: funded_by(v, DOE_053_ACCOUNTS))

print(idaho.groupby(is_053)["federal_action_obligation"].agg(["count", "sum"]))
'''
federal_accounts_funding_this_award    count           sum                 
False                                  121          1.009425e+08
True                                   102          1.873827e+09
'''
# looking at the above, ~1.87B are from 053 account (Idaho Operations' contract dollars)

def funded_only_by(value, target_accounts):
    if pd.isna(value):
        return False
    tokens = [t.strip() for t in value.split(";")]
    return all(t in target_accounts for t in tokens)


only_053 = idaho["federal_accounts_funding_this_award"].apply(lambda v: funded_only_by(v, DOE_053_ACCOUNTS))

print(idaho[only_053]["federal_action_obligation"].sum()) # 1472055.4500000002
print(idaho[is_053 & ~only_053]["federal_action_obligation"].sum()) # 1872355084.6299999

# look at the biggest mixed defense/non-defense funded rows
mixed = idaho[is_053 & ~only_053]
print(mixed.nlargest(10, "federal_action_obligation")[
    ["award_id_piid", "recipient_name", "federal_action_obligation", "federal_accounts_funding_this_award"]
].to_string(index=False))
'''
  award_id_piid                recipient_name  federal_action_obligation                                                                                                                                                                                              federal_accounts_funding_this_award
DEAC0705ID14517 BATTELLE ENERGY ALLIANCE, LLC               216929801.48 069-0548;089-0213;089-0216;089-0222;089-0228;089-0236;089-0240;089-0243;089-0251;089-0309;089-0313;089-0314;089-0315;089-0318;089-0319;089-0321;089-0337;089-0346;089-2250;089-2297;089-2301;089-2304;089-4180;089-4563;089-5227
DEAC0705ID14517 BATTELLE ENERGY ALLIANCE, LLC               157203668.97 069-0548;089-0213;089-0216;089-0222;089-0228;089-0236;089-0240;089-0243;089-0251;089-0309;089-0313;089-0314;089-0315;089-0318;089-0319;089-0321;089-0337;089-0346;089-2250;089-2297;089-2301;089-2304;089-4180;089-4563;089-5227
DEAC0705ID14517 BATTELLE ENERGY ALLIANCE, LLC               156936978.12 069-0548;089-0213;089-0216;089-0222;089-0228;089-0236;089-0240;089-0243;089-0251;089-0309;089-0313;089-0314;089-0315;089-0318;089-0319;089-0321;089-0337;089-0346;089-2250;089-2297;089-2301;089-2304;089-4180;089-4563;089-5227
DEAC0705ID14517 BATTELLE ENERGY ALLIANCE, LLC               154855834.45 069-0548;089-0213;089-0216;089-0222;089-0228;089-0236;089-0240;089-0243;089-0251;089-0309;089-0313;089-0314;089-0315;089-0318;089-0319;089-0321;089-0337;089-0346;089-2250;089-2297;089-2301;089-2304;089-4180;089-4563;089-5227
DEAC0705ID14517 BATTELLE ENERGY ALLIANCE, LLC               145412745.25 069-0548;089-0213;089-0216;089-0222;089-0228;089-0236;089-0240;089-0243;089-0251;089-0309;089-0313;089-0314;089-0315;089-0318;089-0319;089-0321;089-0337;089-0346;089-2250;089-2297;089-2301;089-2304;089-4180;089-4563;089-5227
DEAC0705ID14517 BATTELLE ENERGY ALLIANCE, LLC               143991160.76 069-0548;089-0213;089-0216;089-0222;089-0228;089-0236;089-0240;089-0243;089-0251;089-0309;089-0313;089-0314;089-0315;089-0318;089-0319;089-0321;089-0337;089-0346;089-2250;089-2297;089-2301;089-2304;089-4180;089-4563;089-5227
DEAC0705ID14517 BATTELLE ENERGY ALLIANCE, LLC               130541894.22 069-0548;089-0213;089-0216;089-0222;089-0228;089-0236;089-0240;089-0243;089-0251;089-0309;089-0313;089-0314;089-0315;089-0318;089-0319;089-0321;089-0337;089-0346;089-2250;089-2297;089-2301;089-2304;089-4180;089-4563;089-5227
DEAC0705ID14517 BATTELLE ENERGY ALLIANCE, LLC               123998156.39 069-0548;089-0213;089-0216;089-0222;089-0228;089-0236;089-0240;089-0243;089-0251;089-0309;089-0313;089-0314;089-0315;089-0318;089-0319;089-0321;089-0337;089-0346;089-2250;089-2297;089-2301;089-2304;089-4180;089-4563;089-5227
DEAC0705ID14517 BATTELLE ENERGY ALLIANCE, LLC               117662974.14 069-0548;089-0213;089-0216;089-0222;089-0228;089-0236;089-0240;089-0243;089-0251;089-0309;089-0313;089-0314;089-0315;089-0318;089-0319;089-0321;089-0337;089-0346;089-2250;089-2297;089-2301;089-2304;089-4180;089-4563;089-5227
DEAC0705ID14517 BATTELLE ENERGY ALLIANCE, LLC                77688517.94 069-0548;089-0213;089-0216;089-0222;089-0228;089-0236;089-0240;089-0243;089-0251;089-0309;089-0313;089-0314;089-0315;089-0318;089-0319;089-0321;089-0337;089-0346;089-2250;089-2297;089-2301;089-2304;089-4180;089-4563;089-5227
'''
# from above we see that the entire ~1.87B is one contract with Battelle Energy Alliance
# the data tells us an award touched defense money, but not how much much of a given payment was defense.

# funded_by() asks whether an award ever drew on one of the accounts, and then counts the whole transaction

# Ultimately, for Idaho Operations, we exclude it from our data as we encounter mixed funding with no way to split it.

# We will also exclude the offices of Department of Labor (Benefit payments/non-contracts), Defense Nuclear Facilities Safety Board (~$44M, immaterial like PCLOB), and Corps of Engineers (likely included in DOD files).
