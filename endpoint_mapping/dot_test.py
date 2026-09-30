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