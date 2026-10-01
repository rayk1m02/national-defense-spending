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

# check DHS bulk data (toptier_agency_id 63, toptier_code 070)
dhs_bulk_monthly = requests.post(
    "https://api.usaspending.gov/api/v2/bulk_download/list_monthly_files/",
    json={"agency": "63", "fiscal_year": 2024, "type": "contracts"},
    timeout=120
)
print(json.dumps(dhs_bulk_monthly.json(), indent=2))
'''
{
  "monthly_files": [
    {
      "fiscal_year": 2024,
      "agency_name": "Department of Homeland Security",
      "agency_acronym": "DHS",
      "type": "contracts",
      "updated_date": "2026-09-06",
      "file_name": "FY2024_070_Contracts_Full_20260906.zip",
      "url": "https://files.usaspending.gov/award_data_archive/FY2024_070_Contracts_Full_20260906.zip"
    }
  ]
}
'''

# unzip and open generated DHS bulk full data
dhs_full_r = requests.get(dhs_bulk_monthly.json()["monthly_files"][0]["url"], timeout=120)
with open("../bulk_data_samples/zip_dhs_bulk_full.zip", "wb") as f:
    f.write(dhs_full_r.content)

with zipfile.ZipFile("../bulk_data_samples/zip_dhs_bulk_full.zip") as z:
    csv_names = [n for n in z.namelist() if n.endswith(".csv")]                                             # grab every csv file
    df_dhs = pd.concat((pd.read_csv(z.open(n), low_memory=False) for n in csv_names), ignore_index=True)    # concatenate into one dataframe
print(len(df_dhs.columns)) # 297

def funded_by(value, target_accounts):
    if pd.isna(value):
        return False
    tokens = [t.strip() for t in value.split(";")]     # tokens will be a clean list of federal accounts
    return any(t in target_accounts for t in tokens)   # any() - eg. an award funded by three accounts, only one of which is CISA, will still count  

# boolean masking - keep only rows where we have a DHS-CISA federal account as a value
dhs_filtered = df_dhs[df_dhs["federal_accounts_funding_this_award"].apply(lambda v: funded_by(v, DHS_CISA_ACCOUNTS))]
print(len(dhs_filtered)) # 86 (transactions)
print(dhs_filtered[["awarding_agency_name", "funding_agency_name", "federal_action_obligation", "federal_accounts_funding_this_award",]].head())
'''
                 awarding_agency_name              funding_agency_name  federal_action_obligation federal_accounts_funding_this_award
30    Department of Homeland Security  Department of Homeland Security                  653992.11                   070-0412;070-0566
143   Department of Homeland Security  Department of Homeland Security                       0.00                   070-0412;070-0566
1214  Department of Homeland Security  Department of Homeland Security                 6789567.84                   070-0412;070-0566
1968  Department of Homeland Security  Department of Homeland Security                 8501011.13                   070-0412;070-0566
2030  Department of Homeland Security  Department of Homeland Security                 6324000.11                   070-0412;070-0566
'''
print(dhs_filtered["federal_action_obligation"].sum()) # 153241262.32 (~153M)
print(dhs_filtered.groupby(["awarding_agency_name", "funding_agency_name"]).size()) # within DHS bulk file, every CISA contract is funded by DHS
'''
awarding_agency_name             funding_agency_name            
Department of Homeland Security  Department of Homeland Security    86
dtype: int64
'''

# verifying the broader claim that no other agency awarded a CISA-funded contract in FY2024. 
# we used the /download/search API to confirm and it returned identical results.
# this method took ~6 minutes to generate the file, so we will use the bulk file API for our project extraction. 
# code kept for documentation purposes.
'''
payload = {
    "filters": {
        "agencies": [{"type": "funding", "tier": "toptier", "name": "Department of Homeland Security"}],
        "award_type_codes": ["A", "B", "C", "D", "IDV_A", "IDV_B", "IDV_B_A", "IDV_B_B", "IDV_B_C", "IDV_C", "IDV_D", "IDV_E"],
        "time_period": [{"start_date": "2023-10-01", "end_date": "2024-09-30"}]
    },
    "spending_level": ["transactions"],
    "columns": []
}

r3 = requests.post("https://api.usaspending.gov/api/v2/download/search/", json=payload, timeout=30)
result = r3.json()
print(json.dumps(result, indent=2))

while True:
    r4 = requests.get(result["status_url"], timeout=30)
    data = r4.json()
    if data.get("status") in ("finished", "failed"):
        break
    time.sleep(5)
print(json.dumps(data, indent=2))

r5 = requests.get(data["file_url"], timeout=600)
with open("../bulk_data_samples/zip_dhs_download.zip", "wb") as f:
    f.write(r5.content)

with zipfile.ZipFile("../bulk_data_samples/zip_dhs_download.zip") as z:
    csv_names = [n for n in z.namelist() if n.endswith(".csv")]
    df = pd.concat((pd.read_csv(z.open(n), low_memory=False) for n in csv_names), ignore_index=True)

print(len(df)) # 62753

df_filtered = df[df["federal_accounts_funding_this_award"].apply(lambda v: funded_by(v, DHS_CISA_ACCOUNTS))]

print(len(df_filtered)) # 86
print(df_filtered["federal_action_obligation"].sum()) # 153241262.32
print(df_filtered.groupby(["awarding_agency_name", "funding_agency_name"]).size())
'''
'''
awarding_agency_name             funding_agency_name            
Department of Homeland Security  Department of Homeland Security    86
dtype: int64
'''
'''
	                    Bulk file (awarding = DHS)	    Custom download (funding = DHS)
DHS-CISA Rows	                86	                            86
Obligations	                    $153,241,262.32	                $153,241,262.32

* our DOT script verifies that bulk_downloads agency parameter is filetered by awarding agency.

The /download/search API caught every contract funded by DHS, no matter who awarded it, and it found the same 86 rows. 
So no other agency awarded CISA-funded contracts in FY2024.
These are contract totals, meaning the remaining $357M gap is non-contract related spend.
'''