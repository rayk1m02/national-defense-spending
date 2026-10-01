import requests, json
import pandas as pd
import zipfile

# DRA - Defense Related Activites (budget subfunction 054)

# list out the agencies under budget subfunction 054 and their spend
r = requests.post(
    "https://api.usaspending.gov/api/v2/spending/",
    json={"type": "agency", "filters": {"fy": "2024", "quarter": 4, "budget_subfunction": "054"}},
    timeout=120
)
print(json.dumps(r.json(), indent=2))
'''
{
  "total": 175456833128.28,
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
    {
      "id": "731",
      "code": "069",
      "type": "agency",
      "name": "Department of Transportation",
      "amount": 1518330174.83,
      "link": true
    },
    {
      "id": "766",
      "code": "070",
      "type": "agency",
      "name": "Department of Homeland Security",
      "amount": 656218040.04,
      "link": true
    },
    {
      "id": "1143",
      "code": "535",
      "type": "agency",
      "name": "Privacy and Civil Liberties Oversight Board",
      "amount": 11648086.29,
      "link": true
    }
  ]
}
'''

# each agencies federal account and associated spend
for agency_id, agency_name in [("1173", "DOD"), ("252", "DOJ"), ("731", "DOT"), ("766", "DHS"), ("1143", "PCLOB")]:
    r = requests.post(
        "https://api.usaspending.gov/api/v2/spending/",
        json={
            "type": "federal_account",
            "filters": {"fy": "2024", "quarter": 4, "budget_subfunction": "054", "agency": agency_id}
        },
        timeout=120
    )
    print(f"{agency_name}")
    for acnt in sorted(r.json()["results"], key=lambda x: x["amount"], reverse=True):       # returns new sorted list. sorted(iterable, key=use each agencies amount, descending)
        print(f"{acnt['name']:<120} {acnt['amount']:<20,.2f} {acnt['account_number']}")     # '<' left-align with minimum X characters
    print() 
'''
DOD
Payments to Military Retirement Fund, Defense                                                                            151,521,000,000.00   097-0040    # intragovernment fund transfer, no contribution to Contracts/IDV activity
Payment to Department of Defense Medicare-Eligible Retiree Health Care Fund                                              9,584,000,000.00     097-0850    # intragovernment fund transfer, no contribution to Contracts/IDV activity

DOJ
Salaries and Expenses, Federal Bureau of Investigation, Justice                                                          12,033,323,454.69    015-0200    # umbrella operating account (not all is defense spend, not useable at individual award level)
Payment to the Radiation Exposure Compensation Trust Fund, Justice                                                       80,000,000.00        015-0333    # compensation programs, unlikely to have Contracts/IDV activity
Radiation Exposure Compensation Trust Fund, Justice                                                                      52,313,372.43        015-8116    # compensation programs, unlikely to have Contracts/IDV activity

DOT
Ready Reserve Force, Maritime Administration, Transportation                                                             1,136,580,881.97     069-1710
Maritime Security Program, Maritime Administration, Transportation                                                       311,749,292.86       069-1711
Tanker Security Program, Maritime Administration, Transportation                                                         60,000,000.00        069-1718
Cable Security Fleet, Maritime Administration, Transportation                                                            10,000,000.00        069-1717

DHS
Procurement, Construction, and Improvements, Cybersecurity and Infrastructure Security Agency, Homeland Security         506,501,490.81       070-0412
Federal Assistance, Countering Weapons of Mass Destruction Office, Homeland Security                                     146,403,866.15       070-0411
Research and Development, Cybersecurity and Infrastructure Security Agency, Homeland Security                            3,312,683.08         070-0805
Infrastructure Protection and Information Security, Cybersecurity and Infrastructure Security Agency, Homeland Security  0.00                 070-0565
Cybersecurity Response and Recovery Fund, Cybersecurity and Infrastructure Security Agency, Homeland Security.           0.00                 070-1911

PCLOB
Salaries and Expenses, Privacy and Civil Liberties Oversight Board                                                       11,648,086.29        535-2724    # ~11M, immaterial
'''

# See dhs_test.py and dot_test.py for continuation