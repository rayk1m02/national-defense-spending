import requests, json, time
import pandas as pd
import zipfile

# DHS and DOT federal accounts under DRA

### ----------------------------------------------------------------------------------------------------------------------------- ###

# * account_number field from api/v2/spending/ with budget_subfunction 054 and agency_id, matches our federal_accounts_funding_this_award column values
DHS_CISA_ACCOUNTS = {"070-0412", "070-0805", "070-0565", "070-1911"}


# zip process for DHS (toptier_agency_id 63, toptier_code 070)
    # find file url
dhs_bulk_monthly = requests.post(
    "https://api.usaspending.gov/api/v2/bulk_download/list_monthly_files/",
    json={"agency": "63", "fiscal_year": 2024, "type": "contracts"},
    timeout=120
)
# print(json.dumps(dhs_bulk_monthly.json(), indent=2))


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


# unzip and open generated file url for full data
dhs_full_r = requests.get(dhs_bulk_monthly.json()["monthly_files"][0]["url"], timeout=120)
with open("dhs_full.zip", "wb") as f:
    f.write(dhs_full_r.content)

with zipfile.ZipFile("dhs_full.zip") as z:
    csv_names = [n for n in z.namelist() if n.endswith(".csv")]
    # print(csv_names) # ['FY2024_070_Contracts_Full_20260909_1.csv']
    df_dhs = pd.concat((pd.read_csv(z.open(n), low_memory=False) for n in csv_names), ignore_index=True)

print('DHS col len: ', len(df_dhs.columns))


def funded_by(value, target_accounts):
    if pd.isna(value):
        return False
    tokens = [t.strip() for t in value.split(";")]
    return any(t in target_accounts for t in tokens)

dhs_filtered = df_dhs[df_dhs["federal_accounts_funding_this_award"].apply(lambda v: funded_by(v, DHS_CISA_ACCOUNTS))]
print('DHS-CISA accounts funding len: ', len(dhs_filtered))

'''
297 - same schema as DOD
86 - CISA account real transaction count
'''

print('DHS federal action obligation sum: ', dhs_filtered["federal_action_obligation"].sum())
print('DHS group by awarding agency, funding agency size: ', dhs_filtered.groupby(["awarding_agency_name", "funding_agency_name"]).size())


### ----------------------------------------------------------------------------------------------------------------------------- ###

# /download/search/ filtered by funding agency instead of awarding agency to see if some CISA-funded contracts are awarded by other agencies
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

status_url = result["status_url"]

while True:
    r4 = requests.get(status_url, timeout=30)
    data = r4.json()
    if data.get("status") in ("finished", "failed"):
        break
    time.sleep(5)

print(json.dumps(data, indent=2))
if data.get("status") != "finished":
    raise SystemExit("Download job did not finish, stopping.")

print(data.get("status"), data.get("message"))

r5 = requests.get(data["file_url"], timeout=600)
with open("dhs_funding_test.zip", "wb") as f:
    f.write(r5.content)

with zipfile.ZipFile("dhs_funding_test.zip") as z:
    csv_names = [n for n in z.namelist() if n.endswith(".csv")]
    print(csv_names)
    df = pd.concat((pd.read_csv(z.open(n), low_memory=False) for n in csv_names), ignore_index=True)

print(len(df))

filtered = df[df["federal_accounts_funding_this_award"].apply(lambda v: funded_by(v, DHS_CISA_ACCOUNTS))]
print(len(filtered))
print(filtered["federal_action_obligation"].sum())
print(filtered.groupby(["awarding_agency_name", "funding_agency_name"]).size())

'''
{
  "status_url": "https://api.usaspending.gov/api/v2/download/status?file_name=PrimeAwardsTransactionsAndSubawards_2026-09-26_H01M47S25022891.zip",
  "file_name": "PrimeAwardsTransactionsAndSubawards_2026-09-26_H01M47S25022891.zip",
  "file_url": "https://files.usaspending.gov/generated_downloads/PrimeAwardsTransactionsAndSubawards_2026-09-26_H01M47S25022891.zip",
  "download_request": {
    ...
}
{
  "status": "finished",
  "message": null,
  "file_name": "PrimeAwardsTransactionsAndSubawards_2026-09-26_H01M47S25022891.zip",
  "file_url": "https://files.usaspending.gov/generated_downloads/PrimeAwardsTransactionsAndSubawards_2026-09-26_H01M47S25022891.zip",
  "total_size": 12560.625,
  "total_columns": 297,
  "total_rows": 62751,
  "seconds_elapsed": "377.651112"
}

finished None
['Contracts_PrimeTransactions_2026-09-26_H01M47S35_1.csv']
62751
86
153241262.32
awarding_agency_name             funding_agency_name            
Department of Homeland Security  Department of Homeland Security    86
dtype: int64

	                    Bulk file (awarding = DHS)	    Custom download (funding = DHS)
CISA-account rows	                86	                            86
Obligations	                    $153,241,262.32	                $153,241,262.32

The custom download caught every contract funded by DHS, no matter who awarded it, and it found the same 86 rows. 
So no other agency awarded CISA-funded contracts in FY2024, and the bulk file isn't missing anything. 
That also answers the $357M gap: it's CISA account spending that isn't contracts, not contracts hiding in another agency's file.

Conclusion for DHS-CISA: bulk files work. And they're much faster: the custom download took about 6 minutes to generate, while the bulk file was already sitting there.
'''

### ----------------------------------------------------------------------------------------------------------------------------- ###

DOT_MARAD_ACCOUNTS = {"069-1710", "069-1711", "069-1718", "069-1717"}

# 'toptier_agency_id': 62, 'toptier_code': '069'
dot_bulk_monthly = requests.post(
    "https://api.usaspending.gov/api/v2/bulk_download/list_monthly_files/",
    json={"agency": "62", "fiscal_year": 2024, "type": "contracts"},
    timeout=120
)
print(json.dumps(dot_bulk_monthly.json(), indent=2))

dot_full_r = requests.get(dot_bulk_monthly.json()["monthly_files"][0]["url"], timeout=600)
with open("dot_full.zip", "wb") as f:
    f.write(dot_full_r.content)

with zipfile.ZipFile("dot_full.zip") as z:
    csv_names = [n for n in z.namelist() if n.endswith(".csv")]
    print(csv_names)
    df_dot = pd.concat((pd.read_csv(z.open(n), low_memory=False) for n in csv_names), ignore_index=True)

print(len(df_dot.columns))

dot_filtered = df_dot[df_dot["federal_accounts_funding_this_award"].apply(lambda v: funded_by(v, DOT_MARAD_ACCOUNTS))]
print(len(dot_filtered))
print(dot_filtered["federal_action_obligation"].sum())
print(dot_filtered.groupby(["awarding_agency_name", "funding_agency_name"]).size())

for acct in sorted(DOT_MARAD_ACCOUNTS):
    rows = dot_filtered[dot_filtered["federal_accounts_funding_this_award"].apply(lambda v: funded_by(v, {acct}))]
    print(acct, len(rows), rows["federal_action_obligation"].sum())

### ----------------------------------------------------------------------------------------------------------------------------- ###

with zipfile.ZipFile("dot_full.zip") as z:
    csv_names = [n for n in z.namelist() if n.endswith(".csv")]
    df_dot_check = pd.concat(
        (pd.read_csv(z.open(n), usecols=["awarding_agency_name", "funding_agency_name"]) for n in csv_names),
        ignore_index=True
    )

print(df_dot_check["awarding_agency_name"].value_counts())
print(df_dot_check["funding_agency_name"].value_counts())

'''
(venv) PS C:\Users\rkim\Desktop\Learning\national-defense-spending\endpoint_mapping> python tmp.py
awarding_agency_name
Department of Transportation    33688
Name: count, dtype: int64
funding_agency_name
Department of Transportation    31301
Department of Defense            2311
Surface Transportation Board       76
Name: count, dtype: int64
(venv) PS C:\Users\rkim\Desktop\Learning\national-defense-spending\endpoint_mapping>
'''