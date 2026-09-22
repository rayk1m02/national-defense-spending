import requests, time, json

### ----------------------------------------------------------------------------------------------------------------------------- ###

# testing the /api/v2/download/* API for DOD

payload = {
    "filters": {
        "agencies": [{"type": "awarding", "tier": "toptier", "name": "Department of Energy"}],
        "award_type_codes": ["A"],
        "time_period": [{"start_date": "2024-01-01", "end_date": "2024-01-31"}],
    },
    "spending_level": ["transactions"],
    "columns": []  # empty = all columns
}

r = requests.post("https://api.usaspending.gov/api/v2/download/search/", json=payload, timeout=30)
result = r.json()
print(r.status_code)
print(json.dumps(result, indent=2))

status_url = result["status_url"]

while True:
    r = requests.get(status_url, timeout=30)
    data = r.json()
    print(data.get("status"), data.get("message", ""))
    if data.get("status") in ("finished", "failed"):
        break
    time.sleep(5)

print(json.dumps(data, indent=2))

### ----------------------------------------------------------------------------------------------------------------------------- ###

# r2 = requests.get(f"https://api.usaspending.gov/api/v2/agency/089/sub_agency/", timeout=30)
# print(r2.status_code)
# print(json.dumps(r2.json(), indent=2))