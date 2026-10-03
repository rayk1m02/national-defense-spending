import requests, time
import json, zipfile
import pandas as pd


DOE_053_ACCOUNTS = {"089-0240", "089-0251", "089-0309", "089-0314", "089-0243", "089-0313", "089-0244", "089-0249"}

def funded_by(value, target_accounts):
    if pd.isna(value):
        return False
    tokens = [t.strip() for t in value.split(";")]     # tokens will be a clean list of federal accounts
    return any(t in target_accounts for t in tokens)   # any() - eg. an award funded by three accounts, only one of which is in our target, will still count  

def funded_only_by(value, target_accounts):
    if pd.isna(value):
        return False
    tokens = [t.strip() for t in value.split(";")]
    return all(t in target_accounts for t in tokens)

with zipfile.ZipFile("../bulk_data_samples/zip_2024_doe_bulk_full.zip") as z:
    csv_name = [n for n in z.namelist() if n.endswith(".csv")][0]
    with z.open(csv_name) as f:
        df = pd.read_csv(f, low_memory=False, dtype={"awarding_office_code": str})

idaho = df[df["awarding_office_code"] == "892432"] 
is_053 = idaho["federal_accounts_funding_this_award"].apply(lambda v: funded_by(v, DOE_053_ACCOUNTS))
# print(idaho.groupby(is_053)["federal_action_obligation"].agg(["count", "sum"]))

only_053 = idaho["federal_accounts_funding_this_award"].apply(lambda v: funded_only_by(v, DOE_053_ACCOUNTS))

mixed = idaho[is_053 & ~only_053]
print(mixed.nlargest(10, "federal_action_obligation")[
    ["award_id_piid", "recipient_name", "federal_action_obligation", "federal_accounts_funding_this_award"]
].to_string(index=False))