import requests, time
import json, zipfile
import pandas as pd
import os
from extract.prestage import prestage
from extract.sources import SOURCES
from extract.columns import COLUMNS
from extract.bulkfiles import list_monthly_files, download_monthly_files
from extract.prestage import filter_mask

CHECKS = [
    # ("dhs", 2024, "bulk_data_samples/zip_2024_dhs_bulk_full.zip"),
    # ("dot", 2024, "bulk_data_samples/zip_2024_dot_bulk_full.zip"),
    # ("dhs", 2018, None),
    # ("dot", 2017, None),
    # ("dot", 2018, None),
    ("dhs", 2017, None),
]

for name, fy, local_zip in CHECKS:
    source = SOURCES[name]
    col = source["filter"]["column"]

    if local_zip:
        zip_path = local_zip
    else:
        url = "https://files.usaspending.gov/award_data_archive/FY2017_070_Contracts_Full_20260906.zip"
        zip_path = download_monthly_files(url, os.path.join("bulk_data_samples", "FY2017_070_Contracts_Full_20260906.zip"))

    with zipfile.ZipFile(zip_path) as z:
        csv_names = [n for n in z.namelist() if n.endswith(".csv")]
        df = pd.concat(
            (pd.read_csv(z.open(n), dtype=str, usecols=[col, "federal_action_obligation", "award_or_idv_flag"])
             for n in csv_names),
            ignore_index=True,
        )

    blank = df[col].isna()
    obl = pd.to_numeric(df["federal_action_obligation"]).fillna(0)
    matched = filter_mask(df, source["filter"])

    print(f"\n{name} {fy}: rows={len(df)} matched={matched.sum()}")
    print(f"  blank rows={blank.mean():.3f}  blank dollars={obl[blank].abs().sum() / obl.abs().sum():.3f}")
    print(df.loc[blank, "award_or_idv_flag"].value_counts().to_string())

    if not local_zip:
        os.remove(zip_path)