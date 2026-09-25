import requests, json
import pandas as pd
import zipfile

# DRA - Defense Related Activites (budget function 054)

'''
For Reference:

Department of Defense                              161,105,000,000.00   #1173
Department of Justice                              12,165,636,827.12    #252
Department of Transportation                       1,518,330,174.83     #731
Department of Homeland Security                    656,218,040.04       #766
Privacy and Civil Liberties Oversight Board        11,648,086.29        #1143
'''

# each sub-agency under DRA and their spend
r = requests.post(
    "https://api.usaspending.gov/api/v2/spending/",
    json={"type": "agency", "filters": {"fy": "2024", "quarter": 4, "budget_subfunction": "054"}},
    timeout=30
)
# print(json.dumps(r.json(), indent=2))
'''
eg:

  "end_date": "2024-09-30T00:00:00Z",
  "results": [
    {
      "id": "1173",
      "code": "097",
      "type": "agency",
      "name": "Department of Defense",
      "amount": 161105000000.0,
      "link": true
    },
    {
      "id": "252",
      "code": "015",
      "type": "agency",
      "name": "Department of Justice",
      "amount": 12165636827.12,
      "link": true
    },
'''

# each federal account under each sub-agency and their spend
for agency_id, agency_name in [("1173", "DOD"), ("252", "DOJ"), ("731", "DOT"), ("766", "DHS"), ("1143", "PCLOB")]:
    r = requests.post(
        "https://api.usaspending.gov/api/v2/spending/",
        json={
            "type": "federal_account",
            "filters": {"fy": "2024", "quarter": 4, "budget_subfunction": "054", "agency": agency_id}
        },
        timeout=30
    )
    # print(f"--- {agency_name} ---")
    # for acct in sorted(r.json()["results"], key=lambda x: x["amount"], reverse=True):
    #     print(f"{acct['name']:<70} {acct['amount']:,.2f}")
    # print()
'''
eg:

--- DOJ ---
Salaries and Expenses, Federal Bureau of Investigation, Justice        12,033,323,454.69
Payment to the Radiation Exposure Compensation Trust Fund, Justice     80,000,000.00
Radiation Exposure Compensation Trust Fund, Justice                    52,313,372.43
'''

# find dhs id
r1 = requests.post(
    "https://api.usaspending.gov/api/v2/bulk_download/list_agencies/",
    json={"type": "award_agencies"},
    timeout=30
)
dhs = next(a for a in r1.json()["agencies"]["cfo_agencies"] if "Homeland Security" in a["name"])
# print(dhs) 
# {'name': 'Department of Homeland Security', 'toptier_agency_id': 63, 'toptier_code': '070'}

# each sub-agency under DHS
r2 = requests.get(
    f"https://api.usaspending.gov/api/v2/agency/{dhs['toptier_code']}/sub_agency/?fiscal_year=2024",
    timeout=30
)
# for sub in r2.json()["results"]:
#     print(sub["name"])
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
# since our sub-agency under DHS does not show DHS-CISA, we use DOD zip file to see if we can filter by column in bulk download url
with zipfile.ZipFile(r"C:\Users\rkim\Desktop\Learning\national-defense-spending\endpoint_mapping\dod_test.zip") as z:
    print(z.namelist())
    with z.open(z.namelist()[0]) as f:
        df = pd.read_csv(f, nrows=5)
matches = [c for c in df.columns if "treasury" in c.lower() or "federal_account" in c.lower()]
# print(matches)
'''
['FY2024_097_Contracts_Full_20260906_1.csv', 'FY2024_097_Contracts_Full_20260906_2.csv', 'FY2024_097_Contracts_Full_20260906_3.csv', 'FY2024_097_Contracts_Full_20260906_4.csv', 'FY2024_097_Contracts_Full_20260906_5.csv']
['treasury_accounts_funding_this_award', 'federal_accounts_funding_this_award']
'''

# find the format those values come in
with zipfile.ZipFile(r"C:\Users\rkim\Desktop\Learning\national-defense-spending\endpoint_mapping\dod_test.zip") as z:
    with z.open(z.namelist()[0]) as f:
        df = pd.read_csv(f, usecols=["treasury_accounts_funding_this_award", "federal_accounts_funding_this_award"], nrows=20)
# for val in df["treasury_accounts_funding_this_award"].dropna().unique()[:10]:
#     print(repr(val))
'''
['FY2024_097_Contracts_Full_20260906_1.csv', 'FY2024_097_Contracts_Full_20260906_2.csv', 'FY2024_097_Contracts_Full_20260906_3.csv', 'FY2024_097_Contracts_Full_20260906_4.csv', 'FY2024_097_Contracts_Full_20260906_5.csv']
'021-2024/2024-2020-000'
'057-2022/2022-3400-000;057-2023/2023-3400-000;057-2024/2024-3400-000;057-2025/2025-3400-000;057-2026/2026-3400-000;097-2022/2022-0130-000;097-2023/2023-0130-000'
'097-2023/2023-0100-000;097-2024/2024-0100-000;097-2025/2025-0100-000'
'017-2023/2023-1804-000'
'021-2014/2014-2020-000;021-2015/2015-2020-000;021-2016/2016-2020-000;021-2017/2017-2020-000;021-2018/2018-2020-000;021-2019/2019-2020-000;021-2020/2020-2020-000;021-2021/2021-2020-000;021-2022/2022-2020-000;021-2023/2023-2020-000;021-2024/2024-2020-000;021-2025/2025-2020-000;097-2014/2014-0130-000'
'''
# for val in df["federal_accounts_funding_this_award"].dropna().unique()[:10]:
#     print(repr(val))
'''
'021-2020'
'057-3400;097-0130'
'097-0100'
'017-1804'
'021-2020;097-0130'
'''

# context
    # agency_code:          federal agency (DOD: 097, DHS: 070, DOJ: 015, etc)
    # main_account_code:    federal account under an agency (Procurement, Construction, and..: 0412, Ready Reserve Force, Maritime...: 1710)
    # sub_account_code:     further subdivision within a federal account (so far every example has shown 000, general fund)

# treasury_accounts_funding_this_award holds <agency_code>-<period of availability>-<main_account_code>-<sub_account_code>
    # 097-2023/2023-0100-000
        # 097: DOD agency code
        # 2023/2023: fiscal year
        # 0100: main account code
        # 000: no sub-account

# federal_accounts_funding_this_award holds just the <agency_code>-<main_account_code>

for agency_id, agency_name in [("766", "DHS"), ("731", "DOT")]:
    r = requests.post(
        "https://api.usaspending.gov/api/v2/spending/",
        json={
            "type": "federal_account",
            "filters": {"fy": "2024", "quarter": 4, "budget_subfunction": "054", "agency": agency_id}
        },
        timeout=30
    )
    # print(f"--- {agency_name} ---")
    # print(json.dumps(r.json()["results"], indent=2))
'''
--- DHS ---
[
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
'''

# * account_number field from api/v2/spending/ with budget_subfunction 054 and agency_id, matches our federal_accounts_funding_this_award column values
DHS_CISA_ACCOUNTS = {"070-0412", "070-0805", "070-0565", "070-1911"}
DOT_MARAD_ACCOUNTS = {"069-1710", "069-1711", "069-1718", "069-1717"}

# zip process for DHS (toptier 070) and DOT (toptier 069)
# implement

# def funded_by(value, target_accounts):
#     if pd.isna(value):
#         return False
#     tokens = [t.strip() for t in value.split(";")]
#     return any(t in target_accounts for t in tokens)

# dhs_filtered = df_dhs[df_dhs["federal_accounts_funding_this_award"].apply(lambda v: funded_by(v, DHS_CISA_ACCOUNTS))]
# dot_filtered = df_dot[df_dot["federal_accounts_funding_this_award"].apply(lambda v: funded_by(v, DOT_MARAD_ACCOUNTS))]