import requests, json
import pandas as pd
import zipfile

# list all the agencies, find DHS toptier_code
r1 = requests.post("https://api.usaspending.gov/api/v2/bulk_download/list_agencies/", json={"type": "award_agencies"}, timeout=120)
dhs = next(a for a in r1.json()["agencies"]["cfo_agencies"] if "Homeland Security" in a["name"])
print(dhs) 
# {'name': 'Department of Homeland Security', 'toptier_agency_id': 63, 'toptier_code': '070'}

# list DHS sub-agencies and offices
r2 = requests.get(f"https://api.usaspending.gov/api/v2/agency/{dhs['toptier_code']}/sub_agency/", timeout=30)
# create json file
with open("../bulk_data_samples/json_dhs_sub_agencies.json", "w", encoding="utf-8") as f:
    json.dump(r2.json(), f, indent=2)
# list the sub-agency names
for sub in r2.json()["results"]:
    print(sub["name"])
'''
Federal Emergency Management Agency
U.S. Customs and Border Protection
Office of Procurement Operations
U.S. Coast Guard
U.S. Immigration and Customs Enforcement
Transportation Security Administration
U.S. Citizenship and Immigration Services
U.S. Secret Service
Federal Law Enforcement Training Center
Countering Weapons of Mass Destruction
'''

# since the sub-agency list does not include DHS-CISA (which is a federal account), we will use dod_bulk_full.zip as a means to check if there is a federal account column for us to filter by for DHS-CISA values
with zipfile.ZipFile(r"C:\Users\rkim\Desktop\Learning\national-defense-spending\bulk_data_samples\zip_dod_bulk_full.zip") as z:
    with z.open(z.namelist()[0]) as f:
        df = pd.read_csv(f, nrows=5)
matches = [c for c in df.columns if "treasury" in c.lower() or "federal_account" in c.lower()]
print(matches)
'''
['treasury_accounts_funding_this_award', 'federal_accounts_funding_this_award']
'''

# find the format those values come in
with zipfile.ZipFile(r"C:\Users\rkim\Desktop\Learning\national-defense-spending\bulk_data_samples\zip_dod_bulk_full.zip") as z:
    with z.open(z.namelist()[0]) as f:
        df = pd.read_csv(f, usecols=["treasury_accounts_funding_this_award", "federal_accounts_funding_this_award"], nrows=20)
for val in df["treasury_accounts_funding_this_award"].dropna().unique()[:10]:
    print(repr(val))
'''
'021-2024/2024-2020-000'
'057-2022/2022-3400-000;057-2023/2023-3400-000;057-2024/2024-3400-000;057-2025/2025-3400-000;057-2026/2026-3400-000;097-2022/2022-0130-000;097-2023/2023-0130-000'
'''
for val in df["federal_accounts_funding_this_award"].dropna().unique()[:10]:
    print(repr(val))
'''
'021-2020'
'057-3400;097-0130'
'''
# terms
    # agency_code:          federal agency (DOD: 097, DHS: 070, DOJ: 015, ...)
    # main_account_code:    federal account under an agency (Procurement, Construction, and..: 0412, Ready Reserve Force, Maritime...: 1710)
    # sub_account_code:     further subdivision within a federal account (so far every example has shown 000, general fund)
# column treasury_accounts_funding_this_award holds <agency_code>-<period of availability>-<main_account_code>-<sub_account_code>
# column federal_accounts_funding_this_award holds just the <agency_code>-<main_account_code>

# now list the federal accounts under DHS
# 766 is from dra_scope.py. The bulk_download/list_agencies api agency_id and toptier_code fields are specific to that api and not interchangable with the v2/spending/ api
agency_id = "766"
r = requests.post(
    "https://api.usaspending.gov/api/v2/spending/",
    json={
        "type": "federal_account",
        "filters": {"fy": "2024", "quarter": 4, "budget_subfunction": "054", "agency": agency_id} 
    },
    timeout=30
)
print(json.dumps(r.json(), indent=2))
'''
{
  "total": 656218040.04,
  "end_date": "2024-09-30T00:00:00Z",
  "results": [
    {
      "id": "5185",
      "code": "0412",
      "type": "federal_account",
      "name": "Procurement, Construction, and Improvements, Cybersecurity and Infrastructure Security Agency, Homeland Security",
      "amount": 506501490.81,
      "account_number": "070-0412"
    },
    {
      "id": "5184",
      "code": "0411",
      "type": "federal_account",
      "name": "Federal Assistance, Countering Weapons of Mass Destruction Office, Homeland Security",
      "amount": 146403866.15,
      "account_number": "070-0411"
    },
    {
      "id": "5254",
      "code": "0805",
      "type": "federal_account",
      "name": "Research and Development, Cybersecurity and Infrastructure Security Agency, Homeland Security",
      "amount": 3312683.08,
      "account_number": "070-0805"
    },
    {
      "id": "5222",
      "code": "0565",
      "type": "federal_account",
      "name": "Infrastructure Protection and Information Security, Cybersecurity and Infrastructure Security Agency, Homeland Security",
      "amount": 0.0,
      "account_number": "070-0565"
    },
    {
      "id": "6453",
      "code": "1911",
      "type": "federal_account",
      "name": "Cybersecurity Response and Recovery Fund, Cybersecurity and Infrastructure Security Agency, Homeland Security.",
      "amount": 0.0,
      "account_number": "070-1911"
    }
  ]
}
'''

# account_number field here mirrors the federal_accounts_funding_this_award column values from api/v2/bulk_download
DHS_CISA_ACCOUNTS = {"070-0412", "070-0805", "070-0565", "070-1911"}