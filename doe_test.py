import requests, time, json

# investigating DOE dollar break down (NNSA), find real agency IDs, check if pre-generated files exist for DOE, figuring out NNSA search name

### ----------------------------------------------------------------------------------------------------------------------------- ###

# scoping DOE sub agencies (we assume 089 is the National Nuclear Security Administration). 
# we see that NNSA makes up about half of DOE's total spending. The rest are non-defense energy programs.
r = requests.get("https://api.usaspending.gov/api/v2/agency/089/sub_agency/", timeout=30)
print(r.status_code)
print(json.dumps(r.json(), indent=2))

### ----------------------------------------------------------------------------------------------------------------------------- ###

# get real agency IDs
r = requests.post(
    "https://api.usaspending.gov/api/v2/bulk_download/list_agencies/",
    json={"type": "award_agencies"},
    timeout=30
)
print(r.status_code)
agencies = r.json()

cfo = agencies["agencies"]["cfo_agencies"]
doe = next(a for a in cfo if "Energy" in a["name"]) # next() pulls first item out of iterator, then raises StopIteration
dod = next(a for a in cfo if "Defense" in a["name"])
print("DOE:", doe) # 089
print("DoD:", dod) # 097

# see DOE's break down by sub-agency (how much is NNSA). This component mirros block 1, but we use and verify with the official agency ID here.
r2 = requests.get(f"https://api.usaspending.gov/api/v2/agency/{doe['toptier_code']}/sub_agency/", timeout=30)
print(r2.status_code)
print(json.dumps(r2.json(), indent=2))

# check if DOE has pre-generated files and if we can filter by NNSA (we cannot). 
# given that, we will need to use /api/v2/download/* instead of /api/v2/bulk_download/* for DOE data
r3 = requests.post(
    "https://api.usaspending.gov/api/v2/bulk_download/list_monthly_files/",
    json={"agency": doe["toptier_agency_id"], "fiscal_year": 2024, "type": "contracts"},
    timeout=30
)
print(r3.status_code)
print(json.dumps(r3.json(), indent=2))

### ----------------------------------------------------------------------------------------------------------------------------- ###

# finding NNSA org search name

payload = {
    "filters": {
        "agencies": [
            {"type": "awarding", "tier": "subtier", "name": "NNSA MO CONTRACTING", "toptier_name": "Department of Energy"}
        ],
        "time_period": [{"start_date": "2023-10-01", "end_date": "2024-09-30"}]  # full FY2024, no award_type_codes filter yet
    },
    "spending_level": ["transactions"],
    "columns": []
}

r = requests.post("https://api.usaspending.gov/api/v2/download/search/", json=payload, timeout=30)
result = r.json()
print(r.status_code, result)

status_url = result["status_url"]
while True:
    r = requests.get(status_url, timeout=30)
    data = r.json()
    if data.get("status") in ("finished", "failed"):
        break
    time.sleep(5)
print(json.dumps(data, indent=2))