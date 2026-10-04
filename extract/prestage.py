import zipfile
import pandas as pd
from extract.columns import COLUMNS, DELTA_ONLY_COLUMNS

def filter_mask(df, flt):
    col = df[flt["column"]]
    if flt["match"] == "exact":
        return col.isin(flt["values"])
    if flt["match"] == "any_token":
        tokens = col.str.split(";").explode().str.strip()
        return tokens.isin(flt["values"]).groupby(level=0).any()
    raise ValueError(f"Unknown match type: {flt['match']}")

def prestage(zip_path, source):
    csv_path = zip_path.replace(".zip", ".csv")
    cols = set(COLUMNS)

    with zipfile.ZipFile(zip_path) as z:
        csv_names = sorted(n for n in z.namelist() if n.endswith(".csv"))

        if not csv_names:
            raise ValueError(f"No csv found in {zip_path}")
        
        for i, name in enumerate(csv_names):
            with z.open(name) as f:
                df = pd.read_csv(f, dtype=str, usecols=lambda c: c in cols)

            missing = set(COLUMNS) - set(df.columns) - DELTA_ONLY_COLUMNS
            if missing:
                raise ValueError(f"{name} is missing expected columns: {sorted(missing)}")

            if source["filter"] is not None:
                df = df[filter_mask(df, source["filter"])]

            df = df.reindex(columns=COLUMNS) # returns df with exactly each COLUMNS in order, listed COLUMNS that DNE filled with NaN
            df.to_csv(csv_path, mode="w" if i == 0 else "a", header=(i == 0), index=False) # "w" creates file, "a" appends, only first part gets column header, no row pandas row index

    return csv_path