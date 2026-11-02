# this file writes the CREATE SCHEMA and CREATE TABLE SQL for raw_nds.contract_transaactions so that we do not hand-type the 68 columns.
# run this once, then run the generated ddl/raw_contract_transactions.sql in Redshift

import pandas as pd

from extract.columns import COLUMNS

'''
df_itr = pd.read_csv(r"downloads\dod\FY....csv", dtype=str, chunksize=500_000) # iterator of DataFrames
for chunk in df_itr:
    chunk_maxes.append(chunk.apply(lambda s: s.dropna().astype(str).str.encode('utf-8').str.len().max())) # chunk.apply() runs lambda once per column
max_bytes = pd.concat(chunk_maxes, axis=1).max(axis=1) # takes the max across chunks per column.
'''
MAX_BYTES_PATH = "load/max_bytes.csv"
DDL_PATH = "load/ddl/raw_contract_transactions.sql"

# max observed bytes, declared width
TIERS = [(8, 16), (32, 64), (64, 128), (128, 256), (256, 512)]
OVERRIDES = {
    "federal_accounts_funding_this_award": 4096,    # this column's values are ";" separated, no fixed max
    "correction_delete_ind": 16,                    # this column's values are blank in the Full files
}
METADATA_COLUMNS = [
    "source varchar(16)",
    "source_file varchar(512)",
    "_loaded_at timestamp DEFAULT GETDATE()",
]


# smallest width whose tier fits n
def tier_width(n):
    for max_bytes, declared_width in TIERS:
        if n <= max_bytes:
            return declared_width
    raise ValueError(f"no tier for {n} bytes")


def build_ddl(max_bytes):
    lines = []
    for col in COLUMNS:
        if col in OVERRIDES:
            width = OVERRIDES[col]
        else:
            width = tier_width(max_bytes[col])
        lines.append(f"    {col} varchar({width})")
    for line in METADATA_COLUMNS:
        lines.append(f"    {line}")
    body = ",\n".join(lines)
    return f"""CREATE SCHEMA IF NOT EXISTS raw_nds;

CREATE TABLE IF NOT EXISTS raw_nds.contract_transactions (
{body}
);
"""


if __name__ == "__main__":
    max_bytes = pd.read_csv(MAX_BYTES_PATH, index_col=0).iloc[:,0]
    with open(DDL_PATH, "w") as f:
        f.write(build_ddl(max_bytes))