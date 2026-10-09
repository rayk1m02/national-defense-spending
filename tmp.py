import requests, time
import json, zipfile
import pandas as pd
import os
from extract.prestage import prestage
from extract.sources import SOURCES
from extract.columns import COLUMNS
from extract.bulkfiles import list_monthly_files, download_monthly_files
from extract.prestage import filter_mask

'''
pd.read_csv(path, dtype=str, chunksize=500_000) returns an iterator of DataFrames. You loop over it with for chunk in ....

chunk.apply(lambda s: s.str.encode('utf-8').str.len().max()) runs that expression on each column (apply on a DataFrame passes one column Series at a time) and returns a Series of max lengths indexed by column name.

Append each chunk’s result to a list, then pd.concat(results, axis=1).max(axis=1) lines them up side by side (axis=1 = as columns) and takes the max across chunks for each row (each original column).
'''

df_itr = pd.read_csv(r"downloads\dod\FY2017_097_Contracts_Full_20260906.csv", dtype=str, chunksize=500_000)
chunk_maxes = []
for chunk in df_itr:
    chunk_maxes.append(chunk.apply(lambda s: s.dropna().astype(str).str.encode('utf-8').str.len().max()))  
    # print(chunk[chunk["funding_agency_code"].str.len() > 3]["funding_agency_code"].unique())
# max_bytes = pd.concat(chunk_maxes, axis=1).max(axis=1) 
#max_bytes.to_csv("load/max_bytes.csv", index_label="column", header=["max_bytes"])
# print(max_bytes.sort_values(ascending=False).to_string())