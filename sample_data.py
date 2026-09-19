#%%
import pandas as pd
pd.set_option('display.max_columns', None)
pd.set_option('display.float_format', lambda x: f'{x:,.2f}')

# Custom Award Data
df_prime = pd.read_csv(r"C:\Users\rkim\Desktop\Learning\national-defense-spending\bulk_files_sample\Prime_Transactions_Sample_2026.csv", nrows=20)
df_prime.columns.tolist()
df_prime

# Award Data Archive - Same columns as Prime_Transactions_Sample_2025.csv
# df_full = pd.read_csv(r"C:\Users\rkim\Desktop\Learning\national-defense-spending\bulk_files_sample\All_Contracts_Sample_2026.csv", nrows=20)
# df_full.columns.tolist()
# df_full