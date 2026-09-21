import requests, time

payload = {
    "filters": {
        "agencies": [{"type": "awarding", "tier": "toptier", "name": "Department of Defense"}],
        "award_type_codes": ["A"],
        "time_period": [{"start_date": "2024-01-01", "end_date": "2024-01-31"}],
    },
    "spending_level": ["transactions"],
    "columns": []  # empty = all columns
}

r = requests.post("https://api.usaspending.gov/api/v2/download/search/", json=payload, timeout=30)
result = r.json()
print(r.status_code)
print(result)

status_url = result["status_url"]

while True:
    r = requests.get(status_url, timeout=30)
    data = r.json()
    print(data.get("status"), data.get("message", ""))
    if data.get("status") in ("finished", "failed"):
        break
    time.sleep(5)

print(data)