import requests, json

# DRA - Defense Related Activites (budget function 054)

r3 = requests.post(
    "https://api.usaspending.gov/api/v2/spending/",
    json={"type": "agency", "filters": {"fy": "2024", "quarter": 4, "budget_subfunction": "054"}},
    timeout=30
)
print(json.dumps(r3.json(), indent=2))


for agency_id, agency_name in [("1173", "DOD"), ("252", "DOJ"), ("731", "DOT"), ("766", "DHS"), ("1143", "PCLOB")]:
    r = requests.post(
        "https://api.usaspending.gov/api/v2/spending/",
        json={
            "type": "federal_account",
            "filters": {"fy": "2024", "quarter": 4, "budget_subfunction": "054", "agency": agency_id}
        },
        timeout=30
    )
    print(f"--- {agency_name} ---")
    for acct in sorted(r.json()["results"], key=lambda x: x["amount"], reverse=True):
        print(f"{acct['name']:<70} {acct['amount']:,.2f}")
    print()

'''
Department of Defense                              161,105,000,000.00   1173
Department of Justice                              12,165,636,827.12    252
Department of Transportation                       1,518,330,174.83     731
Department of Homeland Security                    656,218,040.04       766
Privacy and Civil Liberties Oversight Board        11,648,086.29        1143
'''