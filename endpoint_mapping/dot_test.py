import requests, time
import json, zipfile
import pandas as pd

# list all the agencies, find DOT toptier_code
r1 = requests.post("https://api.usaspending.gov/api/v2/bulk_download/list_agencies/", json={"type": "award_agencies"}, timeout=120)
dot = next(a for a in r1.json()["agencies"]["cfo_agencies"] if "Transportation" in a["name"])
print(dot) 
# {'name': 'Department of Transportation', 'toptier_agency_id': 62, 'toptier_code': '069'}

# list DOT sub-agencies and offices
r2 = requests.get(f"https://api.usaspending.gov/api/v2/agency/{dot['toptier_code']}/sub_agency/", timeout=30)
# create json file
with open("../bulk_data_samples/json_dot_sub_agencies.json", "w", encoding="utf-8") as f:
    json.dump(r2.json(), f, indent=2)
# list the sub-agency names
for sub in r2.json()["results"]:
    print(sub["name"])
'''
Federal Highway Administration
Federal Aviation Administration
Federal Transit Administration
Federal Railroad Administration
Maritime Administration
National Highway Traffic Safety Administration
Immediate Office of the Secretary of Transportation
Federal Motor Carrier Safety Administration
Pipeline and Hazardous Materials Safety Administration
Saint Lawrence Seaway Development Corporation
'''

# list the federal accounts under DOT
agency_id = "731"
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
  "total": 1518330174.83,
  "end_date": "2024-09-30T00:00:00Z",
  "results": [
    {
      "id": "5055",
      "code": "1710",
      "type": "federal_account",
      "name": "Ready Reserve Force, Maritime Administration, Transportation",
      "amount": 1136580881.97,
      "account_number": "069-1710"
    },
    {
      "id": "5056",
      "code": "1711",
      "type": "federal_account",
      "name": "Maritime Security Program, Maritime Administration, Transportation",
      "amount": 311749292.86,
      "account_number": "069-1711"
    },
    {
      "id": "6468",
      "code": "1718",
      "type": "federal_account",
      "name": "Tanker Security Program, Maritime Administration, Transportation",
      "amount": 60000000.0,
      "account_number": "069-1718"
    },
    {
      "id": "6371",
      "code": "1717",
      "type": "federal_account",
      "name": "Cable Security Fleet, Maritime Administration, Transportation",
      "amount": 10000000.0,
      "account_number": "069-1717"
    }
  ]
}
'''

DOT_MARAD_ACCOUNTS = {"069-1710", "069-1711", "069-1718", "069-1717"}

# check DOT bulk data (toptier_agency_id 62, toptier_code 069)
dot_bulk_monthly = requests.post(
    "https://api.usaspending.gov/api/v2/bulk_download/list_monthly_files/",
    json={"agency": "62", "fiscal_year": 2024, "type": "contracts"},
    timeout=120
)
print(json.dumps(dot_bulk_monthly.json(), indent=2))

# unzip and open generated DOT bulk full data
dot_full_r = requests.get(dot_bulk_monthly.json()["monthly_files"][0]["url"], timeout=600)
with open("../bulk_data_samples/zip_dot_bulk_full.zip", "wb") as f:
    f.write(dot_full_r.content)

with zipfile.ZipFile("../bulk_data_samples/zip_dot_bulk_full.zip") as z:
    csv_names = [n for n in z.namelist() if n.endswith(".csv")]
    df_dot = pd.concat((pd.read_csv(z.open(n), low_memory=False) for n in csv_names), ignore_index=True)
print(len(df_dot.columns)) # 297

def funded_by(value, target_accounts):
    if pd.isna(value):
        return False
    tokens = [t.strip() for t in value.split(";")] 
    return any(t in target_accounts for t in tokens)  

# boolean masking - keep only rows where we have a DOT federal account as a value
dot_filtered = df_dot[df_dot["federal_accounts_funding_this_award"].apply(lambda v: funded_by(v, DOT_MARAD_ACCOUNTS))]

print(len(dot_filtered)) # 2838

print(dot_filtered[["awarding_agency_name", "funding_agency_name", "federal_action_obligation", "federal_accounts_funding_this_award",]].head())
'''
            awarding_agency_name           funding_agency_name  federal_action_obligation federal_accounts_funding_this_award
1   Department of Transportation  Department of Transportation                  248141.99                            069-1710
2   Department of Transportation         Department of Defense                       0.00                            069-1710
5   Department of Transportation  Department of Transportation                   35000.00                            069-1710
9   Department of Transportation         Department of Defense                       0.00                            069-1710
16  Department of Transportation  Department of Transportation                   51893.00                            069-1710
'''

print(dot_filtered["federal_action_obligation"].sum()) # 1024531655.9

print(dot_filtered.groupby(["awarding_agency_name", "funding_agency_name"]).size())
'''
awarding_agency_name          funding_agency_name         
Department of Transportation  Department of Defense           2207
                              Department of Transportation     631
dtype: int64
'''

for acct in sorted(DOT_MARAD_ACCOUNTS):
    rows = dot_filtered[dot_filtered["federal_accounts_funding_this_award"].apply(lambda v: funded_by(v, {acct}))]
    print(acct, len(rows), rows["federal_action_obligation"].sum())
'''
069-1710 2838 1024531655.9
069-1711 0 0.0
069-1717 0 0.0
069-1718 0 0.0
'''
# Only Ready Reserve Force (069-1710) produces Contracts/IDV activity, the other three accounts are subsidy programs

with zipfile.ZipFile("../bulk_data_samples/zip_dot_bulk_full.zip") as z:
    csv_names = [n for n in z.namelist() if n.endswith(".csv")]
    df_dot_check = pd.concat(
        (pd.read_csv(z.open(n), usecols=["awarding_agency_name", "funding_agency_name"]) for n in csv_names),
        ignore_index=True
    )
print(df_dot_check["awarding_agency_name"].value_counts())
'''
awarding_agency_name
Department of Transportation    33688
Name: count, dtype: int64
'''
print(df_dot_check["funding_agency_name"].value_counts())
'''
funding_agency_name
Department of Transportation    31301
Department of Defense            2311
Surface Transportation Board       76
Name: count, dtype: int64
'''