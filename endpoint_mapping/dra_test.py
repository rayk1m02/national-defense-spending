import requests, time
import json, zipfile
import pandas as pd

# DRA - Defense Related Activites (budget function 054)

# list agencies
r = requests.post(
    "https://api.usaspending.gov/api/v2/bulk_download/list_agencies/",
    json={"type": "award_agencies"},
    timeout=30
)
agencies = r.json()

# find DRA toptier_code
cfo = agencies["agencies"]["cfo_agencies"]
dra = next(a for a in cfo if "Homeland Security" in a["name"]) # check other agencies as well.
# print("DRA:", dra) # 070

# see DRA sub-agency breakdown
r1 = requests.get(f"https://api.usaspending.gov/api/v2/agency/{dra['toptier_code']}/budget_function/?fiscal_year=2024", timeout=30)
# print(json.dumps(r1.json(), indent=2))

'''
Updated reasoning: 054 is NOT negligible in dollar terms. 
DHS + DoD have only been confirmed as two of the agencies holding 054 dollars, not necessarily all of them. 
Government-wide agency breakdown for 054 (via /api/v2/spending/, type=agency, filtered on the 054 subfunction id) pending
'''

hits = []
url = "https://api.usaspending.gov/api/v2/agency/097/federal_account/?fiscal_year=2024&limit=100"

while url:
    r = requests.get(url, timeout=30)
    data = r.json()
    for account in data["results"]:
        for child in account["children"]:
            hits.append((child["name"], child["obligated_amount"]))
    next_page = data["page_metadata"]["next"]
    url = f"https://api.usaspending.gov/api/v2/agency/097/federal_account/?fiscal_year=2024&limit=100&page={next_page}" if next_page else None

for name, amt in hits:
    if any(kw in name.lower() for kw in ["retire", "health", "medicare"]):
        print(name, amt)