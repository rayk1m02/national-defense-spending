SOURCES = {
    "dod": {
        "agency_id": 126,
        "toptier_code": "097",
        "has_delta_file": True,
        "filter": None,
    },
    "doe": {
        "agency_id": 78,
        "toptier_code": "089",
        "has_delta_file": True,
        "filter": {
            "column": "awarding_office_code",
            "match": "exact",                                                   # cell holds one value
            "values": [
                "892332", "892330", "892331",                                   # NNSA (National Nuclear Security Administration)
                "893033", "893035", "893031", "893042", "893034", "893032",     # EM (Environmental Management)
                "893039",                                                       # Hanford Field Office
                "893040",                                                       # Office of River Protection
            ]
        }
    },
    "dhs": {
        "agency_id": 63,
        "toptier_code": "070",
        "has_delta_file": False,
        "filter": {
            "column": "federal_accounts_funding_this_award",
            "match": "any_token",                                       # cell can hold several values separated by ";"
            "values": [
                "070-0412", "070-0805", "070-0565", "070-1911"          # CISA (Cybersecurity and Infrastructure Security Agency)
            ]
        }
    },
    "dot": {
        "agency_id": 62,
        "toptier_code": "069",
        "has_delta_file": True,
        "filter": {
            "column": "federal_accounts_funding_this_award",
            "match": "any_token",
            "values": ["069-1710", "069-1711", "069-1718", "069-1717"]  # MARAD (Maritime Administration, Transportation)
        }
    }
}