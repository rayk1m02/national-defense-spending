import requests, time
import json, zipfile
import pandas as pd

with zipfile.ZipFile("../bulk_data_samples/dod_bulk_full.zip") as z:
    csv_name = [n for n in z.namelist() if n.endswith(".csv")][0]
    with z.open(csv_name) as f:
        df = pd.read_csv(f, nrows=5)

pd.Series(df.columns, name="column").to_csv("../bulk_data_samples/dod_bulk_full_columns.csv", index=False)