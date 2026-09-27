import requests, json

# each federal account under each sub-agency and their spend
for agency_id, agency_name in [("1173", "DOD"), ("252", "DOJ"), ("731", "DOT"), ("766", "DHS"), ("1143", "PCLOB")]:
    r = requests.post(
        "https://api.usaspending.gov/api/v2/spending/",
        json={
            "type": "federal_account",
            "filters": {"fy": "2024", "quarter": 4, "budget_subfunction": "054", "agency": agency_id}
        },
        timeout=120
    )
    print(json.dumps(r.json(), indent=2))

    # print(f"--- {agency_name} ---")
    # print(json.dumps(r.json()["results"], indent=2))

    # print(f"--- {agency_name} ---")
    # for acct in sorted(r.json()["results"], key=lambda x: x["amount"], reverse=True):
    #     print(f"{acct['name']:<70} {acct['amount']:,.2f} {acct['account_number']}")
    #     # print(json.dumps(r.json()["results"], indent=2)) -- SEE BELOW (duplication)
    # print() 