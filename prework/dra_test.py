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
dra = next(a for a in cfo if "Homeland Security" in a["name"])
print("DRA:", dra) # 070

# see DRA sub-agency breakdown
r1 = requests.get(f"https://api.usaspending.gov/api/v2/agency/{dra['toptier_code']}/budget_function/?fiscal_year=2024", timeout=30)
print(json.dumps(r1.json(), indent=2))

'''
{
    "name": "National Defense",
    "children": [
    {
        "name": "Defense-related activities",
        "obligated_amount": 656218040.04,
        "gross_outlay_amount": 728327839.95
    }
    ],
    "obligated_amount": 656218040.04,
    "gross_outlay_amount": 728327839.95
},

Conclusion: 656M (DRA) against roughly 850B (National Defense) is about 0.08% - negligible.
'''