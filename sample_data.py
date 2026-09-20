#%%
import pandas as pd
pd.set_option('display.max_columns', None)
pd.set_option('display.float_format', lambda x: f'{x:,.2f}')

# Custom Award Data
df_prime = pd.read_csv(r"C:\Users\rkim\Desktop\Learning\national-defense-spending\bulk_files_sample\Prime_Transactions_Sample_2026.csv", nrows=5)
df_prime.columns.tolist()

# Award Data Archive - Same columns as Prime_Transactions_Sample_2025.csv
# df_full = pd.read_csv(r"C:\Users\rkim\Desktop\Learning\national-defense-spending\bulk_files_sample\All_Contracts_Sample_2026.csv", nrows=20)
# df_full.columns.tolist()
# df_full

cols = [
    # Fact table candidates (identifiers + measures)
    # fct_transaction, PK = contract_transaction_unique_key
    "contract_transaction_unique_key",
    "contract_award_unique_key",
    "award_id_piid",
    "transaction_number",
    "modification_number",
    "action_type",
    "action_type_code",
    "federal_action_obligation",                # amount obligated by this transaction alone (flow, additive, safe to sum)
    "total_dollars_obligated",                  # cumulative obligated total for the whole award, as of this transaction (snapshot, not additive)
    "total_outlayed_amount_for_overall_award",  # actual cash disbursed for the whole award to date (snapshot, not additive)
    "current_total_value_of_award",             # contract's value = base period + options exercised so far (snapshot ceiling, "what it's worth right now")
    "potential_total_value_of_award",           # contract's value = base period + all possible options, whether exercised or not (snapshot ceiling, "max it could ever be worth")

    # Date dimension
    # dim_date, PK = action_date
    "action_date",                              # when action happened
    "action_date_fiscal_year",
    "period_of_performance_start_date",         # when the awarded work runs
    "period_of_performance_current_end_date",
    "solicitation_date",

    # Agency dimension (awarding [who issues and administers the contract] vs funding [whose budget the obligated dollars actually come from]).
    # Usually awarding and funding agency are the same as the department buys something and administers the contract itself.
    # dim_agency, PK (surrogate key needed)
    "awarding_agency_code",
    "awarding_agency_name",
    "awarding_sub_agency_name",
    "funding_agency_code",
    "funding_agency_name",
    "funding_sub_agency_name",

    # Recipient dimension (SCD2 candidate)
    # dim_recipient, PK (surrogate key needed) since recipient_uei can change
    "recipient_uei",
    "recipient_name",
    "recipient_parent_uei",
    "recipient_parent_name",
    "recipient_state_code",
    "veteran_owned_business",
    "woman_owned_business",
    "women_owned_small_business",
    "minority_owned_business",
    "small_disadvantaged_business",
    "c8a_program_participant",
    "historically_underutilized_business_zone_hubzone_firm",
    "contracting_officers_determination_of_business_size",

    # Place of performance dimension
    # dim_location, PK (surrogate key needed) with grain of state, county, city, country
    "primary_place_of_performance_state_code", 
    "primary_place_of_performance_state_name",
    "primary_place_of_performance_city_name",
    "primary_place_of_performance_county_name",
    "primary_place_of_performance_country_name",

    # Product/service classification dimension
    # dim_product, PK (surrogate key needed) with grain of naisc code, product_or_service code
    "naics_code",
    "naics_description",
    "product_or_service_code",
    "product_or_service_code_description",

    # Award type / IDV dimension
    # dim_award, PK (surrogate key needed) with grain of award_type_code, idv_type, related fields
    "award_or_idv_flag",
    "award_type_code",
    "award_type",
    "idv_type",
    "parent_award_id_piid",         # self-referencing key
    "parent_award_type",
    "multiple_or_single_award_idv",
    "type_of_idc",

    # Competition / set-aside (junk dimension candidate)
    # dim_competition, PK (surrogate key needed) with grain of related fields
    "extent_competed",
    "type_of_set_aside",
    "other_than_full_and_open_competition",
    "number_of_offers_received",
]

df_prime[cols]