import zipfile
import pandas as pd
from extract.columns import COLUMNS, DELTA_ONLY_COLUMNS
from extract.settings import FIRST_FISCAL_YEAR

# eg. flt:
# flt = {
#     "column": "federal_accounts_funding_this_award",
#     "match": "any_token",
#     "values": ["069-1710", "069-1711", "069-1718", "069-1717"],
# }
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

    with zipfile.ZipFile(zip_path) as z: # opens zip without extracting to disk (reads packing list / info)
        csv_names = sorted(n for n in z.namelist() if n.endswith(".csv")) # list the csv parts inside the zip, in order by name

        if not csv_names:
            raise ValueError(f"No csv found in {zip_path}")
        
        for i, name in enumerate(csv_names):
            with z.open(name) as f: # open stream
                df = pd.read_csv(f, dtype=str, usecols=lambda c: c in cols) # read and build df in RAM, usecols trims columns to our set of columns

            missing = set(COLUMNS) - set(df.columns) - DELTA_ONLY_COLUMNS # fail if USASpending dropped or renamed a column we need (delta "correction_delete_ind" field ('C'=correction, 'D'=deleted, ''=new) is excused)
            if missing:
                raise ValueError(f"{name} is missing expected columns: {sorted(missing)}")

            if source["filter"] is not None:
                df = df[filter_mask(df, source["filter"])]

            fy = pd.to_numeric(df["action_date_fiscal_year"])
            df = df[fy.isna() | (fy >= FIRST_FISCAL_YEAR)] 

            df = df.reindex(columns=COLUMNS)                                                # returns df with exactly each COLUMNS in order, listed COLUMNS that DNE filled with NaN
            df.to_csv(csv_path, mode="w" if i == 0 else "a", header=(i == 0), index=False)  # "w" creates file, "a" appends, only first part gets column header, no pandas row index

    return csv_path